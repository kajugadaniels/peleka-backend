import os
import random
from django.db import models
from account.managers import *
from django.utils import timezone
from django.utils.text import slugify
from imagekit.processors import ResizeToFill
from imagekit.models import ProcessedImageField
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Permission

class Role(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    permissions = models.ManyToManyField(Permission, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def has_permission(self, permission_codename):
        """Check if the given permission codename exists in the stored permissions."""
        return self.permissions.filter(codename=permission_codename).exists()

    def update_users_with_role_permissions(self):
        """Update all users who have this role with the current permissions."""
        users_with_role = User.objects.filter(role=self)
        for user in users_with_role:
            user.assign_role_permissions()

    def __str__(self):
        return self.name or "Unnamed Role"

def user_image_path(instance, filename):
    base_filename, file_extension = os.path.splitext(filename)
    return f'users/user_{slugify(instance.name)}_{instance.phone_number}_{instance.email}{file_extension}'

class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    username = models.CharField(unique=True, max_length=255, null=True, blank=True)
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

    def generate_username(self):
        """Generate a unique username based on name and random 4 digits."""
        base_username = slugify(self.name) if self.name else "user"
        random_digits = str(random.randint(1000, 9999))
        return f"{base_username}-{random_digits}"

    def assign_role_permissions(self):
        """Assign or update permissions based on the user's role."""
        if self.role:
            role_permissions = self.role.permissions.all()
            # Add new permissions without removing existing ones
            for perm in role_permissions:
                self.user_permissions.add(perm)

    def save(self, *args, **kwargs):
        # If username is not set or name has changed, regenerate the username
        if not self.username or self.name and self.pk:
            self.username = self.generate_username()

        # Save the user object first, then assign permissions
        super(User, self).save(*args, **kwargs)
        self.assign_role_permissions()

    def __str__(self):
        return f"{self.name}"