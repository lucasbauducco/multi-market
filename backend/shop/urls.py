from django.urls import path

from .Api.auth import VerifyUserToken
from .Api.category import CategoriesByShopView, CategoriesWithProductsView, CategoryList
from .Api.order import CheckoutView, ShopOrderListView, ShopOrderStatusView
from .Api.product import (
    ProductDeleteView,
    ProductDetailAPIView,
    ProductListCreateView,
    ProductRetrieveUpdateDestroyView,
    ProductsByCategory,
    ProductsByCategoryShop,
    ProductsByShopAndBestDiscountView,
    ProductsByShopAndSubcategoryView,
    ProductsByShopView,
    ProductsSearchView,
    ProductUpdateView,
    search_products,
)
from .Api.shop import ProductShopView, ShopProductsListView
from .Api.subcategory import SubCategoryList
from .Api.user import (
    ChangeUserStateView,
    CreateUserView,
    CustomUserDetailView,
    RegisterShopView,
    UpdateUserView,
)

urlpatterns = [
    # Usuarios / tiendas
    path('register/', RegisterShopView.as_view(), name='register_shop'),
    path('create_user/', CreateUserView.as_view(), name='create_user'),
    path('update_user/<int:pk>/', UpdateUserView.as_view(), name='update_user'),
    path('change_user_state/<int:pk>/', ChangeUserStateView.as_view(), name='change_user_state'),
    path('users/<str:username>/', CustomUserDetailView.as_view(), name='custom-user-detail'),
    path('token/verify/', VerifyUserToken.as_view(), name='verify_user_token'),

    # Pedidos
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('orders/', ShopOrderListView.as_view(), name='shop-orders'),
    path('orders/<int:pk>/status/', ShopOrderStatusView.as_view(), name='shop-order-status'),

    # Gestión de productos (tienda autenticada, solo los propios)
    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductRetrieveUpdateDestroyView.as_view(), name='product-retrieve-update-destroy'),
    path('product/update/<int:pk>/', ProductUpdateView.as_view(), name='product-update'),
    path('products/delete/<int:pk>/', ProductDeleteView.as_view(), name='delete-product'),

    # Lectura pública
    path('product/<int:pk>/', ProductDetailAPIView.as_view(), name='product-detail'),
    path('product/<int:product_id>/shop/', ProductShopView.as_view(), name='product_shop'),
    path('shop/<int:shop_id>/products/', ShopProductsListView.as_view(), name='shop-products-list'),
    path('products/shop/<int:shop_id>/', ProductsByShopView.as_view()),
    path('products/shop/<int:shop_id>/category/<int:category_id>/', ProductsByCategoryShop.as_view()),
    path('products/shop/<int:shop_id>/subcategory/<int:subcategory_id>/', ProductsByShopAndSubcategoryView.as_view()),
    path('products/category/<int:category_id>/', ProductsByCategory.as_view(), name='products-by-category'),
    path('products/shop/<str:shop_id>/best_discount/', ProductsByShopAndBestDiscountView.as_view()),
    path('products/search/', ProductsSearchView.as_view()),
    path('search_products/', search_products, name='search_products'),

    # Categorías
    path('categories/', CategoryList.as_view(), name='user-category-list'),
    path('categories/categories-with-products/', CategoriesWithProductsView.as_view(), name='categories-with-products'),
    path('categories/shop/<int:shop_id>/', CategoriesByShopView.as_view(), name='categories-by-shop'),
    path('subcategories/', SubCategoryList.as_view(), name='subcategories-list'),
]
