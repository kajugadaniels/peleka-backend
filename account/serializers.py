import re
from account.models import *
from django.db.models import Q
from datetime import timedelta
from rest_framework import serializers
from django.contrib.auth.models import Permission

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

class PermissionSerializer(serializers.ModelSerializer):
    permission_string = serializers.SerializerMethodField()
    
    class Meta:
        model = Permission
        fields = ('id', 'name', 'permission_string',)
    
    def get_permission_string(self, obj):
        """
        Return permission in 'app_label.codename' format.
        """
        app_label = obj.content_type.app_label
        codename = obj.codename
        return f"{app_label}.{codename}"

class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Permission.objects.all(),
        write_only=True,
        source='permissions'
    )

    class Meta:
        model = Role
        fields = ['id', 'name', 'permissions', 'permission_ids']
    
    def create(self, validated_data):
        permissions = validated_data.pop('permissions', [])
        role = Role.objects.create(**validated_data)
        role.permissions.set(permissions)
        return role
    
    def update(self, instance, validated_data):
        permissions = validated_data.pop('permissions', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if permissions is not None:
            instance.permissions.set(permissions)
        instance.save()
        return instance 

class UserSerializer(serializers.ModelSerializer):
    role = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        required=False,
        allow_null=True
    )
    role_name = serializers.CharField(source='role.name', read_only=True)
    user_permissions = serializers.SerializerMethodField()
    role_permissions = serializers.SerializerMethodField()
    image = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = (
            'id', 'name', 'email', 'phone_number', 'role', 'role_name', 'image', 'password', 'user_permissions', 'role_permissions'
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_user_permissions(self, obj):
        """Retrieve the user's direct permissions."""
        return obj.get_all_permissions()

    def get_role_permissions(self, obj):
        """Retrieve the permissions related to the user's role."""
        if obj.role:
            return obj.role.permissions.values_list('codename', flat=True)
        return []

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        user.assign_role_permissions()

        return user

    def update(self, instance, validated_data):
        """
        Update user details and hash the password if provided.
        """
        old_role = instance.role
        password = validated_data.pop('password', None)
        instance = super().update(instance, validated_data)

        # Handle image upload separately if provided
        if 'image' in validated_data:
            instance.image = validated_data.pop('image')

        # If a password is provided, hash it using set_password
        if password:
            instance.set_password(password)
            instance.save()

        # If the role has changed, update permissions
        if old_role != instance.role:
            instance.assign_role_permissions()

        # Update the remaining fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance