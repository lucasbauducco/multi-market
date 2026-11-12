from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (Category, CustomUser, Order, OrderItem, Product, ProductImage, State,
                     SubCategory, User_Category, UserHistory, UserType)


@admin.action(description='Aprobar tiendas seleccionadas (activar)')
def approve_shops(modeladmin, request, queryset):
    queryset.update(is_active=True)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'razon_social', 'email', 'cuit', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_staff')
    search_fields = ('username', 'razon_social', 'cuit', 'email')
    actions = [approve_shops]
    fieldsets = UserAdmin.fieldsets + (
        ('Datos de la tienda', {'fields': ('user_type', 'state', 'cuit', 'razon_social', 'domicilio_fiscal',
                                           'ingresos_brutos', 'inicio_actividades', 'telefono',
                                           'slug', 'logo', 'banner', 'description')}),
    )


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    list_display = ('name', 'shop', 'price', 'discount', 'stock', 'state', 'created_at')
    list_filter = ('state', 'subcategory__category')
    search_fields = ('name', 'barcode', 'shop__razon_social')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'name', 'unit_price', 'quantity')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'shop', 'buyer_name', 'total', 'status', 'payment_method', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_method', 'payment_status')
    inlines = [OrderItemInline]


for model in (UserType, UserHistory, User_Category, SubCategory, Category, State):
    admin.site.register(model)
