from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from .models import Vendor, Product, Category, OrderItem
import re  # unused atm but might need for validation later

# VENDOR SIGNUP FORM
class VendorSignupForm(forms.ModelForm):
    # TODO: add email verification later
    # User fields
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password (min 6 characters)'
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )
    
    class Meta:
        model = Vendor
        fields = [
            'shop_name', 'owner_name', 'email', 'phone',
            'address', 'city', 'state', 'pincode',
            'latitude', 'longitude', 'delivery_radius',
            'shop_logo', 'shop_banner'
        ]
        widgets = {
            'shop_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Shop Name'}),
            'owner_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your@email.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1234567890'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Full Address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 560001, 560034'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '28.7041', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '77.1025', 'step': '0.000001'}),
            'delivery_radius': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '5.0', 'step': '0.5'}),
            'shop_logo': forms.FileInput(attrs={'class': 'form-control'}),
            'shop_banner': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Username already exists')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Vendor.objects.filter(email=email).exists():
            raise ValidationError('Email already registered as vendor')
        return email

    def clean_pincode(self):
        raw_value = self.cleaned_data.get('pincode', '')
        digit_chunks = re.findall(r'\d+', raw_value)
        pins = []
        seen = set()

        for chunk in digit_chunks:
            if len(chunk) != 6:
                raise ValidationError('Each pincode must be exactly 6 digits.')
            pin = chunk
            if pin not in seen:
                pins.append(pin)
                seen.add(pin)

        if not pins:
            raise ValidationError('Please enter at least one valid 6-digit pincode.')

        return ', '.join(pins)
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password:
            if password != confirm_password:
                raise ValidationError('Passwords do not match')
            if len(password) < 6:
                raise ValidationError('Password must be at least 6 characters')
        
        return cleaned_data


# VENDOR LOGIN FORM
class VendorLoginForm(forms.Form):
    # login here
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )


# VENDOR PROFILE FORM
class VendorProfileForm(forms.ModelForm):
    # edit shop details
    class Meta:
        model = Vendor
        fields = [
            'shop_name', 'owner_name', 'email', 'phone',
            'address', 'city', 'state', 'pincode',
            'latitude', 'longitude', 'delivery_radius',
            'shop_logo', 'shop_banner'
        ]
        widgets = {
            'shop_name': forms.TextInput(attrs={'class': 'form-control'}),
            'owner_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 560001, 560034'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'delivery_radius': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'shop_logo': forms.FileInput(attrs={'class': 'form-control'}),
            'shop_banner': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_pincode(self):
        raw_value = self.cleaned_data.get('pincode', '')
        digit_chunks = re.findall(r'\d+', raw_value)
        pins = []
        seen = set()

        for chunk in digit_chunks:
            if len(chunk) != 6:
                raise ValidationError('Each pincode must be exactly 6 digits.')
            pin = chunk
            if pin not in seen:
                pins.append(pin)
                seen.add(pin)

        if not pins:
            raise ValidationError('Please enter at least one valid 6-digit pincode.')

        return ', '.join(pins)


# PRODUCT FORM
class ProductForm(forms.ModelForm):
    # FIXME: add image preview later
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="Select a category",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically load active categories
        self.fields['category'].queryset = Category.objects.filter(is_active=True)
    
    class Meta:
        model = Product
        fields = [
            'name', 'category', 'description', 'price', 'discount_price',
            'quantity', 'weight', 'unit', 'low_stock_threshold',
            'image'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Product Description'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'discount_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Optional', 'step': '0.01'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Optional', 'step': '0.01'}),
            'unit': forms.Select(attrs={'class': 'form-control'}),
            'low_stock_threshold': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '10'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        discount_price = cleaned_data.get('discount_price')
        
        if discount_price and price:
            if discount_price >= price:
                raise ValidationError('Discount price must be less than regular price')
        
        return cleaned_data



# ORDER STATUS UPDATE FORM
class OrderStatusUpdateForm(forms.ModelForm):
    # update order status fields
    class Meta:
        model = OrderItem
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
