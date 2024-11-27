import re
from account.models import *
from django.db.models import Q
from datetime import timedelta
from rest_framework import serializers
from django.contrib.auth.models import Permission
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

class PermissionSerializer(serializers.ModelSerializer):
    permission_string = serializers.SerializerMethodField()

    class Meta:
        model = Permission
        fields = ('permission_string',)

    def get_permission_string(self, obj):
        """
        Return permission in 'app_label.codename' format.
        """
        app_label = obj.content_type.app_label
        codename = obj.codename
        return f"{app_label}.{codename}"

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ('id', 'name')

class UserSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.name', read_only=True)
    user_permissions = serializers.SerializerMethodField()
    image = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = (
            'id', 'name', 'email', 'phone_number', 'role', 'role_name', 'image', 'password', 'user_permissions'
        )
        extra_kwargs = {
            'password': {'write_only': True}  # Password should be write-only for security
        }

    def get_user_permissions(self, obj):
        """Retrieve the user's direct permissions."""
        return obj.get_all_permissions()

    def create(self, validated_data):
        """
        Create a new user with a hashed password.
        """
        password = validated_data.pop('password', None)
        user = User.objects.create_user(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        """
        Update user details and hash the password if provided.
        """
        # Handle image upload separately if provided
        if 'image' in validated_data:
            instance.image = validated_data.pop('image')

        # If a password is provided, hash it using set_password
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)  # Hash and set the new password

        # Update the remaining fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

class PasswordResetRequestSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField()

    def validate_email_or_phone(self, value):
        """
        Validate that the identifier is either a valid email or phone number and exists in the database.
        """
        user_exists = User.objects.filter(Q(email=value) | Q(phone_number=value)).exists()
        if not user_exists:
            raise serializers.ValidationError('User with this email or phone number does not exist.')

        # Additional format validation
        if "@" in value:
            try:
                validate_email(value)
            except ValidationError:
                raise serializers.ValidationError("Invalid email address.")
        else:
            phone_regex = re.compile(r'^\+?1?\d{9,15}$')
            if not phone_regex.match(value):
                raise serializers.ValidationError("Invalid phone number format.")

        return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField()
    otp = serializers.CharField(max_length=7)
    password = serializers.CharField(write_only=True)

    def validate_email_or_phone(self, value):
        """
        Validate that the identifier is either a valid email or phone number.
        """
        if "@" in value:
            try:
                validate_email(value)
            except ValidationError:
                raise serializers.ValidationError("Invalid email address.")
        else:
            phone_regex = re.compile(r'^\+?1?\d{9,15}$')
            if not phone_regex.match(value):
                raise serializers.ValidationError("Invalid phone number format.")
        return value

    def validate_otp(self, value):
        """
        Validate OTP format (assuming it's a 7-digit numeric code).
        """
        if not value.isdigit() or len(value) != 7:
            raise serializers.ValidationError("OTP must be a 7-digit number.")
        return value

    def validate_password(self, value):
        """
        Validate password strength.
        """
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("Password must contain at least one special character.")
        return value

    def validate(self, attrs):
        email_or_phone = attrs.get('email_or_phone')
        otp = attrs.get('otp')

        try:
            user = User.objects.get(
                Q(email=email_or_phone) | Q(phone_number=email_or_phone),
                reset_otp=otp,
                otp_created_at__gte=timezone.now() - timedelta(minutes=10)
            )
        except User.DoesNotExist:
            raise serializers.ValidationError('Invalid OTP or OTP has expired.')

        self.context['user'] = user
        return attrs

    def save(self):
        user = self.context['user']
        password = self.validated_data['password']

        # Set the new password
        user.set_password(password)

        # Clear OTP fields
        user.reset_otp = None
        user.otp_created_at = None
        user.save()

        return user