"""Medios de pago disponibles por tienda. Cada medio es un código estable usado en Order.payment_method."""
from .models import ShopPaymentSettings

LABELS = {
    'mercadopago': 'Mercado Pago',
    'transfer': 'Transferencia bancaria',
    'cash': 'Efectivo / retiro en local',
    'link': 'Link de pago',
}


def settings_for(shop):
    obj, _ = ShopPaymentSettings.objects.get_or_create(shop=shop)
    return obj


def available_methods(shop):
    ps = settings_for(shop)
    out = []
    if ps.mp_enabled and ps.mp_connected:
        out.append({'code': 'mercadopago', 'label': LABELS['mercadopago'], 'online': True,
                    'description': 'Tarjetas, dinero en cuenta, cuotas y QR. Pagás ahora de forma segura.'})
    if ps.accepts_transfer and (ps.transfer_alias or ps.transfer_cbu):
        out.append({'code': 'transfer', 'label': LABELS['transfer'], 'online': False,
                    'description': 'Te mostramos los datos para transferir y subís el comprobante.'})
    if ps.accepts_link and ps.link_url:
        out.append({'code': 'link', 'label': ps.link_label or LABELS['link'], 'online': False,
                    'description': 'Pagás desde el link de la tienda.'})
    if ps.accepts_cash:
        out.append({'code': 'cash', 'label': LABELS['cash'], 'online': False,
                    'description': ps.cash_instructions or 'Pagás al retirar o al recibir el pedido.'})
    return out


def payment_instructions(order):
    """Datos que ve el comprador después de comprar, según el medio elegido."""
    ps = settings_for(order.shop)
    if order.payment_method == 'transfer':
        return {'type': 'transfer', 'holder': ps.transfer_holder, 'cbu': ps.transfer_cbu,
                'alias': ps.transfer_alias, 'amount': str(order.total)}
    if order.payment_method == 'link':
        return {'type': 'link', 'label': ps.link_label or LABELS['link'], 'url': ps.link_url,
                'amount': str(order.total)}
    if order.payment_method == 'cash':
        return {'type': 'cash', 'instructions': ps.cash_instructions, 'amount': str(order.total)}
    if order.payment_method == 'mercadopago':
        return {'type': 'mercadopago', 'amount': str(order.total)}
    return {}
