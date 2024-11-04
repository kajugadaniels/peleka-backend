from system.models import *
from system.serializers import *
from account.serializers import *
from django.db import transaction
from django.db.models import Count, Q
from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated, AllowAny

class RoleListCreateView(generics.ListCreateAPIView):
    """
    API view to list all roles or create a new role. Ensures only users with appropriate permissions or superusers can access.
    """
    queryset = Role.objects.order_by('-id')
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Superusers have unrestricted access
        if not request.user.is_superuser:
            # Check if the user has permission to view roles
            if not request.user.has_perm('account.view_role'):
                raise PermissionDenied({'message': "You do not have permission to view roles."})
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Superusers can perform any action
        if not request.user.is_superuser:
            # Check if the user has permission to add a role
            if not request.user.has_perm('account.add_role'):
                raise PermissionDenied({'message': "You do not have permission to create roles."})
        # Handle unique constraint explicitly
        if Role.objects.filter(name=request.data.get('name')).exists():
            return Response({
                'message': 'A role with this name already exists.'
            }, status=status.HTTP_400_BAD_REQUEST)
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        # Save and respond with a custom message
        role = serializer.save()
        return Response({
            'message': 'Role created successfully.',
            'data': RoleSerializer(role).data
        }, status=status.HTTP_201_CREATED)

class RoleRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a role. Ensures only users with appropriate permissions or superusers can access.
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        role = get_object_or_404(Role, pk=self.kwargs['pk'])
        return role

    def get(self, request, *args, **kwargs):
        # Superusers have unrestricted access
        if not request.user.is_superuser:
            # Check if the user has permission to view roles
            if not request.user.has_perm('account.view_role'):
                raise PermissionDenied({'message': "You do not have permission to view roles."})
        return super().retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        # Superusers can perform any action
        if not request.user.is_superuser:
            # Check if the user has permission to change roles
            if not request.user.has_perm('account.change_role'):
                raise PermissionDenied({'message': "You do not have permission to update roles."})

        # Check for unique role name excluding the current role
        if Role.objects.filter(name=request.data.get('name')).exclude(id=kwargs['pk']).exists():
            return Response({
                'message': 'A role with this name already exists.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        response = super().update(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            response.data['message'] = 'Role updated successfully.'
            return Response(response.data, status=status.HTTP_200_OK)
        else:
            return Response({
                'message': 'Role update failed.',
                'errors': response.data
            }, status=response.status_code)

    def delete(self, request, *args, **kwargs):
        # Superusers can perform any action
        if not request.user.is_superuser:
            # Check if the user has permission to delete roles
            if not request.user.has_perm('account.delete_role'):
                raise PermissionDenied({'message': "You do not have permission to delete roles."})

        role = self.get_object()
        role.delete()
        return Response({'message': 'Role deleted successfully.'}, status=status.HTTP_200_OK)

class PermissionListView(generics.ListAPIView):
    """
    View to list all permissions. Accessible only to superusers or users with the 'view_permission' permission.
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated]  # Access restricted to authenticated users

    def get_queryset(self):
        # Superusers can access all permissions
        if self.request.user.is_superuser:
            return super().get_queryset()

        # Users require 'auth.view_permission' permission to access this endpoint
        if not self.request.user.has_perm('auth.view_permission'):
            raise PermissionDenied({'message': "You do not have permission to view permissions."})

        return super().get_queryset()

class AssignPermissionView(APIView):
    """
    API view to assign permissions to a user. Only superusers or users with 'change_user' permission can access.
    """
    permission_classes = [permissions.IsAdminUser]  # Restricted to admin users

    def post(self, request, *args, **kwargs):
        # Superusers can bypass the permission check
        if not request.user.is_superuser and not request.user.has_perm('auth.change_user'):
            raise PermissionDenied({'message': "You do not have permission to assign permissions."})

        user_id = request.data.get('user_id')
        permission_codenames = request.data.get('permission_codename', [])
        response_data = []

        # Check if user exists
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Assign each permission if the user doesn't already have it
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

        return Response({'results': response_data}, status=status.HTTP_200_OK)

class RemovePermissionView(APIView):
    """
    API view to remove permissions from a user. Only superusers or users with 'change_user' permission can access.
    """
    permission_classes = [permissions.IsAdminUser]  # Restricted to admin users

    def post(self, request, *args, **kwargs):
        if not request.user.is_superuser and not request.user.has_perm('auth.change_user'):
            raise PermissionDenied({'message': "You do not have permission to remove permissions."})

        user_id = request.data.get('user_id')
        permissions_codenames = request.data.get('permission_codename', [])
        results = []

        # Check if user exists
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'message': "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Remove each permission if the user has it
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
    API view to retrieve all permissions of a specific user. Restricted to superusers or users with 'view_permission' permission.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id, *args, **kwargs):
        if not request.user.is_superuser and not request.user.has_perm('auth.view_permission'):
            raise PermissionDenied({'message': "You do not have permission to view this user's permissions."})

        # Check if the user exists
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Retrieve direct and group permissions
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

class UserListView(APIView):
    """
    API view to list all users and their roles. Accessible only to superusers or users with 'view_user' permission.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Superusers can access all users
        if request.user.is_superuser:
            users = User.objects.all().order_by('-id')
        elif request.user.has_perm('account.view_user'):
            # Users with the 'view_user' permission can access all users
            users = User.objects.all().order_by('-id')
        else:
            # If the user lacks the necessary permission, return a forbidden response
            return Response({"error": "You do not have permission to view this resource."},
                            status=status.HTTP_403_FORBIDDEN)

        # Serialize user data for response
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserDetailView(APIView):
    """
    API view to retrieve, update, or delete user details by ID.
    Accessible only to superusers or users with specific permissions for each action.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, user_id):
        # Retrieve user or return None if not found
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    def get(self, request, user_id):
        user = self.get_object(user_id)
        if user is None:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Only superusers or users with 'view_user' permission can view user details
        if not request.user.is_superuser and not request.user.has_perm('account.view_user'):
            return Response({"error": "You do not have permission to view this user."}, status=status.HTTP_403_FORBIDDEN)

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, user_id):
        user = self.get_object(user_id)
        if user is None:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Only superusers or users with 'change_user' permission can update user details
        if not request.user.is_superuser and not request.user.has_perm('account.change_user'):
            return Response({"error": "You do not have permission to edit this user."}, status=status.HTTP_403_FORBIDDEN)

        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User updated successfully", "user": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id):
        user = self.get_object(user_id)
        if user is None:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Only superusers or users with 'delete_user' permission can delete users
        if not request.user.is_superuser and not request.user.has_perm('account.delete_user'):
            return Response({"error": "You do not have permission to delete this user."}, status=status.HTTP_403_FORBIDDEN)

        user.delete()
        return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class RiderListCreateView(generics.ListCreateAPIView):
    """
    API view to list all Riders and allow creation of new Riders.
    - Accessible to users with 'view_rider' or 'add_rider' permissions.
    """
    queryset = Rider.objects.all()
    serializer_class = RiderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Check if the user has permission to view riders
        if not request.user.is_superuser and not request.user.has_perm('system.view_rider'):
            raise PermissionDenied({'message': "You do not have permission to view riders."})
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Check if the user has permission to add a rider
        if not request.user.is_superuser and not request.user.has_perm('system.add_rider'):
            raise PermissionDenied({'message': "You do not have permission to add riders."})
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        # Save the rider and return a custom response
        rider = serializer.save()
        return Response({
            'message': 'Rider created successfully.',
            'data': RiderSerializer(rider).data
        }, status=status.HTTP_201_CREATED)

class RiderRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a Rider.
    - Only accessible to users with 'view_rider', 'change_rider', or 'delete_rider' permissions.
    """
    queryset = Rider.objects.all()
    serializer_class = RiderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Ensure user has 'view_rider' permission to retrieve Rider details
        if not request.user.is_superuser and not request.user.has_perm('system.view_rider'):
            raise PermissionDenied({'message': "You do not have permission to view this resource."})
        
        # Call the default retrieve method without modifying response.data
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        # Ensure user has 'change_rider' permission to update Rider details
        if not request.user.is_superuser and not request.user.has_perm('system.change_rider'):
            raise PermissionDenied({'message': "You do not have permission to edit this resource."})
        
        # Call the default update method and include a success message
        response = self.update(request, *args, **kwargs)
        response.data = {'message': "Rider updated successfully", **response.data}
        return response

    def delete(self, request, *args, **kwargs):
        # Ensure user has 'delete_rider' permission to delete a Rider
        if not request.user.is_superuser and not request.user.has_perm('system.delete_rider'):
            raise PermissionDenied({'message': "You do not have permission to delete this resource."})
        
        # Call the default destroy method and include a success message
        response = self.destroy(request, *args, **kwargs)
        response.data = {'message': "Rider deleted successfully"}
        return response

class DeliveryRequestListView(generics.ListAPIView):
    """
    API view to list all Delivery Requests.
    - Accessible only to users with 'view_deliveryrequest' permission.
    """
    queryset = DeliveryRequest.objects.all().order_by('-created_at')
    serializer_class = DeliveryRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Check if the user has permission to view delivery requests
        if not request.user.is_superuser and not request.user.has_perm('system.view_deliveryrequest'):
            raise PermissionDenied({'message': "You do not have permission to view delivery requests."})
        
        # Call the default get method to list delivery requests
        return super().get(request, *args, **kwargs)