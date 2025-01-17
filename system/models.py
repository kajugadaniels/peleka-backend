import os
from web.models import *
from account.models import *
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from imagekit.processors import ResizeToFill
from imagekit.models import ProcessedImageField

def rider_image_path(instance, filename):
    base_filename, file_extension = os.path.splitext(filename)
    return f'riders/rider_{slugify(instance.name)}_{instance.phone_number}_{instance.plate_number}_{instance.code}{file_extension}'

def rider_permit_image_path(instance, filename):
    base_filename, file_extension = os.path.splitext(filename)
    return f'riders/permits/rider_{slugify(instance.name)}_{instance.plate_number}_{instance.phone_number}_{instance.code}{file_extension}'

class Rider(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.CharField(max_length=100, unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    code = models.CharField(max_length=20, unique=True, null=True, blank=True)
    nid = models.CharField(max_length=20, unique=True, null=True, blank=True)
    plate_number = models.CharField(max_length=255, null=True, blank=True)
    permit_image = ProcessedImageField(
        upload_to=rider_permit_image_path,
        processors=[ResizeToFill(1270, 1270)],
        format='JPEG',
        options={'quality': 90},
        null=True,
        blank=True
    )
    insurance = models.CharField(max_length=255, null=True, blank=True)
    image = ProcessedImageField(
        upload_to=rider_image_path,
        processors=[ResizeToFill(1270, 1270)],
        format='JPEG',
        options={'quality': 90},
        null=True,
        blank=True
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='rider_profile',
        help_text="Link to the rider's User account."
    )
    commissioner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='commissioner_riders',
        help_text="Optional: The commission agent for this rider."
    )
    boss = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='boss_riders',
        help_text="Optional: The boss agent for this rider."
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class DistancePricing(models.Model):
    BASE_DISTANCE = 5  # kilometers
    BASE_PRICE = 1000  # RWF
    ADDITIONAL_DISTANCE = 5  # kilometers for each additional rate
    ADDITIONAL_PRICE = 500  # RWF for every additional 5km

    class Meta:
        verbose_name = 'Distance Pricing'
        verbose_name_plural = 'Distance Pricing'

    @classmethod
    def calculate_price(cls, distance_km):
        if distance_km <= cls.BASE_DISTANCE:
            return cls.BASE_PRICE
        additional_distance = max(0, distance_km - cls.BASE_DISTANCE)
        additional_blocks = additional_distance // cls.ADDITIONAL_DISTANCE
        if additional_distance % cls.ADDITIONAL_DISTANCE > 0:
            additional_blocks += 1
        return cls.BASE_PRICE + (additional_blocks * cls.ADDITIONAL_PRICE)

# Function to define the image upload path for delivery requests
def delivery_request_image_path(instance, filename):
    base_filename, file_extension = os.path.splitext(filename)
    return f'delivery_requests/request_{slugify(instance.client.name)}_{instance.created_at}{file_extension}'

class DeliveryRequest(models.Model):
    REQUEST_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Successful', 'Successful'),
        ('Failed', 'Failed'),
        ('Cancelled', 'Cancelled'),
        ('Refunded', 'Refunded'),
    ]

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='delivery_requests', help_text='The client who requested the delivery')
    pickup_address = models.TextField(blank=True, null=True, help_text='The address where the package should be picked up')
    pickup_lat = models.CharField(max_length=100, null=True, blank=True, help_text='Latitude of the pickup location')
    pickup_lng = models.CharField(max_length=100, null=True, blank=True, help_text='Longitude of the pickup location')
    
    delivery_address = models.TextField(blank=True, null=True, help_text='The address where the package should be delivered')
    delivery_lat = models.CharField(max_length=100, null=True, blank=True, help_text='Latitude of the delivery location')
    delivery_lng = models.CharField(max_length=100, null=True, blank=True, help_text='Longitude of the delivery location')

    package_name = models.CharField(max_length=255, blank=True, null=True, help_text='Name of the package being delivered')
    package_description = models.TextField(blank=True, null=True, help_text='A description of the package to be delivered')
    recipient_name = models.CharField(max_length=255, blank=True, null=True, help_text='Name of the recipient')
    recipient_phone = models.CharField(max_length=15, blank=True, null=True, help_text='Phone number of the recipient')
    estimated_distance_km = models.CharField(max_length=15, blank=True, null=True, help_text='Estimated distance of the delivery in kilometers')
    estimated_delivery_time = models.CharField(max_length=15, blank=True, null=True, help_text='The estimated time for the package to be delivered')
    value_of_product = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text='The value of the product being delivered in RWF')
    delivery_price = models.CharField(max_length=100, null=True, blank=True, help_text='The calculated price for the delivery in RWF')
    payment_type = models.CharField(blank=True, null=True, max_length=255, help_text='The payment method for this delivery')
    
    image = ProcessedImageField(
        upload_to=delivery_request_image_path,
        processors=[ResizeToFill(1000, 1000)],
        format='JPEG',
        options={'quality': 90},
        null=True,
        blank=True,
        help_text='An optional image of the package'
    )
    
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending', help_text='Status of the payment')
    tx_ref = models.CharField(max_length=255, null=True, blank=True, unique=True, help_text='Unique transaction reference from Flutterwave')

    status = models.CharField(max_length=20, choices=REQUEST_STATUS_CHOICES, default='Pending', help_text='The current status of the delivery request')
    delete_status = models.BooleanField(default=False, help_text='Indicates if the delivery request has been deleted')
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='deleted_delivery_requests', help_text='The user who deleted the delivery request')
    
    created_at = models.DateTimeField(auto_now_add=True, help_text='The date and time when the request was created')
    updated_at = models.DateTimeField(auto_now=True, help_text='The date and time when the request was last updated')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Delivery Request'
        verbose_name_plural = 'Delivery Requests'

    def __str__(self):
        return f"Delivery Request by {self.client} - {self.status}"

class RiderDelivery(models.Model):
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE, related_name='rider_delivery', help_text='The rider assigned to deliveries')
    last_assigned_at = models.DateTimeField(blank=True, null=True, help_text='The last time the rider was assigned a delivery')
    delivery_request = models.ForeignKey(DeliveryRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name='rider_assignment', help_text='The delivery request currently assigned to the rider')
    delivered = models.BooleanField(default=False, help_text='Indicates whether the delivery has been completed')
    assigned_at = models.DateTimeField(blank=True, null=True, help_text='The timestamp when the rider was assigned to a delivery')
    in_progress_at = models.DateTimeField(blank=True, null=True, help_text='The timestamp when the delivery started')
    delivered_at = models.DateTimeField(blank=True, null=True, help_text='The timestamp when the delivery was completed')

    class Meta:
        verbose_name = 'Rider Delivery'
        verbose_name_plural = 'Rider Deliveries'

    def __str__(self):
        return f"Rider: {self.rider.name} - Status: {self.delivered}"

class BookRiderAssignment(models.Model):
    book_rider = models.ForeignKey(BookRider, on_delete=models.CASCADE, related_name='assignments', help_text='The booking request to which the rider is assigned')
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE, related_name='book_rider_assignments', help_text='The rider assigned to the booking')
    assigned_at = models.DateTimeField(blank=True, null=True, help_text='Timestamp when the rider was assigned')
    in_progress_at = models.DateTimeField(blank=True, null=True, help_text='Timestamp when the booking started')
    completed_at = models.DateTimeField(blank=True, null=True, help_text='Timestamp when the booking was completed')
    cancelled_at = models.DateTimeField(blank=True, null=True, help_text='Timestamp when the booking was cancelled')
    status = models.CharField(max_length=20, choices=BookRider.STATUS_CHOICES, default='Pending', help_text='Current status of the assignment')

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-assigned_at']
        verbose_name = 'Book Rider Assignment'
        verbose_name_plural = 'Book Rider Assignments'

    def __str__(self):
        return f"Assignment for {self.book_rider} to Rider: {self.rider.name} - Status: {self.status}"
