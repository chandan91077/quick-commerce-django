"""
User application views.

This module handles user-related views including:
- Home page display with products
- User registration and authentication
- Order management
"""

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required

from .models import ContactMessage


# ==================== PUBLIC VIEWS ====================

def home(request):
    """
    Display home page with featured products from approved vendors.
    
    Context:
        products: Latest 20 active products from approved vendors
        categories: All active product categories
    """
    try:
        from vendor.models import Product, Category
        
        products = Product.objects.filter(
            is_active=True,
            is_available=True,
            vendor__status='approved'
        ).select_related(
            'category',
            'vendor'
        ).order_by('-created_at')[:20]
        
        categories = Category.objects.filter(
            is_active=True
        ).order_by('name')
        
        context = {
            'products': products,
            'categories': categories
        }
    except Exception as error:
        messages.error(request, 'Error loading products. Please try again later.')
        context = {
            'products': [],
            'categories': []
        }
        print(f"Error loading products: {error}")
    
    return render(request, 'home.html', context)


def contact_us(request, source='user'):
    """
    Handle Contact Us form submissions.

    Stores messages in the database and sends an acknowledgement email.
    """
    initial_name = ''
    initial_email = ''

    if request.user.is_authenticated:
        initial_name = request.user.get_full_name() or request.user.username
        initial_email = request.user.email

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if not name or not email or not subject or not message:
            messages.error(request, 'All fields are required.')
        else:
            ContactMessage.objects.create(
                user=request.user if request.user.is_authenticated else None,
                source=source,
                name=name,
                email=email,
                subject=subject,
                message=message,
            )

            try:
                ack_subject = 'We received your message'
                ack_message = (
                    f"Hi {name},\n\n"
                    "Thanks for contacting Blinkit. We will reach out to you as soon as possible.\n\n"
                    "Regards,\n"
                    "Blinkit Team"
                )
                send_mail(
                    ack_subject,
                    ack_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
            except Exception as error:
                messages.warning(request, 'Message saved, but email could not be sent.')
                print(f"Contact email error: {error}")

            messages.success(request, 'Thanks! Your message has been sent.')
            return redirect('contact_us' if source == 'user' else 'vendor_contact')

    context = {
        'name': initial_name,
        'email': initial_email,
        'source': source,
    }
    return render(request, 'contact.html', context)


# ==================== AUTHENTICATION VIEWS ====================

def register_view(request):
    """
    Handle user registration with validation.
    
    Validates:
        - Username uniqueness
        - Email uniqueness
        - Password strength and confirmation
    
    On success: Auto-logs in user and redirects to home
    """
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        # Validation
        validation_errors = _validate_registration(username, email, password, confirm_password)
        
        if validation_errors:
            for error in validation_errors:
                messages.error(request, error)
            return redirect('register')
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # Send welcome email
            _send_welcome_email(username, email)
            
            # Auto-login
            login(request, user)
            messages.success(request, f'Welcome to Blinkit, {username}!')
            return redirect('home')
            
        except Exception as error:
            messages.error(request, 'Error creating account. Please try again.')
            print(f"Registration error: {error}")
            return redirect('register')
    
    return render(request, 'register.html')


def login_view(request):
    """
    Handle user login with authentication.
    
    Validates username and password against Django User model.
    On success: Redirects to home page
    """
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        # Validation
        if not username or not password:
            messages.error(request, 'Username and password are required')
            return redirect('login')
        
        # Authenticate
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('login')
    
    return render(request, 'login.html')


def logout_view(request):
    """
    Handle user logout and redirect to home page.
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('home')


# ==================== ORDER VIEWS ====================

@login_required(login_url='login')
def place_order(request, product_id):
    """
    Create and place a new order for a product.
    
    Args:
        request: HTTP request object
        product_id: ID of the product to order
    
    Validates:
        - Product exists
        - Product is in stock
    
    Creates:
        - Order instance with customer info
        - OrderItem linking product to order
    """
    try:
        from vendor.models import Product, Order, OrderItem
        
        product = Product.objects.get(id=product_id)
        
        # Validate stock
        if product.quantity < 1:
            messages.error(request, f'{product.name} is currently out of stock.')
            return redirect('home')
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            total_amount=product.get_display_price(),
            customer_name=request.user.get_full_name() or request.user.username,
            customer_phone='',
            delivery_address='',
            payment_method='cod',
            is_paid=False
        )
        
        # Create order item
        OrderItem.objects.create(
            order=order,
            product=product,
            vendor=product.vendor,
            quantity=1,
            price=product.get_display_price(),
            status='Pending'
        )
        
        # Update inventory
        product.quantity -= 1
        product.save()
        
        messages.success(request, f'Order placed successfully for {product.name}!')
        return redirect('user_orders')
        
    except Product.DoesNotExist:
        messages.error(request, 'Product not found')
        return redirect('home')
    except Exception as error:
        messages.error(request, 'Error placing order. Please try again.')
        print(f"Order placement error: {error}")
        return redirect('home')


@login_required(login_url='login')
def user_orders(request):
    """
    Display user's order history with all order items.
    
    Optimized queries using prefetch_related for order items.
    """
    try:
        from vendor.models import Order
        
        orders = Order.objects.filter(
            user=request.user
        ).prefetch_related(
            'items__product'
        ).order_by('-created_at')
        
        context = {'orders': orders}
    except Exception as error:
        messages.error(request, 'Error loading orders')
        context = {'orders': []}
        print(f"Error loading orders: {error}")
    
    return render(request, 'user_orders.html', context)


# ==================== HELPER FUNCTIONS ====================

def _validate_registration(username, email, password, confirm_password):
    """
    Validate registration form data.
    
    Args:
        username: Proposed username
        email: Proposed email
        password: Proposed password
        confirm_password: Password confirmation
    
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    # Username validation
    if not username:
        errors.append('Username is required')
    elif len(username) < 3:
        errors.append('Username must be at least 3 characters')
    elif User.objects.filter(username=username).exists():
        errors.append('Username already exists')
    
    # Email validation
    if email and User.objects.filter(email=email).exists():
        errors.append('Email already registered')
    
    # Password validation
    if not password:
        errors.append('Password is required')
    elif len(password) < 6:
        errors.append('Password must be at least 6 characters')
    elif password != confirm_password:
        errors.append('Passwords do not match')
    
    return errors


def _send_welcome_email(username, email):
    """
    Send welcome email to new user.
    
    Args:
        username: User's username
        email: User's email address
    """
    try:
        subject = "Welcome to Blinkit!"
        message = f"""
Hello {username},

Welcome to Blinkit! Your account has been created successfully.

Start browsing thousands of products from vendors near you and get them delivered quickly.

Best regards,
Blinkit Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=True
        )
    except Exception as error:
        print(f"Error sending welcome email: {error}")
