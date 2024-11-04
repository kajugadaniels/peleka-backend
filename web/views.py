from system.models import *
from web.serializers import *
from system.serializers import *
from account.serializers import *
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics, permissions, status

class RiderListView(generics.ListAPIView):
    """
    API view to list all Riders.
    Accessible to anyone.
    """
    queryset = Rider.objects.all()
    serializer_class = RiderSerializer
    permission_classes = [AllowAny]  # Allow any user to access this view

class RiderDetailView(generics.RetrieveAPIView):
    """
    API view to retrieve Rider details.
    Accessible to anyone.
    """
    queryset = Rider.objects.all()
    serializer_class = RiderSerializer
    permission_classes = [AllowAny]  # Allow any user to access this view

class UserDeliveryRequestListView(generics.ListAPIView):
    """
    API view to list all Delivery Requests for the logged-in user.
    - Accessible only to authenticated users.
    """
    serializer_class = DeliveryRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only fetch delivery requests made by the logged-in user
        user = self.request.user
        return DeliveryRequest.objects.filter(client=user, delete_status=False).order_by('-created_at')

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class UserDeliveryRequestCreateView(generics.CreateAPIView):
    """
    API view to create a new Delivery Request for the logged-in user.
    - Accessible only to authenticated users.
    """
    serializer_class = UserDeliveryRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Automatically set the client as the logged-in user
        serializer.save(client=self.request.user, status="Pending")

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class UserDeliveryRequestDetailView(generics.RetrieveAPIView):
    """
    API view to retrieve a Delivery Request by ID for the logged-in user.
    - Accessible only to authenticated users.
    """
    serializer_class = DeliveryRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DeliveryRequest.objects.filter(client=self.request.user, delete_status=False)

    def get_object(self):
        try:
            return self.get_queryset().get(pk=self.kwargs['pk'])
        except DeliveryRequest.DoesNotExist:
            raise NotFound({'message': "Delivery request not found."})

class UserDeliveryRequestUpdateView(generics.UpdateAPIView):
    """
    API view to update a Delivery Request for the logged-in user.
    - Accessible only to authenticated users.
    """
    serializer_class = DeliveryRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DeliveryRequest.objects.filter(client=self.request.user, delete_status=False)

    def update(self, request, *args, **kwargs):
        delivery_request = self.get_object()

        # Check if the status allows updating
        if delivery_request.status not in ['Pending', 'Cancelled']:
            return Response(
                {'message': "Only requests with status 'Pending' or 'Cancelled' can be updated."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Deserialize and validate the data
        serializer = self.get_serializer(delivery_request, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # Save the updated delivery request
        self.perform_update(serializer)

        return Response({
            "message": "Delivery request updated successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

class UserDeleteDeliveryRequestView(generics.DestroyAPIView):
    """
    API view to delete a Delivery Request for the logged-in user.
    - Accessible only to authenticated users.
    """
    serializer_class = DeliveryRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DeliveryRequest.objects.filter(client=self.request.user, delete_status=False)

    def delete(self, request, *args, **kwargs):
        delivery_request = self.get_object()

        # Check if the status allows deletion
        if delivery_request.status not in ['Pending', 'Cancelled']:
            return Response(
                {'message': "Only requests with status 'Pending' or 'Cancelled' can be deleted."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Mark the delivery request as deleted
        delivery_request.delete_status = True
        delivery_request.save()

        return Response({
            'message': "Delivery request marked as deleted successfully."
        }, status=status.HTTP_200_OK)