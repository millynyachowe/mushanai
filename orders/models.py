from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal

User = get_user_model()


class Cart(models.Model):
    """
    Shopping cart for customers
    """
    customer = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart', limit_choices_to={'user_type': 'CUSTOMER'})
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_abandoned = models.BooleanField(default=False)
    abandoned_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Cart for {self.customer.username}"
    
    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())
    
    @property
    def item_count(self):
        return self.items.count()


class CartItem(models.Model):
    """
    Items in shopping cart
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['cart', 'product']
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name} in {self.cart.customer.username}'s cart"
    
    @property
    def subtotal(self):
        return self.product.price * self.quantity


class Order(models.Model):
    """
    Customer orders
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
        ('REFUNDED', 'Refunded'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('PARTIAL', 'Partially Paid'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]
    
    # Order identification
    order_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', limit_choices_to={'user_type': 'CUSTOMER'})
    
    # Project voting
    selected_project = models.ForeignKey('projects.CommunityProject', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    is_default_vote = models.BooleanField(default=False)  # Whether default vote was used
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    total = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    
    # Shipping
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_country = models.CharField(max_length=100, default='Zimbabwe')
    shipping_phone = models.CharField(max_length=20)
    
    # Payment
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    
    # Fiscalization
    fiscal_receipt_number = models.CharField(max_length=100, blank=True, null=True)
    fiscal_receipt_data = models.JSONField(blank=True, null=True)  # Store ZIMRA fiscal data
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['order_number']),
            models.Index(fields=['payment_status', 'status']),
        ]
    
    def __str__(self):
        return f"Order {self.order_number} - {self.customer.username}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate unique order number
            from datetime import datetime
            import random
            if not self.pk:
                super().save(*args, **kwargs)  # Save first to get an ID
            self.order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{self.id}-{random.randint(1000, 9999)}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """
    Individual items in an order
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True, related_name='order_items')
    vendor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='order_items', limit_choices_to={'user_type': 'VENDOR'})
    product_name = models.CharField(max_length=200)  # Store name in case product is deleted
    product_sku = models.CharField(max_length=100, blank=True, null=True)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])  # Price at time of order
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"{self.quantity}x {self.product_name} in Order {self.order.order_number}"


class OrderPaymentSubmission(models.Model):
    """
    Payment details submitted by customer for an order (per vendor)
    """
    PAYMENT_TYPE_CHOICES = [
        ('CASH_ON_DELIVERY', 'Cash on Delivery'),
        ('ECOCASH', 'EcoCash'),
        ('ONEMONEY', 'OneMoney'),
        ('INNBUCKS', 'InnBucks'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payment_submissions')
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_payments', limit_choices_to={'user_type': 'VENDOR'}, null=True, blank=True)
    payment_type = models.CharField(max_length=30, choices=PAYMENT_TYPE_CHOICES)
    payment_phone = models.CharField(max_length=50, blank=True, null=True)
    payer_name = models.CharField(max_length=200, help_text='Name that appears on the payment transaction')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    proof_of_payment = models.FileField(upload_to='payments/', blank=True, null=True)
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending Confirmation'),
        ('ACKNOWLEDGED', 'Acknowledged by Vendor'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    submitted_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"Payment for Order {self.order.order_number}"
