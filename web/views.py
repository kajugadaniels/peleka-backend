from system.models import *
from system.serializers import *
from account.serializers import *
from rest_framework.permissions import AllowAny
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

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
    serializer_class = DeliveryRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        estimated_distance_km = serializer.validated_data.get('estimated_distance_km')

        # Calculate the estimated delivery time based on distance (example logic)
        estimated_delivery_time = self.calculate_estimated_time(estimated_distance_km)

        # Save the delivery request with the logged-in user as the client
        serializer.save(client=user, estimated_delivery_time=estimated_delivery_time, status='Pending')

    def calculate_estimated_time(self, distance_km):
        # Example logic to calculate estimated delivery time
        # Here we add 10 minutes for every kilometer
        from datetime import timedelta
        return timezone.now() + timedelta(minutes=int(distance_km * 10))

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)