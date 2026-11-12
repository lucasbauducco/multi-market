import uuid

from django.db import migrations
from django.utils.text import slugify


def populate(apps, schema_editor):
    Order = apps.get_model('shop', 'Order')
    for order in Order.objects.all():
        order.public_token = uuid.uuid4()
        order.save(update_fields=['public_token'])

    User = apps.get_model('shop', 'CustomUser')
    used = set(User.objects.exclude(slug__isnull=True).values_list('slug', flat=True))
    for user in User.objects.filter(slug__isnull=True):
        base = (slugify(user.razon_social)[:50] or user.username)
        slug, n = base, 2
        while slug in used:
            slug, n = f'{base}-{n}', n + 1
        used.add(slug)
        user.slug = slug
        user.save(update_fields=['slug'])


class Migration(migrations.Migration):
    dependencies = [('shop', '0009_profiles_payments')]
    operations = [migrations.RunPython(populate, migrations.RunPython.noop)]
