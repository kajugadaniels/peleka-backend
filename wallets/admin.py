from wallets.models import *
from django.contrib import admin

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'rider', 'rider_total', 'commissioner_total', 'boss_total', 'created_at', 'updated_at')

@admin.register(TransactionHistory)
class TransactionHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'transaction', 'role', 'amount', 'created_at')
