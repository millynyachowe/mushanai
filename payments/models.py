from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()


class PaymentMethod(models.Model):
    """
    Available payment methods (EcoCash, TeleCash, etc.)
    """
    PAYMENT_TYPE_CHOICES = [
        ('ECOCASH', 'EcoCash'),
        ('TELECASH', 'TeleCash'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('CARD', 'Credit/Debit Card'),
        ('CASH', 'Cash on Delivery'),
        ('OTHER', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    is_active = models.BooleanField(default=True)
    requires_verification = models.BooleanField(default=True)
    
    # Configuration
    merchant_code = models.CharField(max_length=100, blank=True, null=True)
    api_key = models.CharField(max_length=200, blank=True, null=True)
    api_secret = models.CharField(max_length=200, blank=True, null=True)
    webhook_url = models.URLField(blank=True, null=True)
    
    # Settings
    supports_fiscalization = models.BooleanField(default=True)  # ZIMRA fiscal compliance
    processing_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    processing_fee_fixed = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    
    description = models.TextField(blank=True, null=True)
    instructions = models.TextField(blank=True, null=True)  # Instructions for customers
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class PaymentTransaction(models.Model):
    """
    Payment transactions for orders
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
        ('REFUNDED', 'Refunded'),
    ]
    
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='payment_transactions')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, related_name='transactions')
    
    # Amounts
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    processing_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Payment details
    payment_reference = models.CharField(max_length=100, unique=True)
    external_transaction_id = models.CharField(max_length=100, blank=True, null=True)  # From payment gateway
    payer_phone = models.CharField(max_length=20, blank=True, null=True)  # For mobile money
    payer_email = models.EmailField(blank=True, null=True)
    
    # Response data
    gateway_response = models.JSONField(blank=True, null=True)  # Store full response from gateway
    error_message = models.TextField(blank=True, null=True)
    
    # Fiscalization
    fiscal_receipt_number = models.CharField(max_length=100, blank=True, null=True)
    fiscal_receipt_data = models.JSONField(blank=True, null=True)  # ZIMRA fiscal data
    is_fiscalized = models.BooleanField(default=False)
    fiscalization_error = models.TextField(blank=True, null=True)
    
    # Timestamps
    initiated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order', 'status']),
            models.Index(fields=['payment_reference']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"Payment {self.payment_reference} - {self.status} - {self.amount}"
    
    def save(self, *args, **kwargs):
        if not self.payment_reference:
            from datetime import datetime
            import random
            self.payment_reference = f"PAY-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"
        super().save(*args, **kwargs)


class FiscalReceipt(models.Model):
    """
    Fiscal receipts for ZIMRA compliance
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUBMITTED', 'Submitted to ZIMRA'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('ERROR', 'Error'),
    ]
    
    payment_transaction = models.OneToOneField(PaymentTransaction, on_delete=models.CASCADE, related_name='fiscal_receipt')
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='fiscal_receipts')
    
    # Fiscal details
    receipt_number = models.CharField(max_length=100, unique=True)
    fiscal_number = models.CharField(max_length=100, blank=True, null=True)  # From ZIMRA
    qr_code = models.ImageField(upload_to='fiscal_receipts/qr/', blank=True, null=True)
    
    # ZIMRA data
    zimra_tax_invoice = models.CharField(max_length=100, blank=True, null=True)
    fiscal_data = models.JSONField()  # Complete fiscal data sent/received
    zimra_response = models.JSONField(blank=True, null=True)  # Response from ZIMRA
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    error_message = models.TextField(blank=True, null=True)
    
    # Submission
    submitted_at = models.DateTimeField(blank=True, null=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Fiscal Receipt {self.receipt_number} - {self.status}"


class PaymentWebhook(models.Model):
    """
    Log of payment webhooks received from payment gateways
    """
    payment_transaction = models.ForeignKey(PaymentTransaction, on_delete=models.CASCADE, related_name='webhooks', null=True, blank=True)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, related_name='webhooks')
    
    # Webhook data
    payload = models.JSONField()
    headers = models.JSONField(blank=True, null=True)
    signature = models.CharField(max_length=500, blank=True, null=True)
    
    # Processing
    is_processed = models.BooleanField(default=False)
    processing_error = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Webhook for {self.payment_method} - {self.created_at}"
