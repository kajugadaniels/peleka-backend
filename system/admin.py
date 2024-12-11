from web.models import *
from system.models import *
from account.models import *
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    list_filter = ('name',)
    ordering = ('name',)
    empty_value_display = '-Empty-'

    def has_add_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'email', 'name', 'phone_number', 'role', 'is_staff', 'is_active', 'created_at')
    list_filter = ('is_staff', 'is_active', 'role')
    search_fields = ('email', 'name', 'phone_number')
    ordering = ('-created_at',)
    readonly_fields = ('last_login', 'created_at', 'otp_created_at')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(RequestDemo)
class RequestDemoAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'company_name', 'contact_number', 'email')
    search_fields = ('name', 'company_name', 'contact_number', 'email')
    ordering = ('id',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'subject', 'submitted_at')
    search_fields = ('name', 'email', 'subject', 'message')
    list_filter = ('submitted_at',)
    ordering = ('-submitted_at',)
    readonly_fields = ('submitted_at',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Rider)
class RiderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone_number', 'code', 'plate_number', 'insurance', 'image_tag', 'permit_image_tag', 'created_at', 'updated_at')
    search_fields = ('name', 'phone_number', 'code', 'plate_number', 'nid')
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    fields = (
        'name', 'phone_number', 'address', 'code', 'nid', 'plate_number',
        'insurance', 'image', 'permit_image', 'created_at', 'updated_at'
    )

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;"/>', obj.image.url)
        return "-"
    image_tag.short_description = 'Image'

    def permit_image_tag(self, obj):
        if obj.permit_image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;"/>', obj.permit_image.url)
        return "-"
    permit_image_tag.short_description = 'Permit Image'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class RiderDeliveryInline(admin.TabularInline):
    model = RiderDelivery
    extra = 0
    readonly_fields = ('delivered', 'assigned_at', 'in_progress_at', 'delivered_at')
    can_delete = False
    show_change_link = True
    fields = ('rider', 'delivered', 'assigned_at', 'in_progress_at', 'delivered_at')

@admin.register(DeliveryRequest)
class DeliveryRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'client', 'package_name', 'estimated_distance_km', 'delivery_price',
        'status', 'payment_type', 'created_at', 'updated_at'
    )
    list_filter = ('status', 'payment_type', 'created_at', 'updated_at')
    search_fields = (
        'client__name', 'client__email', 'package_name', 'recipient_name',
        'recipient_phone'
    )
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [RiderDeliveryInline]
    list_select_related = ('client',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(RiderDelivery)
class RiderDeliveryAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'rider', 'delivery_request', 'delivered',
        'assigned_at', 'in_progress_at', 'delivered_at'
    )
    list_filter = ('delivered', 'assigned_at', 'in_progress_at', 'delivered_at')
    search_fields = ('rider__name', 'delivery_request__id')
    ordering = ('-assigned_at',)
    readonly_fields = ('assigned_at', 'in_progress_at', 'delivered_at')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.site_header = "Peleka Admin"
admin.site.site_title = "Peleka Admin Portal"
admin.site.index_title = "Welcome to the Peleka Admin Portal"
