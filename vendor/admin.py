from django.contrib import admin
from django.utils.html import format_html
from .models import Vendor, Category, Product, Order, OrderItem
import logging

logger = logging.getLogger(__name__)  # TODO: use this somewhere

# VENDOR ADMIN
@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    # Admin for Vendor model
    list_display = [
        'shop_name', 'owner_name', 'email', 'phone', 'city', 
        'status_badge', 'total_products', 'created_at'
    ]
    list_filter = ['status', 'city', 'state', 'created_at']
    search_fields = ['shop_name', 'owner_name', 'email', 'phone', 'city']
    readonly_fields = ['created_at', 'updated_at', 'user']
    
    fieldsets = (
        ('User Account', {
            'fields': ('user', 'status')
        }),
        ('Shop Information', {
            'fields': ('shop_name', 'owner_name', 'email', 'phone')
        }),
        ('Location Details', {
            'fields': ('address', 'city', 'state', 'pincode')
        }),
        ('Branding', {
            'fields': ('shop_logo', 'shop_banner'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_vendors', 'reject_vendors', 'block_vendors']
    
    def status_badge(self, obj):
        """Display status with color badge"""
        colors = {
            'pending': '#ffc107',
            'approved': '#28a745',
            'rejected': '#dc3545',
            'blocked': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def total_products(self, obj):
        """Display total number of products"""
        return obj.products.count()
    total_products.short_description = 'Products'
    
    def approve_vendors(self, request, queryset):
        """Bulk approve vendors"""
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} vendor(s) approved successfully')
    approve_vendors.short_description = 'Approve selected vendors'
    
    def reject_vendors(self, request, queryset):
        """Bulk reject vendors"""
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} vendor(s) rejected')
    reject_vendors.short_description = 'Reject selected vendors'
    
    def block_vendors(self, request, queryset):
        """Bulk block vendors"""
        updated = queryset.update(status='blocked')
        self.message_user(request, f'{updated} vendor(s) blocked')
    block_vendors.short_description = 'Block selected vendors'


# ==================== CATEGORY ADMIN ====================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for Category model
    """
    list_display = ['name', 'is_active', 'product_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    
    def product_count(self, obj):
        """Display number of products in category"""
        return obj.products.count()
    product_count.short_description = 'Products'


# ==================== PRODUCT ADMIN ====================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin interface for Product model
    """
    list_display = [
        'name', 'vendor', 'category', 'price_display', 'quantity', 
        'availability_badge', 'is_active', 'created_at'
    ]
    list_filter = ['is_available', 'is_active', 'category', 'vendor', 'created_at']
    search_fields = ['name', 'vendor__shop_name', 'category__name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Product Information', {
            'fields': ('vendor', 'category', 'name', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'discount_price')
        }),
        ('Inventory', {
            'fields': ('quantity', 'weight', 'unit', 'low_stock_threshold')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Status', {
            'fields': ('is_available', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def price_display(self, obj):
        """Display price with discount"""
        if obj.discount_price:
            return format_html(
                '<span style="text-decoration: line-through; color: #999;">₹{}</span> <strong style="color: #28a745;">₹{}</strong>',
                obj.price, obj.discount_price
            )
        return f'₹{obj.price}'
    price_display.short_description = 'Price'
    
    def availability_badge(self, obj):
        """Display availability status"""
        if obj.is_available and obj.quantity > 0:
            color = '#28a745'
            text = 'Available'
        elif obj.quantity == 0:
            color = '#dc3545'
            text = 'Out of Stock'
        else:
            color = '#ffc107'
            text = 'Unavailable'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, text
        )
    availability_badge.short_description = 'Availability'


# ==================== ORDER ADMIN ====================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Admin interface for Order model
    """
    list_display = [
        'id', 'user', 'customer_name', 'total_amount', 
        'payment_method', 'payment_status', 'items_count', 'created_at'
    ]
    list_filter = ['payment_method', 'is_paid', 'created_at']
    search_fields = ['id', 'user__username', 'customer_name', 'customer_phone']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('user', 'total_amount', 'payment_method', 'is_paid')
        }),
        ('Customer Details', {
            'fields': ('customer_name', 'customer_phone', 'delivery_address', 'delivery_latitude', 'delivery_longitude')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def payment_status(self, obj):
        """Display payment status badge"""
        if obj.is_paid:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px;">Paid</span>'
            )
        return format_html(
            '<span style="background-color: #ffc107; color: white; padding: 3px 8px; border-radius: 3px;">Unpaid</span>'
        )
    payment_status.short_description = 'Payment'
    
    def items_count(self, obj):
        """Display number of items in order"""
        return obj.items.count()
    items_count.short_description = 'Items'


# ==================== ORDER ITEM ADMIN ====================
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Admin interface for OrderItem model
    """
    list_display = [
        'id', 'order', 'product', 'vendor', 'quantity', 
        'price', 'total_price', 'status_badge', 'created_at'
    ]
    list_filter = ['status', 'vendor', 'created_at']
    search_fields = ['order__id', 'product__name', 'vendor__shop_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Order Item Information', {
            'fields': ('order', 'product', 'vendor', 'quantity', 'price', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_price(self, obj):
        """Display total price for item"""
        return f'₹{obj.get_total_price()}'
    total_price.short_description = 'Total'
    
    def status_badge(self, obj):
        """Display status with color badge"""
        colors = {
            'Pending': '#ffc107',
            'Accepted': '#17a2b8',
            'Packed': '#6f42c1',
            'Out for Delivery': '#fd7e14',
            'Delivered': '#28a745',
            'Cancelled': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.status
        )
    status_badge.short_description = 'Status'


# Customize admin site header
admin.site.site_header = 'Blinkit Vendor Admin'
admin.site.site_title = 'Blinkit Admin'
admin.site.index_title = 'Vendor Management Dashboard'
