import random
from system.models import *
from rest_framework import serializers
from django.contrib.auth import get_user_model

class DeliveryRequestSerializer(serializers.ModelSerializer):
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
            'value_of_product', 'delivery_price', 'image', 'status', 'rider_name', 'rider_phone_number', 'rider_address', 
            'rider_code', 'rider_nid', 'rider_image', 'payment_type', 'created_at', 'updated_at'
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
        # validated_data['in_progress_at'] = timezone.now()

        # Update the delivery request status
        delivery_request = validated_data.get('delivery_request')
        if delivery_request:
            delivery_request.status = 'Accepted'
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
    Automatically generates a unique code based on name initials and a unique 8-digit number.
    Also automatically creates a corresponding User record using the provided name, email, and phone_number.
    """
    # Include the images, making them optional.
    image = serializers.ImageField(required=False)
    permit_image = serializers.ImageField(required=False)
    code = serializers.CharField(read_only=True)  # Code is auto-generated and read-only.

    # For output, include delivery history if needed.
    delivery_history = RiderDeliverySerializer(
        source='rider_delivery', many=True, read_only=True,
        help_text='The delivery history of the rider'
    )
    
    # Add a write-only email field (since the Rider model does not have an email field).
    email = serializers.EmailField(write_only=True, required=True)

    class Meta:
        model = Rider
        fields = [
            'id', 'name', 'email', 'phone_number', 'address', 'code', 'nid',
            'image', 'permit_image', 'plate_number', 'insurance', 'delivery_history'
        ]
        read_only_fields = ['code', 'delivery_history']

    def generate_unique_code(self, name):
        """
        Generates a unique code based on the first two initials of the name and a random 8-digit number.
        Ensures uniqueness by checking against existing codes in the Rider model.
        """
        # Extract the first two initials from the provided name
        initials = ''.join([part[0].upper() for part in name.split() if part])[:2]
        # Attempt generating a unique code in a loop
        while True:
            random_number = ''.join([str(random.randint(0, 9)) for _ in range(8)])
            code = f"{initials}{random_number}"
            if not Rider.objects.filter(code=code).exists():
                return code

    def create(self, validated_data):
        """
        Overrides the default create behavior:
          - Extracts the required fields for the User model.
          - Creates a corresponding User record with default password "Password!7".
          - Associates the created user with the new Rider.
          - Generates a unique code for the Rider.
        """
        # Extract required fields for creating the User record.
        name = validated_data.get('name', '')
        phone_number = validated_data.get('phone_number', '')
        email = validated_data.pop('email')  # Remove email from validated_data as Rider model doesn't use it.

        # Generate the unique rider code.
        validated_data['code'] = self.generate_unique_code(name)

        # Create the corresponding user record.
        User = get_user_model()
        try:
            user = User.objects.create_user(
                name=name,
                email=email,
                phone_number=phone_number,
                password="Password!7"
            )
        except Exception as e:
            # You might want to log the error and raise a more specific exception.
            raise serializers.ValidationError({"user_creation": "Could not create associated user account.", "detail": str(e)})

        # Link the created user to the Rider.
        validated_data['user'] = user

        # Create and return the Rider instance.
        rider = super().create(validated_data)
        return rider

    def update(self, instance, validated_data):
        """
        Update instance while handling image uploads if provided.
        """
        if 'image' in validated_data:
            instance.image = validated_data.pop('image')

        # Update the remaining fields.
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def to_representation(self, instance):
        """
        Optionally include delivery_history only for single retrieve operations.
        """
        representation = super().to_representation(instance)
        request = self.context.get('request')
        view = self.context.get('view')
        if request and view and 'pk' in view.kwargs:
            representation['delivery_history'] = RiderDeliverySerializer(instance.rider_delivery.all(), many=True).data
        else:
            representation.pop('delivery_history', None)
        return representation

class DeliveryRequestCompleteSerializer(serializers.ModelSerializer):
    """
    Serializer for marking a DeliveryRequest as Completed.
    Only allows the status to be set to 'Completed'.
    """

    class Meta:
        model = DeliveryRequest
        fields = ['status']
        read_only_fields = ['status']

    def validate(self, attrs):
        if attrs.get('status') != 'Completed':
            raise serializers.ValidationError("Status can only be updated to 'Completed'.")
        return attrs

class BookRiderSerializer(serializers.ModelSerializer):
    """
    Serializer for the BookRider model.
    Includes client information and ensures that delete_status is read-only.
    """
    client_name = serializers.ReadOnlyField(source='client.name', help_text='The name of the client who booked the rider')
    client_phone = serializers.ReadOnlyField(source='client.phone_number', help_text='The phone number of the client who booked the rider')

    class Meta:
        model = BookRider
        fields = [
            'id', 'client', 'client_name', 'client_phone', 'pickup_address', 'pickup_lat', 'pickup_lng',
            'delivery_address', 'delivery_lat', 'delivery_lng', 'estimated_distance_km', 
            'estimated_delivery_time', 'booking_price', 'payment_type', 'status', 
            'delete_status', 'deleted_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'delete_status', 'deleted_by', 'created_at', 'updated_at', 'client_name', 'client_phone']
        extra_kwargs = {
            'client': {'write_only': True},
            'booking_price': {'required': False, 'allow_null': True},
            'payment_type': {'required': False, 'allow_null': True},
        }

    def create(self, validated_data):
        """
        Create a new BookRider instance.
        Automatically sets the client to the requesting user.
        """
        book_rider = BookRider(**validated_data)
        book_rider.save()
        return book_rider

    def update(self, instance, validated_data):
        """
        Update an existing BookRider instance.
        Prevents modification of read-only fields.
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class BookRiderAssignmentSerializer(serializers.ModelSerializer):
    """
    Serializer for the BookRiderAssignment model.
    Includes client information and rider information as read-only fields.
    """
    client_name = serializers.ReadOnlyField(source='book_rider.client.name', help_text='Name of the client who made the booking')
    client_phone = serializers.ReadOnlyField(source='book_rider.client.phone_number', help_text='Phone number of the client who made the booking')
    rider_name = serializers.ReadOnlyField(source='rider.name', help_text='Name of the assigned rider')
    rider_phone_number = serializers.ReadOnlyField(source='rider.phone_number', help_text='Phone number of the assigned rider')
    
    class Meta:
        model = BookRiderAssignment
        fields = [
            'id', 'book_rider', 'client_name', 'client_phone', 'rider', 'rider_name', 'rider_phone_number',
            'assigned_at', 'in_progress_at', 'completed_at', 'cancelled_at', 'status',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'client_name', 'client_phone', 'rider_name', 'rider_phone_number',
            'assigned_at', 'in_progress_at', 'completed_at', 'cancelled_at',
            'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'book_rider': {'write_only': True},
            'rider': {'write_only': True},
            'status': {'required': False},
        }

    def create(self, validated_data):
        """
        Assign a rider to a BookRider request.
        Automatically sets the assigned_at timestamp and updates the BookRider status to 'Confirmed'.
        """
        rider = validated_data.get('rider')
        book_rider = validated_data.get('book_rider')
        
        # Check if the rider is available (no active assignments)
        if BookRiderAssignment.objects.filter(rider=rider, status__in=['Pending', 'Confirmed', 'In Progress']).exists():
            raise serializers.ValidationError("This rider is currently unavailable for a new assignment.")
        
        # Create the assignment
        assignment = BookRiderAssignment.objects.create(
            book_rider=book_rider,
            rider=rider,
            assigned_at=timezone.now(),
            status='Confirmed'
        )
        
        # Update the BookRider status
        book_rider.status = 'Confirmed'
        book_rider.save()
        
        return assignment

    def update(self, instance, validated_data):
        """
        Update an existing BookRiderAssignment instance.
        Handles status transitions and timestamp updates.
        """
        status = validated_data.get('status', instance.status)
        
        # Allow only 'rider' to be updated
        if 'rider' in validated_data:
            new_rider = validated_data.pop('rider')
            # Check if the new rider is available
            if BookRiderAssignment.objects.filter(rider=new_rider, status__in=['Pending', 'Confirmed', 'In Progress']).exists():
                raise serializers.ValidationError("The new rider is currently unavailable for assignment.")
            instance.rider = new_rider
            instance.assigned_at = timezone.now()
        
        if status != instance.status:
            if status == 'In Progress':
                instance.in_progress_at = timezone.now()
            elif status == 'Completed':
                instance.completed_at = timezone.now()
                # Update the BookRider status
                instance.book_rider.status = 'Completed'
                instance.book_rider.save()
            elif status == 'Cancelled':
                instance.cancelled_at = timezone.now()
                # Update the BookRider status
                instance.book_rider.status = 'Cancelled'
                instance.book_rider.save()
        
        instance.status = status
        instance.save()
        return instance

class BookRiderAssignmentCompleteSerializer(serializers.ModelSerializer):
    """
    Serializer for marking a BookRiderAssignment as Completed.
    Only allows the status to be set to 'Completed' and prevents completion if cancelled.
    """
    
    class Meta:
        model = BookRiderAssignment
        fields = ['status']
    
    def validate(self, attrs):
        if attrs.get('status') != 'Completed':
            raise serializers.ValidationError("Status can only be updated to 'Completed'.")
        # Check if the current status is 'Cancelled'
        if self.instance.status == 'Cancelled':
            raise serializers.ValidationError("Cannot complete a cancelled booking.")
        # Ensure current status is 'In Progress'
        if self.instance.status != 'In Progress':
            raise serializers.ValidationError("Only assignments with status 'In Progress' can be marked as 'Completed'.")
        return attrs

    def update(self, instance, validated_data):
        """
        Update the status of the BookRiderAssignment to 'Completed' and set the completed_at timestamp.
        """
        instance.status = 'Completed'
        instance.completed_at = timezone.now()
        instance.save()

        # Update the related BookRider status
        book_rider = instance.book_rider
        book_rider.status = 'Completed'
        book_rider.save()

        return instance