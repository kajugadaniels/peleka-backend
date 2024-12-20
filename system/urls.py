from django.urls import path
from django.conf import settings
from system.views import *
from django.conf.urls.static import static

app_name = 'system'

urlpatterns = [
    path('roles/', RoleListCreateView.as_view(), name='RoleListCreate'),
    path('roles/<int:pk>/', RoleRetrieveUpdateDestroyView.as_view(), name='RoleRetrieveUpdateDelete'),

    path('permissions/', PermissionListView.as_view(), name='permissionList'),
    path('assign-permission/', AssignPermissionView.as_view(), name='assignPermission'),
    path('remove-permission/', RemovePermissionView.as_view(), name='removePermission'),
    path('permissions/<int:user_id>/', UserPermissionsView.as_view(), name='userPermissions'),

    path('users/', UserListView.as_view(), name='UserList'),
    path('user/<int:user_id>/', UserDetailView.as_view(), name='UserDetail'),

    path('riders/', RiderListCreateView.as_view(), name='RiderListCreate'),
    path('riders/<int:pk>/', RiderRetrieveUpdateDeleteView.as_view(), name='RiderRetrieveUpdateDelete'),

    path('delivery-requests/', DeliveryRequestListView.as_view(), name='deliveryRequestList'),
    path('delivery-request/', DeliveryRequestCreateView.as_view(), name='deliveryRequest'),
    path('delivery-request/<int:pk>/', DeliveryRequestDetailView.as_view(), name='deliveryRequestDetail'),
    path('delivery-request/update/<int:pk>/', DeliveryRequestUpdateView.as_view(), name='updateDeliveryRequest'),
    path('delivery-request/delete/<int:pk>/', DeleteDeliveryRequestView.as_view(), name='deleteDeliveryRequest'),
    path('delivery-request/<int:pk>/complete/', CompleteDeliveryRequestView.as_view(), name='completeDeliveryRequest'),

    path('rider-deliveries/', RiderDeliveryListView.as_view(), name='riderDeliveryList'),
    path('rider-delivery/', AddRiderDeliveryView.as_view(), name='addRiderDelivery'),
    path('rider-delivery/<int:pk>/', RiderDeliveryDetailView.as_view(), name='riderDeliveryDetail'),
    path('rider-delivery/<int:pk>/set-in-progress/', SetRiderDeliveryInProgressView.as_view(), name='setRiderDeliveryInProgress'),
]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)