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
]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)