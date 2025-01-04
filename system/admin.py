from django.contrib import admin
from system.models import Rider, DistancePricing, DeliveryRequest, RiderDelivery
from django.utils.html import format_html

class ReadOnlyAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in self.model._meta.fields]


@admin.register(Rider)
class RiderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone_number', 'code', 'plate_number', 'insurance', 'image_tag', 'permit_image_tag', 'created_at', 'updated_at')
    search_fields = ('name', 'phone_number', 'code', 'plate_number', 'nid')
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)

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


# @admin.register(DistancePricing)
# class DistancePricingAdmin(ReadOnlyAdmin):
#     list_display = ('BASE_DISTANCE', 'BASE_PRICE', 'ADDITIONAL_DISTANCE', 'ADDITIONAL_PRICE')
#     ordering = ('BASE_DISTANCE',)


@admin.register(DeliveryRequest)
class DeliveryRequestAdmin(ReadOnlyAdmin):
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
    list_select_related = ('client',)


@admin.register(RiderDelivery)
class RiderDeliveryAdmin(ReadOnlyAdmin):
    list_display = (
        'id', 'rider', 'delivery_request', 'delivered',
        'assigned_at', 'in_progress_at', 'delivered_at'
    )
    list_filter = ('delivered', 'assigned_at', 'in_progress_at', 'delivered_at')
    search_fields = ('rider__name', 'delivery_request__id')
    ordering = ('-assigned_at',)
