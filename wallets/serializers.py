from wallets.models import *
from rest_framework import serializers

class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = ['id', 'owner', 'wallet_type', 'balance', 'created_at']

class WalletSerializer(serializers.ModelSerializer):
    transactions = WalletTransactionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Wallet
        fields = ['id', 'owner', 'wallet_type', 'balance', 'transactions', 'created_at', 'updated_at']
