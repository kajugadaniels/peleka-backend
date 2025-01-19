from transactions.models import *
from transactions.serializers import *
from rest_framework import generics, permissions

class TransactionListView(generics.ListAPIView):
    queryset = Transaction.objects.all().order_by('-created_at')
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
