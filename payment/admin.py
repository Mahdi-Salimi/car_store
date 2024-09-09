# payment/admin.py
from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'ad', 'amount', 'is_successful', 'transaction_id', 'created_at')
    list_filter = ('is_successful', 'created_at')
    search_fields = ('user__email', 'ad__car__title', 'transaction_id')
    readonly_fields = ('amount', 'is_successful', 'transaction_id', 'created_at')
