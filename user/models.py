from django.db import models
from django.contrib.auth.models import User
from datetime import datetime  # unused atm
import uuid

# Create your models here.

class UserProfile(models.Model):
    # user profile extension
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}"


class ContactMessage(models.Model):
    SOURCE_CHOICES = [
        ('user', 'User'),
        ('vendor', 'Vendor'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='user')
    name = models.CharField(max_length=120)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"
