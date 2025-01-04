from account.models import *
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)
    list_filter = ('name',)
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at')

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'email', 'name', 'phone_number', 'role', 'is_staff', 'is_active', 'created_at')
    list_filter = ('is_staff', 'is_active', 'role')
    search_fields = ('email', 'name', 'phone_number')
    ordering = ('-created_at',)
    readonly_fields = ('last_login', 'created_at', 'otp_created_at')

    # Define fieldsets to organize the admin form
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('name', 'phone_number', 'image')}),
        (_('Permissions'), {
            'fields': ('role', 'is_active', 'is_staff', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'created_at', 'otp_created_at')}),
    )

    # Define add_fieldsets to handle user creation
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'phone_number', 'password1', 'password2'),
        }),
    )

    # Customize readonly fields
    readonly_fields = ('last_login', 'created_at', 'otp_created_at')

    # Ensure related fields are fetched efficiently
    list_select_related = ('role',)

    # Remove ReadOnlyAdmin behavior to allow changes
    def has_add_permission(self, request):
        return True  # Allow adding users

    def has_change_permission(self, request, obj=None):
        return True  # Allow changing users

    def has_delete_permission(self, request, obj=None):
        return True  # Allow deleting users
