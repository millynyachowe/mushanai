from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class SupplierProfile(models.Model):
    """
    Profiles for raw material suppliers (manually added by admin)
    """
    supplier = models.OneToOneField(User, on_delete=models.CASCADE, related_name='supplier_profile', limit_choices_to={'user_type': 'SUPPLIER'})
    company_name = models.CharField(max_length=200)
    brand_name = models.CharField(max_length=200, blank=True, null=True)
    contact_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # Supplier details
    description = models.TextField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    
    # Admin managed
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='suppliers_added', limit_choices_to={'user_type': 'ADMIN'})
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'supplier_profiles'
        ordering = ['company_name']
    
    def __str__(self):
        return f"{self.company_name} - {self.contact_number}"


class RawMaterialCategory(models.Model):
    """
    Categories for raw materials
    """
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Raw Material Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class RawMaterial(models.Model):
    """
    Raw materials available from suppliers (requires admin approval)
    """
    APPROVAL_STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    detailed_description = models.TextField(blank=True, null=True)
    
    # Relationships
    supplier = models.ForeignKey(SupplierProfile, on_delete=models.CASCADE, related_name='raw_materials')
    category = models.ForeignKey(RawMaterialCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='materials')
    
    # Approval System
    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default='PENDING')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_materials', limit_choices_to={'user_type': 'ADMIN'})
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    # Sustainability and origin
    origin = models.CharField(max_length=200, blank=True, null=True)  # Where it's sourced from
    is_locally_sourced = models.BooleanField(default=True)
    sustainability_info = models.TextField(blank=True, null=True)  # Sustainability details
    environmental_impact = models.TextField(blank=True, null=True)
    
    # Pricing and availability
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50, default='kg')  # kg, liters, pieces, etc.
    min_order_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    stock_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_available = models.BooleanField(default=True)
    
    # Usage tracking (for ministry analytics)
    usage_count = models.PositiveIntegerField(default=0)  # Track how often used in manufacturing
    purchase_count = models.PositiveIntegerField(default=0)  # Track purchase frequency
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Display
    image = models.ImageField(upload_to='raw_materials/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    
    # Access control - hidden page/portal
    is_hidden = models.BooleanField(default=False)  # Only accessible via suppliers module
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['is_available', 'is_locally_sourced']),
            models.Index(fields=['supplier', 'is_available']),
            models.Index(fields=['approval_status', 'is_available']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.supplier.company_name}"
    
    @property
    def is_approved(self):
        return self.approval_status == 'APPROVED'


class MaterialUsage(models.Model):
    """
    Track which materials are used in products (for ministry analytics)
    """
    material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE, related_name='usage_records')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='material_usage')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    unit = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['material', 'product']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.material.name} used in {self.product.name}"


class RawMaterialPurchase(models.Model):
    """
    Track purchases of raw materials by vendors
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
    ]
    
    # Purchase details
    purchase_number = models.CharField(max_length=100, unique=True, db_index=True)
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='raw_material_purchases', limit_choices_to={'user_type': 'VENDOR'})
    material = models.ForeignKey(RawMaterial, on_delete=models.PROTECT, related_name='purchases')
    supplier = models.ForeignKey(SupplierProfile, on_delete=models.PROTECT, related_name='sales')
    
    # Order details
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    
    # Delivery
    delivery_address = models.TextField()
    delivery_city = models.CharField(max_length=100)
    delivery_phone = models.CharField(max_length=50)
    
    # Notes
    vendor_notes = models.TextField(blank=True, null=True)
    supplier_notes = models.TextField(blank=True, null=True)
    admin_notes = models.TextField(blank=True, null=True)
    
    # Timestamps
    ordered_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-ordered_at']
        indexes = [
            models.Index(fields=['vendor', 'status']),
            models.Index(fields=['supplier', 'status']),
            models.Index(fields=['payment_status', 'status']),
        ]
    
    def __str__(self):
        return f"{self.purchase_number} - {self.vendor.username}"
    
    def save(self, *args, **kwargs):
        if not self.purchase_number:
            from django.utils import timezone
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            self.purchase_number = f"RMP-{self.vendor.id}-{timestamp}"
        super().save(*args, **kwargs)


class RawMaterialInquiry(models.Model):
    """
    Inquiries/contact requests from vendors to suppliers
    """
    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('READ', 'Read'),
        ('REPLIED', 'Replied'),
        ('CLOSED', 'Closed'),
    ]
    
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='material_inquiries', limit_choices_to={'user_type': 'VENDOR'})
    material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE, related_name='inquiries')
    supplier = models.ForeignKey(SupplierProfile, on_delete=models.CASCADE, related_name='inquiries')
    
    # Inquiry details
    subject = models.CharField(max_length=200)
    message = models.TextField()
    vendor_email = models.EmailField()
    vendor_phone = models.CharField(max_length=50)
    
    # Response
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    supplier_response = models.TextField(blank=True, null=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Raw Material Inquiries'
    
    def __str__(self):
        return f"{self.subject} - {self.vendor.username}"
