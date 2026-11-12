from django.urls import path

from . import views

urlpatterns = [
    path('checkout/methods/', views.CheckoutMethodsView.as_view(), name='checkout-methods'),
    path('shop/payment-settings/', views.ShopPaymentSettingsView.as_view(), name='payment-settings'),
    path('orders/track/<uuid:token>/', views.OrderTrackView.as_view(), name='order-track'),
    path('orders/track/<uuid:token>/proof/', views.OrderProofView.as_view(), name='order-proof'),
    path('orders/<int:pk>/payment/', views.ShopOrderPaymentView.as_view(), name='order-payment'),
    path('orders/<uuid:token>/pay/mercadopago/', views.MercadoPagoPreferenceView.as_view(), name='mp-preference'),
    path('payments/mercadopago/connect/', views.MercadoPagoConnectView.as_view(), name='mp-connect'),
    path('payments/mercadopago/disconnect/', views.MercadoPagoDisconnectView.as_view(), name='mp-disconnect'),
    path('payments/mercadopago/oauth/callback/', views.MercadoPagoCallbackView.as_view(), name='mp-callback'),
    path('payments/mercadopago/webhook/', views.MercadoPagoWebhookView.as_view(), name='mp-webhook'),
]
