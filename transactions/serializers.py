from rest_framework import serializers
from .models import Transaction, TransactionHistory

class TransactionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionHistory
        exclude = ['created_at']
        fields = ['__all__']

class TransactionSerializer(serializers.ModelSerializer):
    histories = TransactionHistorySerializer(many=True, read_only=True)
    
    class Meta:
        model = Transaction
        exclude = ['created_at', 'updated_at']
        fields = ['__all__']
