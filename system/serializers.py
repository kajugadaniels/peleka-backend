import random
from rest_framework import serializers
from system.models import *

class RiderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Rider model.
    Includes auto-generated, read-only code based on name initials and a unique 8-digit number.
    """
    image = serializers.ImageField(required=False)
    code = serializers.CharField(read_only=True)  # Code is read-only

    class Meta:
        model = Rider
        fields = ['id', 'name', 'phone_number', 'address', 'code', 'nid', 'image']
        read_only_fields = ['code']

    def generate_unique_code(self, name):
        """
        Generates a unique code based on name initials and a random 8-digit number.
        Ensures uniqueness by checking against existing codes in the Rider model.
        """
        # Extract initials (first letters of each name)
        initials = ''.join([part[0].upper() for part in name.split() if part])[:2]  # Only the first 2 initials

        # Generate a unique code by appending an 8-digit random number
        while True:
            random_number = ''.join([str(random.randint(0, 9)) for _ in range(8)])
            code = f"{initials}{random_number}"

            # Check if the generated code is unique
            if not Rider.objects.filter(code=code).exists():
                return code

    def create(self, validated_data):
        """
        Overrides create method to generate and set a unique code for each Rider.
        """
        # Extract name from validated data to generate the code
        name = validated_data.get('name', '')
        validated_data['code'] = self.generate_unique_code(name)

        # Create and return the Rider instance
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Handle image upload separately if provided
        if 'image' in validated_data:
            instance.image = validated_data.pop('image')

        # Update the other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

class DeliveryRequestSerializer(serializers.ModelSerializer):
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

class RiderDeliverySerializer(serializers.ModelSerializer):
    # Rider information fields
    rider_id = serializers.ReadOnlyField(source='rider.id', help_text='The id of the rider')
    rider_name = serializers.ReadOnlyField(source='rider.name', help_text='The name of the rider')
    rider_phone_number = serializers.ReadOnlyField(source='rider.phone_number', help_text='The phone number of the rider')
    rider_address = serializers.ReadOnlyField(source='rider.address', help_text='The address of the rider')
    rider_code = serializers.ReadOnlyField(source='rider.code', help_text='The unique code of the rider')
    rider_nid = serializers.ReadOnlyField(source='rider.nid', help_text='The national ID of the rider')
    rider_image = serializers.ImageField(source='rider.image', help_text='The image of the rider', read_only=True)

    # Delivery request details
    delivery_request_id = serializers.ReadOnlyField(source='delivery_request.id', help_text='The ID of the delivery request')
    pickup_address = serializers.ReadOnlyField(source='delivery_request.pickup_address', help_text='The pickup address of the delivery request')
    delivery_address = serializers.ReadOnlyField(source='delivery_request.delivery_address', help_text='The delivery address of the delivery request')
    package_description = serializers.ReadOnlyField(source='delivery_request.package_description', help_text='Description of the package')
    estimated_distance_km = serializers.ReadOnlyField(source='delivery_request.estimated_distance_km', help_text='The estimated distance in kilometers')
    estimated_delivery_time = serializers.ReadOnlyField(source='delivery_request.estimated_delivery_time', help_text='The estimated delivery time')
    value_of_product = serializers.ReadOnlyField(source='delivery_request.value_of_product', help_text='The value of the product being delivered')
    delivery_price = serializers.ReadOnlyField(source='delivery_request.delivery_price', help_text='The delivery price calculated')
    status = serializers.ReadOnlyField(source='delivery_request.status', help_text='The status of the delivery request')

    # Client information
    client_name = serializers.ReadOnlyField(source='delivery_request.client.name', help_text='The name of the client')
    client_phone = serializers.ReadOnlyField(source='delivery_request.client.phone_number', help_text='The email of the client')
    client_phone_number = serializers.ReadOnlyField(source='delivery_request.client.phone_number', help_text='The phone number of the client')
    created_at = serializers.ReadOnlyField(source='delivery_request.created_at', help_text='The creation date of the delivery request')
    updated_at = serializers.ReadOnlyField(source='delivery_request.updated_at', help_text='The last update date of the delivery request')

    class Meta:
        model = RiderDelivery
        fields = [
            'id', 'rider_id', 'rider_name', 'rider_phone_number', 'rider_address', 'rider_code',
            'rider_nid', 'rider_image', 'current_status', 'last_assigned_at',
            'delivery_request_id', 'pickup_address', 'delivery_address',
            'package_description', 'estimated_distance_km', 'estimated_delivery_time',
            'value_of_product', 'delivery_price', 'status', 'client_name',
            'client_phone', 'client_phone_number', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'rider_id', 'rider_name', 'rider_phone_number', 'rider_address',
            'rider_code', 'rider_nid', 'rider_image', 'last_assigned_at',
            'delivery_request_id', 'pickup_address', 'delivery_address',
            'package_description', 'estimated_distance_km', 'estimated_delivery_time',
            'value_of_product', 'delivery_price', 'status', 'client_name',
            'client_phone', 'client_phone_number', 'created_at', 'updated_at'
        ]

    def validate(self, data):
        """Ensure that a rider can be assigned only if they are available."""
        rider = data.get('rider')
        if rider and RiderDelivery.objects.filter(rider=rider).exclude(current_status='Available').exists():
            raise serializers.ValidationError("Rider is currently unavailable for a new delivery assignment.")
        return data

    def create(self, validated_data):
        """Create a new RiderDelivery instance."""
        rider = validated_data.get('rider')
        delivery_request = validated_data.get('delivery_request')

        # Set the initial status to 'In Progress'
        validated_data['current_status'] = 'In Progress'
        validated_data['assigned_at'] = timezone.now()
        validated_data['in_progress_at'] = timezone.now()

        # Update the delivery request status
        if delivery_request:
            delivery_request.status = 'In Progress'
            delivery_request.save()

        return super().create(validated_data)