from django.contrib import admin
<<<<<<< HEAD
from .models import UserProfile
import csv  # FIXME: implement export-to-csv admin action later
import csv  # FIXME: implement export-to-csv admin action

# Register your models here.

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user']
    search_fields = ['user__username', 'user__email']
=======
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
>>>>>>> 66b6aa0 (added the checkout page)
