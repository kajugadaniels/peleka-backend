from system.models import *
from django.db import models
from django.conf import settings

class Transaction(models.Model):
    rider = models.OneToOneField(
        Rider, 
        on_delete=models.CASCADE, 
        related_name='wallet_transaction'
    )
    # These fields hold the cumulative total amounts earned/received.
    rider_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    commissioner_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    boss_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wallet for Rider: {self.rider}"

class TransactionHistory(models.Model):
    ROLE_CHOICES = (
        ('rider', 'Rider'),
        ('commissioner', 'Commissioner'),
        ('boss', 'Boss'),
    )
    transaction = models.ForeignKey(
        Transaction, 
        on_delete=models.CASCADE, 
        related_name='history'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"History [{self.role}]: {self.amount}"
