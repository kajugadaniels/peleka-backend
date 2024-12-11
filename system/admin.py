from web.models import *
from system.models import *
from account.models import *
from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# -----------------------------
# Role Admin
# -----------------------------

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # Removed 'created_at'
    search_fields = ('name',)
    list_filter = ('name',)
    ordering = ('name',)
    empty_value_display = '-Empty-'

    def has_add_permission(self, request):
        return True  # Allow adding roles

    def has_delete_permission(self, request, obj=None):
        return True  # Allow deleting roles

# -----------------------------
# User Admin
# -----------------------------

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('name', 'phone_number', 'role', 'image')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'created_at')}),
        (_('Security'), {'fields': ('reset_otp', 'otp_created_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'phone_number', 'password1', 'password2'),
        }),
    )
    list_display = ('id', 'email', 'name', 'phone_number', 'role', 'is_staff', 'is_active', 'created_at')
    list_filter = ('is_staff', 'is_active', 'role')
    search_fields = ('email', 'name', 'phone_number')
    ordering = ('-created_at',)
    readonly_fields = ('last_login', 'created_at', 'otp_created_at')

    # Custom actions
    actions = ['activate_users', 'deactivate_users', 'reset_otp_for_users']

    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} user(s) successfully activated.")
    activate_users.short_description = "Activate selected users"

    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} user(s) successfully deactivated.")
    deactivate_users.short_description = "Deactivate selected users"

    def reset_otp_for_users(self, request, queryset):
        for user in queryset:
            user.reset_otp = ''
            user.otp_created_at = None
            user.save()
        self.message_user(request, "OTP reset for selected users.")
    reset_otp_for_users.short_description = "Reset OTP for selected users"

# -----------------------------
# RequestDemo Admin
# -----------------------------

@admin.register(RequestDemo)
class RequestDemoAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'company_name', 'contact_number', 'email')  # Removed 'created_at'
    search_fields = ('name', 'company_name', 'contact_number', 'email')
    list_filter = ()  # Removed 'created_at' filter
    ordering = ('id',)  # Changed ordering
    readonly_fields = ()  # Removed 'created_at' as it's nonexistent

# -----------------------------
# ContactUs Admin
# -----------------------------

@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'subject', 'submitted_at')
    search_fields = ('name', 'email', 'subject', 'message')
    list_filter = ('submitted_at',)
    ordering = ('-submitted_at',)
    readonly_fields = ('submitted_at',)

# -----------------------------
# Rider Admin
# -----------------------------

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

    # Display images in admin list view
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

# -----------------------------
# DistancePricing Admin
# -----------------------------

# Removed DistancePricingAdmin since the model does not have corresponding fields.
# If you intend to manage distance pricing via the admin, consider redesigning the model to include instance fields.

# Alternatively, if DistancePricing is meant to be a singleton, you can implement it accordingly.

# -----------------------------
# DeliveryRequest Admin
# -----------------------------

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

    # Display image thumbnail
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "-"
    image_preview.short_description = 'Image'

    # Custom actions
    actions = ['mark_as_completed', 'mark_as_cancelled']

    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='Completed')
        self.message_user(request, f"{updated} delivery request(s) marked as Completed.")
    mark_as_completed.short_description = "Mark selected deliveries as Completed"

    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='Cancelled')
        self.message_user(request, f"{updated} delivery request(s) marked as Cancelled.")
    mark_as_cancelled.short_description = "Mark selected deliveries as Cancelled"

# -----------------------------
# RiderDelivery Admin
# -----------------------------

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

    # Custom actions
    actions = ['mark_as_delivered']

    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(delivered=True, delivered_at=timezone.now())
        self.message_user(request, f"{updated} delivery(s) marked as Delivered.")
    mark_as_delivered.short_description = "Mark selected deliveries as Delivered"

# -----------------------------
# Registering Unregistered Models
# -----------------------------

# If there are any models not yet registered, register them here.
# For example, if you have additional models in 'web', 'system', or 'account' apps.

# -----------------------------
# Customizing Admin Site
# -----------------------------

admin.site.site_header = "Peleka Admin"
admin.site.site_title = "Peleka Admin Portal"
admin.site.index_title = "Welcome to the Peleka Admin Portal"
