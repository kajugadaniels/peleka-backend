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
    client_email = serializers.ReadOnlyField(source='client.email', help_text='The email of the client who made the request')
    delivery_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True, help_text='Automatically calculated price based on distance')

    class Meta:
        model = DeliveryRequest
        fields = [
            'id', 'client', 'client_name', 'client_email', 'pickup_address', 'delivery_address',
            'package_description', 'estimated_distance_km', 'estimated_delivery_time',
            'value_of_product', 'delivery_price', 'image', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'delivery_price']
        extra_kwargs = {
            'client': {'write_only': True},
            'image': {'required': False, 'allow_null': True},
            'estimated_delivery_time': {'required': True}  # Ensure this field is mandatory
        }

    def validate_estimated_distance_km(self, value):
        """Ensure that the estimated distance is positive."""
        if value <= 0:
            raise serializers.ValidationError("Estimated distance must be greater than zero.")
        return value

    def create(self, validated_data):
        """Override create method to ensure price calculation on creation."""
        delivery_request = DeliveryRequest(**validated_data)
        delivery_request.save()  # This triggers the save method in the model to calculate price
        return delivery_request

    def update(self, instance, validated_data):
        """Override update method to handle image updates and other changes."""
        image = validated_data.pop('image', None)
        if image is not None:
            instance.image = image

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()  # Trigger the save method in the model to recalculate price if necessary
        return instance

class RiderDeliverySerializer(serializers.ModelSerializer):
    rider_name = serializers.ReadOnlyField(source='rider.name', help_text='The name of the rider')
    rider_phone = serializers.ReadOnlyField(source='rider.phone_number', help_text='The phone number of the rider')
    delivery_request_info = serializers.SerializerMethodField(help_text='Detailed information about the assigned delivery request, including client details')

    class Meta:
        model = RiderDelivery
        fields = [
            'id', 'rider', 'rider_name', 'rider_phone', 'current_status', 'last_assigned_at',
            'delivery_request', 'delivery_request_info'
        ]
        read_only_fields = ['id', 'rider_name', 'rider_phone', 'last_assigned_at', 'delivery_request_info']
        extra_kwargs = {
            'rider': {'write_only': True},
            'delivery_request': {'required': False, 'allow_null': True},
        }

    def get_delivery_request_info(self, obj):
        """Return comprehensive details about the assigned delivery request, including client information."""
        if obj.delivery_request:
            delivery_request = obj.delivery_request
            return {
                "id": delivery_request.id,
                "pickup_address": delivery_request.pickup_address,
                "delivery_address": delivery_request.delivery_address,
                "package_description": delivery_request.package_description,
                "estimated_distance_km": delivery_request.estimated_distance_km,
                "estimated_delivery_time": delivery_request.estimated_delivery_time,
                "value_of_product": delivery_request.value_of_product,
                "delivery_price": delivery_request.delivery_price,
                "status": delivery_request.status,
                "client_info": {
                    "name": delivery_request.client.name,
                    "email": delivery_request.client.email,
                    "phone_number": delivery_request.client.phone_number,
                },
                "created_at": delivery_request.created_at,
                "updated_at": delivery_request.updated_at
            }
        return None

    def validate(self, data):
        """Ensure that a rider cannot be assigned to a delivery if not available."""
        if data.get('current_status') not in ['Available', 'Assigned']:
            raise serializers.ValidationError("Rider must be either 'Available' or 'Assigned' to manage deliveries.")
        return data

    def update(self, instance, validated_data):
        """Handle the update logic to change the rider's status and delivery assignment."""
        delivery_request = validated_data.get('delivery_request')
        if delivery_request:
            if not instance.is_available():
                raise serializers.ValidationError("Rider is not available for a new delivery assignment.")
            instance.assign_delivery(delivery_request)

        current_status = validated_data.get('current_status')
        if current_status == 'In Progress':
            instance.mark_as_in_progress()
        elif current_status == 'Available':
            instance.mark_as_available()

        return super().update(instance, validated_data)