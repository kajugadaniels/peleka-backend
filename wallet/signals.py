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

        # Create transaction for commissioner wallet, if exists
        if rider_obj.commissioner:
            if hasattr(rider_obj.commissioner, 'wallet'):
                wallet = rider_obj.commissioner.wallet
                wallet.credit(commissioner_amount)
                WalletTransaction.objects.create(
                    wallet=wallet,
                    amount=commissioner_amount,
                    transaction_type='credit',
                    description=f"Commission from RiderDelivery {instance.id} (DeliveryRequest {instance.delivery_request.id})",
                    reference=str(instance.id)
                )

        # Create transaction for boss wallet (assume there is exactly one boss user with a wallet)
        # For simplicity, we retrieve the boss wallet by filtering on wallet_type
        try:
            wallet = Wallet.objects.get(wallet_type='boss')
            wallet.credit(boss_amount)
            WalletTransaction.objects.create(
                wallet=wallet,
                amount=boss_amount,
                transaction_type='credit',
                description=f"Boss share from RiderDelivery {instance.id} (DeliveryRequest {instance.delivery_request.id})",
                reference=str(instance.id)
            )
        except Wallet.DoesNotExist:
            pass

@receiver(post_save, sender=BookRiderAssignment)
def create_wallet_transactions_for_bookriderassignment(sender, instance, created, **kwargs):
    """
    When a BookRiderAssignment is marked as Completed,
    create wallet transactions similarly using the booking_price from BookRider.
    """
    # Process only when status is completed and not previously processed.
    if instance.status == 'Completed':
        if hasattr(instance, 'wallet_transaction_created') and instance.wallet_transaction_created:
            return
        instance.wallet_transaction_created = True

        # Get price from related BookRider (booking_price)
        booking_price = get_amount_from_str(instance.book_rider.booking_price)
        if booking_price <= 0:
            return

        # Calculate splits:
        rider_amount = booking_price * RIDER_SHARE
        rider_obj = instance.rider  # instance.rider is a Rider instance
        if rider_obj.commissioner:
            commissioner_amount = booking_price * COMMISSIONER_SHARE
            boss_amount = booking_price * BOSS_SHARE_WITH_COMMISSIONER
        else:
            commissioner_amount = Decimal('0.00')
            boss_amount = booking_price * BOSS_SHARE_NO_COMMISSIONER

        # Create transaction for rider wallet
        if rider_obj.user and hasattr(rider_obj.user, 'wallet'):
            wallet = rider_obj.user.wallet
            wallet.credit(rider_amount)
            WalletTransaction.objects.create(
                wallet=wallet,
                amount=rider_amount,
                transaction_type='credit',
                description=f"Booking Payment from BookRider {instance.book_rider.id} via Assignment {instance.id}",
                reference=str(instance.id)
            )

        # Create transaction for commissioner wallet, if exists
        if rider_obj.commissioner:
            if hasattr(rider_obj.commissioner, 'wallet'):
                wallet = rider_obj.commissioner.wallet
                wallet.credit(commissioner_amount)
                WalletTransaction.objects.create(
                    wallet=wallet,
                    amount=commissioner_amount,
                    transaction_type='credit',
                    description=f"Commission from BookRiderAssignment {instance.id} (BookRider {instance.book_rider.id})",
                    reference=str(instance.id)
                )

        # Create transaction for boss wallet
        try:
            wallet = Wallet.objects.get(wallet_type='boss')
            wallet.credit(boss_amount)
            WalletTransaction.objects.create(
                wallet=wallet,
                amount=boss_amount,
                transaction_type='credit',
                description=f"Boss share from BookRiderAssignment {instance.id} (BookRider {instance.book_rider.id})",
                reference=str(instance.id)
            )