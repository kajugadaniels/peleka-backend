from django.contrib import admin
from .models import Wallet, WalletTransaction

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'wallet_type', 'balance', 'created_at', 'updated_at')
    list_filter = ('wallet_type', 'created_at')
    search_fields = ('owner__username', 'owner__email')
    ordering = ('-created_at',)
    # Commit: git commit -m "Register Wallet model in admin with list_display, filters, and search_fields"

@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'wallet', 'transaction_type', 'amount', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('wallet__owner__username', 'wallet__owner__email', 'description')
    ordering = ('-created_at',)
    # Commit: git commit -m "Register WalletTransaction model in admin with list_display, filters, and search_fields"
