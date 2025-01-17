from wallet.models import *
from wallet.serializers import *
from rest_framework.response import Response
from rest_framework import generics, permissions

class WalletDetailView(generics.RetrieveAPIView):
    """
    Retrieve wallet details for the authenticated user.
    """
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Assuming each user has exactly one wallet.
        return self.request.user.wallet

class WalletTransactionListView(generics.ListAPIView):
    """
    List all wallet transactions for the authenticated user.
    """
    serializer_class = WalletTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.wallet.transactions.all().order_by('-created_at')