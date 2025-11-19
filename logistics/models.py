from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()


class DeliveryGroup(models.Model):
    """
    Groups of vendors collaborating for shared deliveries
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('FORMING', 'Forming'),
        ('ACTIVE', 'Active'),
        ('ROUTING', 'Routing'),
        ('IN_TRANSIT', 'In Transit'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    name = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Route information
    origin_address = models.TextField()
    destination_city = models.CharField(max_length=100)
    destination_country = models.CharField(max_length=100, default='Zimbabwe')
    
    # Cost sharing
    total_logistics_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    cost_per_vendor = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    
    # Optimization
    optimized_route = models.TextField(blank=True, null=True)  # JSON field for route details
    estimated_distance = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    estimated_duration = models.IntegerField(blank=True, null=True)  # in minutes
    
    # Dates
    scheduled_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Delivery Group {self.id} - {self.status}"


class SharedDelivery(models.Model):
    """
    Individual vendor participation in shared delivery groups
    """
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_deliveries', limit_choices_to={'user_type': 'VENDOR'})
    delivery_group = models.ForeignKey(DeliveryGroup, on_delete=models.CASCADE, related_name='participants')
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='shared_deliveries', null=True, blank=True)
    
    # Cost allocation
    allocated_cost = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    has_paid = models.BooleanField(default=False)
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    
    # Delivery details
    delivery_address = models.TextField()
    contact_phone = models.CharField(max_length=20)
    
    # Status
    is_confirmed = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['vendor', 'delivery_group', 'order']
        ordering = ['joined_at']
    
    def __str__(self):
        return f"{self.vendor.username} - Delivery Group {self.delivery_group.id}"


class DeliveryRoute(models.Model):
    """
    Optimized delivery routes for shared logistics
    """
    delivery_group = models.OneToOneField(DeliveryGroup, on_delete=models.CASCADE, related_name='route')
    
    # Route data (JSON serialized)
    waypoints = models.JSONField(default=list)  # List of delivery addresses in order
    optimized_waypoints = models.JSONField(default=list)  # Optimized order
    
    # Metrics
    total_distance_km = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    estimated_time_minutes = models.IntegerField(blank=True, null=True)
    fuel_estimate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Driver info
    driver_name = models.CharField(max_length=200, blank=True, null=True)
    driver_phone = models.CharField(max_length=20, blank=True, null=True)
    vehicle_info = models.CharField(max_length=200, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Route for Delivery Group {self.delivery_group.id}"


class LogisticsCostShare(models.Model):
    """
    Detailed cost sharing breakdown for vendors in shared deliveries
    """
    shared_delivery = models.ForeignKey(SharedDelivery, on_delete=models.CASCADE, related_name='cost_breakdown')
    
    # Cost breakdown
    base_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    distance_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    weight_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    fuel_surcharge = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    total_allocated = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    # Calculation method
    calculation_method = models.CharField(max_length=50, default='equal')  # equal, by_weight, by_distance, by_value
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Cost share for {self.shared_delivery.vendor.username} - {self.total_allocated}"
