"""
Integración con Mercado Pago (Checkout Pro, modelo marketplace) según la documentación oficial:

* OAuth del vendedor:   https://auth.mercadopago.com.ar/authorization  +  POST /oauth/token
* Preferencia de pago:  POST /checkout/preferences   (con el access_token DEL VENDEDOR y marketplace_fee)
* Notificaciones:       webhook "payment" con cabecera x-signature (HMAC-SHA256); el estado real se
                        consulta siempre con GET /v1/payments/{id}, nunca se confía en el cuerpo recibido.

Pendiente de validar contra sandbox cuando haya credenciales reales (MP_CLIENT_ID, MP_CLIENT_SECRET,
MP_WEBHOOK_SECRET). Los tests usan respuestas simuladas.
"""
import hashlib
import hmac
import logging
from datetime import timedelta
from decimal import Decimal
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.core import signing
from django.db import transaction
from django.utils import timezone

from payments.models import Payment

log = logging.getLogger(__name__)

API = 'https://api.mercadopago.com'
AUTH_URL = 'https://auth.mercadopago.com.ar/authorization'
TIMEOUT = 15

STATUS_MAP = {
    'approved': 'paid',
    'authorized': 'pending',
    'pending': 'pending',
    'in_process': 'pending',
    'in_mediation': 'pending',
    'rejected': 'failed',
    'cancelled': 'failed',
    'refunded': 'refunded',
    'charged_back': 'refunded',
}


class MercadoPagoError(Exception):
    pass


def is_configured():
    return bool(settings.MP_CLIENT_ID and settings.MP_CLIENT_SECRET)


def callback_url():
    return f'{settings.BACKEND_PUBLIC_URL}/api/payments/mercadopago/oauth/callback/'


# ------------------------------------------------------------------ OAuth
def authorization_url(shop):
    if not is_configured():
        raise MercadoPagoError('La plataforma no tiene credenciales de Mercado Pago configuradas.')
    state = signing.dumps({'shop': shop.pk}, salt='mp-oauth')
    return AUTH_URL + '?' + urlencode({
        'client_id': settings.MP_CLIENT_ID, 'response_type': 'code', 'platform_id': 'mp',
        'state': state, 'redirect_uri': callback_url(),
    })


def read_state(state, max_age=900):
    try:
        return signing.loads(state, salt='mp-oauth', max_age=max_age)['shop']
    except (signing.BadSignature, KeyError):
        raise MercadoPagoError('Estado OAuth inválido o vencido.')


def _oauth_token(payload):
    resp = requests.post(f'{API}/oauth/token', json=payload, timeout=TIMEOUT,
                         headers={'accept': 'application/json'})
    if resp.status_code != 200:
        log.warning('MP oauth/token falló: %s %s', resp.status_code, resp.text[:300])
        raise MercadoPagoError('Mercado Pago rechazó la autorización.')
    return resp.json()


def connect_with_code(payment_settings, code):
    data = _oauth_token({
        'client_id': settings.MP_CLIENT_ID, 'client_secret': settings.MP_CLIENT_SECRET,
        'grant_type': 'authorization_code', 'code': code, 'redirect_uri': callback_url(),
    })
    payment_settings.set_mp_tokens(data['access_token'], data.get('refresh_token'), data.get('expires_in'),
                                   data.get('user_id'), data.get('public_key', ''))
    payment_settings.save()


def valid_token(payment_settings):
    """Access token del vendedor; se renueva con el refresh_token si está por vencer."""
    exp = payment_settings.mp_expires_at
    if exp and exp - timezone.now() < timedelta(days=1) and payment_settings.mp_refresh_token:
        data = _oauth_token({
            'client_id': settings.MP_CLIENT_ID, 'client_secret': settings.MP_CLIENT_SECRET,
            'grant_type': 'refresh_token', 'refresh_token': payment_settings.mp_refresh_token,
        })
        payment_settings.set_mp_tokens(data['access_token'], data.get('refresh_token'), data.get('expires_in'),
                                       data.get('user_id'), data.get('public_key', ''))
        payment_settings.save()
    return payment_settings.mp_access_token


# ------------------------------------------------------------------ Preferencia
def create_preference(order, payment_settings):
    token = valid_token(payment_settings)
    if not token:
        raise MercadoPagoError('La tienda no tiene Mercado Pago conectado.')
    front = settings.FRONTEND_URL.rstrip('/')
    back = f'{front}/pedido/{order.public_token}'
    body = {
        'items': [{
            'id': str(i.product_id or i.pk), 'title': i.name[:250], 'quantity': i.quantity,
            'unit_price': float(i.unit_price), 'currency_id': 'ARS',
        } for i in order.items.all()],
        'external_reference': str(order.pk),
        'back_urls': {'success': back, 'pending': back, 'failure': back},
        'statement_descriptor': 'MULTIMARKET',
    }
    if order.buyer_email:
        body['payer'] = {'name': order.buyer_name, 'email': order.buyer_email}
    if front.startswith('https://'):
        body['auto_return'] = 'approved'
    if settings.BACKEND_PUBLIC_URL.startswith('https://'):  # MP exige una URL pública
        body['notification_url'] = f'{settings.BACKEND_PUBLIC_URL}/api/payments/mercadopago/webhook/?order={order.pk}'
    if order.platform_fee and order.platform_fee > 0:
        body['marketplace_fee'] = float(order.platform_fee)

    resp = requests.post(f'{API}/checkout/preferences', json=body, timeout=TIMEOUT,
                         headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'})
    if resp.status_code not in (200, 201):
        log.warning('MP preferencia falló: %s %s', resp.status_code, resp.text[:300])
        raise MercadoPagoError('No pudimos iniciar el pago con Mercado Pago.')
    data = resp.json()
    url = data.get('sandbox_init_point') if settings.MP_USE_SANDBOX_URL else data.get('init_point')
    return {'preference_id': data.get('id'), 'init_point': url or data.get('init_point')}


# ------------------------------------------------------------------ Webhook
def verify_signature(secret, signature_header, request_id, data_id):
    """Valida x-signature: HMAC-SHA256 sobre 'id:<data.id>;request-id:<x-request-id>;ts:<ts>;'."""
    if not (signature_header and data_id):
        return False
    parts = dict(p.strip().split('=', 1) for p in signature_header.split(',') if '=' in p)
    ts, v1 = parts.get('ts'), parts.get('v1')
    if not ts or not v1:
        return False
    manifest = f'id:{str(data_id).lower()};request-id:{request_id or ""};ts:{ts};'
    expected = hmac.new(secret.encode(), manifest.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, v1)


def fetch_payment(payment_id, token):
    resp = requests.get(f'{API}/v1/payments/{payment_id}', timeout=TIMEOUT,
                        headers={'Authorization': f'Bearer {token}'})
    if resp.status_code != 200:
        raise MercadoPagoError(f'No se pudo consultar el pago {payment_id} ({resp.status_code}).')
    return resp.json()


@transaction.atomic
def apply_payment(order, data):
    """Registra el pago (idempotente) y actualiza el pedido. Devuelve el estado interno resultante."""
    if str(data.get('external_reference')) != str(order.pk):
        raise MercadoPagoError('El pago no corresponde a este pedido.')
    status = STATUS_MAP.get(data.get('status'), 'pending')
    amount = Decimal(str(data.get('transaction_amount', 0)))
    if status == 'paid' and amount < order.total:
        log.error('Pago %s por %s menor al total %s del pedido %s', data.get('id'), amount, order.total, order.pk)
        status = 'failed'
    Payment.objects.update_or_create(
        provider='mercadopago', external_id=str(data['id']),
        defaults={'order': order, 'status': data.get('status', ''), 'amount': amount, 'raw': data},
    )
    # Un pago aprobado posterior no se pisa con uno pendiente/rechazado viejo.
    if not (order.payment_status == 'paid' and status in ('pending', 'failed')):
        order.payment_status = status
        order.save(update_fields=['payment_status'])
    return order.payment_status
