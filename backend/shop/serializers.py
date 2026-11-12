import base64
import uuid

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework import serializers

from .models import Category, CustomUser, Order, OrderItem, Product, State, SubCategory

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

    class Meta:
        model = Product
        fields = ['id', 'shop', 'shop_name', 'name', 'description', 'price', 'discount', 'final_price',
                  'barcode', 'image', 'image_base64', 'subcategory', 'stock', 'state', 'created_at']
        read_only_fields = ['shop', 'created_at']

    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return obj.image_base64 or None

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

    def create(self, validated_data):
        self._apply_image(validated_data)
        validated_data['shop'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        self._apply_image(validated_data)
        return super().update(instance, validated_data)


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
    shop_phone = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'shop', 'shop_name', 'shop_phone', 'buyer_name', 'buyer_phone', 'buyer_email',
                  'notes', 'status', 'total', 'created_at', 'items']

    def get_shop_phone(self, obj):
        return str(obj.shop.telefono) if obj.shop.telefono else None


class CheckoutItemSerializer(serializers.Serializer):
    product = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, max_value=999)


class CheckoutSerializer(serializers.Serializer):
    buyer_name = serializers.CharField(max_length=120)
    buyer_phone = serializers.CharField(max_length=40)
    buyer_email = serializers.EmailField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True, max_length=500)
    items = CheckoutItemSerializer(many=True, allow_empty=False)

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

        orders = []
        for lines in by_shop.values():
            order = Order.objects.create(
                shop=lines[0][0].shop,
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
            order.save(update_fields=['total'])
            orders.append(order)
        return orders
