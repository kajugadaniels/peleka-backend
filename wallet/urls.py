from wallet import views
from django.urls import path

app_name = 'wallet'

urlpatterns = [
    path('detail/', views.WalletDetailView.as_view(), name='detail'),
    path('transactions/', views.WalletTransactionListView.as_view(), name='transactions'),
]
