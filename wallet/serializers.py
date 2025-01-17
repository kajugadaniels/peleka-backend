from wallet.models import *
from rest_framework import serializers

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'user', 'wallet_type', 'balance', 'created_at', 'updated_at']

