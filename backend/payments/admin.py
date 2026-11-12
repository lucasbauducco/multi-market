from django.contrib import admin

from .models import Payment, ShopPaymentSettings


@admin.register(ShopPaymentSettings)
class ShopPaymentSettingsAdmin(admin.ModelAdmin):
    list_display = ('shop', 'accepts_transfer', 'accepts_cash', 'accepts_link', 'mp_enabled', 'mp_user_id')
    # Los tokens cifrados no se muestran ni editan desde el admin.
    exclude = ('mp_access_token_enc', 'mp_refresh_token_enc')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('provider', 'external_id', 'order', 'status', 'amount', 'created_at')
    readonly_fields = ('raw',)
