from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('products/', views.products, name='products'),
    path('search/', views.search, name='search'),
    path('favorites/', views.favorites, name='favorites'),
    path('add_to_favorites/<int:product_id>/', views.add_to_favorites, name='add_to_favorites'),
    path('remove_from_favorites/<int:product_id>/', views.remove_from_favorites, name='remove_from_favorites'),
    path('cart/', views.cart, name='cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('make_order/', views.make_order, name='make_order'),
    path('success/', views.success, name='success'),
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('stripe_webhook/', views.my_webhook_view, name='stripe_webhook'),
]
