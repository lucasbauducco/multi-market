import base64
import tempfile

from django.core.cache import cache
from django.test import override_settings
from rest_framework.test import APITestCase

from shop.models import Category, CustomUser, Order, Product, SubCategory

PNG_1PX = ('data:image/png;base64,' + base64.b64encode(
    base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
                     )).decode())


def make_shop(username, **extra):
    data = dict(razon_social=username.title(), cuit='20123456789', domicilio_fiscal='x',
                ingresos_brutos='1', email=f'{username}@x.com')
    data.update(extra)
    return CustomUser.objects.create_user(username, password='Secret123!', **data)


class BaseTest(APITestCase):
    def setUp(self):
        cache.clear()
        self.cat = Category.objects.create(name='Tech')
        self.sub = SubCategory.objects.create(category=self.cat, name='Phones')
        self.shop_a = make_shop('shopa')
        self.shop_b = make_shop('shopb')
        self.prod_a = Product.objects.create(shop=self.shop_a, name='Phone A', description='d', price=100,
                                             barcode='A1', discount=10, subcategory=self.sub, stock=5)
        self.prod_b = Product.objects.create(shop=self.shop_b, name='Phone B', description='d', price=200,
                                             barcode='B1', subcategory=self.sub)


class PermissionsTests(BaseTest):
    def test_public_detail_is_read_only(self):
        url = f'/api/product/{self.prod_a.id}/'
        self.assertEqual(self.client.get(url).status_code, 200)
        for method in ('patch', 'put', 'delete'):
            resp = getattr(self.client, method)(url, {'price': '1'}, format='json')
            self.assertEqual(resp.status_code, 405, method)
        self.prod_a.refresh_from_db()
        self.assertEqual(self.prod_a.price, 100)

    def test_cannot_edit_or_delete_other_shops_product(self):
        self.client.force_authenticate(self.shop_a)
        self.assertEqual(self.client.patch(f'/api/products/{self.prod_b.id}/', {'price': '1'}).status_code, 404)
        self.assertEqual(self.client.delete(f'/api/products/delete/{self.prod_b.id}/').status_code, 404)
        self.assertEqual(self.client.patch(f'/api/product/update/{self.prod_b.id}/', {'price': '1'}).status_code, 404)
        self.assertTrue(Product.objects.filter(pk=self.prod_b.id).exists())

    def test_anonymous_cannot_manage_products(self):
        self.assertEqual(self.client.post('/api/products/', {}).status_code, 401)
        self.assertEqual(self.client.delete(f'/api/products/delete/{self.prod_a.id}/').status_code, 401)

    def test_owner_can_edit_but_not_reassign_shop(self):
        self.client.force_authenticate(self.shop_a)
        resp = self.client.patch(f'/api/products/{self.prod_a.id}/', {'price': '120', 'shop': self.shop_b.id},
                                 format='json')
        self.assertEqual(resp.status_code, 200)
        self.prod_a.refresh_from_db()
        self.assertEqual(self.prod_a.price, 120)
        self.assertEqual(self.prod_a.shop, self.shop_a)

    def test_user_profile_only_own_or_staff(self):
        self.client.force_authenticate(self.shop_a)
        self.assertEqual(self.client.get('/api/users/shopa/').status_code, 200)
        self.assertEqual(self.client.get('/api/users/shopb/').status_code, 403)
        self.assertNotIn('password', self.client.get('/api/users/shopa/').json())

    def test_create_user_requires_admin(self):
        self.client.force_authenticate(self.shop_a)
        self.assertEqual(self.client.post('/api/create_user/', {}).status_code, 403)


class ProductTests(BaseTest):
    def test_create_product_assigns_shop_and_saves_image_file(self):
        self.client.force_authenticate(self.shop_a)
        with self.settings(MEDIA_ROOT=tempfile.mkdtemp()):
            resp = self.client.post('/api/products/', {
                'name': 'N', 'description': 'd', 'price': '50', 'barcode': 'NEW1', 'discount': '0',
                'subcategory': self.sub.id, 'image_base64': PNG_1PX}, format='json')
        self.assertEqual(resp.status_code, 201, resp.content)
        p = Product.objects.get(barcode='NEW1')
        self.assertEqual(p.shop, self.shop_a)
        self.assertTrue(p.image.name.startswith('products/'))
        self.assertTrue(resp.json()['image'].endswith('.png'))

    def test_rejects_bad_image_and_bad_discount(self):
        self.client.force_authenticate(self.shop_a)
        base = {'name': 'N', 'description': 'd', 'price': '50', 'barcode': 'X', 'subcategory': self.sub.id}
        r = self.client.post('/api/products/', {**base, 'discount': '150'}, format='json')
        self.assertEqual(r.status_code, 400)
        r = self.client.post('/api/products/', {**base, 'image_base64': 'data:image/svg+xml;base64,AAAA'},
                             format='json')
        self.assertEqual(r.status_code, 400)

    def test_inactive_products_and_pending_shops_are_hidden(self):
        self.prod_b.state = 'inactive'
        self.prod_b.save()
        names = [p['name'] for p in self.client.get('/api/search_products/').json()['products']]
        self.assertEqual(names, ['Phone A'])
        self.assertEqual(self.client.get(f'/api/product/{self.prod_b.id}/').status_code, 404)
        self.shop_a.is_active = False
        self.shop_a.save()
        self.assertEqual(self.client.get('/api/search_products/').json()['products'], [])

    def test_search_filters_and_paginates(self):
        for i in range(30):
            Product.objects.create(shop=self.shop_a, name=f'Cable {i}', description='usb', price=10,
                                   barcode=f'C{i}', subcategory=self.sub)
        data = self.client.get('/api/search_products/?query=cable').json()
        self.assertEqual(data['total'], 30)
        self.assertEqual(len(data['products']), 24)
        self.assertEqual(data['pages'], 2)
        data = self.client.get('/api/search_products/?query=cable&page=2').json()
        self.assertEqual(len(data['products']), 6)
        self.assertEqual(self.client.get('/api/search_products/?query=zzz').json()['total'], 0)

    def test_categories_and_shop_endpoints(self):
        cats = self.client.get('/api/categories/categories-with-products/').json()
        self.assertEqual(len(cats), 1)
        self.assertEqual(self.client.get(f'/api/categories/shop/{self.shop_a.id}/').status_code, 200)
        r = self.client.get(f'/api/products/category/{self.cat.id}/').json()
        self.assertEqual(r['total'], 2)
        self.assertEqual(self.client.get(f'/api/product/{self.prod_a.id}/shop/').json()['id'], self.shop_a.id)

    def test_final_price(self):
        self.assertEqual(str(self.prod_a.final_price), '90.00')


class RegistrationTests(BaseTest):
    payload = {'username': 'newshop', 'password': 'Secret123!', 'email': 'n@x.com', 'cuit': '20999999990',
               'razon_social': 'New Shop', 'domicilio_fiscal': 'x', 'ingresos_brutos': '1'}

    def test_register_creates_inactive_user_who_cannot_login(self):
        self.assertEqual(self.client.post('/api/register/', self.payload, format='json').status_code, 201)
        user = CustomUser.objects.get(username='newshop')
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_staff)
        r = self.client.post('/login/', {'username': 'newshop', 'password': 'Secret123!'}, format='json')
        self.assertEqual(r.status_code, 401)
        user.is_active = True
        user.save()
        r = self.client.post('/login/', {'username': 'newshop', 'password': 'Secret123!'}, format='json')
        self.assertEqual(r.status_code, 200)
        self.assertIn('token', r.json())

    def test_register_validation(self):
        r = self.client.post('/api/register/', {**self.payload, 'cuit': '123', 'password': 'short'}, format='json')
        self.assertEqual(r.status_code, 400)
        self.assertIn('cuit', r.json())
        self.assertIn('password', r.json())

    def test_register_cannot_escalate_privileges(self):
        self.client.post('/api/register/', {**self.payload, 'is_staff': True, 'is_superuser': True}, format='json')
        user = CustomUser.objects.get(username='newshop')
        self.assertFalse(user.is_staff or user.is_superuser)

    def test_login_is_throttled(self):
        codes = [self.client.post('/login/', {'username': 'x', 'password': 'y'}, format='json').status_code
                 for _ in range(12)]
        self.assertEqual(codes[0], 401)
        self.assertEqual(codes[-1], 429)


class OrderTests(BaseTest):
    buyer = {'buyer_name': 'Ana', 'buyer_phone': '1155550000'}

    def checkout(self, items, **extra):
        return self.client.post('/api/checkout/', {**self.buyer, 'items': items, **extra}, format='json')

    def test_checkout_splits_by_shop_and_uses_server_prices(self):
        resp = self.checkout([{'product': self.prod_a.id, 'quantity': 2}, {'product': self.prod_b.id, 'quantity': 1}])
        self.assertEqual(resp.status_code, 201, resp.content)
        self.assertEqual(len(resp.json()), 2)
        order_a = Order.objects.get(shop=self.shop_a)
        self.assertEqual(str(order_a.total), '180.00')  # 2 x 90 (100 con 10% off)
        self.assertEqual(order_a.items.get().unit_price, 90)
        self.prod_a.refresh_from_db()
        self.assertEqual(self.prod_a.stock, 3)

    def test_checkout_rejects_insufficient_stock_without_side_effects(self):
        resp = self.checkout([{'product': self.prod_b.id, 'quantity': 1}, {'product': self.prod_a.id, 'quantity': 6}])
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(Order.objects.count(), 0)
        self.prod_a.refresh_from_db()
        self.assertEqual(self.prod_a.stock, 5)

    def test_checkout_validation(self):
        self.assertEqual(self.checkout([]).status_code, 400)
        self.assertEqual(self.checkout([{'product': 9999, 'quantity': 1}]).status_code, 400)
        self.assertEqual(self.checkout([{'product': self.prod_a.id, 'quantity': 0}]).status_code, 400)
        self.prod_a.state = 'inactive'
        self.prod_a.save()
        self.assertEqual(self.checkout([{'product': self.prod_a.id, 'quantity': 1}]).status_code, 400)

    def test_shop_sees_only_own_orders_and_manages_status(self):
        self.checkout([{'product': self.prod_a.id, 'quantity': 2}, {'product': self.prod_b.id, 'quantity': 1}])
        self.client.force_authenticate(self.shop_a)
        orders = self.client.get('/api/orders/').json()
        self.assertEqual(len(orders), 1)
        oid = orders[0]['id']
        other = Order.objects.get(shop=self.shop_b)
        self.assertEqual(self.client.patch(f'/api/orders/{other.id}/status/', {'status': 'confirmed'}).status_code, 404)
        self.assertEqual(self.client.patch(f'/api/orders/{oid}/status/', {'status': 'delivered'}).status_code, 400)
        self.assertEqual(self.client.patch(f'/api/orders/{oid}/status/', {'status': 'confirmed'}).status_code, 200)

    def test_cancel_restores_stock(self):
        self.checkout([{'product': self.prod_a.id, 'quantity': 2}])
        oid = Order.objects.get().id
        self.client.force_authenticate(self.shop_a)
        self.client.patch(f'/api/orders/{oid}/status/', {'status': 'cancelled'})
        self.prod_a.refresh_from_db()
        self.assertEqual(self.prod_a.stock, 5)

    def test_orders_require_auth(self):
        self.assertEqual(self.client.get('/api/orders/').status_code, 401)


class CatalogApiTests(BaseTest):
    def setUp(self):
        super().setUp()
        self.sub2 = SubCategory.objects.create(category=Category.objects.create(name='Hogar'), name='Cocina')
        self.p3 = Product.objects.create(shop=self.shop_b, name='Olla', description='d', price=300, barcode='O1',
                                         discount=50, subcategory=self.sub2, stock=0)

    def names(self, qs):
        return [p['name'] for p in self.client.get(f'/api/search_products/?{qs}').json()['products']]

    def test_filters(self):
        self.assertEqual(sorted(self.names('category=' + str(self.cat.id))), ['Phone A', 'Phone B'])
        self.assertEqual(self.names(f'shop={self.shop_b.id}&ordering=price_asc'), ['Olla', 'Phone B'])  # 150 < 200
        self.assertEqual(self.names('min_price=100&max_price=170'), ['Olla'])
        self.assertEqual(sorted(self.names('discounted=1')), ['Olla', 'Phone A'])
        self.assertNotIn('Olla', self.names('in_stock=1'))
        self.assertNotIn('Phone A', self.names(f'exclude={self.prod_a.id}'))
        self.assertEqual(self.names('ordering=discount')[0], 'Olla')
        self.assertEqual(self.names('ordering=price_desc')[0], 'Phone B')

    def test_gallery_images_and_slug(self):
        self.client.force_authenticate(self.shop_a)
        with self.settings(MEDIA_ROOT=tempfile.mkdtemp()):
            r = self.client.post('/api/products/', {
                'name': 'G', 'description': 'd', 'price': '5', 'barcode': 'G1', 'subcategory': self.sub.id,
                'image_base64': PNG_1PX, 'images_base64': [PNG_1PX, PNG_1PX]}, format='json')
        self.assertEqual(r.status_code, 201, r.content)
        self.assertEqual(len(r.json()['images']), 3)
        self.assertEqual(self.shop_a.slug, 'shopa')

    def test_home_and_shops(self):
        h = self.client.get('/api/home/').json()
        self.assertEqual(h['deals'][0]['name'], 'Olla')
        self.assertEqual({c['name'] for c in h['categories']}, {'Tech', 'Hogar'})
        self.assertEqual(len(h['shops']), 2)
        d = self.client.get('/api/shops/shopa/').json()
        self.assertEqual((d['razon_social'], d['product_count']), ('Shopa', 1))
        self.assertEqual(self.client.get('/api/shops/nope/').status_code, 404)

    def test_shop_profile_update_and_dashboard(self):
        self.client.force_authenticate(self.shop_a)
        with self.settings(MEDIA_ROOT=tempfile.mkdtemp()):
            r = self.client.patch('/api/shop/profile/', {'description': 'Hola', 'logo_base64': PNG_1PX}, format='json')
        self.assertEqual(r.status_code, 200, r.content)
        self.assertEqual(r.json()['description'], 'Hola')
        self.assertTrue(r.json()['logo'])
        d = self.client.get('/api/shop/dashboard/').json()
        self.assertEqual((d['products_active'], d['orders_total'], d['sales_paid']), (1, 0, '0'))
        self.assertEqual(d['low_stock'], [])
        self.assertEqual(self.client.get('/api/shop/dashboard/').status_code, 200)
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get('/api/shop/dashboard/').status_code, 401)
