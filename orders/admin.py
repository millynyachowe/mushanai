from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem, OrderPaymentSubmission


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['customer', 'item_count', 'total', 'is_abandoned', 'updated_at']
    list_filter = ['is_abandoned', 'created_at', 'updated_at']
    search_fields = ['customer__username', 'customer__email']
    raw_id_fields = ['customer']
    inlines = [CartItemInline]
    readonly_fields = ['created_at', 'updated_at']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'product_sku', 'subtotal']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'status', 'payment_status', 'total', 'selected_project', 'created_at']
    list_filter = ['status', 'payment_status', 'is_default_vote', 'created_at']
    search_fields = ['order_number', 'customer__username', 'customer__email', 'payment_reference']
    raw_id_fields = ['customer', 'selected_project']
    inlines = [OrderItemInline]
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'delivered_at']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'customer', 'status', 'payment_status')
        }),
        ('Project Voting', {
            'fields': ('selected_project', 'is_default_vote')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'shipping_cost', 'discount_amount', 'total')
        }),
        ('Shipping', {
            'fields': ('shipping_address', 'shipping_city', 'shipping_country', 'shipping_phone')
        }),
        ('Payment', {
            'fields': ('payment_method', 'payment_reference', 'fiscal_receipt_number', 'fiscal_receipt_data')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'delivered_at')
        }),
    )


@admin.register(OrderPaymentSubmission)
class OrderPaymentSubmissionAdmin(admin.ModelAdmin):
    list_display = ['order', 'vendor', 'payment_type', 'amount', 'status', 'submitted_at']
    list_filter = ['payment_type', 'status', 'submitted_at']
    search_fields = ['order__order_number', 'vendor__username', 'payer_name', 'payment_phone']
    raw_id_fields = ['order', 'vendor']
    readonly_fields = ['submitted_at', 'acknowledged_at']
