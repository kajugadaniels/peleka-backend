from account.serializers import *
from django.db import transaction
from django.db.models import Count, Q
from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated, AllowAny

class PermissionListView(generics.ListAPIView):
    """
    View to list all permissions. Accessible only to users with appropriate permissions or superusers.
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated] # Change to ensure only authenticated users can access

    def get_queryset(self):
        # Allow superusers unrestricted access
        if self.request.user.is_superuser:
            return super().get_queryset()

        # Check if the user has the 'view_permission' permission
        if not self.request.user.has_perm('auth.view_permission'):
            raise PermissionDenied({'message': "You do not have permission to view permissions."})

        return super().get_queryset()

class AssignPermissionView(APIView):
    """
    View to assign multiple permissions to a user. Handles cases where the user already has the permission and ensures only authorized users can assign permissions.
    """
    # Restrict this API to only those who can manage user permissions
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            # Check if the user has the permission to assign permissions
            if not request.user.has_perm('auth.change_user'):
                raise PermissionDenied({'message': "You do not have permission to assign permissions."})

        user_id = request.data.get('user_id')
        permission_codenames = request.data.get('permission_codename', [])
        response_data = []

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        for codename in permission_codenames:
            try:
                permission = Permission.objects.get(codename=codename)
                if user.user_permissions.filter(id=permission.id).exists():
                    response_data.append({'codename': codename, 'status': f'User already has the "{codename}" permission.'})
                else:
                    user.user_permissions.add(permission)
                    response_data.append({'codename': codename, 'status': 'Permission assigned successfully.'})
            except Permission.DoesNotExist:
                response_data.append({'codename': codename, 'status': 'Permission not found.'})

        if any(item['status'].startswith('User already has') for item in response_data):
            return Response({'results': response_data}, status=status.HTTP_409_CONFLICT)
        return Response({'results': response_data}, status=status.HTTP_200_OK)

class RemovePermissionView(APIView):
    """
    View to remove permissions from a user.
    """
    permission_classes = [permissions.IsAdminUser]  # Only admins can access this

    def post(self, request, *args, **kwargs):
        # Superusers bypass all permissions checks
        if not request.user.is_superuser:
            # Verify the user has permission to change user permissions
            if not request.user.has_perm('auth.change_user'):
                raise PermissionDenied({'message': "You do not have permission to remove permissions."})

        user_id = request.data.get('user_id')
        permissions_codenames = request.data.get('permission_codename', [])
        results = []

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'message': "User not found."}, status=status.HTTP_404_NOT_FOUND)

        for codename in permissions_codenames:
            try:
                permission = Permission.objects.get(codename=codename)
                if user.user_permissions.filter(id=permission.id).exists():
                    user.user_permissions.remove(permission)
                    results.append({"codename": codename, "status": "Permission removed successfully."})
                else:
                    results.append({"codename": codename, "status": "User does not have the specified permission."})
            except Permission.DoesNotExist:
                results.append({"codename": codename, "status": "Permission not found."})

        return Response({"results": results}, status=status.HTTP_200_OK)

class UserPermissionsView(APIView):
    """
    View to list all permissions of a specific user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id, *args, **kwargs):
        # Superusers can access without restrictions
        if not request.user.is_superuser:
            # Check if the user has permission to view user permissions
            if not request.user.has_perm('auth.view_permission'):
                raise PermissionDenied({'message': "You do not have permission to perform this action."})

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Retrieve all user permissions, including group permissions
            user_permissions = user.user_permissions.all() | Permission.objects.filter(group__user=user)
            permissions_data = [{
                'id': perm.id,
                'name': perm.name,
                'codename': perm.codename,
                'content_type': perm.content_type.model
            } for perm in user_permissions.distinct()]

            return Response({
                'message': 'Permissions retrieved successfully.',
                'permissions': permissions_data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'message': 'Failed to retrieve permissions.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserListView(APIView):
    """
    API view to list all users with their roles.
    Only superusers and users with the 'Admin' role can view users.
    """
    permission_classes = [IsAuthenticated]  # Allow access to authenticated users

    def get(self, request):
        try:
            # Check if the user is a superuser or has the role of 'Admin'
            if request.user.is_superuser:
                users = User.objects.all().order_by('-id')
            else:
                # If the user is not authorized, return a forbidden response
                return Response({"error": "You do not have permission to view this resource."},
                                status=status.HTTP_403_FORBIDDEN)

            # Serialize user data with roles
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)