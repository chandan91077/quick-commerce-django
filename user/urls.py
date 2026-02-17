from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # path('admin/', admin.site.urls),  # Removed redundant admin url
    path('', views.home, name='home'),
    path('contact/', views.contact_us, name='contact_us'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('track-orders/', views.user_orders, name='user_orders'),
    path('category/<slug:category_slug>/', views.category_products, name='category_products'),
    
    # Cart & Checkout
    path('cart/', views.view_cart, name='view_cart'),
    path('add-to-cart/<slug:product_slug>/', views.add_to_cart, name='add_to_cart'),
    # path('place-order/<int:product_id>/', views.place_order, name='place_order'), # Replaced by cart flow
    path('update-cart/<int:item_id>/<str:action>/', views.update_cart_item, name='update_cart_item'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('process-checkout/', views.process_checkout, name='process_checkout'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
