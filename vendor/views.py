# Vendor views - handles all vendor stuff

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q, F
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
from decimal import Decimal
import csv
import json  # might use later

from .models import Vendor, Product, Category, OrderItem, calculate_distance
from .forms import (
    VendorSignupForm,
    VendorLoginForm,
    VendorProfileForm,
    ProductForm,
    OrderStatusUpdateForm
)


# ==================== DECORATORS ====================

def vendor_required(view_func):
    # make sure vendor is approved
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'vendor_profile'):
            messages.error(request, 'You need to register as a vendor first')
            return redirect('register_vendor')
        
        vendor = request.user.vendor_profile
        
        if vendor.status == 'pending':
            return redirect('vendor_pending_approval')
        
        if vendor.status in ['rejected', 'blocked']:
            messages.error(request, f'Your vendor account is {vendor.status}')
            return redirect('home')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


# ==================== AUTHENTICATION VIEWS ====================

def register_vendor(request):
    """
    Handle vendor registration with business information.
    
    Validates:
        - Username uniqueness
        - Email availability
        - Required vendor fields
    
    Creates:
        - Django User account
        - Vendor profile (status: pending)
    
    Actions:
        - Sends registration confirmation email
        - Auto-logs in new vendor
        - Redirects to approval page
    """
    if request.user.is_authenticated and hasattr(request.user, 'vendor_profile'):
        return redirect('vendor_dashboard')
    
    if request.method == 'POST':
        form = VendorSignupForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                # Create user
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    password=form.cleaned_data['password'],
                    email=form.cleaned_data['email']
                )
                
                # Create vendor profile
                vendor = form.save(commit=False)
                vendor.user = user
                vendor.status = 'pending'
                vendor.save()
                
                # Send registration email
                _send_vendor_registration_email(vendor)
                
                # Auto-login
                login(request, user)
                messages.success(request, 'Registration successful! Your account is pending approval.')
                
                return redirect('vendor_pending_approval')
                
            except Exception as error:
                messages.error(request, 'Error creating vendor account. Please try again.')
                print(f"Vendor registration error: {error}")
                return redirect('register_vendor')
    else:
        form = VendorSignupForm()
    
    return render(request, 'vendor/vendor_signup.html', {'form': form})


def login_vendor(request):
    """
    Handle vendor login with status validation.
    
    Validates:
        - Credentials against User model
        - User has vendor profile
        - Vendor account is approved
    
    Status handling:
        - pending: Redirect to approval page
        - approved: Redirect to dashboard
        - rejected/blocked: Logout and show error
    """
    if request.user.is_authenticated and hasattr(request.user, 'vendor_profile'):
        return redirect('vendor_dashboard')
    
    if request.method == 'POST':
        form = VendorLoginForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                # Check vendor profile exists
                if not hasattr(user, 'vendor_profile'):
                    messages.error(request, 'This account is not registered as a vendor')
                    return redirect('login_vendor')
                
                vendor = user.vendor_profile
                login(request, user)
                
                # Handle vendor status
                if vendor.status == 'pending':
                    return redirect('vendor_pending_approval')
                elif vendor.status == 'approved':
                    messages.success(request, f'Welcome back, {vendor.shop_name}!')
                    return redirect('vendor_dashboard')
                else:
                    logout(request)
                    messages.error(request, f'Your vendor account is {vendor.status}')
                    return redirect('login_vendor')
            else:
                messages.error(request, 'Invalid username or password')
                return redirect('login_vendor')
    else:
        form = VendorLoginForm()
    
    return render(request, 'vendor/vendor_login.html', {'form': form})


@login_required
def logout_vendor(request):
    """Log out vendor and redirect to home."""
    logout(request)
    messages.success(request, 'You have been logged out')
    return redirect('home')


@login_required
def vendor_pending_approval(request):
    """
    Display pending approval page for vendors awaiting admin review.
    
    If vendor is already approved, redirects to dashboard.
    """
    if not hasattr(request.user, 'vendor_profile'):
        return redirect('register_vendor')
    
    vendor = request.user.vendor_profile
    
    if vendor.status == 'approved':
        return redirect('vendor_dashboard')
    
    return render(request, 'vendor/pending_approval.html', {'vendor': vendor})


# ==================== DASHBOARD ====================

@login_required
@vendor_required
def vendor_dashboard(request):
    """
    Main vendor dashboard with key metrics and recent activity.
    
    Shows:
        - Product inventory stats
        - Order statistics
        - Revenue calculations (today, week, month)
        - Recent orders and low stock alerts
    """
    vendor = request.user.vendor_profile
    
    # Date ranges
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Product statistics
    total_products = vendor.products.count()
    active_products = vendor.products.filter(is_available=True).count()
    low_stock_products = vendor.products.filter(
        quantity__gt=0,
        quantity__lte=F('low_stock_threshold')
    ).count()
    
    # Order statistics
    total_orders = vendor.order_items.count()
    pending_orders = vendor.order_items.filter(status='Pending').count()
    delivered_orders = vendor.order_items.filter(status='Delivered').count()
    
    # Revenue calculations
    total_revenue = vendor.order_items.filter(
        status='Delivered'
    ).aggregate(
        total=Sum(F('quantity') * F('price'))
    )['total'] or Decimal('0.00')
    
    today_revenue = vendor.order_items.filter(
        status='Delivered',
        updated_at__date=today
    ).aggregate(
        total=Sum(F('quantity') * F('price'))
    )['total'] or Decimal('0.00')
    
    week_revenue = vendor.order_items.filter(
        status='Delivered',
        updated_at__date__gte=week_ago
    ).aggregate(
        total=Sum(F('quantity') * F('price'))
    )['total'] or Decimal('0.00')
    
    month_revenue = vendor.order_items.filter(
        status='Delivered',
        updated_at__date__gte=month_ago
    ).aggregate(
        total=Sum(F('quantity') * F('price'))
    )['total'] or Decimal('0.00')
    
    # Recent data
    recent_orders = vendor.order_items.select_related(
        'order',
        'product'
    ).order_by('-created_at')[:10]
    
    low_stock_items = vendor.products.filter(
        quantity__gt=0,
        quantity__lte=F('low_stock_threshold')
    ).order_by('quantity')[:5]
    
    context = {
        'vendor': vendor,
        'total_products': total_products,
        'active_products': active_products,
        'low_stock_products': low_stock_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'delivered_orders': delivered_orders,
        'total_revenue': total_revenue,
        'today_revenue': today_revenue,
        'week_revenue': week_revenue,
        'month_revenue': month_revenue,
        'recent_orders': recent_orders,
        'low_stock_items': low_stock_items,
    }
    
    return render(request, 'vendor/dashboard.html', context)


# ==================== VENDOR PROFILE ====================

@login_required
@vendor_required
def vendor_profile(request):
    """
    View and edit vendor profile and business information.
    
    Allows vendors to update:
        - Shop details (name, description)
        - Contact information
        - Delivery settings
        - Branding (logo, banner)
    """
    vendor = request.user.vendor_profile
    
    if request.method == 'POST':
        form = VendorProfileForm(request.POST, request.FILES, instance=vendor)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('vendor_profile')
    else:
        form = VendorProfileForm(instance=vendor)
    
    context = {
        'form': form,
        'vendor': vendor
    }
    
    return render(request, 'vendor/profile.html', context)


# ==================== PRODUCT MANAGEMENT ====================

@login_required
@vendor_required
def product_list(request):
    """
    Display vendor's product inventory with filtering options.
    
    Filters:
        - Category
        - Availability (available/unavailable)
    """
    vendor = request.user.vendor_profile
    
    # Base queryset
    products = vendor.products.select_related('category').order_by('-created_at')
    
    # Apply filters
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    availability = request.GET.get('availability')
    if availability == 'available':
        products = products.filter(is_available=True)
    elif availability == 'unavailable':
        products = products.filter(is_available=False)
    
    categories = Category.objects.filter(is_active=True)
    
    context = {
        'vendor': vendor,
        'products': products,
        'categories': categories,
    }
    
    return render(request, 'vendor/product_list.html', context)


@login_required
@vendor_required
def add_product(request):
    """
    Add new product to vendor catalog.
    
    Validates:
        - Required fields
        - Discount price < regular price
        - Image upload (optional)
    """
    vendor = request.user.vendor_profile
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = vendor
            product.save()
            
            messages.success(request, f'Product "{product.name}" added successfully!')
            return redirect('product_list')
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'vendor': vendor,
        'action': 'Add'
    }
    
    return render(request, 'vendor/product_form.html', context)


@login_required
@vendor_required
def edit_product(request, product_id):
    """
    Edit existing product details.
    
    Only vendor who created product can edit.
    """
    vendor = request.user.vendor_profile
    product = get_object_or_404(Product, id=product_id, vendor=vendor)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        
        if form.is_valid():
            form.save()
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'vendor': vendor,
        'product': product,
        'action': 'Edit'
    }
    
    return render(request, 'vendor/product_form.html', context)


@login_required
@vendor_required
def delete_product(request, product_id):
    """
    Delete product from catalog with confirmation.
    """
    vendor = request.user.vendor_profile
    product = get_object_or_404(Product, id=product_id, vendor=vendor)
    
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully!')
        return redirect('product_list')
    
    context = {
        'product': product,
        'vendor': vendor
    }
    
    return render(request, 'vendor/product_confirm_delete.html', context)


@login_required
@vendor_required
def toggle_product_availability(request, product_id):
    """
    Toggle product between available and unavailable status.
    """
    vendor = request.user.vendor_profile
    product = get_object_or_404(Product, id=product_id, vendor=vendor)
    
    product.is_available = not product.is_available
    product.save()
    
    status = 'available' if product.is_available else 'unavailable'
    messages.success(request, f'Product "{product.name}" is now {status}')
    
    return redirect('product_list')


# ==================== ORDER MANAGEMENT ====================

@login_required
@vendor_required
def vendor_orders(request):
    """
    Display all orders containing vendor products with filtering.
    
    Filters:
        - Order status
        - Date range
    """
    vendor = request.user.vendor_profile
    
    # Base queryset with optimized queries
    order_items = vendor.order_items.select_related(
        'order',
        'product',
        'order__user'
    ).order_by('-created_at')
    
    # Apply status filter
    status = request.GET.get('status')
    if status:
        order_items = order_items.filter(status=status)
    
    # Apply date filters
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if date_from:
        order_items = order_items.filter(created_at__date__gte=date_from)
    if date_to:
        order_items = order_items.filter(created_at__date__lte=date_to)
    
    context = {
        'vendor': vendor,
        'order_items': order_items,
        'status_choices': OrderItem.STATUS_CHOICES,
    }
    
    return render(request, 'vendor/order_list.html', context)


@login_required
@vendor_required
def vendor_order_detail(request, order_item_id):
    """
    Display detailed order information for vendor.
    """
    vendor = request.user.vendor_profile
    
    order_item = get_object_or_404(
        OrderItem.objects.select_related('order', 'product', 'order__user'),
        id=order_item_id,
        vendor=vendor
    )
    
    context = {
        'vendor': vendor,
        'order_item': order_item,
    }
    
    return render(request, 'vendor/order_detail.html', context)


@login_required
@vendor_required
def update_order_status(request, order_item_id):
    """
    Update order item status and notify customer via email.
    """
    vendor = request.user.vendor_profile
    order_item = get_object_or_404(
        OrderItem.objects.select_related('order'),
        id=order_item_id,
        vendor=vendor
    )
    
    if request.method == 'POST':
        form = OrderStatusUpdateForm(request.POST, instance=order_item)
        
        if form.is_valid():
            form.save()
            messages.success(request, f'Order status updated to {order_item.status}')
            
            # Send notification email
            _send_order_status_email(order_item)
            
            return redirect('vendor_order_detail', order_item_id=order_item.id)
    else:
        form = OrderStatusUpdateForm(instance=order_item)
    
    context = {
        'vendor': vendor,
        'order_item': order_item,
        'form': form,
    }
    
    return render(request, 'vendor/update_order_status.html', context)


# ==================== ANALYTICS & REPORTS ====================

@login_required
@vendor_required
def earnings_report(request):
    """
    Display sales and revenue analytics with advanced filtering.
    
    Filters:
        - Date range
        - Product
        - Category
    
    Shows:
        - Total revenue and order count
        - Revenue breakdown by product
        - Revenue breakdown by category
    """
    vendor = request.user.vendor_profile
    
    # Get filter parameters
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    product_id = request.GET.get('product')
    category_id = request.GET.get('category')
    
    # Base queryset
    order_items = vendor.order_items.filter(
        status='Delivered'
    ).select_related('product', 'product__category')
    
    # Apply filters
    if date_from:
        order_items = order_items.filter(updated_at__date__gte=date_from)
    if date_to:
        order_items = order_items.filter(updated_at__date__lte=date_to)
    if product_id:
        order_items = order_items.filter(product_id=product_id)
    if category_id:
        order_items = order_items.filter(product__category_id=category_id)
    
    # Calculate totals
    total_revenue = order_items.aggregate(
        total=Sum(F('quantity') * F('price'))
    )['total'] or Decimal('0.00')
    
    total_orders = order_items.count()
    total_items_sold = order_items.aggregate(total=Sum('quantity'))['total'] or 0
    
    # Revenue by product
    revenue_by_product = order_items.values('product__name').annotate(
        revenue=Sum(F('quantity') * F('price')),
        orders=Count('id')
    ).order_by('-revenue')[:10]
    
    # Revenue by category
    revenue_by_category = order_items.values('product__category__name').annotate(
        revenue=Sum(F('quantity') * F('price')),
        orders=Count('id')
    ).order_by('-revenue')
    
    context = {
        'vendor': vendor,
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'total_items_sold': total_items_sold,
        'revenue_by_product': revenue_by_product,
        'revenue_by_category': revenue_by_category,
        'products': vendor.products.all(),
        'categories': Category.objects.filter(is_active=True),
    }
    
    return render(request, 'vendor/earnings.html', context)


@login_required
@vendor_required
def export_sales_csv(request):
    """
    Export sales data to CSV file for offline analysis.
    
    Includes:
        - Order ID
        - Product details
        - Quantity and price
        - Order status
        - Date information
    """
    vendor = request.user.vendor_profile
    
    # Create CSV response
    filename = f"sales_report_{vendor.shop_name}_{datetime.now().strftime('%Y%m%d')}.csv"
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Write CSV
    writer = csv.writer(response)
    writer.writerow(['Order ID', 'Product', 'Quantity', 'Price', 'Total', 'Status', 'Date'])
    
    order_items = vendor.order_items.filter(
        status='Delivered'
    ).select_related('product', 'order')
    
    for item in order_items:
        writer.writerow([
            item.order.id,
            item.product.name,
            item.quantity,
            item.price,
            item.get_total_price(),
            item.status,
            item.created_at.strftime('%Y-%m-%d %H:%M')
        ])
    
    return response


# ==================== HELPER FUNCTIONS ====================

def _send_vendor_registration_email(vendor):
    """Send registration confirmation email to vendor."""
    try:
        subject = "Vendor Registration Confirmation"
        message = f"""
Hello {vendor.owner_name},

Thank you for registering as a vendor on Blinkit!

Shop: {vendor.shop_name}
Status: Pending Approval

Our admin team will review your application and approve it shortly.
You'll receive an email notification once your account is approved.

In the meantime, you can log in and prepare your product catalog.

Best regards,
Blinkit Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [vendor.email],
            fail_silently=True
        )
    except Exception as error:
        print(f"Error sending registration email: {error}")


def _send_order_status_email(order_item):
    """Send order status update email to customer."""
    try:
        subject = f"Order Update - {order_item.product.name}"
        message = f"""
Hello {order_item.order.customer_name},

Your order has been updated:

Product: {order_item.product.name}
Quantity: {order_item.quantity}
Current Status: {order_item.status}

Order ID: #{order_item.order.id}

Thank you for shopping with Blinkit!
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [order_item.order.user.email],
            fail_silently=True
        )
    except Exception as error:
        print(f"Error sending order status email: {error}")


def get_products_in_delivery_range(user_latitude, user_longitude):
    """
    Get products from vendors within delivery range of user location.
    
    Uses Haversine formula to calculate distance between
    user location and vendor locations.
    
    Args:
        user_latitude: Customer's latitude coordinate
        user_longitude: Customer's longitude coordinate
    
    Returns:
        QuerySet of available products from vendors in range
    """
    if not user_latitude or not user_longitude:
        return Product.objects.filter(
            is_available=True,
            is_active=True,
            vendor__status='approved'
        )
    
    available_products = []
    vendors = Vendor.objects.filter(status='approved')
    
    for vendor in vendors:
        if vendor.latitude and vendor.longitude:
            distance = calculate_distance(
                user_latitude,
                user_longitude,
                vendor.latitude,
                vendor.longitude
            )
            
            # Include products if within delivery range
            if distance and distance <= float(vendor.delivery_radius):
                vendor_products = vendor.products.filter(
                    is_available=True,
                    is_active=True
                )
                available_products.extend(vendor_products)
    
    return available_products
