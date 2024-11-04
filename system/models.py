import os
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

def rider_image_path(instance, filename):
    base_filename, file_extension = os.path.splitext(filename)
    return f'riders/rider_{slugify(instance.name)}_{instance.phone_number}_{instance.code}{file_extension}'

class Rider(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    address = models.CharField(max_length=20, null=True, blank=True)
    code = models.CharField(max_length=20, unique=True, null=True, blank=True)
    nid = models.CharField(max_length=20, unique=True, null=True, blank=True)
    image = ProcessedImageField(
        upload_to=rider_image_path,
        processors=[ResizeToFill(1270, 1270)],
        format='JPEG',
        options={'quality': 90},
        null=True,
        blank=True
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

