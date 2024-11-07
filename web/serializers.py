from system.models import *
from rest_framework import serializers

class UserDeliveryRequestSerializer(serializers.ModelSerializer):
    delivery_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    client_name = serializers.ReadOnlyField(source='client.name', help_text='The name of the client who made the request')

    class Meta:
        model = DeliveryRequest
        fields = [
            'id', 'client_name', 'pickup_address', 'delivery_address', 
            'package_name', 'package_description', 'recipient_name', 'recipient_phone',
            'estimated_distance_km', 'estimated_delivery_time', 
            'value_of_product', 'delivery_price', 'status', 'payment_type', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'client_name', 'delivery_price', 'status', 'created_at', 'updated_at']

    def validate_estimated_distance_km(self, value):
        """Ensure that the estimated distance is positive."""
        if value <= 0:
            raise serializers.ValidationError("Estimated distance must be greater than zero.")
        return value