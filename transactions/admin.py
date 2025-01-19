from .models import *
from django.contrib import admin

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'rider', 'commissioner', 'boss',
        'rider_total', 'commissioner_total', 'boss_total', 'created_at'
    )
    ordering = ('-created_at',)

@admin.register(TransactionHistory)
class TransactionHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'transaction', 'delivery_request',
        'rider_amount', 'commissioner_amount', 'boss_amount', 'created_at'
    )
    ordering = ('-created_at',)
