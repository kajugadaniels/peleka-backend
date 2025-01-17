from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
from system.models import RiderDelivery, BookRiderAssignment
from wallet.models import Wallet, WalletTransaction

# Define the percentages as Decimal values
RIDER_SHARE = Decimal('0.90')
COMMISSIONER_SHARE = Decimal('0.03')
BOSS_SHARE_WITH_COMMISSIONER = Decimal('0.07')
BOSS_SHARE_NO_COMMISSIONER = Decimal('0.10')

def get_amount_from_str(amount_str):
    """
    Helper function to convert amount from string field to Decimal.
    Assumes the amount is stored in a format compatible with Decimal.
    """
    try:
        return Decimal(amount_str)
    except Exception:
        return Decimal('0.00')