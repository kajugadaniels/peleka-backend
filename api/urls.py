from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('system.urls')),
    path('api/web/', include('web.urls')),
    path('api/auth/', include('account.urls')),
    path('api/wallet/', include('wallet.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)