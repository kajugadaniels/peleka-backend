from django.urls import path
from django.conf import settings
from web.views import *
from django.conf.urls.static import static

app_name = 'web'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile-update/', UpdateUserView.as_view(), name='update'),

    path('riders/login/', RiderCodeSearchView.as_view(), name='rider-login'),
    path('riders/', RiderListView.as_view(), name='getRiders'),
    path('rider/<int:pk>/', RiderDetailView.as_view(), name='getRiderDetails'),

    path('contact-us/', ContactUsView.as_view(), name='contact-us'),

    path('delivery-requests/', UserDeliveryRequestListView.as_view(), name='userDeliveryRequestList'),
    path('delivery-request/', UserDeliveryRequestCreateView.as_view(), name='userDeliveryRequestCreate'),
    path('delivery-request/<int:pk>/', UserDeliveryRequestDetailView.as_view(), name='userDeliveryRequestDetail'),
    path('delivery-request/update/<int:pk>/', UserDeliveryRequestUpdateView.as_view(), name='userDeliveryRequestUpdate'),
    path('delivery-request/delete/<int:pk>/', UserDeleteDeliveryRequestView.as_view(), name='userDeliveryRequestDelete'),
    
    path('book-riders/', UserBookRiderListView.as_view(), name='userBookRiderList'),
    path('book-rider/', UserBookRiderCreateView.as_view(), name='userBookRiderCreate'),
    path('book-rider/<int:pk>/', UserBookRiderDetailView.as_view(), name='userBookRiderDetail'),
    path('book-rider/update/<int:pk>/', UserBookRiderUpdateView.as_view(), name='userBookRiderUpdate'),
    path('book-rider/delete/<int:pk>/', UserDeleteBookRiderView.as_view(), name='userBookRiderDelete'),
    path('book-rider/cancel/<int:pk>/', UserCancelBookRiderView.as_view(), name='userCancelBookRider'),
    path('book-rider/complete/<int:pk>/', UserCompleteBookRiderView.as_view(), name='userCompleteBookRider'),

    path('rider-delivery/<int:pk>/set-in-progress/', SetRiderDeliveryInProgressView.as_view(), name='setRiderDeliveryInProgress'),
    path('book-rider-assignment/<int:pk>/set-in-progress/', SetBookRiderAssignmentInProgressView.as_view(), name='setBookRiderAssignmentInProgress'),
]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)