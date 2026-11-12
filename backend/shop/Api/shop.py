from rest_framework import status, views
from rest_framework.response import Response

from shop.models import Product
from shop.serializers import ProductSerializer, ShopSerializer


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
