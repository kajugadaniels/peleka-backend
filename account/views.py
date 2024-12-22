import logging
from web.utils import *
from system.models import *
from web.serializers import *
from django.db.models import Q
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.exceptions import NotFound
from rest_framework.authtoken.models import Token
from rest_framework.generics import GenericAPIView
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated, AllowAny

logger = logging.getLogger(__name__)

class LoginView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            logger.warning(f"Login failed due to validation errors: {e.detail}")
            return Response({
                'error': 'Login failed due to invalid input.',
                'details': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)

        email_or_phone = serializer.validated_data['email_or_phone']
        password = serializer.validated_data['password']

        # Determine if the identifier is an email or phone number
        user = None
        if "@" in email_or_phone:
            user = authenticate(username=email_or_phone, password=password)
            if user:
                logger.info(f"User {user.email} logged in successfully.")
            else:
                logger.warning(f"Login failed for email: {email_or_phone}. Incorrect credentials.")
        else:
            try:
                user = User.objects.get(phone_number=email_or_phone)
                if user.check_password(password):
                    logger.info(f"User with phone number {email_or_phone} logged in successfully.")
                else:
                    user = None
                    logger.warning(f"Login failed for phone number: {email_or_phone}. Incorrect password.")
            except User.DoesNotExist:
                logger.warning(f"Login failed: No user found with phone number: {email_or_phone}")

        if user:
            # Delete old token and generate a new one
            Token.objects.filter(user=user).delete()
            token, created = Token.objects.get_or_create(user=user)

            return Response({
                'token': token.key,
                'user': UserSerializer(user).data,
                'message': f'Login successful. Welcome back, {user.name}!'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'error': 'Authentication failed. Please check your email/phone number and password.'
        }, status=status.HTTP_401_UNAUTHORIZED)

class RegisterView(generics.CreateAPIView):
    """
    View to register a new user. Accessible to any user.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "message": f"User '{user.name}' registered successfully.",
                "user": UserSerializer(user, context={'request': request}).data,
                "token": token.key
            }, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            return Response({
                "error": "User registration failed due to invalid input.",
                "details": e.detail
            }, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            if hasattr(request.user, 'auth_token'):
                request.user.auth_token.delete()
                return Response({
                    "message": "Logout successful. Your session has been terminated."
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "warning": "No active session found to logout."
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "error": f"An unexpected error occurred during logout: {str(e)}. Please try again later."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateUserView(generics.UpdateAPIView):
    """
    API view to update user profile details.
    - Automatically hashes the password if updated.
    """
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        """
        Retrieve the current user instance.
        """
        return self.request.user

    def update(self, request, *args, **kwargs):
        """
        Update user details, including password, if provided.
        """
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response({
                "message": "Your account has been updated successfully.",
                "user": serializer.data
            }, status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            return Response({
                "error": "Account update failed due to invalid input.",
                "details": e.detail
            }, status=status.HTTP_400_BAD_REQUEST)