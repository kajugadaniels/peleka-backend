from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('system.urls')),
    path('api/auth/', include('account.urls')),
]
