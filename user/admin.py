from django.contrib import admin
from .models import UserProfile, ContactMessage, Cart, CartItem

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(ContactMessage)

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    inlines = [CartItemInline]
