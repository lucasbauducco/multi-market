import base64
import uuid

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework import serializers

from decimal import ROUND_HALF_UP, Decimal

from django.conf import settings

from .models import (Category, CustomUser, Order, OrderItem, Product, ProductImage, State,
                     SubCategory)

User = get_user_model()
MAX_IMAGE_BYTES = 3 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {'png', 'jpeg', 'jpg', 'webp', 'gif'}


def image_from_base64(data):
    """Convierte un data-URI base64 en un ContentFile validando tipo y tamaño."""
    try:
        header, imgstr = data.split(';base64,')
        ext = header.split('/')[-1].lower()
        raw = base64.b64decode(imgstr)
    except Exception:
        raise serializers.ValidationError('Imagen inválida.')
    if ext not in ALLOWED_IMAGE_TYPES:
        raise serializers.ValidationError('Formato de imagen no permitido.')
    if len(raw) > MAX_IMAGE_BYTES:
        raise serializers.ValidationError('La imagen supera los 3 MB.')
    return ContentFile(raw, name=f'{uuid.uuid4().hex}.{ext}')


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'razon_social', 'telefono', 'email']


class CustomUserSerializer(serializers.ModelSerializer):
    """Uso administrativo (crear/actualizar usuarios)."""
    motive = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'user_type', 'state', 'motive', 'cuit',
                  'razon_social', 'telefono', 'domicilio_fiscal', 'ingresos_brutos', 'inicio_actividades']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        validated_data.pop('motive', None)
        return CustomUser.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('motive', None)
        password = validated_data.pop('password', None)
        instance = super().update(instance, validated_data)
        if password:
            instance.set_password(password)
            instance.save()
        return instance


class ShopRegisterSerializer(serializers.ModelSerializer):
    """Alta pública de una tienda. Queda inactiva hasta que un administrador la apruebe."""
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'cuit', 'razon_social', 'telefono',
                  'domicilio_fiscal', 'ingresos_brutos', 'inicio_actividades']
        extra_kwargs = {'email': {'required': True}}

    def validate_cuit(self, value):
        if not value.isdigit() or len(value) != 11:
            raise serializers.ValidationError('El CUIT debe tener 11 dígitos numéricos.')
        return value

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        user.is_active = False
        user.save(update_fields=['is_active'])
        return user


class CustomUserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'user_type', 'state', 'cuit', 'razon_social', 'telefono',
                  'domicilio_fiscal', 'ingresos_brutos', 'inicio_actividades']


class StateChangeSerializer(serializers.Serializer):
    state = serializers.CharField(max_length=100)
    motive = serializers.CharField(max_length=200, required=False)

    def validate_state(self, value):
        try:
            return State.objects.get(name=value)
        except State.DoesNotExist:
            raise serializers.ValidationError('Estado inexistente.')


class ProductSerializer(serializers.ModelSerializer):
    """
    Lectura: `image` es la URL del archivo (o el base64 heredado si no hay archivo).
    Escritura: se puede enviar `image_base64` (data-URI) y se guarda como archivo.
    `shop` siempre se toma del usuario autenticado.
    """
    image = serializers.SerializerMethodField()
    image_base64 = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    shop_name = serializers.CharField(source='shop.razon_social', read_only=True)
    shop_slug = serializers.CharField(source='shop.slug', read_only=True)
    images = serializers.SerializerMethodField()
    images_base64 = serializers.ListField(child=serializers.CharField(), write_only=True, required=False,
                                          max_length=8)
    category_id = serializers.IntegerField(source='subcategory.category_id', read_only=True, default=None)
    category_name = serializers.CharField(source='subcategory.category.name', read_only=True, default=None)
    subcategory_name = serializers.CharField(source='subcategory.name', read_only=True, default=None)

    class Meta:
        model = Product
        fields = ['id', 'shop', 'shop_name', 'shop_slug', 'name', 'description', 'price', 'discount',
                  'final_price', 'barcode', 'image', 'image_base64', 'images', 'images_base64', 'subcategory',
                  'category_id', 'category_name', 'subcategory_name', 'stock', 'state', 'created_at']
        read_only_fields = ['shop', 'created_at']

    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return obj.image_base64 or None

    def get_images(self, obj):
        request = self.context.get('request')
        urls = []
        main = self.get_image(obj)
        if main:
            urls.append(main)
        for g in obj.gallery.all():
            urls.append(request.build_absolute_uri(g.image.url) if request else g.image.url)
        return urls

    def validate_discount(self, value):
        if not 0 <= value <= 100:
            raise serializers.ValidationError('El descuento debe estar entre 0 y 100.')
        return value

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError('El precio no puede ser negativo.')
        return value

    def validate_state(self, value):
        if value not in ('active', 'inactive'):
            raise serializers.ValidationError('El estado debe ser active o inactive.')
        return value

    def _apply_image(self, validated_data):
        b64 = validated_data.pop('image_base64', None)
        if b64:
            validated_data['image'] = image_from_base64(b64)
            validated_data['image_base64'] = None

    def _save_gallery(self, product, extra):
        start = product.gallery.count()
        for i, b64 in enumerate(extra or []):
            ProductImage.objects.create(product=product, image=image_from_base64(b64), position=start + i)

    def create(self, validated_data):
        extra = validated_data.pop('images_base64', None)
        self._apply_image(validated_data)
        validated_data['shop'] = self.context['request'].user
        product = super().create(validated_data)
        self._save_gallery(product, extra)
        return product

    def update(self, instance, validated_data):
        extra = validated_data.pop('images_base64', None)
        self._apply_image(validated_data)
        product = super().update(instance, validated_data)
        self._save_gallery(product, extra)
        return product


class SubCategoryLiteSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'category', 'category_name']


class SubCategorySerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()

    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'description', 'products']

    def get_products(self, obj):
        qs = obj.products.filter(state='active', shop__is_active=True)
        return ProductSerializer(qs, many=True, context=self.context).data


class CategoryWithProductsSerializer(serializers.ModelSerializer):
    subcategories = SubCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'subcategories']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']


class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['product', 'name', 'unit_price', 'quantity', 'subtotal']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    shop_name = serializers.CharField(source='shop.razon_social', read_only=True)
    shop_slug = serializers.CharField(source='shop.slug', read_only=True)
    shop_phone = serializers.SerializerMethodField()
    has_proof = serializers.SerializerMethodField()
    proof_url = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'public_token', 'shop', 'shop_name', 'shop_slug', 'shop_phone', 'buyer_name',
                  'buyer_phone', 'buyer_email', 'notes', 'status', 'total', 'created_at', 'items',
                  'delivery_method', 'shipping_address', 'payment_method', 'payment_status',
                  'platform_fee', 'has_proof', 'proof_url']

    def get_shop_phone(self, obj):
        return str(obj.shop.telefono) if obj.shop.telefono else None

    def get_has_proof(self, obj):
        return bool(obj.payment_proof)

    def get_proof_url(self, obj):
        if not obj.payment_proof:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(obj.payment_proof.url) if request else obj.payment_proof.url


class CheckoutItemSerializer(serializers.Serializer):
    product = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, max_value=999)


class CheckoutSerializer(serializers.Serializer):
    buyer_name = serializers.CharField(max_length=120)
    buyer_phone = serializers.CharField(max_length=40)
    buyer_email = serializers.EmailField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True, max_length=500)
    items = CheckoutItemSerializer(many=True, allow_empty=False)
    delivery_method = serializers.ChoiceField(choices=['shipping', 'pickup'], default='pickup')
    shipping_address = serializers.CharField(required=False, allow_blank=True, max_length=250)
    # {"<id de tienda>": "mercadopago|transfer|cash|link"}; si falta, se usa el primer medio de la tienda.
    payment_methods = serializers.DictField(child=serializers.CharField(), required=False)

    def validate(self, attrs):
        if attrs['delivery_method'] == 'shipping' and not attrs.get('shipping_address', '').strip():
            raise serializers.ValidationError({'shipping_address': 'Indicá la dirección de envío.'})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        """Crea un pedido por tienda. Precios y stock se toman SIEMPRE del servidor."""
        wanted = {}
        for it in validated_data['items']:
            wanted[it['product']] = wanted.get(it['product'], 0) + it['quantity']

        products = {p.id: p for p in Product.objects.select_for_update()
                    .select_related('shop').filter(id__in=wanted, state='active', shop__is_active=True)}
        missing = set(wanted) - set(products)
        if missing:
            raise serializers.ValidationError({'items': f'Productos no disponibles: {sorted(missing)}'})

        by_shop = {}
        for pid, qty in wanted.items():
            p = products[pid]
            if p.stock is not None and qty > p.stock:
                raise serializers.ValidationError({'items': f'Stock insuficiente para "{p.name}".'})
            by_shop.setdefault(p.shop_id, []).append((p, qty))

        from payments.methods import available_methods  # import local: evita ciclo shop <-> payments
        chosen = validated_data.get('payment_methods', {})
        fee_pct = Decimal(str(settings.PLATFORM_FEE_PERCENT or 0))
        orders = []
        for shop_id, lines in by_shop.items():
            shop = lines[0][0].shop
            codes = [m['code'] for m in available_methods(shop)]
            method = chosen.get(str(shop_id)) or (codes[0] if codes else None)
            if method not in codes:
                raise serializers.ValidationError(
                    {'payment_methods': f'"{shop.razon_social}" no acepta el medio de pago "{method}".'})
            order = Order.objects.create(
                shop=shop,
                delivery_method=validated_data['delivery_method'],
                shipping_address=validated_data.get('shipping_address', ''),
                payment_method=method,
                buyer_name=validated_data['buyer_name'],
                buyer_phone=validated_data['buyer_phone'],
                buyer_email=validated_data.get('buyer_email', ''),
                notes=validated_data.get('notes', ''),
            )
            total = 0
            for p, qty in lines:
                OrderItem.objects.create(order=order, product=p, name=p.name,
                                         unit_price=p.final_price, quantity=qty)
                total += p.final_price * qty
                if p.stock is not None:
                    p.stock -= qty
                    p.save(update_fields=['stock'])
            order.total = total
            order.platform_fee = (total * fee_pct / 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            order.save(update_fields=['total', 'platform_fee'])
            orders.append(order)
        return orders
