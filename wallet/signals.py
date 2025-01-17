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

@receiver(post_save, sender=RiderDelivery)
def create_wallet_transactions_for_riderdelivery(sender, instance, created, **kwargs):
    """
    When a RiderDelivery is marked delivered for the first time,
    create wallet transactions for:
      - The rider: receives 90% of the delivery price.
      - The commissioner: receives 3% (if assigned)
      - The boss: receives 7% if commissioner exists, or 10% otherwise.
    """
    # Only process if delivery has just been marked as delivered
    if instance.delivered and instance.delivered_at is not None:
        # Check whether we’ve already recorded transactions (you might mark your record with a flag)
        if hasattr(instance, 'wallet_transaction_created') and instance.wallet_transaction_created:
            return
        # Mark as processed (you might add a BooleanField on RiderDelivery to avoid duplicates)
        instance.wallet_transaction_created = True
        # Get the price (assuming delivery_request.delivery_price is a string field)
        price = get_amount_from_str(instance.delivery_request.delivery_price)
        if price <= 0:
            return  # Nothing to process

        # Calculate splits:
        rider_amount = price * RIDER_SHARE
        # Check if the rider has a commissioner assigned (through the Rider profile)
        rider_obj = instance.rider  # instance.rider is a Rider instance
        if rider_obj.commissioner:
            commissioner_amount = price * COMMISSIONER_SHARE
            boss_amount = price * BOSS_SHARE_WITH_COMMISSIONER
        else:
            commissioner_amount = Decimal('0.00')
            boss_amount = price * BOSS_SHARE_NO_COMMISSIONER

        # Create transaction for rider wallet
        if rider_obj.user and hasattr(rider_obj.user, 'wallet'):
            wallet = rider_obj.user.wallet
            wallet.credit(rider_amount)
            WalletTransaction.objects.create(
                wallet=wallet,
                amount=rider_amount,
                transaction_type='credit',
                description=f"Delivery Payment from DeliveryRequest {instance.delivery_request.id} via RiderDelivery {instance.id}",
                reference=str(instance.id)
            )