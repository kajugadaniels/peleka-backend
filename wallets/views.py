from wallets.models import *
from wallets.serializers import *
from rest_framework import generics, permissions

class WalletDetailView(generics.RetrieveAPIView):
    """
    API view for a user to retrieve his/her wallet details and transaction history.
    """
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Expecting a query parameter "type" to determine which wallet to return.
        wallet_type = self.request.query_params.get('type', 'rider')  # default to rider
        # For boss wallet, there is only one; for rider or commissioner, use the linked user.
        return Wallet.objects.filter(owner=self.request.user, wallet_type=wallet_type).first()