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