from django.db import models

class Rider(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    address = models.CharField(max_length=20, null=True, blank=True)
    code = models.CharField(max_length=20, unique=True, null=True, blank=True)
    nid = models.CharField(max_length=20, unique=True, null=True, blank=True)

    def __str__(self):
        return self.name