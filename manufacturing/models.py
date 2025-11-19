from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal

User = get_user_model()


class BillOfMaterials(models.Model):
    """
    Product Recipe - What materials are needed to make a product
    """
    product = models.OneToOneField('products.Product', on_delete=models.CASCADE, related_name='bom')
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='boms', limit_choices_to={'user_type': 'VENDOR'})
    
    # Production info
    batch_size = models.DecimalField(max_digits=10, decimal_places=2, default=1, help_text='How many units this recipe makes')
    production_time_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text='Time needed to produce one batch')
    
    # Costing (auto-calculated)
    total_material_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    labor_cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Optional labor cost')
    overhead_cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Optional overhead')
    total_cost_per_unit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Suggested pricing
    markup_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=50, help_text='Suggested markup %')
    suggested_selling_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Notes
    instructions = models.TextField(blank=True, null=True, help_text='Production instructions')
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Bill of Materials'
        verbose_name_plural = 'Bills of Materials'
        ordering = ['product__name']
    
    def __str__(self):
        return f"BOM: {self.product.name}"
    
    def calculate_costs(self):
        """Calculate all costs based on materials"""
        # Material costs
        material_cost = sum(
            item.quantity * (item.raw_material.unit_price if item.raw_material else 0)
            for item in self.items.all()
        )
        self.total_material_cost = material_cost / self.batch_size if self.batch_size else material_cost
        
        # Total cost per unit
        self.total_cost_per_unit = self.total_material_cost + self.labor_cost_per_unit + self.overhead_cost_per_unit
        
        # Suggested selling price
        markup_multiplier = 1 + (self.markup_percentage / 100)
        self.suggested_selling_price = self.total_cost_per_unit * Decimal(str(markup_multiplier))
        
        self.save()
        return self.total_cost_per_unit
    
    def check_materials_available(self, quantity=1):
        """Check if enough materials are available for production"""
        batches_needed = quantity / self.batch_size if self.batch_size else quantity
        
        for item in self.items.all():
            required_qty = item.quantity * Decimal(str(batches_needed))
            # Here you would check against inventory
            # For now, just return True
        return True


class BOMItem(models.Model):
    """
    Individual materials in a product recipe
    """
    bom = models.ForeignKey(BillOfMaterials, on_delete=models.CASCADE, related_name='items')
    raw_material = models.ForeignKey('suppliers.RawMaterial', on_delete=models.PROTECT, related_name='bom_usage')
    
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    unit = models.CharField(max_length=50, help_text='kg, meters, pieces, etc.')
    
    # Notes
    notes = models.CharField(max_length=200, blank=True, null=True, help_text='e.g., "Cut into 10cm pieces"')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"{self.raw_material.name} - {self.quantity}{self.unit}"
    
    @property
    def cost(self):
        return self.quantity * self.raw_material.unit_price


class ManufacturingOrder(models.Model):
    """
    Production Order - Make X units of a product
    """
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('READY', 'Ready to Start'),
        ('IN_PROGRESS', 'In Progress'),
        ('QUALITY_CHECK', 'Quality Check'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    mo_number = models.CharField(max_length=100, unique=True, db_index=True)
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='manufacturing_orders', limit_choices_to={'user_type': 'VENDOR'})
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT, related_name='manufacturing_orders')
    bom = models.ForeignKey(BillOfMaterials, on_delete=models.PROTECT, related_name='orders')
    
    # Order details
    quantity_to_produce = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    quantity_produced = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity_approved = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity_rejected = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    priority = models.CharField(max_length=20, choices=[('LOW', 'Low'), ('NORMAL', 'Normal'), ('HIGH', 'High'), ('URGENT', 'Urgent')], default='NORMAL')
    
    # Dates
    scheduled_date = models.DateField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Costing
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    actual_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Notes
    production_notes = models.TextField(blank=True, null=True)
    
    # Community impact
    local_materials_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['vendor', 'status']),
            models.Index(fields=['status', 'scheduled_date']),
        ]
    
    def __str__(self):
        return f"{self.mo_number} - {self.product.name}"
    
    def save(self, *args, **kwargs):
        if not self.mo_number:
            from django.utils import timezone
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            self.mo_number = f"MO-{self.vendor.id}-{timestamp}"
        
        # Calculate estimated cost
        if self.bom:
            self.estimated_cost = self.bom.total_cost_per_unit * self.quantity_to_produce
        
        super().save(*args, **kwargs)
    
    def start_production(self):
        """Start the manufacturing order"""
        from django.utils import timezone
        self.status = 'IN_PROGRESS'
        self.started_at = timezone.now()
        self.save()
    
    def complete_production(self):
        """Complete the manufacturing order and update inventory"""
        from django.utils import timezone
        self.status = 'COMPLETED'
        self.completed_at = timezone.now()
        self.quantity_produced = self.quantity_to_produce
        self.save()
        
        # Update product inventory
        if self.product.track_inventory:
            self.product.stock_quantity += int(self.quantity_approved)
            self.product.save()
    
    def calculate_local_percentage(self):
        """Calculate percentage of locally sourced materials"""
        if not self.bom:
            return 0
        
        total_items = self.bom.items.count()
        if total_items == 0:
            return 0
        
        local_items = self.bom.items.filter(raw_material__is_locally_sourced=True).count()
        self.local_materials_percentage = (local_items / total_items) * 100
        self.save()
        return self.local_materials_percentage


class QualityCheck(models.Model):
    """
    Simple quality check for manufactured products
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('REWORK', 'Needs Rework'),
    ]
    
    manufacturing_order = models.ForeignKey(ManufacturingOrder, on_delete=models.CASCADE, related_name='quality_checks')
    checked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='quality_checks_performed')
    
    quantity_checked = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_approved = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity_rejected = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    rejection_reason = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    checked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-checked_at']
    
    def __str__(self):
        return f"QC: {self.manufacturing_order.mo_number} - {self.status}"


class ProductionWorker(models.Model):
    """
    Track workers involved in production (for job creation stats)
    """
    manufacturing_order = models.ForeignKey(ManufacturingOrder, on_delete=models.CASCADE, related_name='workers')
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='production_work')
    
    worker_name = models.CharField(max_length=200)
    role = models.CharField(max_length=100, blank=True, null=True, help_text='e.g., Craftsman, Assembly, Packaging')
    
    hours_worked = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    total_payment = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    notes = models.TextField(blank=True, null=True)
    work_date = models.DateField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-work_date']
    
    def __str__(self):
        return f"{self.worker_name} - {self.manufacturing_order.mo_number}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate payment
        if self.hours_worked and self.hourly_rate:
            self.total_payment = self.hours_worked * self.hourly_rate
        super().save(*args, **kwargs)


class ManufacturingAnalytics(models.Model):
    """
    Monthly analytics for vendors (auto-generated)
    """
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='manufacturing_analytics')
    month = models.DateField()
    
    # Production
    total_orders = models.PositiveIntegerField(default=0)
    total_units_produced = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_production_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Materials
    local_materials_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_material_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Jobs
    total_workers = models.PositiveIntegerField(default=0)
    total_hours_worked = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_wages_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Community impact
    community_contribution = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text='1% of production value')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['vendor', 'month']
        ordering = ['-month']
        verbose_name_plural = 'Manufacturing Analytics'
    
    def __str__(self):
        return f"{self.vendor.username} - {self.month.strftime('%B %Y')}"

