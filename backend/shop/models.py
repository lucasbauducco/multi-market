import uuid
from django.db import models
from decimal import Decimal
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
class User_Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name
# Create your models here.
class UserType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    user_categories = models.ManyToManyField(User_Category)
    def __str__(self):
        return self.name
class State(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name
class CustomUser(AbstractUser):
    user_type = models.ForeignKey(UserType, on_delete=models.SET_NULL, null=True, blank=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True)
    cuit = models.CharField(max_length=11)
    razon_social = models.CharField(max_length=100)
    domicilio_fiscal = models.CharField(max_length=200)
    ingresos_brutos = models.CharField(max_length=50)
    inicio_actividades = models.DateField(null=True, blank=True)
    telefono = PhoneNumberField(null=True, blank=True, unique=True, region="AR")
    # Perfil público de la tienda (página /tienda/<slug>)
    slug = models.SlugField(max_length=60, unique=True, null=True, blank=True)
    logo = models.ImageField(upload_to='shops/logos/', null=True, blank=True)
    banner = models.ImageField(upload_to='shops/banners/', null=True, blank=True)
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug and self.razon_social:
            from django.utils.text import slugify
            base = slugify(self.razon_social)[:50] or self.username
            slug, n = base, 2
            while CustomUser.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug, n = f'{base}-{n}', n + 1
            self.slug = slug
        super().save(*args, **kwargs)
class UserHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='history')
    modified_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='modified_users')
    modified_at = models.DateTimeField(auto_now_add=True)
    motive = models.CharField(max_length=200, blank=True, null=True)
    changes = models.TextField()

    def __str__(self):
        return f"History for {self.user.username} modified by {self.modified_by.username} at {self.modified_at}"
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class SubCategory(models.Model):
    category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
class Product(models.Model):
    STATE_CHOICES = (('active', 'Active'), ('inactive', 'Inactive'))

    shop = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='shop_products')
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    barcode = models.CharField(max_length=100, unique=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    # Campo heredado (imágenes antiguas en base64). Las nuevas se guardan en `image`.
    image_base64 = models.TextField(blank=True, null=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    # None = stock ilimitado / no controlado.
    stock = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    state = models.CharField(max_length=12, default='active', choices=STATE_CHOICES)

    def __str__(self):
        return self.name

    @property
    def final_price(self):
        return (Decimal(self.price) * (100 - Decimal(self.discount)) / 100).quantize(Decimal('0.01'))


class ProductImage(models.Model):
    """Imágenes adicionales de un producto (la principal sigue en Product.image)."""
    product = models.ForeignKey(Product, related_name='gallery', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['position', 'id']


class Order(models.Model):
    """Pedido de un comprador a UNA tienda (un checkout multi-tienda genera varios pedidos)."""
    STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmado'),
        ('delivered', 'Entregado'),
        ('cancelled', 'Cancelado'),
    )
    shop = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='orders')
    buyer_name = models.CharField(max_length=120)
    buyer_phone = models.CharField(max_length=40)
    buyer_email = models.EmailField(blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    # Entrega y pago
    DELIVERY_CHOICES = (('shipping', 'Envío'), ('pickup', 'Retiro en local'))
    PAYMENT_METHODS = (('mercadopago', 'Mercado Pago'), ('transfer', 'Transferencia'),
                       ('cash', 'Efectivo / retiro'), ('link', 'Link de pago'))
    PAYMENT_STATUS = (('unpaid', 'Sin pagar'), ('pending', 'Pago pendiente'), ('paid', 'Pagado'),
                      ('failed', 'Rechazado'), ('refunded', 'Reembolsado'))
    delivery_method = models.CharField(max_length=10, choices=DELIVERY_CHOICES, default='pickup')
    shipping_address = models.CharField(max_length=250, blank=True)
    payment_method = models.CharField(max_length=12, choices=PAYMENT_METHODS, default='cash')
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='unpaid')
    platform_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    public_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    payment_proof = models.ImageField(upload_to='proofs/', null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Pedido #{self.pk} - {self.buyer_name}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=200)  # copia del nombre al momento de la compra
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)  # precio final con descuento
    quantity = models.PositiveIntegerField()

    @property
    def subtotal(self):
        return self.unit_price * self.quantity
