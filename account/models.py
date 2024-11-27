import os
import random
from django.db import models
from account.managers import *
from django.utils import timezone
from django.utils.text import slugify
from imagekit.processors import ResizeToFill
from imagekit.models import ProcessedImageField
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

class Role(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name or "Unnamed Role"

def user_image_path(instance, filename):
    base_filename, file_extension = os.path.splitext(filename)
    return f'users/user_{slugify(instance.name)}_{instance.phone_number}_{instance.email}{file_extension}'

class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone_number = models.CharField(unique=True, max_length=20, null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True, blank=True)
    image = ProcessedImageField(
        upload_to=user_image_path,
        processors=[ResizeToFill(1270, 1270)],
        format='JPEG',
        options={'quality': 90},
        null=True,
        blank=True
    )
    password = models.CharField(max_length=255, null=True, blank=True)
    reset_otp = models.CharField(max_length=7, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone_number']

    def __str__(self):
        return f"{self.name}"