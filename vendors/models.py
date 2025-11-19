from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Sum
from decimal import Decimal
from datetime import timedelta

User = get_user_model()


class VendorBadge(models.Model):
    """
    Badge types that can be awarded to vendors
    """
    BADGE_TYPE_CHOICES = [
        ('TOP_SELLER', 'Top Seller'),
        ('LOCAL_CHAMPION', 'Local Champion'),
        ('ECO_FRIENDLY', 'Eco-Friendly'),
        ('FAST_RESPONDER', 'Fast Responder'),
        ('HIGH_RATED', 'High Rated'),
        ('VERIFIED', 'Verified'),
        ('COMMUNITY_HERO', 'Community Hero'),
        ('TRUSTED_VENDOR', 'Trusted Vendor'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    badge_type = models.CharField(max_length=50, choices=BADGE_TYPE_CHOICES, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True, null=True)  # Icon class or emoji
    color = models.CharField(max_length=20, default='#be8400')  # Badge color
    is_active = models.BooleanField(default=True)
    
    # Criteria for auto-assignment (optional - for automated badge assignment)
    min_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    min_reviews = models.PositiveIntegerField(null=True, blank=True)
    min_sales = models.PositiveIntegerField(null=True, blank=True)
    min_revenue = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_response_time_hours = models.PositiveIntegerField(null=True, blank=True)  # For Fast Responder
    min_local_products = models.PositiveIntegerField(null=True, blank=True)  # For Local Champion
    min_eco_products = models.PositiveIntegerField(null=True, blank=True)  # For Eco-Friendly
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class VendorProfile(models.Model):
    """
    Extended profile for vendors
    """
    vendor = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendor_profile', limit_choices_to={'user_type': 'VENDOR'})
    company_name = models.CharField(max_length=200)
    registration_number = models.CharField(max_length=100, blank=True, null=True)
    tax_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Business info
    business_type = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='vendors/logos/', blank=True, null=True)
    
    # Contact
    business_phone = models.CharField(max_length=20, blank=True, null=True)
    business_email = models.EmailField(blank=True, null=True)
    business_address = models.TextField(blank=True, null=True)
    
    # Features
    has_advanced_dashboard = models.BooleanField(default=False)  # Access to advanced Odoo-like features
    is_verified = models.BooleanField(default=False)
    
    # Settings
    accepts_shared_logistics = models.BooleanField(default=True)  # Participate in shared deliveries
    auto_approve_orders = models.BooleanField(default=False)
    
    # Project contribution
    selected_project = models.ForeignKey('projects.CommunityProject', on_delete=models.SET_NULL, null=True, blank=True, related_name='contributing_vendors')
    participate_in_projects = models.BooleanField(default=True)  # Whether vendor wants to participate in projects
    
    # Badges
    badges = models.ManyToManyField(VendorBadge, related_name='vendors', blank=True)
    
    # Delivery settings (baseline)
    delivery_free_city = models.CharField(max_length=100, blank=True, null=True)
    delivery_free_radius_km = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    delivery_base_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    delivery_per_km_fee = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Harare-specific delivery fees
    harare_radius_km = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('10.00'))
    harare_within_radius_fee = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    harare_beyond_radius_fee = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Vendor location for distance calculation
    location_address = models.TextField(blank=True, null=True, help_text='Full address for delivery distance calculation')
    location_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text='Latitude for distance calculation (optional)')
    location_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text='Longitude for distance calculation (optional)')
    
    # Rating metrics (cached)
    overall_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_reviews = models.PositiveIntegerField(default=0)
    average_response_time_hours = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Last calculated
    ratings_last_calculated = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'vendor_profiles'
    
    def __str__(self):
        return f"{self.company_name} - {self.vendor.username}"


class VendorDeliveryZone(models.Model):
    """
    Per-city delivery fees configured by vendors
    """
    CITY_CHOICES = [
        ('HARARE', 'Harare (General)'),
        ('MUTARE', 'Mutare'),
        ('BULAWAYO', 'Bulawayo'),
        ('KADOMA', 'Kadoma'),
        ('NORTON', 'Norton'),
        ('CHEGUTU', 'Chegutu'),
        ('VICTORIA_FALLS', 'Victoria Falls'),
        ('KWEKWE', 'Kwekwe'),
        ('GWERU', 'Gweru'),
        ('MASVINGO', 'Masvingo'),
        ('BINDURA', 'Bindura'),
        ('CHINHOYI', 'Chinhoyi'),
        ('MAZOE', 'Mazowe'),
        ('CHIVHU', 'Chivhu'),
        ('CHIREDZI', 'Chiredzi'),
        ('CHITUNGWIZA', 'Chitungwiza'),
    ]
    
    vendor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='delivery_zones',
        limit_choices_to={'user_type': 'VENDOR'}
    )
    city = models.CharField(max_length=50, choices=CITY_CHOICES)
    fee = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['vendor', 'city']
        ordering = ['city']
    
    def __str__(self):
        return f"{self.get_city_display()} - {self.vendor.username}"


class VendorEvent(models.Model):
    """
    Upcoming events for local brands/vendors
    """
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('ECOCASH', 'EcoCash'),
        ('ONEMONEY', 'OneMoney'),
        ('INNBUCKS', 'InnBucks'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('OTHER', 'Other'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    early_bird_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    early_bird_deadline = models.DateTimeField(null=True, blank=True)
    image = models.ImageField(upload_to='events/', null=True, blank=True)
    payment_methods = models.JSONField(default=list, blank=True)
    is_global = models.BooleanField(default=True, help_text='If checked, visible to all vendors.')
    vendors = models.ManyToManyField(
        User,
        blank=True,
        related_name='assigned_events',
        limit_choices_to={'user_type': 'VENDOR'},
        help_text='Select vendors if this event is targeted. Leave empty for all vendors.'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['start_datetime']
    
    def __str__(self):
        return self.title
    
    def is_upcoming(self):
        from django.utils import timezone
        return self.start_datetime >= timezone.now()
    
    def payment_methods_display(self):
        labels = dict(self.PAYMENT_METHOD_CHOICES)
        return [labels.get(code, code) for code in (self.payment_methods or [])]
    
    def calculate_rating(self):
        """
        Calculate overall rating from all product reviews
        """
        from products.models import ProductReview
        
        reviews = ProductReview.objects.filter(
            product__vendor=self.vendor,
            is_approved=True
        )
        
        if reviews.exists():
            rating_data = reviews.aggregate(
                avg_rating=Avg('rating'),
                total_reviews=Count('id')
            )
            self.overall_rating = rating_data['avg_rating'] or 0.0
            self.total_reviews = rating_data['total_reviews'] or 0
        else:
            self.overall_rating = 0.0
            self.total_reviews = 0
        
        from django.utils import timezone
        self.ratings_last_calculated = timezone.now()
        self.save(update_fields=['overall_rating', 'total_reviews', 'ratings_last_calculated'])
        
        return self.overall_rating
    
    def calculate_response_time(self):
        """
        Calculate average response time to reviews (in hours)
        """
        from products.models import ProductReview
        from django.utils import timezone
        from django.db.models import Avg, F
        from datetime import timedelta
        
        # Get reviews with responses and calculate time difference
        reviews_with_responses = ProductReview.objects.filter(
            product__vendor=self.vendor,
            vendor_response__isnull=False,
            vendor_response_date__isnull=False,
            is_approved=True
        )
        
        if reviews_with_responses.exists():
            # Calculate average response time using database aggregation
            # Convert timedelta to hours
            total_seconds = 0
            count = 0
            
            for review in reviews_with_responses:
                if review.vendor_response_date and review.created_at:
                    time_diff = review.vendor_response_date - review.created_at
                    total_seconds += time_diff.total_seconds()
                    count += 1
            
            if count > 0:
                self.average_response_time_hours = (total_seconds / count) / 3600
            else:
                self.average_response_time_hours = None
        else:
            self.average_response_time_hours = None
        
        self.save(update_fields=['average_response_time_hours'])
        
        return self.average_response_time_hours
    
    def assign_badges(self):
        """
        Automatically assign badges based on vendor metrics
        """
        from products.models import ProductReview, Product
        from orders.models import OrderItem
        from django.utils import timezone
        
        # Clear existing badges (we'll reassign)
        self.badges.clear()
        
        # Get vendor metrics
        products = Product.objects.filter(vendor=self.vendor, is_active=True)
        reviews = ProductReview.objects.filter(
            product__vendor=self.vendor,
            is_approved=True
        )
        
        # Calculate metrics
        total_reviews = reviews.count()
        avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
        
        # Sales metrics
        order_items = OrderItem.objects.filter(
            vendor=self.vendor,
            order__payment_status='PAID'
        )
        total_sales = order_items.count()
        total_revenue = order_items.aggregate(total=Sum('subtotal'))['total'] or 0
        
        # Local products count
        local_products_count = products.filter(is_made_from_local_materials=True).count()
        
        # Response time
        response_time = self.average_response_time_hours or 999
        
        # Get all active badges
        all_badges = VendorBadge.objects.filter(is_active=True)
        
        for badge in all_badges:
            should_assign = False
            
            if badge.badge_type == 'VERIFIED' and self.is_verified:
                should_assign = True
            elif badge.badge_type == 'HIGH_RATED':
                if badge.min_rating and avg_rating >= badge.min_rating:
                    if not badge.min_reviews or total_reviews >= badge.min_reviews:
                        should_assign = True
            elif badge.badge_type == 'TOP_SELLER':
                if badge.min_sales and total_sales >= badge.min_sales:
                    if not badge.min_revenue or total_revenue >= badge.min_revenue:
                        should_assign = True
            elif badge.badge_type == 'LOCAL_CHAMPION':
                if badge.min_local_products and local_products_count >= badge.min_local_products:
                    should_assign = True
            elif badge.badge_type == 'ECO_FRIENDLY':
                if badge.min_eco_products and local_products_count >= badge.min_eco_products:
                    should_assign = True
            elif badge.badge_type == 'FAST_RESPONDER':
                # Check if vendor has responded to at least 5 reviews
                reviews_with_responses_count = ProductReview.objects.filter(
                    product__vendor=self.vendor,
                    vendor_response__isnull=False,
                    is_approved=True
                ).count()
                
                if badge.max_response_time_hours and response_time <= badge.max_response_time_hours:
                    if reviews_with_responses_count >= 5:  # At least 5 reviews with responses
                        should_assign = True
            elif badge.badge_type == 'COMMUNITY_HERO':
                if self.participate_in_projects and self.selected_project:
                    should_assign = True
            elif badge.badge_type == 'TRUSTED_VENDOR':
                if avg_rating >= 4.0 and total_reviews >= 10 and self.is_verified:
                    should_assign = True
            
            if should_assign:
                self.badges.add(badge)
        
        self.save()
        return self.badges.all()
    
    def update_metrics(self):
        """
        Update all vendor metrics (ratings, response time, badges)
        """
        self.calculate_rating()
        self.calculate_response_time()
        self.assign_badges()
        return self
    
    @property
    def rating_display(self):
        """Get rating as formatted string"""
        if self.overall_rating > 0:
            return f"{self.overall_rating:.1f}"
        return "No ratings yet"
    
    @property
    def response_time_display(self):
        """Get response time as formatted string"""
        if self.average_response_time_hours:
            hours = float(self.average_response_time_hours)
            if hours < 24:
                if hours < 1:
                    minutes = int(hours * 60)
                    return f"{minutes} minute{'s' if minutes != 1 else ''}"
                elif hours == int(hours):
                    return f"{int(hours)} hour{'s' if hours != 1 else ''}"
                else:
                    return f"{hours:.1f} hours"
            else:
                days = hours / 24
                if days == int(days):
                    return f"{int(days)} day{'s' if days != 1 else ''}"
                else:
                    return f"{days:.1f} days"
        return "No responses yet"


class VendorPaymentOption(models.Model):
    """
    Payment options available for a vendor (cash, mobile wallets, etc.)
    """
    PAYMENT_TYPE_CHOICES = [
        ('CASH_ON_DELIVERY', 'Cash on Delivery'),
        ('ECOCASH', 'EcoCash'),
        ('ONEMONEY', 'OneMoney'),
        ('INNBUCKS', 'InnBucks'),
    ]
    
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_options', limit_choices_to={'user_type': 'VENDOR'})
    payment_type = models.CharField(max_length=30, choices=PAYMENT_TYPE_CHOICES)
    phone_number = models.CharField(max_length=50, blank=True, null=True, help_text='Phone number for receiving payments')
    merchant_name = models.CharField(max_length=200, blank=True, null=True, help_text='Full name or merchant name as it appears when transferring money (required for mobile wallets)')
    instructions = models.TextField(blank=True, null=True)
    is_enabled = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['vendor', 'payment_type']]
        ordering = ['vendor', 'payment_type']
    
    def __str__(self):
        return f"{self.vendor.username} - {self.get_payment_type_display()}"


class VendorCompany(models.Model):
    """
    Multi-company support for vendors with advanced features
    """
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vendor_companies', limit_choices_to={'user_type': 'VENDOR'})
    name = models.CharField(max_length=200)
    registration_number = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Vendor Companies'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.vendor.username})"


class VendorAnalytics(models.Model):
    """
    Analytics data for vendors (sales, revenue, etc.)
    """
    vendor = models.OneToOneField(User, on_delete=models.CASCADE, related_name='analytics', limit_choices_to={'user_type': 'VENDOR'})
    
    # Sales metrics
    total_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_orders = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Product metrics
    total_products = models.PositiveIntegerField(default=0)
    active_products = models.PositiveIntegerField(default=0)
    
    # Abandoned carts
    total_abandoned_carts = models.PositiveIntegerField(default=0)
    abandoned_cart_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Timestamps
    last_calculated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Vendor Analytics'
    
    def __str__(self):
        return f"Analytics for {self.vendor.username}"


class CashReceipt(models.Model):
    """
    Cash receipts for vendors (walk-in clients, own accounting)
    """
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cash_receipts', limit_choices_to={'user_type': 'VENDOR'})
    receipt_number = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    customer_name = models.CharField(max_length=200, blank=True, null=True)
    is_walk_in = models.BooleanField(default=False)  # Walk-in client payment
    receipt_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-receipt_date']
    
    def __str__(self):
        return f"Receipt {self.receipt_number} - {self.vendor.username}"


class JobPosting(models.Model):
    """
    Job postings by vendors (integrated job board)
    """
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('ACTIVE', 'Active'),
        ('CLOSED', 'Closed'),
        ('EXPIRED', 'Expired'),
    ]
    
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_postings', limit_choices_to={'user_type': 'VENDOR'})
    title = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.TextField(blank=True, null=True)
    
    # Job details
    job_type = models.CharField(max_length=50, blank=True, null=True)  # Full-time, Part-time, Contract, etc.
    location = models.CharField(max_length=200, blank=True, null=True)
    salary_range = models.CharField(max_length=100, blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    # Dates
    posted_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(blank=True, null=True)
    closed_date = models.DateTimeField(blank=True, null=True)
    
    # Applications
    application_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-posted_date']
    
    def __str__(self):
        return f"{self.title} - {self.vendor.username}"


# ============================================
# ACCOUNTING & SALES MODULE MODELS
# ============================================

class AccountingJournalEntry(models.Model):
    """
    Double-entry accounting journal entries
    """
    ENTRY_TYPE_CHOICES = [
        ('SALE', 'Sale'),
        ('EXPENSE', 'Expense'),
        ('PAYMENT', 'Payment Received'),
        ('REFUND', 'Refund'),
        ('ADJUSTMENT', 'Adjustment'),
    ]
    
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='journal_entries', limit_choices_to={'user_type': 'VENDOR'})
    company = models.ForeignKey(VendorCompany, on_delete=models.CASCADE, related_name='journal_entries', null=True, blank=True)
    entry_number = models.CharField(max_length=100, unique=True)
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPE_CHOICES)
    date = models.DateField()
    description = models.TextField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Reference to related objects
    sale_receipt = models.ForeignKey('SaleReceipt', on_delete=models.SET_NULL, null=True, blank=True, related_name='journal_entries')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name_plural = 'Accounting Journal Entries'
    
    def __str__(self):
        return f"{self.entry_number} - {self.get_entry_type_display()}"


class SaleReceipt(models.Model):
    """
    Sales receipts for walk-in or online customers (POS)
    """
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('ECOCASH', 'EcoCash'),
        ('ONEMONEY', 'OneMoney'),
        ('INNBUCKS', 'InnBucks'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('CARD', 'Card'),
        ('OTHER', 'Other'),
    ]
    
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sale_receipts', limit_choices_to={'user_type': 'VENDOR'})
    company = models.ForeignKey(VendorCompany, on_delete=models.CASCADE, related_name='sale_receipts', null=True, blank=True)
    receipt_number = models.CharField(max_length=100, unique=True, db_index=True)
    
    # Customer info
    customer_name = models.CharField(max_length=200)
    customer_phone = models.CharField(max_length=50, blank=True, null=True)
    customer_email = models.EmailField(blank=True, null=True)
    
    # Payment details
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Notes
    notes = models.TextField(blank=True, null=True)
    
    # Flags
    is_walk_in = models.BooleanField(default=True)  # Walk-in or online
    is_printed = models.BooleanField(default=False)
    
    # Timestamps
    sale_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-sale_date', '-created_at']
    
    def __str__(self):
        return f"Receipt {self.receipt_number} - {self.customer_name}"
    
    def save(self, *args, **kwargs):
        if not self.receipt_number:
            # Generate receipt number
            from django.utils import timezone
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            vendor_id = self.vendor.id
            self.receipt_number = f"RCP-{vendor_id}-{timestamp}"
        super().save(*args, **kwargs)


class SaleReceiptItem(models.Model):
    """
    Line items for sale receipts
    """
    receipt = models.ForeignKey(SaleReceipt, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True, blank=True, related_name='receipt_items')
    
    # Product details (stored for record-keeping)
    product_name = models.CharField(max_length=200)
    product_sku = models.CharField(max_length=100, blank=True, null=True)
    
    # Pricing
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        # Calculate line total
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class VendorExpense(models.Model):
    """
    Business expenses tracked by vendors
    """
    EXPENSE_CATEGORY_CHOICES = [
        ('SUPPLIES', 'Supplies & Materials'),
        ('SHIPPING', 'Shipping & Delivery'),
        ('MARKETING', 'Marketing & Advertising'),
        ('UTILITIES', 'Utilities'),
        ('RENT', 'Rent'),
        ('SALARIES', 'Salaries & Wages'),
        ('EQUIPMENT', 'Equipment'),
        ('PROFESSIONAL_SERVICES', 'Professional Services'),
        ('OTHER', 'Other'),
    ]
    
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses', limit_choices_to={'user_type': 'VENDOR'})
    company = models.ForeignKey(VendorCompany, on_delete=models.CASCADE, related_name='expenses', null=True, blank=True)
    
    description = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=EXPENSE_CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    expense_date = models.DateField()
    
    # Payment details
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    
    # Supporting documents
    receipt_image = models.ImageField(upload_to='expenses/', blank=True, null=True)
    
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-expense_date', '-created_at']
    
    def __str__(self):
        return f"{self.description} - ${self.amount}"


class VendorInvoice(models.Model):
    """
    Invoices issued by vendors to customers
    """
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices', limit_choices_to={'user_type': 'VENDOR'})
    company = models.ForeignKey(VendorCompany, on_delete=models.CASCADE, related_name='invoices', null=True, blank=True)
    invoice_number = models.CharField(max_length=100, unique=True, db_index=True)
    
    # Customer
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField(blank=True, null=True)
    customer_phone = models.CharField(max_length=50, blank=True, null=True)
    customer_address = models.TextField(blank=True, null=True)
    
    # Amounts
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    # Dates
    issue_date = models.DateField()
    due_date = models.DateField()
    paid_date = models.DateField(blank=True, null=True)
    
    # Notes
    notes = models.TextField(blank=True, null=True)
    terms = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-issue_date', '-created_at']
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.customer_name}"
    
    @property
    def balance_due(self):
        return self.total_amount - self.amount_paid
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            from django.utils import timezone
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            vendor_id = self.vendor.id
            self.invoice_number = f"INV-{vendor_id}-{timestamp}"
        super().save(*args, **kwargs)


class VendorInvoiceItem(models.Model):
    """
    Line items for vendor invoices
    """
    invoice = models.ForeignKey(VendorInvoice, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True, blank=True)
    
    description = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"{self.description} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)


# ============================================
# VENDOR DISCUSSION/FORUM MODELS
# ============================================

class VendorDiscussionCategory(models.Model):
    """
    Categories for vendor discussions
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Vendor Discussion Categories'
    
    def __str__(self):
        return self.name


class VendorDiscussion(models.Model):
    """
    Discussion threads between vendors
    """
    category = models.ForeignKey(VendorDiscussionCategory, on_delete=models.CASCADE, related_name='discussions')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vendor_discussions', limit_choices_to={'user_type': 'VENDOR'})
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    # Flags
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    is_announcement = models.BooleanField(default=False)
    
    # Engagement
    view_count = models.PositiveIntegerField(default=0)
    reply_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_pinned', '-last_activity_at']
    
    def __str__(self):
        return self.title


class VendorDiscussionReply(models.Model):
    """
    Replies to vendor discussions
    """
    discussion = models.ForeignKey(VendorDiscussion, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vendor_discussion_replies', limit_choices_to={'user_type': 'VENDOR'})
    
    content = models.TextField()
    
    # Engagement
    helpful_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name_plural = 'Vendor Discussion Replies'
    
    def __str__(self):
        return f"Reply by {self.author.username} on {self.discussion.title}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update discussion reply count and last activity
        self.discussion.reply_count = self.discussion.replies.count()
        self.discussion.last_activity_at = self.created_at
        self.discussion.save(update_fields=['reply_count', 'last_activity_at'])
