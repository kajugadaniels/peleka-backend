from django.contrib import admin
from account.models import *

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone_number', 'is_active', 'is_staff')
    search_fields = ('name', 'email', 'phone_number')