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

    path('book-riders/', BookRiderListView.as_view(), name='bookRiderList'),
    path('book-rider/', BookRiderCreateView.as_view(), name='bookRiderCreate'),
    path('book-rider/<int:pk>/', BookRiderDetailView.as_view(), name='bookRiderDetail'),
    path('book-rider/update/<int:pk>/', BookRiderUpdateView.as_view(), name='updateBookRider'),
    path('book-rider/delete/<int:pk>/', DeleteBookRiderView.as_view(), name='deleteBookRider'),
    path('book-rider/<int:pk>/complete/', CompleteBookRiderView.as_view(), name='completeRiderBook'),

    path('book-rider-assignments/', BookRiderAssignmentListView.as_view(), name='bookRiderAssignmentList'),
    path('book-rider-assignment/', AddBookRiderAssignmentView.as_view(), name='addBookRiderAssignment'),
    path('book-rider-assignment/<int:pk>/', BookRiderAssignmentDetailView.as_view(), name='bookRiderAssignmentDetail'),
    path('book-rider-assignment/update/<int:pk>/', UpdateBookRiderAssignmentView.as_view(), name='updateBookRiderAssignment'),
    path('book-rider-assignment/delete/<int:pk>/', DeleteBookRiderAssignmentView.as_view(), name='deleteBookRiderAssignment'),
    path('book-rider-assignment/<int:pk>/complete/', CompleteBookRiderAssignmentView.as_view(), name='completeBookRiderAssignment'),
]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)