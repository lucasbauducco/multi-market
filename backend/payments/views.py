import json
import logging
import uuid

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from rest_framework import permissions, serializers, status, views
from rest_framework.response import Response

from shop.models import CustomUser, Order
from shop.serializers import OrderSerializer, image_from_base64

from . import methods
from .models import ShopPaymentSettings
from .providers import mercadopago as mp

log = logging.getLogger(__name__)


class ShopPaymentSettingsSerializer(serializers.ModelSerializer):
    mp_connected = serializers.BooleanField(read_only=True)
    mp_platform_configured = serializers.SerializerMethodField()

    class Meta:
        model = ShopPaymentSettings
        # Los tokens NUNCA se exponen.
        fields = ['accepts_transfer', 'transfer_holder', 'transfer_cbu', 'transfer_alias',
                  'accepts_cash', 'cash_instructions', 'accepts_link', 'link_label', 'link_url',
                  'mp_enabled', 'mp_connected', 'mp_platform_configured', 'mp_user_id']
        read_only_fields = ['mp_user_id']

    def get_mp_platform_configured(self, obj):
        return mp.is_configured()

    def validate_transfer_cbu(self, value):
        if value and (not value.isdigit() or len(value) != 22):
            raise serializers.ValidationError('El CBU/CVU debe tener 22 dígitos.')
        return value

    def validate_link_url(self, value):
        if value and not value.lower().startswith('https://'):
            raise serializers.ValidationError('El link debe comenzar con https://')
        return value


class ShopPaymentSettingsView(views.APIView):
    """Configuración de medios de pago de la tienda autenticada."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(ShopPaymentSettingsSerializer(methods.settings_for(request.user)).data)

    def patch(self, request):
        ps = methods.settings_for(request.user)
        ser = ShopPaymentSettingsSerializer(ps, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data)


class CheckoutMethodsView(views.APIView):
    """Medios de pago disponibles por tienda: /api/checkout/methods/?shops=1,2"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        try:
            ids = [int(x) for x in request.query_params.get('shops', '').split(',') if x][:20]
        except ValueError:
            return Response({'error': 'shops inválido'}, status=400)
        out = {}
        for shop in CustomUser.objects.filter(id__in=ids, is_active=True):
            out[shop.id] = {'name': shop.razon_social, 'methods': methods.available_methods(shop)}
        return Response(out)


# ------------------------------------------------------------------ Mercado Pago: OAuth
class MercadoPagoConnectView(views.APIView):
    """Devuelve la URL de autorización para que el vendedor conecte su cuenta."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            return Response({'url': mp.authorization_url(request.user)})
        except mp.MercadoPagoError as e:
            return Response({'detail': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class MercadoPagoCallbackView(views.APIView):
    """Redirección de Mercado Pago tras autorizar. Guarda los tokens y vuelve al panel."""
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def get(self, request):
        back = f'{settings.FRONTEND_URL.rstrip("/")}/panel/configuracion'
        try:
            shop = get_object_or_404(CustomUser, pk=mp.read_state(request.query_params.get('state', '')))
            code = request.query_params.get('code')
            if not code:
                raise mp.MercadoPagoError('Falta el código de autorización.')
            mp.connect_with_code(methods.settings_for(shop), code)
        except mp.MercadoPagoError as e:
            log.warning('Callback OAuth MP falló: %s', e)
            return HttpResponseRedirect(f'{back}?mp=error')
        return HttpResponseRedirect(f'{back}?mp=connected')


class MercadoPagoDisconnectView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        ps = methods.settings_for(request.user)
        ps.clear_mp()
        ps.save()
        return Response(ShopPaymentSettingsSerializer(ps).data)


# ------------------------------------------------------------------ Mercado Pago: pago y webhook
class MercadoPagoPreferenceView(views.APIView):
    """Crea la preferencia de pago de un pedido y devuelve la URL de Checkout Pro."""
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'payments'

    def post(self, request, token):
        order = get_object_or_404(Order.objects.select_related('shop').prefetch_related('items'), public_token=token)
        if order.payment_method != 'mercadopago':
            return Response({'detail': 'El pedido no usa Mercado Pago.'}, status=400)
        if order.payment_status == 'paid':
            return Response({'detail': 'El pedido ya está pagado.'}, status=400)
        if order.status == 'cancelled':
            return Response({'detail': 'El pedido está cancelado.'}, status=400)
        try:
            data = mp.create_preference(order, methods.settings_for(order.shop))
        except mp.MercadoPagoError as e:
            return Response({'detail': str(e)}, status=status.HTTP_502_BAD_GATEWAY)
        return Response(data)


class MercadoPagoWebhookView(views.APIView):
    """
    Notificación de Mercado Pago. Se valida la firma (si hay secreto configurado) y SIEMPRE se
    consulta el pago a la API con el token del vendedor antes de actualizar el pedido.
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        try:
            body = json.loads(request.body or b'{}')
        except ValueError:
            body = {}
        kind = request.query_params.get('type') or request.query_params.get('topic') or body.get('type') or body.get('topic')
        data_id = request.query_params.get('data.id') or (body.get('data') or {}).get('id') or request.query_params.get('id')
        if kind != 'payment' or not data_id:
            return Response(status=status.HTTP_200_OK)  # otros eventos: se ignoran

        secret = settings.MP_WEBHOOK_SECRET
        if secret and not mp.verify_signature(secret, request.headers.get('x-signature'),
                                              request.headers.get('x-request-id'), data_id):
            return Response({'detail': 'Firma inválida.'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            order = Order.objects.select_related('shop').get(pk=int(request.query_params.get('order', 0)))
        except (Order.DoesNotExist, ValueError):
            return Response({'detail': 'Pedido desconocido.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            token = mp.valid_token(methods.settings_for(order.shop))
            payment = mp.fetch_payment(data_id, token)
            mp.apply_payment(order, payment)
        except mp.MercadoPagoError as e:
            log.warning('Webhook MP rechazado: %s', e)
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)


# ------------------------------------------------------------------ Seguimiento de pedido (comprador)
def tracking_payload(order, request):
    data = OrderSerializer(order, context={'request': request}).data
    data['payment_instructions'] = methods.payment_instructions(order)
    return data


class OrderTrackView(views.APIView):
    """Estado de un pedido por su token público (no requiere cuenta)."""
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'track'

    def get(self, request, token):
        order = get_object_or_404(Order.objects.select_related('shop').prefetch_related('items'), public_token=token)
        return Response(tracking_payload(order, request))


class OrderProofView(views.APIView):
    """El comprador sube el comprobante de una transferencia."""
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'track'

    def post(self, request, token):
        order = get_object_or_404(Order.objects.select_related('shop'), public_token=token)
        if order.payment_method != 'transfer' or order.payment_status == 'paid':
            return Response({'detail': 'Este pedido no admite comprobante.'}, status=400)
        b64 = request.data.get('image_base64')
        if not b64:
            return Response({'image_base64': 'Requerido.'}, status=400)
        try:
            order.payment_proof = image_from_base64(b64)
        except serializers.ValidationError as e:
            return Response({'image_base64': e.detail}, status=400)
        order.payment_status = 'pending'
        order.save(update_fields=['payment_proof', 'payment_status'])
        return Response(tracking_payload(order, request))


class ShopOrderPaymentView(views.APIView):
    """La tienda confirma manualmente un pago (transferencia / efectivo / link)."""
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        order = get_object_or_404(Order, pk=pk, shop=request.user)
        if order.payment_method == 'mercadopago':
            return Response({'detail': 'Los pagos de Mercado Pago se actualizan automáticamente.'}, status=400)
        new = request.data.get('payment_status')
        if new not in ('unpaid', 'paid'):
            return Response({'payment_status': 'Debe ser unpaid o paid.'}, status=400)
        order.payment_status = new
        order.save(update_fields=['payment_status'])
        return Response(OrderSerializer(order, context={'request': request}).data)
