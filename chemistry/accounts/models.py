from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Add custom fields here if needed
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    is_approved = models.BooleanField(default=False)  # Field to track approval status
    pass
