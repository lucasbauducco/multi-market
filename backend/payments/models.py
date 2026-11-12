from django.conf import settings
from django.db import models
from datetime import timedelta

from django.utils import timezone

from . import crypto


class ShopPaymentSettings(models.Model):
    """Medios de pago que acepta cada tienda."""
    shop = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payment_settings')

    # Transferencia bancaria
    accepts_transfer = models.BooleanField(default=False)
    transfer_holder = models.CharField(max_length=120, blank=True)
    transfer_cbu = models.CharField(max_length=22, blank=True)
    transfer_alias = models.CharField(max_length=40, blank=True)

    # Efectivo / retiro en local / contra entrega
    accepts_cash = models.BooleanField(default=True)
    cash_instructions = models.CharField(max_length=300, blank=True)

    # Link de pago externo (Ualá Bis, MODO, PayPal.me, etc.)
    accepts_link = models.BooleanField(default=False)
    link_label = models.CharField(max_length=40, blank=True)
    link_url = models.URLField(blank=True)

    # Mercado Pago (OAuth del vendedor). Los tokens se guardan cifrados.
    mp_enabled = models.BooleanField(default=True)
    mp_user_id = models.CharField(max_length=40, blank=True)
    mp_public_key = models.CharField(max_length=120, blank=True)
    mp_access_token_enc = models.TextField(blank=True)
    mp_refresh_token_enc = models.TextField(blank=True)
    mp_expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Shop payment settings'

    def __str__(self):
        return f'Pagos de {self.shop}'

    @property
    def mp_connected(self):
        return bool(self.mp_access_token_enc)

    @property
    def mp_access_token(self):
        return crypto.decrypt(self.mp_access_token_enc)

    @property
    def mp_refresh_token(self):
        return crypto.decrypt(self.mp_refresh_token_enc)

    def set_mp_tokens(self, access_token, refresh_token, expires_in=None, user_id='', public_key=''):
        self.mp_access_token_enc = crypto.encrypt(access_token)
        self.mp_refresh_token_enc = crypto.encrypt(refresh_token or '')
        self.mp_expires_at = timezone.now() + timedelta(seconds=int(expires_in)) if expires_in else None
        if user_id:
            self.mp_user_id = str(user_id)
        if public_key:
            self.mp_public_key = public_key

    def clear_mp(self):
        self.mp_access_token_enc = self.mp_refresh_token_enc = ''
        self.mp_user_id = self.mp_public_key = ''
        self.mp_expires_at = None


class Payment(models.Model):
    """Registro de cada pago informado por una pasarela (idempotente por proveedor + id externo)."""
    order = models.ForeignKey('shop.Order', on_delete=models.CASCADE, related_name='payments')
    provider = models.CharField(max_length=20)
    external_id = models.CharField(max_length=64)
    status = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    raw = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('provider', 'external_id')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.provider}:{self.external_id} ({self.status})'
