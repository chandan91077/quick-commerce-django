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


# ... (imports remain the same)

def home(request):
    """
    Display home page with featured products from approved vendors.
    
    Context:
        products: Latest 20 active products from approved vendors (filtered by category if selected)
        categories: All active product categories
        selected_category: The currently selected category object (if any)
    """
    try:
        from vendor.models import Product, Category
        
        # Get category filter (now using slug)
        category_slug = request.GET.get('category')
        selected_category = None
        
        # Base query
        products = Product.objects.filter(
            is_active=True,
            is_available=True,
            vendor__status='approved'
        ).select_related(
            'category',
            'vendor'
        )
        
        # Apply filter if selected
        if category_slug:
            try:
                selected_category = Category.objects.get(slug=category_slug)
                products = products.filter(category=selected_category)
            except Category.DoesNotExist:
                pass
        
        # Order and limit
        products = products.order_by('-created_at')[:20]
        
        categories = Category.objects.filter(
            is_active=True
        ).order_by('name')
        
        # Map images to categories (temporary helper until images are in DB)
        # TODO: Add image field to Category model in future
        category_images = {
            'Paan Corner': 'images/paan-corner_web.png',
            'Dairy, Bread & Eggs': 'images/Dairy,Bread&Eggs.png',
            'Fruits & Vegetables': 'images/Fruits&Vegetables.png',
            'Cold Drinks & Juices': 'images/ColdDrinks&Juices.png',
            'Snacks & Munchies': 'images/Snacks&Munchies.png',
            'Breakfast & Instant Food': 'images/Breakfast&InstantFood.png',
            'Sweet Tooth': 'images/SweetTooth.png',
            'Bakery & Biscuits': 'images/Bakery&Biscuits.png',
            'Tea, Coffee & Milk Drinks': 'images/Tea,Coffee&MilkDrinks.png',
            'Atta, Rice & Dal': 'images/Atta,Rice&Dal.png',
            'Masala, Oil & More': 'images/Masala,Oil&More.png',
            'Sauces & Spreads': 'images/Sauces&Spreads.png',
            'Chicken, Meat & Fish': 'images/Chicken,Meat&Fish.png',
            'Organic & Healthy Living': 'images/Organic&HealthyLiving.png',
            'Baby Care': 'images/BabyCare.png',
            'Pharma & Wellness': 'images/Pharma&Wellness.png',
            'Cleaning Essentials': 'images/CleaningEssentials.png',
            'Home & Office': 'images/Home&Office.png',
            'Personal Care': 'images/PersonalCare.png',
            'Pet Care': 'images/PetCare.png',
        }
        
        # Attach images to category objects
        for cat in categories:
            cat.image_url = category_images.get(cat.name, 'images/default_cat.png')
            
        # Get special category IDs for banner cards (using slugs for URLs, but ID lookup is fine internally if needed, or switch to slug)
        # Actually special_cats are used in home.html for links, so we should ideally use slugs there too if we update template
        special_cats = {
            'pharma': Category.objects.filter(name__icontains='Pharma').first(),
            'pet': Category.objects.filter(name__icontains='Pet').first(),
            'baby': Category.objects.filter(name__icontains='Baby').first(),
        }
        
        context = {
            'products': products,
            'categories': categories,
            'selected_category': selected_category,
            'special_cats': special_cats
        }
    except Exception as error:
        messages.error(request, 'Error loading products. Please try again later.')
        context = {
            'products': [],
            'categories': [],
            'selected_category': None,
            'special_cats': {}
        }
        print(f"Error loading products: {error}")
    
    return render(request, 'home.html', context)


def category_products(request, category_slug):
    """
    Display all products for a specific category.
    """
    try:
        from vendor.models import Product, Category
        
        category = Category.objects.get(slug=category_slug)
        
        products = Product.objects.filter(
            category=category,
            is_active=True,
            is_available=True,
            vendor__status='approved'
        ).select_related('vendor').order_by('-created_at')
        
        # Get all categories for sidebar
        categories = Category.objects.filter(is_active=True).order_by('name')
        
        # Map image for the category header and sidebar (reusing same logic)
        category_images = {
            'Paan Corner': 'images/paan-corner_web.png',
            'Dairy, Bread & Eggs': 'images/Dairy,Bread&Eggs.png',
            'Fruits & Vegetables': 'images/Fruits&Vegetables.png',
            'Cold Drinks & Juices': 'images/ColdDrinks&Juices.png',
            'Snacks & Munchies': 'images/Snacks&Munchies.png',
            'Breakfast & Instant Food': 'images/Breakfast&InstantFood.png',
            'Sweet Tooth': 'images/SweetTooth.png',
            'Bakery & Biscuits': 'images/Bakery&Biscuits.png',
            'Tea, Coffee & Milk Drinks': 'images/Tea,Coffee&MilkDrinks.png',
            'Atta, Rice & Dal': 'images/Atta,Rice&Dal.png',
            'Masala, Oil & More': 'images/Masala,Oil&More.png',
            'Sauces & Spreads': 'images/Sauces&Spreads.png',
            'Chicken, Meat & Fish': 'images/Chicken,Meat&Fish.png',
            'Organic & Healthy Living': 'images/Organic&HealthyLiving.png',
            'Baby Care': 'images/BabyCare.png',
            'Pharma & Wellness': 'images/Pharma&Wellness.png',
            'Cleaning Essentials': 'images/CleaningEssentials.png',
            'Home & Office': 'images/Home&Office.png',
            'Personal Care': 'images/PersonalCare.png',
            'Pet Care': 'images/PetCare.png',
        }
        
        # Attach images to all categories
        for cat in categories:
            cat.image_url = category_images.get(cat.name, 'images/default_cat.png')
            
        # Attach image for current category specifically (though it's in the list too)
        category.image_url = category_images.get(category.name, 'images/default_cat.png')
        
        context = {
            'category': category,
            'products': products,
            'categories': categories # Passed for sidebar
        }
        return render(request, 'category_products.html', context)
        
    except Category.DoesNotExist:
        messages.error(request, 'Category not found')
        return redirect('home')
    except Exception as error:
        print(f"Error loading category products: {error}")
        messages.error(request, 'Error loading products')
        return redirect('home')


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

# ==================== CART VIEWS ====================

@login_required(login_url='login')
def add_to_cart(request, product_slug):
    """
    Add a product to the user's cart.
    """
    try:
        from vendor.models import Product
        from .models import Cart, CartItem
        
        product = Product.objects.get(slug=product_slug)
        
        if product.quantity < 1:
            messages.error(request, 'Product is out of stock')
            return redirect('home')
        
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
        
        if not item_created:
            if cart_item.quantity + 1 > product.quantity:
                 messages.warning(request, f'Only {product.quantity} items available in stock.')
            else:
                cart_item.quantity += 1
                cart_item.save()
                messages.success(request, 'Item quantity updated in cart')
        else:
            cart_item.quantity = 1
            cart_item.save()
            messages.success(request, 'Item added to cart')
            
        return redirect('view_cart')
        
    except Product.DoesNotExist:
        messages.error(request, 'Product not found')
        return redirect('home')
    except Exception as e:
        print(f"Error adding to cart: {e}")
        messages.error(request, 'Error adding item to cart')
        return redirect('home')


@login_required(login_url='login')
def view_cart(request):
    """
    Display the user's cart.
    """
    try:
        from .models import Cart
        cart, created = Cart.objects.get_or_create(user=request.user)
        return render(request, 'cart.html', {'cart': cart})
    except Exception as e:
        print(f"Error viewing cart: {e}")
        messages.error(request, 'Error loading cart')
        return redirect('home')


@login_required(login_url='login')
def update_cart_item(request, item_id, action):
    """
    Update quantity of a cart item.
    action: 'increment' or 'decrement'
    """
    try:
        from .models import CartItem
        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        
        if action == 'increment':
            if cart_item.quantity + 1 > cart_item.product.quantity:
                messages.warning(request, f'Only {cart_item.product.quantity} items available.')
            else:
                cart_item.quantity += 1
                cart_item.save()
        elif action == 'decrement':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
        
        return redirect('view_cart')
        
    except CartItem.DoesNotExist:
        messages.error(request, 'Item not found in cart')
        return redirect('view_cart')


@login_required(login_url='login')
def remove_from_cart(request, item_id):
    """
    Remove an item from the cart.
    """
    try:
        from .models import CartItem
        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        cart_item.delete()
        messages.success(request, 'Item removed from cart')
        return redirect('view_cart')
    except CartItem.DoesNotExist:
        messages.error(request, 'Item not found')
        return redirect('view_cart')


@login_required(login_url='login')
def checkout(request):
    """
    Display checkout page with order summary.
    """
    try:
        from .models import Cart
        cart = Cart.objects.get(user=request.user)
        
        if cart.items.count() == 0:
            messages.warning(request, 'Your cart is empty')
            return redirect('home')
            
        context = {
            'cart': cart,
            'user': request.user
        }
        return render(request, 'checkout.html', context)
        
    except Cart.DoesNotExist:
        messages.warning(request, 'Your cart is empty')
        return redirect('home')


@login_required(login_url='login')
def process_checkout(request):
    """
    Process the checkout form and create order.
    """
    if request.method != 'POST':
        return redirect('checkout')
        
    try:
        from vendor.models import Order, OrderItem
        from .models import Cart
        
        cart = Cart.objects.get(user=request.user)
        if cart.items.count() == 0:
            return redirect('home')
            
        # Get form data
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        payment_method = request.POST.get('payment_method')
        
        if not all([name, phone, address, payment_method]):
            messages.error(request, 'All fields are required')
            return redirect('checkout')
            
        # Create Order
        order = Order.objects.create(
            user=request.user,
            total_amount=cart.get_total_price(),
            customer_name=name,
            customer_phone=phone,
            delivery_address=address,
            payment_method=payment_method,
            is_paid=(payment_method != 'cod') # Simplified for now
        )
        
        # Create Order Items
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                vendor=item.product.vendor,
                quantity=item.quantity,
                price=item.product.get_display_price(),
                status='Pending'
            )
            
            # Reduce stock
            item.product.quantity -= item.quantity
            item.product.save()
            
        # Clear Cart
        cart.items.all().delete()
        
        messages.success(request, 'Order placed successfully!')
        return redirect('user_orders')
        
    except Exception as e:
        print(f"Checkout error: {e}")
        messages.error(request, 'Error processing checkout')
        return redirect('checkout')
