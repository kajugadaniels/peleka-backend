from django.urls import path
from django.conf import settings
from web.views import *
from django.conf.urls.static import static

app_name = 'web'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('riders/', RiderListView.as_view(), name='getRiders'),
    path('rider/<int:pk>/', RiderDetailView.as_view(), name='getRiderDetails'),


    path('delivery-requests/', UserDeliveryRequestListView.as_view(), name='userDeliveryRequestList'),
    path('delivery-request/', UserDeliveryRequestCreateView.as_view(), name='userDeliveryRequestCreate'),
    path('delivery-request/<int:pk>/', UserDeliveryRequestDetailView.as_view(), name='userDeliveryRequestDetail'),
    path('delivery-request/update/<int:pk>/', UserDeliveryRequestUpdateView.as_view(), name='userDeliveryRequestUpdate'),
    path('delivery-request/delete/<int:pk>/', UserDeleteDeliveryRequestView.as_view(), name='userDeliveryRequestDelete'),
]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)