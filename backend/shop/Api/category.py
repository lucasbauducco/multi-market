from django.db.models import Count, Q
from rest_framework import generics

from shop.models import Category
from shop.serializers import CategorySerializer, CategoryWithProductsSerializer

ACTIVE = Q(subcategories__products__state='active', subcategories__products__shop__is_active=True)


class CategoryList(generics.ListAPIView):
    """Todas las categorías."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoriesWithProductsView(generics.ListAPIView):
    """Categorías con al menos un producto activo (incluye subcategorías y productos)."""
    serializer_class = CategoryWithProductsSerializer

    def get_queryset(self):
        return (Category.objects.annotate(n=Count('subcategories__products', filter=ACTIVE, distinct=True))
                .filter(n__gt=0).prefetch_related('subcategories__products'))


class CategoriesByShopView(generics.ListAPIView):
    """Categorías en las que una tienda tiene productos activos."""
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(
            subcategories__products__shop_id=self.kwargs['shop_id'],
            subcategories__products__state='active',
        ).distinct()
