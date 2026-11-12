from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import permissions, serializers, status, views
from rest_framework.response import Response

from shop.models import CustomUser, Product
from shop.serializers import ProductSerializer, ShopSerializer, image_from_base64


class ProductShopView(views.APIView):
    """Información de la tienda que vende un producto."""

    def get(self, request, product_id):
        try:
            product = Product.objects.select_related('shop').get(id=product_id, state='active', shop__is_active=True)
        except Product.DoesNotExist:
            return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return Response(ShopSerializer(product.shop).data)


class ShopProductsListView(views.APIView):
    """Productos activos de una tienda, más nuevos primero."""

    def get(self, request, shop_id):
        qs = Product.objects.filter(shop_id=shop_id, state='active', shop__is_active=True).order_by('-created_at')
        return Response(ProductSerializer(qs, many=True, context={'request': request}).data)


class ShopPublicSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()
    banner = serializers.SerializerMethodField()
    product_count = serializers.IntegerField(read_only=True, default=0)
    telefono = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'razon_social', 'slug', 'description', 'logo', 'banner', 'product_count', 'telefono']

    def _url(self, f):
        if not f:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(f.url) if request else f.url

    def get_logo(self, obj):
        return self._url(obj.logo)

    def get_banner(self, obj):
        return self._url(obj.banner)

    def get_telefono(self, obj):
        return str(obj.telefono) if obj.telefono else None


def _active_shops():
    return (CustomUser.objects.filter(is_active=True, is_staff=False)
            .annotate(product_count=Count('shop_products', filter=Q(shop_products__state='active')))
            .filter(product_count__gt=0))


class ShopListView(views.APIView):
    """Tiendas activas con productos (más productos primero)."""

    def get(self, request):
        qs = _active_shops().order_by('-product_count', 'razon_social')[:50]
        return Response(ShopPublicSerializer(qs, many=True, context={'request': request}).data)


class ShopDetailView(views.APIView):
    """Perfil público de una tienda por slug."""

    def get(self, request, slug):
        shop = get_object_or_404(_active_shops(), slug=slug)
        return Response(ShopPublicSerializer(shop, context={'request': request}).data)


class ShopProfileView(views.APIView):
    """La tienda autenticada edita su perfil público (descripción, logo, banner, teléfono)."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(ShopPublicSerializer(request.user, context={'request': request}).data)

    def patch(self, request):
        user = request.user
        if 'description' in request.data:
            user.description = str(request.data['description'])[:1000]
        for field in ('logo', 'banner'):
            b64 = request.data.get(f'{field}_base64')
            if b64:
                setattr(user, field, image_from_base64(b64))
        user.save()
        return Response(ShopPublicSerializer(user, context={'request': request}).data)
