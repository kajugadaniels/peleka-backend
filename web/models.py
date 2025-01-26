from django.db import models
from account.models import *
from django.utils import timezone
from django.utils.text import slugify
from imagekit.processors import ResizeToFill
from imagekit.models import ProcessedImageField

class RequestDemo(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    company_name = models.CharField(max_length=100, null=True, blank=True)
    contact_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Request Demos"
        verbose_name_plural = "Request Demos"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.company_name}"


class Contact(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    subject = models.CharField(max_length=255, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Contact Us"
        verbose_name_plural = "Contact Us"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"


class BookRider(models.Model):
    STATUS_CHOICES = [
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

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='book_riders', help_text='The client who is booking the rider')
    pickup_address = models.TextField(blank=True, null=True, help_text='The address where the rider should pick up')
    pickup_lat = models.CharField(max_length=100, null=True, blank=True, help_text='Latitude of the pickup location')
    pickup_lng = models.CharField(max_length=100, null=True, blank=True, help_text='Longitude of the pickup location')
    
    delivery_address = models.TextField(blank=True, null=True, help_text='The address where the rider should deliver')
    delivery_lat = models.CharField(max_length=100, null=True, blank=True, help_text='Latitude of the delivery location')
    delivery_lng = models.CharField(max_length=100, null=True, blank=True, help_text='Longitude of the delivery location')

    estimated_distance_km = models.CharField(max_length=15, blank=True, null=True, help_text='Estimated distance in kilometers')
    estimated_delivery_time = models.CharField(max_length=15, blank=True, null=True, help_text='Estimated delivery time')
    booking_price = models.CharField(max_length=100, null=True, blank=True, help_text='Calculated price for booking the rider in RWF')
    payment_type = models.CharField(blank=True, null=True, max_length=255, help_text='Payment method for the booking')
    
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending', help_text='Status of the payment')
    tx_ref = models.CharField(max_length=255, null=True, blank=True, unique=True, help_text='Unique transaction reference from Flutterwave')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending', help_text='Current status of the booking request')
    delete_status = models.BooleanField(default=False, help_text='Indicates if the booking request has been deleted')
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='deleted_book_riders', help_text='User who deleted the booking request')
    
    created_at = models.DateTimeField(auto_now_add=True, help_text='Timestamp when the booking was created')
    updated_at = models.DateTimeField(auto_now=True, help_text='Timestamp when the booking was last updated')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Book Rider'
        verbose_name_plural = 'Book Riders'

    def __str__(self):
        return f"Book Rider by {self.client} - {self.status}"