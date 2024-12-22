from system.models import *
from system.serializers import *
from account.serializers import *
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, permissions, status

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
                raise PermissionDenied({'error': "You do not have the necessary permissions to view roles."})
        response = super().get(request, *args, **kwargs)
        return Response({
            'message': 'Roles retrieved successfully.',
            'data': response.data
        }, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        # Superusers can perform any action
        if not request.user.is_superuser:
            # Check if the user has permission to add a role
            if not request.user.has_perm('account.add_role'):
                raise PermissionDenied({'error': "You do not have the necessary permissions to create roles."})
        # Handle unique constraint explicitly
        if Role.objects.filter(name=request.data.get('name')).exists():
            return Response({
                'error': 'A role with this name already exists. Please choose a different name.'
            }, status=status.HTTP_400_BAD_REQUEST)
        return super().post(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            role = serializer.save()
            return Response({
                'message': 'Role created successfully.',
                'data': RoleSerializer(role, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            return Response({
                'error': 'Role creation failed.',
                'details': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)

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
                raise PermissionDenied({'error': "You do not have the necessary permissions to view this role."})
        role = self.get_object()
        serializer = self.get_serializer(role, context={'request': request})
        return Response({
            'message': f"Role '{role.name}' retrieved successfully.",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        # Superusers can perform any action
        if not request.user.is_superuser:
            # Check if the user has permission to change roles
            if not request.user.has_perm('account.change_role'):
                raise PermissionDenied({'error': "You do not have the necessary permissions to update this role."})

        # Check for unique role name excluding the current role
        role_id = kwargs.get('pk')
        new_name = request.data.get('name')
        if Role.objects.filter(name=new_name).exclude(id=role_id).exists():
            return Response({
                'error': f"A role with the name '{new_name}' already exists. Please choose a different name."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            response = super().update(request, *args, **kwargs)
            return Response({
                'message': f"Role '{response.data.get('name')}' updated successfully.",
                'data': response.data
            }, status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            return Response({
                'error': 'Role update failed.',
                'details': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        # Superusers can perform any action
        if not request.user.is_superuser:
            # Check if the user has permission to delete roles
            if not request.user.has_perm('account.delete_role'):
                raise PermissionDenied({'error': "You do not have the necessary permissions to delete this role."})

        role = self.get_object()
        role.delete()
        return Response({
            'message': f"Role '{role.name}' deleted successfully."
        }, status=status.HTTP_200_OK)

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
            raise PermissionDenied({'error': "You do not have the necessary permissions to view permissions."})

        return super().get_queryset()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response({
            'message': 'Permissions retrieved successfully.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

class AssignPermissionView(APIView):
    """
    API view to assign permissions to a user. Only superusers or users with 'change_user' permission can access.
    """
    permission_classes = [permissions.IsAdminUser]  # Restricted to admin users

    def post(self, request, *args, **kwargs):
        # Superusers can bypass the permission check
        if not request.user.is_superuser and not request.user.has_perm('auth.change_user'):
            raise PermissionDenied({'error': "You do not have the necessary permissions to assign permissions."})

        user_id = request.data.get('user_id')
        permission_codenames = request.data.get('permission_codename', [])
        response_data = []

        # Validate user_id
        if not user_id:
            return Response({
                'error': 'User ID is required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate permission_codenames
        if not permission_codenames:
            return Response({
                'error': 'At least one permission codename must be provided.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if user exists
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': f'User with ID {user_id} does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        # Assign each permission if the user doesn't already have it
        for codename in permission_codenames:
            try:
                permission = Permission.objects.get(codename=codename)
                if user.user_permissions.filter(id=permission.id).exists():
                    response_data.append({'codename': codename, 'status': f'User already has the "{codename}" permission.'})
                else:
                    user.user_permissions.add(permission)
                    response_data.append({'codename': codename, 'status': f'Permission "{codename}" assigned successfully.'})
            except Permission.DoesNotExist:
                response_data.append({'codename': codename, 'status': f'Permission "{codename}" does not exist.'})

        return Response({
            'message': 'Permissions assignment process completed.',
            'results': response_data
        }, status=status.HTTP_200_OK)

class RemovePermissionView(APIView):
    """
    API view to remove permissions from a user. Only superusers or users with 'change_user' permission can access.
    """
    permission_classes = [permissions.IsAdminUser]  # Restricted to admin users

    def post(self, request, *args, **kwargs):
        if not request.user.is_superuser and not request.user.has_perm('auth.change_user'):
            raise PermissionDenied({'error': "You do not have the necessary permissions to remove permissions."})

        user_id = request.data.get('user_id')
        permissions_codenames = request.data.get('permission_codename', [])
        results = []

        # Validate user_id
        if not user_id:
            return Response({
                'error': 'User ID is required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate permissions_codenames
        if not permissions_codenames:
            return Response({
                'error': 'At least one permission codename must be provided.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if user exists
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': f'User with ID {user_id} does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        # Remove each permission if the user has it
        for codename in permissions_codenames:
            try:
                permission = Permission.objects.get(codename=codename)
                if user.user_permissions.filter(id=permission.id).exists():
                    user.user_permissions.remove(permission)
                    results.append({"codename": codename, "status": f'Permission "{codename}" removed successfully.'})
                else:
                    results.append({"codename": codename, "status": f'User does not have the "{codename}" permission.'})
            except Permission.DoesNotExist:
                results.append({"codename": codename, "status": f'Permission "{codename}" does not exist.'})

        return Response({
            "message": "Permissions removal process completed.",
            "results": results
        }, status=status.HTTP_200_OK)

class UserPermissionsView(APIView):
    """
    API view to retrieve all permissions of a specific user. Restricted to superusers or users with 'view_permission' permission.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id, *args, **kwargs):
        if not request.user.is_superuser and not request.user.has_perm('auth.view_permission'):
            raise PermissionDenied({'error': "You do not have the necessary permissions to view this user's permissions."})

        # Check if the user exists
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'error': f'User with ID {user_id} does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        # Retrieve direct and group permissions
        user_permissions = user.user_permissions.all() | Permission.objects.filter(group__user=user)
        permissions_data = [{
            'id': perm.id,
            'name': perm.name,
            'codename': perm.codename,
            'content_type': perm.content_type.model
        } for perm in user_permissions.distinct()]

        return Response({
            'message': f"Permissions for user '{user.name}' retrieved successfully.",
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
            # Users with the 'view_user' permission can access all users excluding superusers
            users = User.objects.exclude(is_superuser=True).order_by('-id')
        else:
            # If the user lacks the necessary permission, return a forbidden response
            return Response({
                "error": "Access denied. You do not have the necessary permissions to view users."
            }, status=status.HTTP_403_FORBIDDEN)

        # Serialize user data for response
        serializer = UserSerializer(users, many=True, context={'request': request})
        return Response({
            'message': 'Users retrieved successfully.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

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
            return Response({
                'error': f"User with ID {user_id} not found."
            }, status=status.HTTP_404_NOT_FOUND)

        # Only superusers or users with 'view_user' permission can view user details
        if not request.user.is_superuser and not request.user.has_perm('account.view_user'):
            return Response({
                "error": "Access denied. You do not have the necessary permissions to view this user's details."
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = UserSerializer(user, context={'request': request})
        return Response({
            'message': f"User '{user.name}' retrieved successfully.",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def put(self, request, user_id):
        user = self.get_object(user_id)
        if user is None:
            return Response({
                'error': f"User with ID {user_id} not found."
            }, status=status.HTTP_404_NOT_FOUND)

        # Only superusers or users with 'change_user' permission can update user details
        if not request.user.is_superuser and not request.user.has_perm('account.change_user'):
            return Response({
                "error": "Access denied. You do not have the necessary permissions to update this user's details."
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = UserSerializer(user, data=request.data, partial=True)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "message": f"User '{user.name}' updated successfully.",
                "user": serializer.data
            }, status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            return Response({
                "error": "User update failed due to invalid input.",
                "details": e.detail
            }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id):
        user = self.get_object(user_id)
        if user is None:
            return Response({
                'error': f"User with ID {user_id} not found."
            }, status=status.HTTP_404_NOT_FOUND)

        # Only superusers or users with 'delete_user' permission can delete users
        if not request.user.is_superuser and not request.user.has_perm('account.delete_user'):
            return Response({
                "error": "Access denied. You do not have the necessary permissions to delete this user."
            }, status=status.HTTP_403_FORBIDDEN)

        user.delete()
        return Response({
            "message": f"User '{user.name}' deleted successfully."
        }, status=status.HTTP_204_NO_CONTENT)

class RiderListCreateView(generics.ListCreateAPIView):
    """
    API view to list all Riders and allow creation of new Riders.
    - Accessible to users with 'view_rider' or 'add_rider' permissions.
    """
    queryset = Rider.objects.all().order_by('-id')
    serializer_class = RiderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Check if the user has permission to view riders
        if not request.user.is_superuser and not request.user.has_perm('system.view_rider'):
            raise PermissionDenied({'error': "You do not have the necessary permissions to view riders."})
        response = super().get(request, *args, **kwargs)
        return Response({
            'message': 'Riders retrieved successfully.',
            'data': response.data
        }, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        # Check if the user has permission to add a rider
        if not request.user.is_superuser and not request.user.has_perm('system.add_rider'):
            raise PermissionDenied({'error': "You do not have the necessary permissions to add riders."})
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            rider = serializer.save()
            return Response({
                'message': f"Rider '{rider.name}' created successfully.",
                'data': RiderSerializer(rider, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            return Response({
                'error': 'Rider creation failed.',
                'details': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)

class RiderRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a Rider.
    - Only accessible to users with 'view_rider', 'change_rider', or 'delete_rider' permissions.
    """
    queryset = Rider.objects.all().order_by('-id')
    serializer_class = RiderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Ensure user has 'view_rider' permission to retrieve Rider details
        if not request.user.is_superuser and not request.user.has_perm('system.view_rider'):
            raise PermissionDenied({'error': "You do not have the necessary permissions to view this rider."})
        
        rider = self.get_object()
        serializer = self.get_serializer(rider, context={'request': request})
        return Response({
            'message': f"Rider '{rider.name}' retrieved successfully.",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        # Ensure user has 'change_rider' permission to update Rider details
        if not request.user.is_superuser and not request.user.has_perm('system.change_rider'):
            raise PermissionDenied({'error': "You do not have the necessary permissions to update this rider."})
        
        rider = self.get_object()
        serializer = self.get_serializer(rider, data=request.data, partial=True)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                'message': f"Rider '{rider.name}' updated successfully.",
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            return Response({
                'error': 'Rider update failed.',
                'details': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        # Ensure user has 'delete_rider' permission to delete a Rider
        if not request.user.is_superuser and not request.user.has_perm('system.delete_rider'):
            raise PermissionDenied({'error': "You do not have the necessary permissions to delete this rider."})
        
        rider = self.get_object()
        rider.delete()
        return Response({
            'message': f"Rider '{rider.name}' deleted successfully."
        }, status=status.HTTP_200_OK)

class DeliveryRequestListView(generics.ListAPIView):
    """
    API view to list all Delivery Requests.
    - Accessible only to users with 'view_deliveryrequest' permission.
    - Superusers can view all requests, including those marked as deleted.
    """
    serializer_class = DeliveryRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Superusers can see all delivery requests, including deleted ones
        if user.is_superuser:
            return DeliveryRequest.objects.all().order_by('-created_at')

        # Other users can only see non-deleted delivery requests
        if user.has_perm('system.view_deliveryrequest'):
            return DeliveryRequest.objects.filter(delete_status=False).order_by('-created_at')

        # If the user does not have the required permission, return an empty queryset
        return DeliveryRequest.objects.none()

    def get(self, request, *args, **kwargs):
        # Check if the user has permission to view delivery requests
        if not request.user.is_superuser and not request.user.has_perm('system.view_deliveryrequest'):
            raise PermissionDenied({'error': "You do not have the necessary permissions to view delivery requests."})

        response = super().get(request, *args, **kwargs)
        return Response({
            'message': 'Delivery requests retrieved successfully.',
            'data': response.data
        }, status=status.HTTP_200_OK)

class DeliveryRequestCreateView(generics.CreateAPIView):
    """
    API view to create a new Delivery Request.
    - Accessible only to authenticated users with 'add_deliveryrequest' permission.
    """
    queryset = DeliveryRequest.objects.all().order_by('-id')
    serializer_class = DeliveryRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Handle the creation of a new delivery request.
        """
        # Check if the user has permission to add a delivery request
        if not request.user.has_perm('system.add_deliveryrequest'):
            raise PermissionDenied({'error': "You do not have the necessary permissions to create delivery requests."})

        # Deserialize the incoming data
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            delivery_request = serializer.save()
            return Response({
                'message': 'Delivery request created successfully.',
                'data': DeliveryRequestSerializer(delivery_request, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            return Response({
                'error': 'Delivery request creation failed due to invalid input.',
                'details': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)

class DeliveryRequestDetailView(generics.RetrieveAPIView):
    """
    API view to retrieve a Delivery Request by its ID.
    - Accessible only to authenticated users with 'view_deliveryrequest' permission.
    """
    queryset = DeliveryRequest.objects.all().order_by('-id')
    serializer_class = DeliveryRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Retrieve and return the DeliveryRequest instance by ID.
        - Check if the user has permission to view the delivery request.
        - If not found, raise a NotFound exception.
        """
        # Check if the user has the 'view_deliveryrequest' permission
        if not self.request.user.has_perm('system.view_deliveryrequest') and not self.request.user.is_superuser:
            raise PermissionDenied({'error': "You do not have the necessary permissions to view this delivery request."})

        try:
            # Fetch the delivery request object by its primary key (ID)
            return DeliveryRequest.objects.get(pk=self.kwargs['pk'])
        except DeliveryRequest.DoesNotExist:
            # Raise a NotFound exception if the object does not exist
            raise NotFound({'error': f"Delivery request with ID {self.kwargs['pk']} not found."})

    def get(self, request, *args, **kwargs):
        delivery_request = self.get_object()
        serializer = self.get_serializer(delivery_request, context={'request': request})
        return Response({
            'message': f"Delivery request ID {delivery_request.id} retrieved successfully.",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

class DeliveryRequestUpdateView(generics.UpdateAPIView):
    """
    API view to update a DeliveryRequest.
    - Only accessible to authenticated users with 'change_deliveryrequest' permission.
    - Automatically sets 'delivered' to True in RiderDelivery when status is updated to 'Completed'.
    """
    queryset = DeliveryRequest.objects.all().order_by('-id')
    serializer_class = DeliveryRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):
        # Check if the user has permission to change the delivery request
        if not request.user.has_perm('system.change_deliveryrequest') and not request.user.is_superuser:
            raise PermissionDenied({'error': "You do not have the necessary permissions to update this delivery request."})

        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        # Retrieve the DeliveryRequest object
        delivery_request = self.get_object()

        # Store the original status to compare later
        original_status = delivery_request.status

        # Use the serializer to update the object with validated data
        serializer = self.get_serializer(delivery_request, data=request.data, partial=True)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            # Get the updated status
            updated_status = serializer.validated_data.get('status', original_status)

            # If the status has been updated to 'Completed' and was not 'Completed' before
            if updated_status == 'Completed' and original_status != 'Completed':
                # Update all related RiderDelivery records to set 'delivered' to True
                updated_count = RiderDelivery.objects.filter(delivery_request=delivery_request, delivered=False).update(
                    delivered=True,
                    delivered_at=timezone.now()
                )
                message_extra = f" Additionally, {updated_count} RiderDelivery record(s) marked as delivered."
            else:
                message_extra = ""

            return Response({
                'message': f"Delivery request '{delivery_request.id}' updated successfully.{message_extra}",
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            return Response({
                'error': 'Delivery request update failed due to invalid input.',
                'details': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)

class DeleteDeliveryRequestView(generics.DestroyAPIView):
    """
    API view to delete a Delivery Request.
    - Accessible only to authenticated users with the 'delete_deliveryrequest' permission.
    """
    queryset = DeliveryRequest.objects.all()
    serializer_class = DeliveryRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Retrieve and return the DeliveryRequest instance.
        Check if the user has permission to delete it.
        """
        try:
            delivery_request = DeliveryRequest.objects.get(pk=self.kwargs['pk'], delete_status=False)
        except DeliveryRequest.DoesNotExist:
            raise NotFound({'error': f"Delivery request with ID {self.kwargs['pk']} not found or already deleted."})

        # Check if the user has the 'delete_deliveryrequest' permission
        if not self.request.user.has_perm('system.delete_deliveryrequest') and not self.request.user.is_superuser:
            raise PermissionDenied({'error': "You do not have the necessary permissions to delete this delivery request."})

        return delivery_request

    def delete(self, request, *args, **kwargs):
        delivery_request = self.get_object()

        # Check if the status allows deletion
        if delivery_request.status not in ['Pending', 'Cancelled']:
            return Response({
                'error': "Only delivery requests with status 'Pending' or 'Cancelled' can be deleted."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Mark the delivery request as deleted
        delivery_request.delete_status = True
        delivery_request.deleted_by = request.user.name
        delivery_request.save()

        return Response({
            'message': f"Delivery request ID {delivery_request.id} marked as deleted successfully.",
            'data': DeliveryRequestSerializer(delivery_request, context={'request': request}).data
        }, status=status.HTTP_200_OK)

class CompleteDeliveryRequestView(generics.UpdateAPIView):
    """
    API view to mark a DeliveryRequest as Completed.
    - Accessible to any authenticated user.
    - Only updates the status to 'Completed'.
    - If already completed, returns a corresponding message.
    - Also updates related RiderDelivery records by setting 'delivered' to True
      and recording the 'delivered_at' timestamp.
    """
    queryset = DeliveryRequest.objects.all()
    serializer_class = DeliveryRequestCompleteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        delivery_request = self.get_object()

        if delivery_request.status == 'Completed':
            return Response({
                'message': 'The delivery request is already marked as completed.',
                'data': DeliveryRequestSerializer(delivery_request, context={'request': request}).data
            }, status=status.HTTP_200_OK)

        # Set status to 'Completed'
        delivery_request.status = 'Completed'
        delivery_request.save()

        # Update related RiderDelivery records
        rider_deliveries = RiderDelivery.objects.filter(
            delivery_request=delivery_request,
            delivered=False
        )
        updated_count = rider_deliveries.update(
            delivered=True,
            delivered_at=timezone.now()
        )

        # Serialize the updated delivery request
        serializer = self.get_serializer(delivery_request)

        return Response({
            'message': f"Delivery request ID {delivery_request.id} marked as completed successfully.",
            'data': serializer.data,
            'rider_deliveries_updated': updated_count
        }, status=status.HTTP_200_OK)

class RiderDeliveryListView(generics.ListAPIView):
    """
    API view to list all Rider Deliveries.
    - Accessible only to authenticated users with 'view_riderdelivery' permission.
    """
    queryset = RiderDelivery.objects.all().order_by('-id')
    serializer_class = RiderDeliverySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Check if the user has the necessary permission
        if not request.user.is_superuser and not request.user.has_perm('system.view_riderdelivery'):
            raise PermissionDenied({'error': "You do not have the necessary permissions to view rider deliveries."})

        response = super().get(request, *args, **kwargs)
        return Response({
            'message': 'Rider deliveries retrieved successfully.',
            'data': response.data
        }, status=status.HTTP_200_OK)

class AddRiderDeliveryView(generics.CreateAPIView):
    """
    API view to assign a rider to a delivery request.
    - Accessible only to authenticated users with appropriate permissions.
    - Automatically updates the delivery request status to "In Progress" upon assignment.
    """
    queryset = RiderDelivery.objects.all().order_by('-id')
    serializer_class = RiderDeliverySerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        rider_id = request.data.get('rider_id')
        delivery_request_id = request.data.get('delivery_request_id')

        # Validate input
        if not rider_id or not delivery_request_id:
            return Response({
                'error': "Both 'rider_id' and 'delivery_request_id' are required to assign a rider to a delivery request."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the rider and delivery request objects
        try:
            rider = Rider.objects.get(id=rider_id)
        except Rider.DoesNotExist:
            return Response({'error': f"Rider with ID {rider_id} does not exist."}, status=status.HTTP_404_NOT_FOUND)

        try:
            delivery_request = DeliveryRequest.objects.get(id=delivery_request_id)
        except DeliveryRequest.DoesNotExist:
            return Response({'error': f"Delivery request with ID {delivery_request_id} does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the rider is available (no RiderDelivery with delivered=False)
        if RiderDelivery.objects.filter(rider=rider, delivered=False).exists():
            return Response({
                'error': f"Rider '{rider.name}' is currently unavailable for a new delivery assignment."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Assign the rider by creating a new RiderDelivery entry with delivered=False
        try:
            rider_delivery = RiderDelivery.objects.create(
                rider=rider,
                delivery_request=delivery_request,
                delivered=False,
                assigned_at=timezone.now(),
                # in_progress_at=timezone.now(),
                last_assigned_at=timezone.now()
            )
        except Exception as e:
            return Response({
                'error': f"An error occurred while assigning the rider: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Update the delivery request status
        delivery_request.status = 'Accepted'
        delivery_request.save()

        serializer = self.get_serializer(rider_delivery, context={'request': request})

        return Response({
            'message': f"Rider '{rider.name}' assigned to delivery request ID {delivery_request.id} successfully.",
            'rider_delivery': serializer.data
        }, status=status.HTTP_201_CREATED)

class RiderDeliveryDetailView(generics.RetrieveAPIView):
    """
    API view to retrieve details of a RiderDelivery by its ID.
    - Accessible only to authenticated users with the appropriate permission.
    """
    queryset = RiderDelivery.objects.all().order_by('-id')
    serializer_class = RiderDeliverySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Retrieve and return the RiderDelivery instance.
        - Ensure the user has permission to view rider deliveries.
        """
        try:
            rider_delivery = RiderDelivery.objects.get(pk=self.kwargs['pk'])
        except RiderDelivery.DoesNotExist:
            raise NotFound({'error': f"RiderDelivery with ID {self.kwargs['pk']} not found."})

        # Check if the user has permission to view rider deliveries
        if not self.request.user.has_perm('system.view_riderdelivery') and not self.request.user.is_superuser:
            raise PermissionDenied({'error': "You do not have the necessary permissions to view this rider delivery."})

        return rider_delivery

    def get(self, request, *args, **kwargs):
        rider_delivery = self.get_object()
        serializer = self.get_serializer(rider_delivery, context={'request': request})
        return Response({
            'message': f"RiderDelivery ID {rider_delivery.id} retrieved successfully.",
            'data': serializer.data
        }, status=status.HTTP_200_OK)