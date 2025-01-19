from django.urls import path
from django.conf import settings
from transactions.views import *
from django.conf.urls.static import static

app_name = 'transactions'

urlpatterns = [
    path('', TransactionListView.as_view(), name='transaction_list'),
]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)