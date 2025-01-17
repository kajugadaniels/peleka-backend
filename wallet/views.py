from rest_framework import generics, permissions
from rest_framework.response import Response
from wallet.models import Wallet, WalletTransaction
from wallet.serializers import WalletSerializer, WalletTransactionSerializer

class WalletDetailView(generics.RetrieveAPIView):
    """
    Retrieve wallet details for the authenticated user.
    """
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Assuming each user has exactly one wallet.
        return self.request.user.wallet