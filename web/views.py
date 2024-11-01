from system.models import *
from system.serializers import *
from account.serializers import *
from rest_framework import generics
from rest_framework.permissions import AllowAny

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
