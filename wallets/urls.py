from django.urls import path
from django.conf import settings
from wallets.views import *
from django.conf.urls.static import static

app_name = 'wallet'

urlpatterns = [
    # 
]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)