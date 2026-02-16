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
    path('place-order/<int:product_id>/', views.place_order, name='place_order'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
