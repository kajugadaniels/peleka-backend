from decimal import Decimal
from django.db import models
from django.conf import settings

WALLET_TYPE_CHOICES = (
    ('rider', 'Rider'),
    ('commissioner', 'Commissioner'),
    ('boss', 'Boss'),
)

class Wallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet'
    )
    wallet_type = models.CharField(max_length=20, choices=WALLET_TYPE_CHOICES)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def credit(self, amount):
        """Credit the wallet by a given amount."""
        self.balance += amount
        self.save()

    def debit(self, amount):
        """Debit the wallet by a given amount."""
        self.balance -= amount
        self.save()

    def __str__(self):
        return f"{self.user} - {self.wallet_type.capitalize()} Wallet"

class WalletTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = (
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    )
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    description = models.TextField(blank=True)
    reference = models.CharField(max_length=255, blank=True, null=True, help_text="Reference ID (e.g., RiderDelivery or BookRiderAssignment pk)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.wallet.user} - {self.transaction_type} of {self.amount}"