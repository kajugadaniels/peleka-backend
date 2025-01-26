from transactions.models import *
from rest_framework import serializers

class TransactionHistorySerializer(serializers.ModelSerializer):
    delivery_request = serializers.PrimaryKeyRelatedField(
        queryset=DeliveryRequest.objects.all(),
        required=False,
        allow_null=True
    )
    book_rider = serializers.PrimaryKeyRelatedField(
        queryset=BookRider.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = TransactionHistory
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    histories = TransactionHistorySerializer(many=True, read_only=True)
    
    class Meta:
        model = Transaction
        exclude = ['created_at', 'updated_at']
        fields = ['__all__']
