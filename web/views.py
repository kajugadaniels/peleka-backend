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
    API view to list all Delivery Requests.
    - Accessible to any user.
    """
    serializer_class = UserDeliveryRequestSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        # Fetch all delivery requests that are not marked as deleted
        return DeliveryRequest.objects.filter(delete_status=False).order_by('-created_at')

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class UserDeliveryRequestCreateView(generics.CreateAPIView):
    """
    API view to create a new Delivery Request.
    - Accessible to any user.
    """
    serializer_class = UserDeliveryRequestSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        # Ensure that the client is provided in the request data
        client = serializer.validated_data.get('client')
        if not client:
            raise serializers.ValidationError({"client": "This field is required."})
        serializer.save(status="Pending")

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserDeliveryRequestDetailView(generics.RetrieveAPIView):
    """
    API view to retrieve a Delivery Request by ID.
    - Accessible to any user.
    """
    serializer_class = UserDeliveryRequestSerializer
    permission_classes = [permissions.AllowAny]

    queryset = DeliveryRequest.objects.filter(delete_status=False)

    def get_object(self):
        try:
            return self.get_queryset().get(pk=self.kwargs['pk'])
        except DeliveryRequest.DoesNotExist:
            raise NotFound({'message': "Delivery request not found."})


class UserDeliveryRequestUpdateView(generics.UpdateAPIView):
    """
    API view to update a Delivery Request.
    - Accessible to any user.
    """
    serializer_class = UserDeliveryRequestSerializer
    permission_classes = [permissions.AllowAny]

    queryset = DeliveryRequest.objects.filter(delete_status=False)

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
    API view to delete a Delivery Request.
    - Accessible to any user.
    """
    serializer_class = UserDeliveryRequestSerializer
    permission_classes = [permissions.AllowAny]

    queryset = DeliveryRequest.objects.filter(delete_status=False)

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