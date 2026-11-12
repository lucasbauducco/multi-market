import io
import colorsys

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw

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


def placeholder_image(text, seed):
    """Imagen de ejemplo (fondo de color + iniciales) para que la demo no quede sin fotos."""
    r, g, b = (int(c * 255) for c in colorsys.hsv_to_rgb((seed * 0.13) % 1, 0.35, 0.92))
    img = Image.new('RGB', (480, 360), (r, g, b))
    d = ImageDraw.Draw(img)
    d.ellipse((150, 80, 330, 260), fill=(255, 255, 255))
    d.text((240, 170), ''.join(w[0] for w in text.split()[:2]).upper(), fill=(r // 2, g // 2, b // 2), anchor='mm', font_size=70)
    buf = io.BytesIO()
    img.save(buf, 'JPEG', quality=85)
    return ContentFile(buf.getvalue(), name='demo.jpg')


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
        for idx, (username, razon, cuit, _cat) in enumerate(SHOPS):
            shop, created = CustomUser.objects.get_or_create(
                username=username,
                defaults=dict(razon_social=razon, cuit=cuit, domicilio_fiscal='Av. Siempreviva 123',
                              ingresos_brutos=cuit, email=f'{username}@example.com',
                              telefono=f'+54911555500{idx:02d}'),
            )
            if created:
                shop.set_password('demo12345')
                shop.save()
            for i, (name, desc, price, disc, sub) in enumerate(products[username]):
                prod, c = Product.objects.get_or_create(
                    barcode=f'DEMO-{username}-{i}',
                    defaults=dict(shop=shop, name=name, description=desc, price=price,
                                  discount=disc, subcategory=subs[sub], stock=20),
                )
                if not prod.image:
                    prod.image = placeholder_image(name, n + i + idx)
                    prod.save(update_fields=['image'])
                n += c
        self.stdout.write(self.style.SUCCESS(
            f'Listo: {n} productos nuevos. Tiendas demo: techzone / casabella / urbanstyle (clave: demo12345)'))
