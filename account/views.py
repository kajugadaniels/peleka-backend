from account.serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.generics import GenericAPIView
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated, AllowAny

class LoginView(GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            return Response({
                'error': 'Login failed due to invalid input.',
                'details': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = authenticate(username=email, password=password)

        if user:
            # Delete old token and generate a new one
            Token.objects.filter(user=user).delete()
            token, created = Token.objects.get_or_create(user=user)

            return Response({
                'token': token.key,
                'user': UserSerializer(user, context={'request': request}).data,
                'message': f'Login successful. Welcome back, {user.name}!'
            }, status=status.HTTP_200_OK)
        else:
            # Check if user exists
            user_exists = User.objects.filter(email=email).exists()
            if not user_exists:
                error_detail = 'No account found with the provided email.'
            else:
                error_detail = 'Incorrect password. Please try again.'

            return Response({
                'error': 'Authentication failed.',
                'details': error_detail
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