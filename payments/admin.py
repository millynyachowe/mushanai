from django.contrib import admin
from .models import PaymentMethod, PaymentTransaction, FiscalReceipt, PaymentWebhook


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'payment_type', 'is_active', 'supports_fiscalization', 'created_at']
    list_filter = ['payment_type', 'is_active', 'supports_fiscalization', 'created_at']
    search_fields = ['name', 'description']


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ['payment_reference', 'order', 'payment_method', 'amount', 'status', 'is_fiscalized', 'created_at']
    list_filter = ['status', 'is_fiscalized', 'payment_method', 'created_at']
    search_fields = ['payment_reference', 'external_transaction_id', 'order__order_number', 'payer_phone', 'payer_email']
    raw_id_fields = ['order', 'payment_method']
    readonly_fields = ['payment_reference', 'created_at', 'updated_at', 'initiated_at', 'completed_at']


@admin.register(FiscalReceipt)
class FiscalReceiptAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'payment_transaction', 'order', 'status', 'fiscal_number', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['receipt_number', 'fiscal_number', 'zimra_tax_invoice', 'order__order_number']
    raw_id_fields = ['payment_transaction', 'order']
    readonly_fields = ['created_at', 'updated_at', 'submitted_at', 'approved_at']


@admin.register(PaymentWebhook)
class PaymentWebhookAdmin(admin.ModelAdmin):
    list_display = ['payment_method', 'is_processed', 'created_at', 'processed_at']
    list_filter = ['is_processed', 'payment_method', 'created_at']
    search_fields = ['payment_transaction__payment_reference']
    raw_id_fields = ['payment_transaction', 'payment_method']
    readonly_fields = ['created_at', 'processed_at']
