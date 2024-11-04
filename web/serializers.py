from system.models import *
from rest_framework import serializers

class UserDeliveryRequestSerializer(serializers.ModelSerializer):
    delivery_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = DeliveryRequest
        fields = [
            'pickup_address', 'delivery_address', 'package_description', 
            'estimated_distance_km', 'estimated_delivery_time', 
            'value_of_product', 'delivery_price', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['delivery_price', 'status', 'created_at', 'updated_at']

    def validate_estimated_distance_km(self, value):
        """Ensure that the estimated distance is positive."""
        if value <= 0:
            raise serializers.ValidationError("Estimated distance must be greater than zero.")
        return value
