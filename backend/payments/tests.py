import base64
import hashlib
import hmac
import tempfile
from decimal import Decimal
from unittest import mock

from django.core.cache import cache
from django.test import override_settings
from rest_framework.test import APITestCase

from payments import methods
from payments.models import Payment
from payments.providers import mercadopago as mp
from shop.models import Category, CustomUser, Order, Product, SubCategory

PNG = 'data:image/png;base64,' + base64.b64encode(base64.b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==')).decode()

MP_SETTINGS = dict(MP_CLIENT_ID='cid', MP_CLIENT_SECRET='csecret', MP_WEBHOOK_SECRET='whsecret',
                   BACKEND_PUBLIC_URL='https://api.example.com', FRONTEND_URL='https://shop.example.com')


class FakeResp:
    def __init__(self, status=200, data=None):
        self.status_code, self._data, self.text = status, data or {}, str(data)

    def json(self):
        return self._data


def make_shop(username):
    return CustomUser.objects.create_user(username, password='Secret123!', razon_social=username.title(),
                                          cuit='20123456789', domicilio_fiscal='x', ingresos_brutos='1',
                                          email=f'{username}@x.com')


class PaymentBase(APITestCase):
    def setUp(self):
        cache.clear()
        cat = Category.objects.create(name='C')
        sub = SubCategory.objects.create(category=cat, name='S')
        self.shop = make_shop('uno')
        self.other = make_shop('dos')
        self.p1 = Product.objects.create(shop=self.shop, name='A', description='d', price=100, barcode='1',
                                         discount=10, subcategory=sub, stock=10)
        self.p2 = Product.objects.create(shop=self.other, name='B', description='d', price=50, barcode='2',
                                         subcategory=sub)

    def enable_mp(self, shop):
        ps = methods.settings_for(shop)
        ps.set_mp_tokens('APP_USR-seller-token', 'refresh-token', 15552000, '777', 'APP_USR-public')
        ps.save()
        return ps

    def checkout(self, items=None, **extra):
        items = items or [{'product': self.p1.id, 'quantity': 2}]
        payload = {'buyer_name': 'Ana', 'buyer_phone': '1155550000', 'buyer_email': 'ana@x.com', 'items': items}
        payload.update(extra)
        return self.client.post('/api/checkout/', payload, format='json')


class PaymentSettingsTests(PaymentBase):
    def test_default_shop_only_accepts_cash(self):
        self.assertEqual([m['code'] for m in methods.available_methods(self.shop)], ['cash'])

    def test_shop_configures_methods_and_validation(self):
        self.client.force_authenticate(self.shop)
        r = self.client.patch('/api/shop/payment-settings/', {
            'accepts_transfer': True, 'transfer_alias': 'uno.tienda', 'transfer_cbu': '1234567890123456789012',
            'accepts_link': True, 'link_label': 'Ualá Bis', 'link_url': 'https://bit.ly/uala'}, format='json')
        self.assertEqual(r.status_code, 200, r.content)
        codes = [m['code'] for m in methods.available_methods(self.shop)]
        self.assertEqual(codes, ['transfer', 'link', 'cash'])
        bad = self.client.patch('/api/shop/payment-settings/', {'transfer_cbu': '123'}, format='json')
        self.assertEqual(bad.status_code, 400)
        bad = self.client.patch('/api/shop/payment-settings/', {'link_url': 'http://insecure.example'}, format='json')
        self.assertEqual(bad.status_code, 400)

    def test_tokens_are_never_exposed_and_are_encrypted(self):
        ps = self.enable_mp(self.shop)
        self.assertNotIn('seller-token', ps.mp_access_token_enc)
        self.assertEqual(ps.mp_access_token, 'APP_USR-seller-token')
        self.client.force_authenticate(self.shop)
        body = self.client.get('/api/shop/payment-settings/').content.decode()
        self.assertNotIn('seller-token', body)
        self.assertNotIn('refresh-token', body)
        self.assertTrue(self.client.get('/api/shop/payment-settings/').json()['mp_connected'])

    def test_settings_require_auth(self):
        self.assertEqual(self.client.get('/api/shop/payment-settings/').status_code, 401)

    def test_public_methods_endpoint(self):
        r = self.client.get(f'/api/checkout/methods/?shops={self.shop.id},{self.other.id}').json()
        self.assertEqual(r[str(self.shop.id)]['methods'][0]['code'], 'cash')
        self.assertNotIn('token', str(r))


class CheckoutPaymentTests(PaymentBase):
    def test_cash_is_default_and_order_has_public_token(self):
        r = self.checkout()
        self.assertEqual(r.status_code, 201, r.content)
        o = r.json()[0]
        self.assertEqual(o['payment_method'], 'cash')
        self.assertEqual(o['payment_status'], 'unpaid')
        self.assertTrue(o['public_token'])

    def test_rejects_method_not_enabled_for_shop(self):
        r = self.checkout(payment_methods={str(self.shop.id): 'mercadopago'})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Order.objects.count(), 0)
        self.p1.refresh_from_db()
        self.assertEqual(self.p1.stock, 10)

    def test_per_shop_method_selection(self):
        self.enable_mp(self.shop)
        ps = methods.settings_for(self.other)
        ps.accepts_transfer, ps.transfer_alias = True, 'dos.alias'
        ps.save()
        r = self.checkout([{'product': self.p1.id, 'quantity': 1}, {'product': self.p2.id, 'quantity': 1}],
                          payment_methods={str(self.shop.id): 'mercadopago', str(self.other.id): 'transfer'})
        self.assertEqual(r.status_code, 201, r.content)
        got = {o['shop']: o['payment_method'] for o in r.json()}
        self.assertEqual(got, {self.shop.id: 'mercadopago', self.other.id: 'transfer'})

    def test_shipping_requires_address(self):
        self.assertEqual(self.checkout(delivery_method='shipping').status_code, 400)
        ok = self.checkout(delivery_method='shipping', shipping_address='Calle 123')
        self.assertEqual(ok.status_code, 201)
        self.assertEqual(ok.json()[0]['shipping_address'], 'Calle 123')

    def test_platform_fee_zero_by_default_and_configurable(self):
        self.assertEqual(Decimal(self.checkout().json()[0]['platform_fee']), 0)
        with override_settings(PLATFORM_FEE_PERCENT='5'):
            self.assertEqual(Decimal(self.checkout().json()[0]['platform_fee']), Decimal('9.00'))  # 5% de 180


class ManualPaymentTests(PaymentBase):
    def make_transfer_order(self):
        ps = methods.settings_for(self.shop)
        ps.accepts_transfer, ps.transfer_alias, ps.transfer_holder = True, 'uno.alias', 'Uno SRL'
        ps.save()
        o = self.checkout(payment_methods={str(self.shop.id): 'transfer'}).json()[0]
        return o

    def test_tracking_shows_transfer_instructions_without_login(self):
        o = self.make_transfer_order()
        r = self.client.get(f'/api/orders/track/{o["public_token"]}/').json()
        self.assertEqual(r['payment_instructions']['alias'], 'uno.alias')
        self.assertEqual(r['payment_instructions']['amount'], '180.00')

    def test_unknown_token_404(self):
        self.assertEqual(self.client.get('/api/orders/track/00000000-0000-0000-0000-000000000000/').status_code, 404)

    def test_buyer_uploads_proof_then_shop_confirms(self):
        o = self.make_transfer_order()
        with self.settings(MEDIA_ROOT=tempfile.mkdtemp()):
            r = self.client.post(f'/api/orders/track/{o["public_token"]}/proof/', {'image_base64': PNG}, format='json')
        self.assertEqual(r.status_code, 200, r.content)
        self.assertEqual(r.json()['payment_status'], 'pending')
        self.assertTrue(r.json()['has_proof'])
        # el comprador no puede marcarlo como pagado; la tienda sí
        self.assertEqual(self.client.patch(f'/api/orders/{o["id"]}/payment/', {'payment_status': 'paid'}).status_code, 401)
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.patch(f'/api/orders/{o["id"]}/payment/', {'payment_status': 'paid'}).status_code, 404)
        self.client.force_authenticate(self.shop)
        r = self.client.patch(f'/api/orders/{o["id"]}/payment/', {'payment_status': 'paid'}, format='json')
        self.assertEqual(r.json()['payment_status'], 'paid')

    def test_proof_rejected_for_non_transfer_orders(self):
        o = self.checkout().json()[0]  # efectivo
        r = self.client.post(f'/api/orders/track/{o["public_token"]}/proof/', {'image_base64': PNG}, format='json')
        self.assertEqual(r.status_code, 400)

    def test_link_instructions(self):
        ps = methods.settings_for(self.shop)
        ps.accepts_link, ps.link_url, ps.link_label = True, 'https://pago.example/abc', 'MODO'
        ps.save()
        o = self.checkout(payment_methods={str(self.shop.id): 'link'}).json()[0]
        ins = self.client.get(f'/api/orders/track/{o["public_token"]}/').json()['payment_instructions']
        self.assertEqual((ins['type'], ins['url'], ins['label']), ('link', 'https://pago.example/abc', 'MODO'))


@override_settings(**MP_SETTINGS)
class MercadoPagoTests(PaymentBase):
    def mp_order(self, **extra):
        self.enable_mp(self.shop)
        r = self.checkout(payment_methods={str(self.shop.id): 'mercadopago'}, **extra)
        self.assertEqual(r.status_code, 201, r.content)
        return Order.objects.get(pk=r.json()[0]['id'])

    # ---- OAuth
    def test_connect_url_contains_oauth_params_and_signed_state(self):
        self.client.force_authenticate(self.shop)
        url = self.client.get('/api/payments/mercadopago/connect/').json()['url']
        self.assertTrue(url.startswith('https://auth.mercadopago.com.ar/authorization?'))
        for part in ('client_id=cid', 'response_type=code', 'platform_id=mp', 'redirect_uri='):
            self.assertIn(part, url)

    def test_connect_unavailable_without_platform_credentials(self):
        self.client.force_authenticate(self.shop)
        with override_settings(MP_CLIENT_ID='', MP_CLIENT_SECRET=''):
            self.assertEqual(self.client.get('/api/payments/mercadopago/connect/').status_code, 503)

    def test_oauth_callback_stores_encrypted_tokens(self):
        state = mp.signing.dumps({'shop': self.shop.pk}, salt='mp-oauth')
        token_resp = FakeResp(200, {'access_token': 'APP_USR-abc', 'refresh_token': 'TG-ref', 'expires_in': 15552000,
                                    'user_id': 999, 'public_key': 'APP_USR-pub'})
        with mock.patch('payments.providers.mercadopago.requests.post', return_value=token_resp) as post:
            r = self.client.get(f'/api/payments/mercadopago/oauth/callback/?code=TG-123&state={state}')
        self.assertEqual(r.status_code, 302)
        self.assertTrue(r['Location'].endswith('/panel/configuracion?mp=connected'))
        sent = post.call_args.kwargs['json']
        self.assertEqual((sent['grant_type'], sent['code'], sent['client_id']), ('authorization_code', 'TG-123', 'cid'))
        ps = methods.settings_for(self.shop)
        self.assertEqual(ps.mp_access_token, 'APP_USR-abc')
        self.assertEqual(ps.mp_user_id, '999')
        self.assertNotIn('APP_USR-abc', ps.mp_access_token_enc)

    def test_oauth_callback_rejects_forged_state(self):
        with mock.patch('payments.providers.mercadopago.requests.post') as post:
            r = self.client.get('/api/payments/mercadopago/oauth/callback/?code=x&state=forged')
        self.assertTrue(r['Location'].endswith('?mp=error'))
        post.assert_not_called()

    def test_disconnect(self):
        ps = self.enable_mp(self.shop)
        self.client.force_authenticate(self.shop)
        self.client.post('/api/payments/mercadopago/disconnect/')
        ps.refresh_from_db()
        self.assertFalse(ps.mp_connected)
        self.assertEqual([m['code'] for m in methods.available_methods(self.shop)], ['cash'])

    def test_expiring_token_is_refreshed(self):
        ps = self.enable_mp(self.shop)
        ps.mp_expires_at = mp.timezone.now() + mp.timedelta(hours=2)
        ps.save()
        new = FakeResp(200, {'access_token': 'NEW', 'refresh_token': 'NEWREF', 'expires_in': 15552000})
        with mock.patch('payments.providers.mercadopago.requests.post', return_value=new) as post:
            self.assertEqual(mp.valid_token(ps), 'NEW')
        self.assertEqual(post.call_args.kwargs['json']['grant_type'], 'refresh_token')

    # ---- Preferencia
    def test_preference_uses_seller_token_items_and_fee(self):
        with override_settings(PLATFORM_FEE_PERCENT='10'):
            order = self.mp_order()
        pref = FakeResp(201, {'id': 'PREF-1', 'init_point': 'https://www.mercadopago.com.ar/checkout/v1/redirect?pref_id=PREF-1'})
        with mock.patch('payments.providers.mercadopago.requests.post', return_value=pref) as post:
            r = self.client.post(f'/api/orders/{order.public_token}/pay/mercadopago/')
        self.assertEqual(r.status_code, 200, r.content)
        self.assertIn('pref_id=PREF-1', r.json()['init_point'])
        call = post.call_args
        self.assertEqual(call.args[0], 'https://api.mercadopago.com/checkout/preferences')
        self.assertEqual(call.kwargs['headers']['Authorization'], 'Bearer APP_USR-seller-token')
        body = call.kwargs['json']
        self.assertEqual(body['external_reference'], str(order.pk))
        self.assertEqual(body['items'][0]['unit_price'], 90.0)
        self.assertEqual(body['items'][0]['quantity'], 2)
        self.assertEqual(body['items'][0]['currency_id'], 'ARS')
        self.assertEqual(body['marketplace_fee'], 18.0)
        self.assertEqual(body['auto_return'], 'approved')
        self.assertEqual(body['back_urls']['success'], f'https://shop.example.com/pedido/{order.public_token}')
        self.assertIn(f'order={order.pk}', body['notification_url'])

    def test_preference_without_fee_omits_marketplace_fee(self):
        order = self.mp_order()
        with mock.patch('payments.providers.mercadopago.requests.post',
                        return_value=FakeResp(201, {'id': 'P', 'init_point': 'https://x'})) as post:
            self.client.post(f'/api/orders/{order.public_token}/pay/mercadopago/')
        self.assertNotIn('marketplace_fee', post.call_args.kwargs['json'])

    def test_preference_errors(self):
        cash_order = self.checkout().json()[0]
        self.assertEqual(self.client.post(f'/api/orders/{cash_order["public_token"]}/pay/mercadopago/').status_code, 400)
        order = self.mp_order()
        with mock.patch('payments.providers.mercadopago.requests.post', return_value=FakeResp(400, {'message': 'x'})):
            self.assertEqual(self.client.post(f'/api/orders/{order.public_token}/pay/mercadopago/').status_code, 502)
        order.payment_status = 'paid'
        order.save()
        self.assertEqual(self.client.post(f'/api/orders/{order.public_token}/pay/mercadopago/').status_code, 400)

    # ---- Webhook
    def sign(self, data_id, request_id='req-1', ts='1704908010', secret='whsecret'):
        manifest = f'id:{data_id};request-id:{request_id};ts:{ts};'
        v1 = hmac.new(secret.encode(), manifest.encode(), hashlib.sha256).hexdigest()
        return {'HTTP_X_SIGNATURE': f'ts={ts},v1={v1}', 'HTTP_X_REQUEST_ID': request_id}

    def notify(self, order, data_id='555', headers=None, payment=None):
        payment = payment or {'id': int(data_id), 'status': 'approved', 'external_reference': str(order.pk),
                              'transaction_amount': float(order.total)}
        with mock.patch('payments.providers.mercadopago.requests.get', return_value=FakeResp(200, payment)) as get:
            r = self.client.post(f'/api/payments/mercadopago/webhook/?type=payment&data.id={data_id}&order={order.pk}',
                                 {'type': 'payment', 'data': {'id': data_id}}, format='json',
                                 **(self.sign(data_id) if headers is None else headers))
        return r, get

    def test_webhook_marks_order_paid_after_verifying_with_api(self):
        order = self.mp_order()
        r, get = self.notify(order)
        self.assertEqual(r.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.payment_status, 'paid')
        self.assertEqual(get.call_args.args[0], 'https://api.mercadopago.com/v1/payments/555')
        self.assertEqual(get.call_args.kwargs['headers']['Authorization'], 'Bearer APP_USR-seller-token')
        self.assertEqual(Payment.objects.get().status, 'approved')

    def test_webhook_is_idempotent(self):
        order = self.mp_order()
        self.notify(order)
        self.notify(order)
        self.assertEqual(Payment.objects.count(), 1)

    def test_webhook_rejects_bad_or_missing_signature(self):
        order = self.mp_order()
        r, get = self.notify(order, headers={'HTTP_X_SIGNATURE': 'ts=1,v1=deadbeef', 'HTTP_X_REQUEST_ID': 'r'})
        self.assertEqual(r.status_code, 401)
        r, get = self.notify(order, headers={})
        self.assertEqual(r.status_code, 401)
        get.assert_not_called()
        order.refresh_from_db()
        self.assertEqual(order.payment_status, 'unpaid')

    def test_webhook_rejects_payment_for_other_order(self):
        order = self.mp_order()
        forged = {'id': 555, 'status': 'approved', 'external_reference': '99999', 'transaction_amount': 180}
        r, _ = self.notify(order, payment=forged)
        self.assertEqual(r.status_code, 400)
        order.refresh_from_db()
        self.assertEqual(order.payment_status, 'unpaid')

    def test_webhook_underpaid_amount_is_not_marked_paid(self):
        order = self.mp_order()
        low = {'id': 555, 'status': 'approved', 'external_reference': str(order.pk), 'transaction_amount': 1}
        self.notify(order, payment=low)
        order.refresh_from_db()
        self.assertEqual(order.payment_status, 'failed')

    def test_status_mapping_and_no_downgrade_of_paid(self):
        order = self.mp_order()
        for mp_status, expected in (('pending', 'pending'), ('rejected', 'failed'), ('approved', 'paid')):
            self.notify(order, data_id=str(hash(mp_status) % 1000 + 1), payment={
                'id': hash(mp_status) % 1000 + 1, 'status': mp_status, 'external_reference': str(order.pk),
                'transaction_amount': float(order.total)})
            order.refresh_from_db()
            self.assertEqual(order.payment_status, expected, mp_status)
        # un rechazo viejo llegando tarde no pisa el pago aprobado
        self.notify(order, data_id='9999', payment={'id': 9999, 'status': 'rejected',
                                                   'external_reference': str(order.pk), 'transaction_amount': 1})
        order.refresh_from_db()
        self.assertEqual(order.payment_status, 'paid')

    def test_webhook_ignores_other_event_types_and_unknown_orders(self):
        order = self.mp_order()
        r = self.client.post('/api/payments/mercadopago/webhook/?type=merchant_order&data.id=1', {}, format='json')
        self.assertEqual(r.status_code, 200)
        r, _ = self.notify(Order(pk=424242, total=1))
        self.assertEqual(r.status_code, 404)
        self.assertTrue(order.pk)

    def test_signature_helper_matches_official_manifest_format(self):
        header = self.sign('abc123')['HTTP_X_SIGNATURE']
        self.assertTrue(mp.verify_signature('whsecret', header, 'req-1', 'ABC123'))  # id en minúsculas en el manifest
        self.assertFalse(mp.verify_signature('otro', header, 'req-1', 'abc123'))
