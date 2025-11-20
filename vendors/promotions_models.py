"""
Vendor Promotions Models
Allows vendors to create and manage product promotions for holidays and special events
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal

User = get_user_model()


class Promotion(models.Model):
    """
    Promotions created by vendors for holidays, sales events, etc.
    """
    STYLE_CHOICES = [
        ('hot-deal', '🔥 Hot Deal'),
        ('limited-time', '⏰ Limited Time'),
        ('seasonal', '🎄 Seasonal'),
        ('flash-sale', '⚡ Flash Sale'),
        ('clearance', '🏷️ Clearance'),
        ('special-offer', '⭐ Special Offer'),
        ('black-friday', '🛍️ Black Friday'),
        ('christmas', '🎅 Christmas'),
        ('new-year', '🎉 New Year'),
        ('easter', '🐰 Easter'),
        ('valentines', '💝 Valentine\'s'),
        ('mothers-day', '👩 Mother\'s Day'),
        ('fathers-day', '👨 Father\'s Day'),
        ('independence', '🇿🇼 Independence Day'),
        ('custom', '✨ Custom'),
    ]
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SCHEDULED', 'Scheduled'),
        ('ACTIVE', 'Active'),
        ('EXPIRED', 'Expired'),
        ('PAUSED', 'Paused'),
    ]
    
    # Basic Information
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='promotions', 
                               limit_choices_to={'user_type': 'VENDOR'})
    company = models.ForeignKey('VendorCompany', on_delete=models.CASCADE, 
                                related_name='promotions', null=True, blank=True)
    
    # Promotion Details
    name = models.CharField(max_length=200, help_text='e.g., "Black Friday Mega Sale", "Christmas Special"')
    description = models.TextField(blank=True, help_text='Detailed description of the promotion')
    style = models.CharField(max_length=50, choices=STYLE_CHOICES, default='special-offer',
                            help_text='Visual style/badge for the promotion')
    
    # Discount Settings
    discount_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01')), MaxValueValidator(Decimal('99.99'))],
        help_text='Discount percentage (e.g., 25 for 25% off)'
    )
    
    # Date Range
    start_date = models.DateTimeField(help_text='When the promotion starts')
    end_date = models.DateTimeField(help_text='When the promotion ends')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    is_active = models.BooleanField(default=True, help_text='Manual toggle to activate/deactivate')
    
    # Display Options
    show_badge = models.BooleanField(default=True, help_text='Show promotion badge on products')
    show_countdown = models.BooleanField(default=False, help_text='Show countdown timer')
    featured = models.BooleanField(default=False, help_text='Feature this promotion on vendor page')
    
    # Analytics
    view_count = models.PositiveIntegerField(default=0, help_text='Number of views')
    click_count = models.PositiveIntegerField(default=0, help_text='Number of clicks')
    conversion_count = models.PositiveIntegerField(default=0, help_text='Number of sales')
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0,
                                       help_text='Total revenue from this promotion')
    
    # Terms & Conditions
    terms = models.TextField(blank=True, help_text='Terms and conditions for this promotion')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['vendor', 'status']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['status', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.discount_percentage}% off"
    
    def save(self, *args, **kwargs):
        # Auto-update status based on dates
        self.update_status()
        super().save(*args, **kwargs)
    
    def update_status(self):
        """
        Automatically update promotion status based on dates and active flag
        """
        if not self.is_active:
            self.status = 'PAUSED'
            return
        
        now = timezone.now()
        
        if self.end_date < now:
            self.status = 'EXPIRED'
        elif self.start_date > now:
            self.status = 'SCHEDULED'
        elif self.start_date <= now <= self.end_date:
            self.status = 'ACTIVE'
    
    @property
    def is_currently_active(self):
        """
        Check if promotion is currently active (within date range and enabled)
        """
        now = timezone.now()
        return (
            self.is_active and 
            self.start_date <= now <= self.end_date and
            self.status == 'ACTIVE'
        )
    
    @property
    def days_remaining(self):
        """
        Calculate days remaining until promotion ends
        """
        if not self.is_currently_active:
            return 0
        
        delta = self.end_date - timezone.now()
        return max(0, delta.days)
    
    @property
    def hours_remaining(self):
        """
        Calculate hours remaining until promotion ends
        """
        if not self.is_currently_active:
            return 0
        
        delta = self.end_date - timezone.now()
        return max(0, int(delta.total_seconds() / 3600))
    
    @property
    def conversion_rate(self):
        """
        Calculate conversion rate (clicks to sales)
        """
        if self.click_count == 0:
            return 0
        return (self.conversion_count / self.click_count) * 100
    
    @property
    def product_count(self):
        """
        Number of products in this promotion
        """
        return self.products.count()
    
    def get_style_display_name(self):
        """
        Get friendly display name with emoji
        """
        return dict(self.STYLE_CHOICES).get(self.style, self.style)
    
    def get_badge_color(self):
        """
        Get color for promotion badge based on style
        """
        color_map = {
            'hot-deal': '#ff4444',
            'limited-time': '#ff9800',
            'seasonal': '#4caf50',
            'flash-sale': '#9c27b0',
            'clearance': '#607d8b',
            'special-offer': '#2196f3',
            'black-friday': '#000000',
            'christmas': '#c62828',
            'new-year': '#ffd700',
            'easter': '#9c27b0',
            'valentines': '#e91e63',
            'mothers-day': '#e91e63',
            'fathers-day': '#1976d2',
            'independence': '#2e7d32',
            'custom': '#ff5722',
        }
        return color_map.get(self.style, '#2196f3')


class ProductPromotion(models.Model):
    """
    Links products to promotions and tracks promotion-specific metrics
    """
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, related_name='product_links')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='promotion_links')
    
    # Calculated Prices
    original_price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Original product price')
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Price after discount')
    savings_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text='Amount saved')
    
    # Analytics per product
    view_count = models.PositiveIntegerField(default=0)
    click_count = models.PositiveIntegerField(default=0)
    sales_count = models.PositiveIntegerField(default=0)
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Metadata
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['promotion', 'product']
        ordering = ['-added_at']
        indexes = [
            models.Index(fields=['promotion', 'product']),
            models.Index(fields=['product']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - {self.promotion.name}"
    
    def save(self, *args, **kwargs):
        # Calculate prices automatically
        self.calculate_prices()
        super().save(*args, **kwargs)
    
    def calculate_prices(self):
        """
        Calculate discounted price and savings based on promotion discount
        """
        self.original_price = self.product.price
        discount_decimal = self.promotion.discount_percentage / Decimal('100')
        self.savings_amount = self.original_price * discount_decimal
        self.discounted_price = self.original_price - self.savings_amount
    
    @property
    def savings_percentage(self):
        """
        Get savings as percentage (same as promotion discount)
        """
        return float(self.promotion.discount_percentage)
    
    @property
    def is_active(self):
        """
        Check if this product promotion is currently active
        """
        return self.promotion.is_currently_active


class PromotionAnalytics(models.Model):
    """
    Daily analytics for promotions
    """
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, related_name='analytics')
    date = models.DateField()
    
    # Daily metrics
    views = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)
    sales = models.PositiveIntegerField(default=0)
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unique_visitors = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['promotion', 'date']
        ordering = ['-date']
        verbose_name_plural = 'Promotion Analytics'
        indexes = [
            models.Index(fields=['promotion', 'date']),
        ]
    
    def __str__(self):
        return f"{self.promotion.name} - {self.date}"

