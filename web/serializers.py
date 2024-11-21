from system.models import *
from rest_framework import serializers
from rest_framework.authtoken.models import Token

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

class UserSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.name', read_only=True)
    image = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = (
            'id', 'name', 'email', 'phone_number', 'role', 'role_name', 'image', 'password'
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        """
        Create a new user with a fixed role ID and hashed password.
        """
        validated_data['role_id'] = 1  # Ensuring the role ID is always 1
        password = validated_data.pop('password', None)
        user = User.objects.create_user(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

class RiderLoginSerializer(serializers.Serializer):
    code = serializers.CharField(write_only=True, required=True, help_text='The unique code of the rider')

    def validate_code(self, value):
        try:
            rider = Rider.objects.get(code=value)
        except Rider.DoesNotExist:
            raise serializers.ValidationError("Invalid code. Please check and try again.")
        
        # Removed the is_active check
        self.context['rider'] = rider
        return value

    def create(self, validated_data):
        rider = self.context['rider']
        token, created = Token.objects.get_or_create(user=rider)
        return token

class UserDeliveryRequestSerializer(serializers.ModelSerializer):
    client_name = serializers.ReadOnlyField(source='client.name', help_text='The name of the client who made the request')
    client_phone = serializers.ReadOnlyField(source='client.phone_number', help_text='The phone number of the client who made the request')
    delivery_price = serializers.DecimalField(max_digits=10, decimal_places=2, help_text='Automatically calculated price based on distance')
    rider_name = serializers.SerializerMethodField()
    rider_phone_number = serializers.SerializerMethodField()
    rider_address = serializers.SerializerMethodField()
    rider_code = serializers.SerializerMethodField()
    rider_nid = serializers.SerializerMethodField()
    rider_image = serializers.SerializerMethodField()

    class Meta:
        model = DeliveryRequest
        fields = [
            'id', 'client', 'client_name', 'client_phone', 'pickup_address', 'pickup_lat', 'pickup_lng',
            'delivery_address', 'delivery_lat', 'delivery_lng', 'package_name', 'package_description',
            'recipient_name', 'recipient_phone', 'estimated_distance_km', 'estimated_delivery_time', 
            'value_of_product', 'delivery_price', 'image', 'status', 'payment_type', 
            'created_at', 'updated_at', 'rider_name', 'rider_phone_number', 'rider_address', 
            'rider_code', 'rider_nid', 'rider_image'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'client': {'write_only': True},
            'image': {'required': False, 'allow_null': True},
        }

    def get_rider_info(self, obj, attribute):
        rider_delivery = obj.rider_assignment.first()
        if rider_delivery and rider_delivery.rider:
            rider = rider_delivery.rider
            return getattr(rider, attribute, None)
        return None

    def get_rider_image(self, obj):
        image = self.get_rider_info(obj, 'image')
        if image:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(image.url)
        return None

    def get_rider_name(self, obj):
        return self.get_rider_info(obj, 'name')

    def get_rider_phone_number(self, obj):
        return self.get_rider_info(obj, 'phone_number')

    def get_rider_address(self, obj):
        return self.get_rider_info(obj, 'address')

    def get_rider_code(self, obj):
        return self.get_rider_info(obj, 'code')

    def get_rider_nid(self, obj):
        return self.get_rider_info(obj, 'nid')

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
    rider_id = serializers.ReadOnlyField(source='rider.id', help_text='The ID of the rider')
    rider_name = serializers.ReadOnlyField(source='rider.name', help_text='The name of the rider')
    rider_phone_number = serializers.ReadOnlyField(source='rider.phone_number', help_text='The phone number of the rider')
    rider_address = serializers.ReadOnlyField(source='rider.address', help_text='The address of the rider')
    rider_code = serializers.ReadOnlyField(source='rider.code', help_text='The unique code of the rider')
    rider_nid = serializers.ReadOnlyField(source='rider.nid', help_text='The national ID of the rider')
    rider_image = serializers.ImageField(source='rider.image', help_text='The image of the rider', read_only=True)

    # Delivery request details
    package_name = serializers.ReadOnlyField(source='delivery_request.package_name', help_text='Name of the package')
    delivery_request_id = serializers.ReadOnlyField(source='delivery_request.id', help_text='The ID of the delivery request')
    pickup_address = serializers.ReadOnlyField(source='delivery_request.pickup_address', help_text='The pickup address of the delivery request')
    pickup_lat = serializers.ReadOnlyField(source='delivery_request.pickup_lat', help_text='The pickup address of the delivery request')
    pickup_lng = serializers.ReadOnlyField(source='delivery_request.pickup_lng', help_text='The pickup address of the delivery request')
    delivery_address = serializers.ReadOnlyField(source='delivery_request.delivery_address', help_text='The delivery address of the delivery request')
    delivery_lat = serializers.ReadOnlyField(source='delivery_request.delivery_lat', help_text='The delivery address of the delivery request')
    delivery_lng = serializers.ReadOnlyField(source='delivery_request.delivery_lng', help_text='The delivery address of the delivery request')
    package_description = serializers.ReadOnlyField(source='delivery_request.package_description', help_text='Description of the package')
    estimated_distance_km = serializers.ReadOnlyField(source='delivery_request.estimated_distance_km', help_text='The estimated distance in kilometers')
    estimated_delivery_time = serializers.ReadOnlyField(source='delivery_request.estimated_delivery_time', help_text='The estimated delivery time')
    value_of_product = serializers.ReadOnlyField(source='delivery_request.value_of_product', help_text='The value of the product being delivered')
    delivery_price = serializers.ReadOnlyField(source='delivery_request.delivery_price', help_text='The delivery price calculated')
    status = serializers.ReadOnlyField(source='delivery_request.status', help_text='The status of the delivery request')

    # Client information
    client_name = serializers.ReadOnlyField(source='delivery_request.client.name', help_text='The name of the client')
    client_phone_number = serializers.ReadOnlyField(source='delivery_request.client.phone_number', help_text='The phone number of the client')

    # Recipient information
    recipient_name = serializers.ReadOnlyField(source='delivery_request.recipient_name', help_text='The name of the client')
    recipient_phone = serializers.ReadOnlyField(source='delivery_request.recipient_phone', help_text='The phone number of the client')

    created_at = serializers.ReadOnlyField(source='delivery_request.created_at', help_text='The creation date of the delivery request')
    updated_at = serializers.ReadOnlyField(source='delivery_request.updated_at', help_text='The last update date of the delivery request')

    class Meta:
        model = RiderDelivery
        fields = [
            'id', 'rider_id', 'rider_name', 'rider_phone_number', 'rider_address', 'rider_code',
            'rider_nid', 'rider_image', 'delivered', 'last_assigned_at', 'package_name',
            'delivery_request_id', 'pickup_address', 'pickup_lat', 'pickup_lng', 'delivery_address', 'delivery_lat', 'delivery_lng',
            'package_description', 'estimated_distance_km', 'estimated_delivery_time',
            'value_of_product', 'delivery_price', 'status', 'client_name',
            'client_phone_number', 'recipient_name', 'recipient_phone', 'assigned_at', 'in_progress_at', 'delivered_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'rider_id', 'rider_name', 'rider_phone_number', 'rider_address',
            'rider_code', 'rider_nid', 'rider_image', 'last_assigned_at', 'package_name',
            'delivery_request_id', 'pickup_address', 'pickup_lat', 'pickup_lng', 'delivery_address', 'delivery_lat', 'delivery_lng',
            'package_description', 'estimated_distance_km', 'estimated_delivery_time',
            'value_of_product', 'delivery_price', 'status', 'client_name',
            'client_phone_number', 'recipient_name', 'recipient_phone', 'assigned_at', 'in_progress_at',
            'delivered_at', 'created_at', 'updated_at'
        ]

    def validate(self, data):
        """Ensure that a rider can be assigned only if they are available."""
        rider = self.initial_data.get('rider')
        if rider and RiderDelivery.objects.filter(rider=rider).exclude(delivered=True).exists():
            raise serializers.ValidationError("Rider is currently unavailable for a new delivery assignment.")
        return data

    def create(self, validated_data):
        """Create a new RiderDelivery instance with assigned_at and in_progress_at set to current time."""
        validated_data['delivered'] = False
        validated_data['assigned_at'] = timezone.now()
        validated_data['in_progress_at'] = timezone.now()

        # Update the delivery request status
        delivery_request = validated_data.get('delivery_request')
        if delivery_request:
            delivery_request.status = 'In Progress'
            delivery_request.save()

        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Handle the update logic to change the rider's delivery assignment."""
        # Update delivered status
        delivered = validated_data.get('delivered')
        if delivered is not None:
            instance.delivered = delivered
            if delivered:
                instance.delivered_at = timezone.now()
                # Optionally, update the delivery_request status
                if instance.delivery_request:
                    instance.delivery_request.status = 'Completed'
                    instance.delivery_request.save()

        instance.save()
        return instance

class RiderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Rider model.
    Includes auto-generated, read-only code based on name initials and a unique 8-digit number.
    Also includes delivery history with detailed information.
    """
    image = serializers.ImageField(required=False)
    permit_image = serializers.ImageField(required=False)
    code = serializers.CharField(read_only=True)  # Code is read-only
    delivery_history = RiderDeliverySerializer(source='rider_delivery', many=True, read_only=True, help_text='The delivery history of the rider')

    class Meta:
        model = Rider
        fields = ['id', 'name', 'phone_number', 'address', 'code', 'nid', 'image', 'permit_image', 'plate_number', 'insurance', 'delivery_history']
        read_only_fields = ['code', 'delivery_history']

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

    def to_representation(self, instance):
        """
        Override to_representation to include delivery_history only when retrieving a single Rider.
        """
        representation = super().to_representation(instance)
        request = self.context.get('request')
        if request and request.method == 'GET' and 'pk' in self.context.get('view').kwargs:
            # Include delivery_history only for retrieve operations
            representation['delivery_history'] = RiderDeliverySerializer(instance.rider_delivery.all(), many=True).data
        else:
            # Optionally, omit or include minimal delivery_history for list operations
            representation.pop('delivery_history', None)
        return representation