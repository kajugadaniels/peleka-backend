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
]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)