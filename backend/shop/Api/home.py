from django.db.models import Count, F, Q, Sum
from rest_framework import permissions, views
from rest_framework.response import Response

from shop.models import Category, Order, Product
from shop.serializers import ProductSerializer

from .product import public_products
from .shop import ShopPublicSerializer, _active_shops


class HomeView(views.APIView):
    """Datos de la portada en una sola llamada: ofertas, categorías con productos y tiendas destacadas."""

    def get(self, request):
        ctx = {'request': request}
        deals = public_products().filter(discount__gt=0).order_by('-discount', '-created_at')[:12]
        newest = public_products().order_by('-created_at')[:12]
        cats = (Category.objects
                .annotate(n=Count('subcategories__products',
                                  filter=Q(subcategories__products__state='active',
                                           subcategories__products__shop__is_active=True), distinct=True))
                .filter(n__gt=0).order_by('-n', 'name'))
        categories = []
        for c in cats:
            prods = public_products().filter(subcategory__category=c).order_by('-created_at')[:10]
            categories.append({'id': c.id, 'name': c.name, 'count': c.n,
                               'products': ProductSerializer(prods, many=True, context=ctx).data})
        shops = _active_shops().order_by('-product_count', 'razon_social')[:8]
        return Response({
            'deals': ProductSerializer(deals, many=True, context=ctx).data,
            'newest': ProductSerializer(newest, many=True, context=ctx).data,
            'categories': categories,
            'shops': ShopPublicSerializer(shops, many=True, context=ctx).data,
        })


class ShopDashboardView(views.APIView):
    """Resumen para el panel de la tienda autenticada."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        shop = request.user
        orders = Order.objects.filter(shop=shop)
        live = orders.exclude(status='cancelled')
        paid = live.filter(payment_status='paid')
        products = Product.objects.filter(shop=shop)
        low = products.filter(state='active', stock__isnull=False, stock__lte=3).order_by('stock')[:8]
        return Response({
            'orders_total': live.count(),
            'orders_pending': orders.filter(status='pending').count(),
            'sales_paid': str(paid.aggregate(t=Sum('total'))['t'] or 0),
            'sales_pending_payment': str(live.exclude(payment_status='paid')
                                         .aggregate(t=Sum('total'))['t'] or 0),
            'products_active': products.filter(state='active').count(),
            'products_total': products.count(),
            'low_stock': [{'id': p.id, 'name': p.name, 'stock': p.stock} for p in low],
            'recent_orders': [{'id': o.id, 'buyer_name': o.buyer_name, 'total': str(o.total), 'status': o.status,
                               'payment_status': o.payment_status, 'created_at': o.created_at}
                              for o in orders.order_by('-created_at')[:5]],
        })
