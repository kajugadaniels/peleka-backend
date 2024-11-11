from system.models import *
from rest_framework import serializers

class UserDeliveryRequestSerializer(serializers.ModelSerializer):
    client_name = serializers.ReadOnlyField(source='client.name', help_text='The name of the client who made the request')
    client_phone = serializers.ReadOnlyField(source='client.phone_number', help_text='The phone number of the client who made the request')
    delivery_price = serializers.DecimalField(max_digits=10, decimal_places=2, help_text='Automatically calculated price based on distance')

    class Meta:
        model = DeliveryRequest
        fields = [
            'id', 'client', 'client_name', 'client_phone', 'pickup_address', 'pickup_lat', 'pickup_lng',
            'delivery_address', 'delivery_lat', 'delivery_lng', 'package_name', 'package_description',
            'recipient_name', 'recipient_phone', 'estimated_distance_km', 'estimated_delivery_time', 
            'value_of_product', 'delivery_price', 'image', 'status', 'payment_type', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'client': {'write_only': True},
            'image': {'required': False, 'allow_null': True},
        }

    def create(self, validated_data):
        delivery_request = DeliveryRequest(**validated_data)
        delivery_request.save()
        return delivery_request

    def update(self, instance, validated_data):
        image = validated_data.pop('image', None)
        if image is not None:
            instance.image = image

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance