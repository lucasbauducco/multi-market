from rest_framework import generics, permissions, status, views
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from shop.models import Order
from shop.serializers import CheckoutSerializer, OrderSerializer

# Transiciones permitidas para el estado de un pedido.
TRANSITIONS = {
    'pending': {'confirmed', 'cancelled'},
    'confirmed': {'delivered', 'cancelled'},
    'delivered': set(),
    'cancelled': set(),
}


class CheckoutView(views.APIView):
    """
    Checkout público (sin cuenta). Recibe datos del comprador y los items del carrito;
    crea un pedido por tienda. Los precios se calculan en el servidor.
    """
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'checkout'

    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        orders = serializer.save()
        return Response(OrderSerializer(orders, many=True).data, status=status.HTTP_201_CREATED)


class ShopOrderListView(generics.ListAPIView):
    """Pedidos recibidos por la tienda autenticada (?status=pending para filtrar)."""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Order.objects.filter(shop=self.request.user).prefetch_related('items').select_related('shop')
        status_filter = self.request.query_params.get('status')
        return qs.filter(status=status_filter) if status_filter else qs


class ShopOrderStatusView(views.APIView):
    """Cambia el estado de un pedido propio. Si se cancela, se devuelve el stock."""
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        order = Order.objects.filter(pk=pk, shop=request.user).prefetch_related('items__product').first()
        if not order:
            return Response({'detail': 'Pedido no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        new = request.data.get('status')
        if new not in TRANSITIONS[order.status]:
            raise ValidationError({'status': f'No se puede pasar de {order.status} a {new}.'})
        if new == 'cancelled':
            for item in order.items.all():
                p = item.product
                if p and p.stock is not None:
                    p.stock += item.quantity
                    p.save(update_fields=['stock'])
        order.status = new
        order.save(update_fields=['status'])
        return Response(OrderSerializer(order).data)
