from web.models import *
from system.models import *
from django.contrib import admin

class ReadOnlyAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in self.model._meta.fields]


@admin.register(RequestDemo)
class RequestDemoAdmin(ReadOnlyAdmin):
    list_display = ('id', 'name', 'company_name', 'contact_number', 'email', 'created_at')
    search_fields = ('name', 'company_name', 'contact_number', 'email')
    ordering = ('-created_at',)


@admin.register(Contact)
class ContactAdmin(ReadOnlyAdmin):
    list_display = ('id', 'name', 'email', 'subject', 'submitted_at')
    search_fields = ('name', 'email', 'subject', 'message')
    list_filter = ('submitted_at',)
    ordering = ('-submitted_at',)


@admin.register(BookRider)
class BookRiderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'client', 'pickup_address', 'delivery_address',
        'estimated_distance_km', 'estimated_delivery_time',
        'booking_price', 'payment_type', 'status', 'delete_status'
    )
    search_fields = (
        'client__username', 'pickup_address', 'delivery_address',
        'payment_type', 'status'
    )
    list_filter = ('status', 'delete_status', 'created_at')
    ordering = ('-created_at',)


@admin.register(BookRiderAssignment)
class BookRiderAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'book_rider', 'rider', 'assigned_at',
        'in_progress_at', 'completed_at', 'cancelled_at', 'status'
    )
    search_fields = (
        'book_rider__client__username', 'rider__name', 'status'
    )
    list_filter = ('status', 'assigned_at', 'in_progress_at', 'completed_at', 'cancelled_at')
    ordering = ('-assigned_at',)
