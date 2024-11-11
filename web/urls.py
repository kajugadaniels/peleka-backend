from django.urls import path
from django.conf import settings
from web.views import *
from django.conf.urls.static import static

app_name = 'web'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),

    path('riders/', RiderListView.as_view(), name='getRiders'),
]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)