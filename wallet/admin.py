from django.contrib import admin
from .models import Wallet, WalletTransaction

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'wallet_type', 'balance', 'created_at', 'updated_at')
    list_filter = ('wallet_type', 'created_at')
    search_fields = ('user__email', 'user__username',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    fieldsets = (
        (None, {
            'fields': ('user', 'wallet_type', 'balance')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
