from django.core.management.base import BaseCommand

from shop.models import Category, CustomUser, Product, State, SubCategory

CATALOG = {
    'Tecnología': ['Celulares', 'Notebooks', 'Accesorios'],
    'Hogar': ['Cocina', 'Decoración'],
    'Moda': ['Remeras', 'Zapatillas'],
    'Gourmet': ['Café', 'Dulces'],
}

SHOPS = [
    ('techzone', 'TechZone', '20111111112', 'Tecnología'),
    ('casabella', 'Casa Bella', '20222222223', 'Hogar'),
    ('urbanstyle', 'Urban Style', '20333333334', 'Moda'),
]


class Command(BaseCommand):
    help = 'Carga datos de ejemplo (categorías, tiendas y productos) para demos. Es idempotente.'

    def handle(self, *args, **opts):
        for name in ('Activo', 'Inactivo'):
            State.objects.get_or_create(name=name, defaults={'description': name})
        subs = {}
        for cat_name, sub_names in CATALOG.items():
            cat, _ = Category.objects.get_or_create(name=cat_name)
            for sn in sub_names:
                subs[sn], _ = SubCategory.objects.get_or_create(category=cat, name=sn)

        products = {
            'techzone': [('Smartphone Aurora 128GB', 'Pantalla AMOLED 6.5", 8GB RAM', 450000, 15, 'Celulares'),
                         ('Notebook Slim 14"', 'Ryzen 5, 16GB, SSD 512GB', 820000, 10, 'Notebooks'),
                         ('Auriculares Bluetooth', 'Cancelación de ruido, 30h de batería', 65000, 25, 'Accesorios')],
            'casabella': [('Set de ollas x5', 'Acero inoxidable, apto inducción', 98000, 20, 'Cocina'),
                          ('Lámpara de mesa nórdica', 'Madera y lino, luz cálida', 32000, 0, 'Decoración')],
            'urbanstyle': [('Remera oversize algodón', '100% algodón peinado', 18000, 30, 'Remeras'),
                           ('Zapatillas urbanas', 'Suela de goma, livianas', 72000, 5, 'Zapatillas')],
        }
        n = 0
        for username, razon, cuit, _cat in SHOPS:
            shop, created = CustomUser.objects.get_or_create(
                username=username,
                defaults=dict(razon_social=razon, cuit=cuit, domicilio_fiscal='Av. Siempreviva 123',
                              ingresos_brutos=cuit, email=f'{username}@example.com'),
            )
            if created:
                shop.set_password('demo12345')
                shop.save()
            for i, (name, desc, price, disc, sub) in enumerate(products[username]):
                _, c = Product.objects.get_or_create(
                    barcode=f'DEMO-{username}-{i}',
                    defaults=dict(shop=shop, name=name, description=desc, price=price,
                                  discount=disc, subcategory=subs[sub], stock=20),
                )
                n += c
        self.stdout.write(self.style.SUCCESS(
            f'Listo: {n} productos nuevos. Tiendas demo: techzone / casabella / urbanstyle (clave: demo12345)'))
