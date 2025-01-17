from decimal import Decimal
from django.db import models
from django.conf import settings

class Wallet(models.Model):
    WALLET_TYPES = (
        ('rider', 'Rider'),
        ('commissioner', 'Commissioner'),
        ('boss', 'Boss'),
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='wallets'
    )
    wallet_type = models.CharField(max_length=20, choices=WALLET_TYPES)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.owner} - {self.wallet_type} Wallet"

    def credit(self, amount, description=""):
        """Increase wallet balance and log a credit transaction."""
        self.balance += amount
        self.save()
        WalletTransaction.objects.create(
            wallet=self, 
            amount=amount, 
            transaction_type='credit', 
            description=description
        )

    def debit(self, amount, description=""):
        """Decrease wallet balance and log a debit transaction."""
        self.balance -= amount
        self.save()
        WalletTransaction.objects.create(
            wallet=self, 
            amount=amount, 
            transaction_type='debit', 
            description=description
        )