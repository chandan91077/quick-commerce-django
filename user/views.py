from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

def home(request):
    return render(request, 'home.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email', '')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not username:
            messages.error(request, 'Username is required')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register')

        if not password:
            messages.error(request, 'Password is required')
            return redirect('register')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('register')

        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters')
            return redirect('register')

        if email and User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        if email:
            subject = "Welcome to Blinkit"
            message = f"Hello {username},\n\nWelcome to Blinkit! Your account was created successfully."
            from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
            try:
                send_mail(subject, message, from_email, [email], fail_silently=False)
            except Exception:
                messages.warning(request, "Account created, but we could not send the welcome email.")
        # Auto-login after registration
        login(request, user)
        messages.success(request, f'Welcome to Blinkit, {username}!')
        return redirect('home')

    return render(request, 'register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, 'Username and password are required')
            return redirect('login')

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
    """Handle user logout"""
    logout(request)
    messages.success(request, 'You have been logged out')
    return redirect('home')

