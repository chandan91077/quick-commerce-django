from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse
from decimal import Decimal
import math
import uuid

# TODO: Add more comprehensive error handling for distance calculations
# VENDOR MODEL
class Vendor(models.Model):
    # Seller profile model
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('blocked', 'Blocked'),
    ]
    
    # Link to Django User
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendor_profile')
    
    # Shop Details
    shop_name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255, unique=True)
    owner_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    
    # Address & Location
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(
        max_length=200,
        help_text='Enter one or more 6-digit pincodes (comma separated)'
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Delivery Settings
    delivery_radius = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=5.0,
        validators=[MinValueValidator(0.5), MaxValueValidator(50.0)],
        help_text="Delivery radius in kilometers"
    )
    
    # Shop Branding
    shop_logo = models.ImageField(upload_to='vendor/logos/', null=True, blank=True)
    shop_banner = models.ImageField(upload_to='vendor/banners/', null=True, blank=True)
    
    # Approval Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Vendor'
        verbose_name_plural = 'Vendors'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.shop_name)
        super(Vendor, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.shop_name} - {self.owner_name}"

    def get_serviceable_pincodes(self):
        """Return unique valid 6-digit pincodes configured for this vendor."""
        if not self.pincode:
            return []

        import re

        parts = re.findall(r'\d{6}', str(self.pincode))
        normalized = []
        seen = set()
        for value in parts:
            pin = value.strip()
            if pin not in seen:
                normalized.append(pin)
                seen.add(pin)
        return normalized
    
    def is_approved(self):
        """Check if vendor is approved"""
        return self.status == 'approved'
    
    def total_products(self):
        """Get total number of products"""
        return self.products.count()
    
    def total_revenue(self):
        """Calculate total revenue from delivered orders"""
        from django.db.models import Sum
        total = self.order_items.filter(status='Delivered').aggregate(
            total=Sum(models.F('quantity') * models.F('price'))
        )['total']
        return total or Decimal('0.00')


# ==================== CATEGORY MODEL ====================
class Category(models.Model):
    # Product categories
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_products', kwargs={'category_slug': self.slug})

# ==================== PRODUCT MODEL ====================
class Product(models.Model):
    # FIXME: Need to handle image upload failures better
    UNIT_CHOICES = [
        ('kg', 'Kilogram'),
        ('g', 'Gram'),
        ('l', 'Liter'),
        ('ml', 'Milliliter'),
        ('piece', 'Piece'),
        ('pack', 'Pack'),
    ]
    
    # Relationships
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    
    # Product Details
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    discount_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)]
    )
    
    # Inventory
    quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='piece')
    low_stock_threshold = models.IntegerField(default=10, validators=[MinValueValidator(0)])
    
    # Media
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    
    # Status
    is_available = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.vendor.shop_name}"

    def get_absolute_url(self):
        return reverse('edit_product', kwargs={'product_slug': self.slug})
    
    def get_display_price(self):
        """Return discount price if available, otherwise regular price"""
        return self.discount_price if self.discount_price else self.price
    
    def is_in_stock(self):
        """Check if product is in stock"""
        return self.quantity > 0
    
    def is_low_stock(self):
        """Check if product stock is low"""
        return 0 < self.quantity <= self.low_stock_threshold
    
    def get_savings(self):
        """Calculate savings if discount price exists"""
        if self.discount_price and self.discount_price < self.price:
            return self.price - self.discount_price
        return Decimal('0.00')


# ==================== ORDER MODEL ====================
class Order(models.Model):
    """
    Order model - customer orders
    """
    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('online', 'Online Payment'),
        ('upi', 'UPI'),
        ('card', 'Card'),
    ]
    
    # Relationships
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    
    # Order Details
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cod')
    is_paid = models.BooleanField(default=False)
    
    # Delivery Address
    delivery_address = models.TextField()
    delivery_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    delivery_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Customer Contact
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=15)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
    
    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"
    
    def get_order_items_count(self):
        """Get total number of items in order"""
        return self.items.count()


# ==================== ORDER ITEM MODEL ====================
class OrderItem(models.Model):
    """
    Order Item model - individual products in an order
    """
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Packed', 'Packed'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]
    
    # Relationships
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='order_items')
    
    # Item Details
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of purchase
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity} - Order #{self.order.id}"
    
    def get_total_price(self):
        """Calculate total price for this item"""
        return self.quantity * self.price
    
    def can_cancel(self):
        """Check if item can be cancelled"""
        return self.status in ['Pending', 'Accepted']


# ==================== HELPER FUNCTIONS ====================
def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two points using Haversine formula
    Returns distance in kilometers
    """
    if not all([lat1, lon1, lat2, lon2]):
        return None
    
    # Convert to float
    lat1, lon1, lat2, lon2 = float(lat1), float(lon1), float(lat2), float(lon2)
    
    # Radius of Earth in kilometers
    R = 6371.0
    
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return round(distance, 2)
