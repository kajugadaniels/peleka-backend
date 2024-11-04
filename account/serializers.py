from rest_framework import serializers
from django.contrib.auth.models import Permission

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