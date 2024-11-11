from system.models import *
from web.serializers import *
from web.serializers import *
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.generics import GenericAPIView
from rest_framework import generics, permissions, status

class LoginView(GenericAPIView):  # Change to GenericAPIView
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = authenticate(username=email, password=password)

        if user:
            # Delete old token and generate a new one
            Token.objects.filter(user=user).delete()
            token, created = Token.objects.get_or_create(user=user)

            return Response({
                'token': token.key,
                'user': UserSerializer(user).data,
                'message': 'Login successful.'
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid email or password.'}, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(generics.CreateAPIView):
    """
    View to register a new user without restrictions. Accessible to any user.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "user": UserSerializer(user, context=self.get_serializer_context()).data,
                "token": token.key,
                "message": "User registered successfully."
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "message": "User registration failed.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

class RiderListView(generics.ListAPIView):
    """
    API view to list all Riders.
    Accessible to anyone.
    """
    queryset = Rider.objects.all()
    serializer_class = RiderSerializer
    permission_classes = [AllowAny]

class RiderDetailView(generics.RetrieveAPIView):
    """
    API view to retrieve Rider details.
    Accessible to anyone.
    """
    queryset = Rider.objects.all()
    serializer_class = RiderSerializer
    permission_classes = [AllowAny]

class UserDeliveryRequestListView(generics.ListAPIView):
    """
    API view to list all Delivery Requests for the logged-in user.
    - Accessible only to authenticated users.
    """
    serializer_class = UserDeliveryRequestSerializer
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
    serializer_class = UserDeliveryRequestSerializer
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
    serializer_class = UserDeliveryRequestSerializer
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