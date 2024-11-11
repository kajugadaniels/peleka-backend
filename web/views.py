from system.models import *
from web.serializers import *
from web.serializers import *
# from account.serializers import *
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework import generics, permissions, status

class RegisterView(generics.CreateAPIView):
    """
    View to register a new user without restrictions. Accessible to any user.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]  # Allow any user to access this view

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

