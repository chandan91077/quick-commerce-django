from django.urls import path
from django.views.decorators.cache import cache_page  # might use for stats
from . import views

urlpatterns = [
    # Authentication
    path('signup/', views.register_vendor, name='register_vendor'),
    path('login/', views.login_vendor, name='login_vendor'),
    path('logout/', views.logout_vendor, name='logout_vendor'),
    path('pending-approval/', views.vendor_pending_approval, name='vendor_pending_approval'),
    
    # Dashboard
    path('dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('profile/', views.vendor_profile, name='vendor_profile'),
    
    # Product Management
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('products/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('products/<int:product_id>/toggle/', views.toggle_product_availability, name='toggle_product_availability'),
    
    # Order Management
    path('orders/', views.vendor_orders, name='vendor_orders'),
    path('orders/<int:order_item_id>/', views.vendor_order_detail, name='vendor_order_detail'),
    path('orders/<int:order_item_id>/update-status/', views.update_order_status, name='update_order_status'),
    
    # Earnings & Analytics
    path('earnings/', views.earnings_report, name='earnings_report'),
    path('earnings/export-csv/', views.export_sales_csv, name='export_sales_csv'),
]
