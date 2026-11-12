from django.core.paginator import Paginator
from decimal import Decimal, InvalidOperation

from django.db.models import DecimalField, ExpressionWrapper, F, Q
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response

from shop.models import Product
from shop.serializers import ProductSerializer


def public_products():
    """Productos visibles para cualquier visitante: activos y de tiendas aprobadas."""
    return Product.objects.filter(state='active', shop__is_active=True).select_related('shop', 'subcategory')


def paginate(request, queryset, default_limit=10, max_limit=100):
    try:
        page = max(int(request.query_params.get('page', 1)), 1)
        limit = min(max(int(request.query_params.get('limit', default_limit)), 1), max_limit)
    except ValueError:
        page, limit = 1, default_limit
    paginator = Paginator(queryset, limit)
    return paginator, paginator.get_page(page)


def paginated_response(request, queryset, key='results', default_limit=10):
    paginator, page = paginate(request, queryset, default_limit)
    data = ProductSerializer(page.object_list, many=True, context={'request': request}).data
    return Response({key: data, 'total': paginator.count, 'pages': paginator.num_pages, 'current': page.number})


# ---------------------------------------------------------------- gestión (tienda autenticada)
class ProductListCreateView(generics.ListCreateAPIView):
    """GET: productos de la tienda autenticada. POST: crea un producto para esa tienda."""
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(shop=self.request.user).order_by('-created_at')


class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Lectura/edición/borrado, solo de productos propios."""
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(shop=self.request.user)


class ProductUpdateView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        product = Product.objects.filter(pk=pk, shop=request.user).first()
        if not product:
            return Response({'detail': 'Producto no encontrado o permiso denegado.'},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = ProductSerializer(product, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ProductDeleteView(generics.DestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(shop=self.request.user)


# ---------------------------------------------------------------- lectura pública
class ProductDetailAPIView(generics.RetrieveAPIView):
    """Detalle público (solo lectura)."""
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return public_products()


class ProductsByShopView(views.APIView):
    def get(self, request, shop_id):
        return paginated_response(request, public_products().filter(shop_id=shop_id).order_by('-created_at'))


class ProductsByCategory(views.APIView):
    def get(self, request, category_id):
        qs = public_products().filter(subcategory__category_id=category_id).order_by('-created_at')
        return paginated_response(request, qs)


class ProductsByCategoryShop(views.APIView):
    def get(self, request, shop_id, category_id):
        qs = public_products().filter(shop_id=shop_id, subcategory__category_id=category_id).order_by('-created_at')
        return paginated_response(request, qs)


class ProductsByShopAndSubcategoryView(views.APIView):
    def get(self, request, shop_id, subcategory_id):
        qs = public_products().filter(shop_id=shop_id, subcategory_id=subcategory_id).order_by('-created_at')
        return paginated_response(request, qs)


class ProductsByShopAndBestDiscountView(views.APIView):
    def get(self, request, shop_id):
        qs = public_products().order_by('-discount')
        if str(shop_id) == '-1':
            qs = qs[:15]
        else:
            qs = qs.filter(shop_id=shop_id)
        return Response(ProductSerializer(qs, many=True, context={'request': request}).data)


ORDERINGS = {
    'relevance': ('-discount', '-created_at'),
    'price_asc': ('final_sort', 'id'),
    'price_desc': ('-final_sort', 'id'),
    'discount': ('-discount', '-created_at'),
    'newest': ('-created_at',),
}


def _num(value):
    try:
        return Decimal(value)
    except (InvalidOperation, TypeError):
        return None


class ProductsSearchView(views.APIView):
    """
    Búsqueda y listado con filtros (todos opcionales):
    query, category, subcategory, shop (id), min_price, max_price (sobre el precio final),
    discounted=1, in_stock=1, exclude (id de producto), ordering=relevance|price_asc|price_desc|discount|newest,
    page, limit.
    """

    def get(self, request):
        q = request.query_params
        qs = public_products().annotate(
            final_sort=ExpressionWrapper(F('price') * (100 - F('discount')) / 100, output_field=DecimalField())
        )
        query = q.get('query', '').strip()
        for word in query.split():
            qs = qs.filter(
                Q(shop__razon_social__icontains=word) | Q(name__icontains=word) |
                Q(description__icontains=word) | Q(subcategory__name__icontains=word) |
                Q(subcategory__category__name__icontains=word)
            )
        if q.get('category', '').isdigit():
            qs = qs.filter(subcategory__category_id=q['category'])
        if q.get('subcategory', '').isdigit():
            qs = qs.filter(subcategory_id=q['subcategory'])
        if q.get('shop', '').isdigit():
            qs = qs.filter(shop_id=q['shop'])
        if q.get('exclude', '').isdigit():
            qs = qs.exclude(pk=q['exclude'])
        lo, hi = _num(q.get('min_price')), _num(q.get('max_price'))
        if lo is not None:
            qs = qs.filter(final_sort__gte=lo)
        if hi is not None:
            qs = qs.filter(final_sort__lte=hi)
        if q.get('discounted') in ('1', 'true'):
            qs = qs.filter(discount__gt=0)
        if q.get('in_stock') in ('1', 'true'):
            qs = qs.filter(Q(stock__isnull=True) | Q(stock__gt=0))
        qs = qs.order_by(*ORDERINGS.get(q.get('ordering'), ORDERINGS['relevance']))
        return paginated_response(request, qs.prefetch_related('gallery'), key='products', default_limit=24)


search_products = ProductsSearchView.as_view()
