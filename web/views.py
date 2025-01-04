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
        if not serializer.is_valid():
            # Log the serializer errors
            logger.warning(f"Login failed due to serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email_or_phone = serializer.validated_data['email_or_phone']
        password = serializer.validated_data['password']

        # Determine if the identifier is an email or phone number
        user = None
        if "@" in email_or_phone:
            user = authenticate(username=email_or_phone, password=password)
            if not user:
                logger.warning(f"Login failed for email: {email_or_phone}")
        else:
            try:
                user = User.objects.get(phone_number=email_or_phone)
                if not user.check_password(password):
                    user = None
                    logger.warning(f"Login failed for phone number: {email_or_phone} due to incorrect password.")
            except User.DoesNotExist:
                logger.warning(f"Login failed: No user found with phone number: {email_or_phone}")

        if user:
            # Delete old token and generate a new one
            Token.objects.filter(user=user).delete()
            token, created = Token.objects.get_or_create(user=user)

            logger.info(f"User {user.email or user.phone_number} logged in successfully.")

            return Response({
                'token': token.key,
                'user': UserSerializer(user).data,
                'message': 'Login successful.'
            }, status=status.HTTP_200_OK)
        
        # For security, do not specify if it's the identifier or password that's wrong
        return Response({'error': 'Invalid credentials.'}, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email_or_phone = serializer.validated_data['email_or_phone']
            user = User.objects.filter(Q(email=email_or_phone) | Q(phone_number=email_or_phone)).first()

            if not user:
                logger.warning(f"Password reset requested for non-existent identifier: {email_or_phone}")
                return Response(
                    {'error': 'User with this email or phone number does not exist.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Generate a 7-digit OTP
            otp = generate_otp()
            user.reset_otp = otp
            user.otp_created_at = timezone.now()
            user.save()

            # Send OTP via Email or SMS
            if user.email and user.email == email_or_phone:
                # Send Email
                subject = 'Password Reset OTP'
                message = f'Your password reset OTP is: {otp}'
                recipient_list = [user.email]
                email_sent = send_email(subject, message, recipient_list)
                if email_sent:
                    logger.info(f"Password reset OTP sent to email: {user.email}")
                    return Response(
                        {'message': 'OTP has been sent to your email.'},
                        status=status.HTTP_200_OK
                    )
                else:
                    logger.error(f"Failed to send OTP email to {user.email}")
                    return Response(
                        {'error': 'Failed to send OTP email. Please try again later.'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            elif user.phone_number and user.phone_number == email_or_phone:
                # Send SMS
                message = f'Your password reset OTP is: {otp}'
                sms_sent = send_sms(user.phone_number, message)
                if sms_sent:
                    logger.info(f"Password reset OTP sent to phone number: {user.phone_number}")
                    return Response(
                        {'message': 'OTP has been sent to your phone number.'},
                        status=status.HTTP_200_OK
                    )
                else:
                    logger.error(f"Failed to send OTP SMS to {user.phone_number}")
                    return Response(
                        {'error': 'Failed to send OTP SMS. Please try again later.'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            else:
                logger.warning(f"Provided contact information does not match for user ID: {user.id}")
                return Response(
                    {'error': 'Provided contact information does not match our records.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            logger.warning(f"Password reset request failed with errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                logger.info(f"Password reset successful for user: {user.email or user.phone_number}")
                return Response({'message': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)
            except ValidationError as ve:
                logger.error(f"Validation error during password reset confirmation: {ve}")
                return Response({
                    "message": "Password reset failed.",
                    "errors": ve.detail
                }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"Unexpected error during password reset confirmation: {e}")
                return Response({
                    "message": "Password reset failed due to an unexpected error.",
                    "errors": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logger.warning(f"Password reset confirmation failed with errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            if hasattr(request.user, 'auth_token'):
                request.user.auth_token.delete()
            return Response({
                "message": "Logout successful."
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": f"An error occurred during logout: {str(e)}"
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
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "user": serializer.data,
            "message": "Account updated successfully."
        }, status=status.HTTP_200_OK)

class RiderCodeSearchView(APIView):
    """
    API view to search for a rider using their unique code.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        serializer = RiderCodeSearchSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

class ContactUsView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ContactUsSerializer(data=request.data)
        if serializer.is_valid():
            contact = serializer.save()
            # Prepare email
            subject = f"New Contact Us Submission: {contact.subject}"
            message = f"""
            You have received a new contact us message.

            Name: {contact.name}
            Email: {contact.email}
            Subject: {contact.subject}
            Message:
            {contact.message}

            Submitted at: {contact.submitted_at}
            """
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [settings.CONTACT_EMAIL]

            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=from_email,
                    recipient_list=recipient_list,
                    fail_silently=False,
                )
                return Response({"detail": "Your message has been sent successfully."}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"detail": f"Failed to send email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

class UserDeleteDeliveryRequestView(generics.DestroyAPIView):
    """
    API view to delete a Delivery Request for the logged-in user.
    - Accessible only to authenticated users.
    """
    serializer_class = UserDeliveryRequestSerializer
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

class SetRiderDeliveryInProgressView(APIView):
    """
    API view to set the 'in_progress_at' field of a RiderDelivery to the current time
    and update the related DeliveryRequest status to 'In Progress'.
    - Accessible to any user without authentication or specific permissions.
    """
    permission_classes = [AllowAny]  # Allow access to any user

    @transaction.atomic
    def post(self, request, pk, *args, **kwargs):
        """
        Set 'in_progress_at' for the RiderDelivery with the given pk and update
        the related DeliveryRequest status to 'In Progress' with validations:
        
        - DeliveryRequest.status must be 'Pending' or 'Accepted' to update to 'In Progress'.
        - If DeliveryRequest.status is 'Completed', do not allow update.
        - RiderDelivery.delivered must be False to allow updating.
        - If RiderDelivery.in_progress_at is already set, do not allow update.
        """
        # Retrieve the RiderDelivery instance along with the related DeliveryRequest
        try:
            rider_delivery = RiderDelivery.objects.select_related('delivery_request').get(pk=pk)
        except RiderDelivery.DoesNotExist:
            raise NotFound({'message': "RiderDelivery not found."})

        delivery_request = rider_delivery.delivery_request

        # Validate if DeliveryRequest exists
        if not delivery_request:
            raise ValidationError({'message': "Associated DeliveryRequest does not exist."})

        # Validate DeliveryRequest status
        if delivery_request.status == 'Completed':
            raise ValidationError({'message': "The delivery has already been completed and cannot be updated."})
        elif delivery_request.status not in ['Pending', 'Accepted']:
            raise ValidationError({'message': f"Cannot update delivery request status from '{delivery_request.status}' to 'In Progress'."})

        # Validate RiderDelivery fields
        if rider_delivery.delivered:
            raise ValidationError({'message': "Cannot update 'in_progress_at' because the delivery has already been completed."})
        
        if rider_delivery.in_progress_at:
            raise ValidationError({'message': "'in_progress_at' has already been set and cannot be updated again."})

        # Update the 'in_progress_at' field to the current time
        rider_delivery.in_progress_at = timezone.now()
        rider_delivery.save()

        # Update the related DeliveryRequest status to 'In Progress'
        delivery_request.status = 'In Progress'
        delivery_request.save()

        # Serialize the updated RiderDelivery instance
        serializer = RiderDeliverySerializer(rider_delivery, context={'request': request})

        return Response({
            'message': "'in_progress_at' set successfully and delivery request status updated to 'In Progress'.",
            'data': serializer.data
        }, status=200)

class UserBookRiderListView(generics.ListAPIView):
    """
    API view to list all BookRider requests for the logged-in user.
    - Accessible only to authenticated users.
    """
    serializer_class = UserBookRiderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only fetch BookRider requests made by the logged-in user
        user = self.request.user
        return BookRider.objects.filter(client=user, delete_status=False).order_by('-created_at')

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class UserBookRiderCreateView(generics.CreateAPIView):
    """
    API view to create a new BookRider request for the logged-in user.
    - Accessible only to authenticated users.
    """
    serializer_class = UserBookRiderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Automatically set the client as the logged-in user
        serializer.save(client=self.request.user, status="Pending")

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class UserBookRiderDetailView(generics.RetrieveAPIView):
    """
    API view to retrieve a BookRider request by ID for the logged-in user.
    - Accessible only to authenticated users.
    """
    serializer_class = UserBookRiderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BookRider.objects.filter(client=self.request.user, delete_status=False)

    def get_object(self):
        try:
            return self.get_queryset().get(pk=self.kwargs['pk'])
        except BookRider.DoesNotExist:
            raise NotFound({'message': "BookRider request not found."})