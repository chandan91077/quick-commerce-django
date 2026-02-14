from django.contrib import admin
from .models import UserProfile
import csv  # FIXME: implement export-to-csv admin action later
import csv  # FIXME: implement export-to-csv admin action

# Register your models here.

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user']
    search_fields = ['user__username', 'user__email']
