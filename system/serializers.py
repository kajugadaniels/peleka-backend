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
        """Override update method to handle image updates and price recalculation."""
        image = validated_data.pop('image', None)
        if image is not None:
            instance.image = image

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()  # This triggers the save method to update the price
        return instance