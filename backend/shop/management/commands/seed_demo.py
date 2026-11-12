import io
import json
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw

from payments.models import ShopPaymentSettings
from shop.models import Category, CustomUser, Product, ProductImage, State, SubCategory

ASSETS = Path(__file__).resolve().parents[3] / 'demo_assets'


def logo_file(initial, color):
    """Logo de demo: monograma sobre fondo de color (creado acá, sin marcas de terceros)."""
    img = Image.new('RGB', (256, 256), color)
    d = ImageDraw.Draw(img)
    d.ellipse((38, 38, 218, 218), fill=(255, 255, 255))
    d.text((128, 132), initial.upper(), fill=color, anchor='mm', font_size=120)
    buf = io.BytesIO()
    img.save(buf, 'PNG')
    return ContentFile(buf.getvalue(), name='logo.png')


def asset(name):
    return ContentFile((ASSETS / 'images' / name).read_bytes(), name=name)


class Command(BaseCommand):
    help = ('Carga datos de ejemplo (categorías, tiendas y productos con fotos libres de licencia) para demos. '
            'Es idempotente. Usá --reset para borrar primero los datos de demo.')

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', help='Borra las tiendas y productos de demo antes de cargar.')

    def handle(self, *args, **opts):
        catalog = json.loads((ASSETS / 'catalog.json').read_text(encoding='utf-8'))

        if opts['reset']:
            usernames = [s['username'] for s in catalog['shops']]
            CustomUser.objects.filter(username__in=usernames).delete()
            self.stdout.write('Datos de demo anteriores eliminados.')

        for name in ('Activo', 'Inactivo'):
            State.objects.get_or_create(name=name, defaults={'description': name})

        subs = {}
        for cat_name, sub_names in catalog['categories'].items():
            cat, _ = Category.objects.get_or_create(name=cat_name)
            for sn in sub_names:
                subs[sn], _ = SubCategory.objects.get_or_create(category=cat, name=sn)

        shops = {}
        for s in catalog['shops']:
            shop, created = CustomUser.objects.get_or_create(
                username=s['username'],
                defaults=dict(razon_social=s['razon_social'], cuit=s['cuit'], domicilio_fiscal='Av. Siempreviva 123',
                              ingresos_brutos=s['cuit'], email=f"{s['username']}@example.com",
                              telefono=s['phone'], description=s['description']),
            )
            if created:
                shop.set_password('demo12345')
            if not shop.logo:
                shop.logo = logo_file(s['razon_social'][0], s['logo_color'])
            if not shop.banner:
                shop.banner = asset(s['banner'])
            shop.save()
            ps, _ = ShopPaymentSettings.objects.get_or_create(shop=shop)
            for k, v in s['payments'].items():
                setattr(ps, k, v)
            ps.save()
            shops[s['username']] = shop

        created_products = 0
        for i, p in enumerate(catalog['products']):
            shop = shops[p['shop']]
            prod, created = Product.objects.get_or_create(
                barcode=f"DEMO-{p['shop']}-{i:03d}",
                defaults=dict(shop=shop, name=p['name'], description=p['description'], price=p['price'],
                              discount=p['discount'], subcategory=subs[p['sub']], stock=p['stock']),
            )
            if created:
                created_products += 1
            if not prod.image:
                prod.image = asset(p['images'][0])
                prod.save(update_fields=['image'])
            if not prod.gallery.exists():
                for pos, img in enumerate(p['images'][1:]):
                    ProductImage.objects.create(product=prod, image=asset(img), position=pos)

        self.stdout.write(self.style.SUCCESS(
            f'Listo: {created_products} productos nuevos en {len(shops)} tiendas. '
            'Usuarios de demo: techzone, casabella, urbanstyle, cafeco, bellapiel, fitzone (clave: demo12345)'))
