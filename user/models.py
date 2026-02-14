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
