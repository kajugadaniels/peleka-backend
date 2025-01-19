from system.models import *
from django.db import models
from django.conf import settings

class Transaction(models.Model):
    rider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rider_transactions'
    )
    commissioner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='commissioner_transactions',
        null=True,
        blank=True
    )
    boss = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='boss_transactions'
    )
    rider_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    commissioner_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    boss_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transaction for Rider: {self.rider}"

class TransactionHistory(models.Model):
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name='histories'
    )
    delivery_request = models.ForeignKey(DeliveryRequest, on_delete=models.CASCADE)
    rider_amount = models.DecimalField(max_digits=10, decimal_places=2)
    commissioner_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    boss_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"History for Transaction {self.transaction.id} (DeliveryRequest {self.delivery_request.id})"
