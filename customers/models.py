from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal

User = get_user_model()


class CustomerDashboard(models.Model):
    """
    Customer dashboard data and preferences
    """
    customer = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_dashboard', limit_choices_to={'user_type': 'CUSTOMER'})
    
    # Preferences
    default_project = models.ForeignKey('projects.CommunityProject', on_delete=models.SET_NULL, null=True, blank=True, related_name='default_for_customers')
    show_abandoned_carts = models.BooleanField(default=True)
    
    # Last viewed
    last_viewed_products = models.ManyToManyField('products.Product', blank=True, related_name='viewed_by_customers')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'customer_dashboards'
    
    def __str__(self):
        return f"Dashboard for {self.customer.username}"


class CustomerImpactMetrics(models.Model):
    """
    Track customer impact metrics (project contributions, voting history, etc.)
    """
    customer = models.OneToOneField(User, on_delete=models.CASCADE, related_name='impact_metrics', limit_choices_to={'user_type': 'CUSTOMER'})
    
    # Project contributions
    total_project_contributions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    projects_supported_count = models.PositiveIntegerField(default=0)
    total_votes_cast = models.PositiveIntegerField(default=0)
    
    # Purchase metrics
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_orders = models.PositiveIntegerField(default=0)
    total_items_purchased = models.PositiveIntegerField(default=0)
    
    # Local brand support
    local_brand_purchases = models.PositiveIntegerField(default=0)
    local_material_product_purchases = models.PositiveIntegerField(default=0)

    # Gamification
    impact_points = models.PositiveIntegerField(default=0)
    current_level = models.ForeignKey('ImpactLevel', on_delete=models.SET_NULL, null=True, blank=True, related_name='customers')
    total_badges_earned = models.PositiveIntegerField(default=0)
    
    # Last calculated
    last_calculated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Customer Impact Metrics'
    
    def __str__(self):
        return f"Impact Metrics for {self.customer.username}"


class VotingHistory(models.Model):
    """
    Detailed voting history for customers
    """
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='voting_history', limit_choices_to={'user_type': 'CUSTOMER'})
    project = models.ForeignKey('projects.CommunityProject', on_delete=models.CASCADE, related_name='voting_history')
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='voting_history')
    vote_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_default_vote = models.BooleanField(default=False)
    
    # Impact tracking
    project_funding_before = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    project_funding_after = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Voting Histories'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.customer.username} voted {self.vote_amount} for {self.project.title}"


class SearchHistory(models.Model):
    """
    Track customer search history for analytics
    """
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='search_history', limit_choices_to={'user_type': 'CUSTOMER'}, null=True, blank=True)
    query = models.CharField(max_length=500)
    results_count = models.PositiveIntegerField(default=0)
    was_product_found = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Search Histories'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'created_at']),
        ]
    
    def __str__(self):
        return f"Search: {self.query} - {self.customer.username if self.customer else 'Anonymous'}"


class ReferralProgram(models.Model):
    """
    Referral program for customers
    """
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_made', limit_choices_to={'user_type': 'CUSTOMER'})
    referral_code = models.CharField(max_length=50, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)
    
    # Statistics
    total_referrals = models.PositiveIntegerField(default=0)
    successful_signups = models.PositiveIntegerField(default=0)  # Referrals who signed up
    successful_purchases = models.PositiveIntegerField(default=0)  # Referrals who made purchases
    
    # Rewards
    total_points_earned = models.PositiveIntegerField(default=0)
    total_rewards_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['referral_code']),
            models.Index(fields=['referrer', 'is_active']),
        ]
    
    def __str__(self):
        return f"Referral code: {self.referral_code} - {self.referrer.username}"


class Referral(models.Model):
    """
    Individual referral tracking
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending Signup'),
        ('SIGNED_UP', 'Signed Up'),
        ('FIRST_PURCHASE', 'First Purchase Made'),
        ('REWARDED', 'Reward Given'),
    ]
    
    referral_program = models.ForeignKey(ReferralProgram, on_delete=models.CASCADE, related_name='referral_instances')
    referred_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referral_received', limit_choices_to={'user_type': 'CUSTOMER'}, null=True, blank=True)
    referral_code_used = models.CharField(max_length=50)
    
    # Tracking
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Rewards
    referrer_points_awarded = models.PositiveIntegerField(default=0)
    referred_points_awarded = models.PositiveIntegerField(default=0)
    
    # First purchase tracking
    first_order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='referral_orders')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    signed_up_at = models.DateTimeField(null=True, blank=True)
    first_purchase_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = [['referral_program', 'referred_user']]
        indexes = [
            models.Index(fields=['referral_code_used', 'status']),
            models.Index(fields=['referral_program', 'status']),
        ]
    
    def __str__(self):
        return f"Referral: {self.referral_code_used} - {self.get_status_display()}"


class CustomerTestimonial(models.Model):
    """
    Customer testimonials for vendor pages
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='testimonials', limit_choices_to={'user_type': 'CUSTOMER'})
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_testimonials', limit_choices_to={'user_type': 'VENDOR'})
    
    # Testimonial content
    title = models.CharField(max_length=200, blank=True, null=True)
    testimonial = models.TextField()
    rating = models.PositiveIntegerField(default=5)  # 1-5 stars
    
    # Verification
    is_verified_purchase = models.BooleanField(default=False)
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='testimonials')
    
    # Approval
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_testimonials', limit_choices_to={'user_type': 'ADMIN'})
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Display
    is_featured = models.BooleanField(default=False)
    display_name = models.CharField(max_length=200, blank=True, null=True)  # Allow customers to use a display name
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_featured', '-created_at']
        indexes = [
            models.Index(fields=['vendor', 'status', 'is_featured']),
            models.Index(fields=['customer', 'vendor']),
        ]
    
    def __str__(self):
        return f"Testimonial by {self.customer.username} for {self.vendor.username}"


class SocialShare(models.Model):
    """
    Track social media shares for analytics
    """
    SHARE_TYPE_CHOICES = [
        ('PRODUCT', 'Product'),
        ('PROJECT', 'Project'),
        ('VENDOR', 'Vendor'),
    ]
    
    PLATFORM_CHOICES = [
        ('FACEBOOK', 'Facebook'),
        ('TWITTER', 'Twitter'),
        ('WHATSAPP', 'WhatsApp'),
        ('LINKEDIN', 'LinkedIn'),
        ('EMAIL', 'Email'),
        ('OTHER', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='social_shares')
    share_type = models.CharField(max_length=20, choices=SHARE_TYPE_CHOICES)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    
    # Related objects
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, null=True, blank=True, related_name='social_shares')
    project = models.ForeignKey('projects.CommunityProject', on_delete=models.CASCADE, null=True, blank=True, related_name='social_shares')
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='vendor_social_shares', limit_choices_to={'user_type': 'VENDOR'})
    
    # Tracking
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['share_type', 'platform', 'created_at']),
            models.Index(fields=['product', 'created_at']),
            models.Index(fields=['project', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_platform_display()} share of {self.get_share_type_display()} by {self.user.username if self.user else 'Anonymous'}"


class Wishlist(models.Model):
    """
    Customer wishlists for saving products
    """
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlists', limit_choices_to={'user_type': 'CUSTOMER'})
    name = models.CharField(max_length=200, default='My Wishlist')
    description = models.TextField(blank=True, null=True)
    is_public = models.BooleanField(default=False)  # Allow sharing
    is_default = models.BooleanField(default=False)  # Default wishlist
    share_token = models.CharField(max_length=50, unique=True, blank=True, null=True, db_index=True)  # For sharing
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_default', '-created_at']
        indexes = [
            models.Index(fields=['customer', 'is_default']),
            models.Index(fields=['share_token']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.customer.username}"
    
    def save(self, *args, **kwargs):
        if not self.share_token and self.is_public:
            import secrets
            import string
            token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
            while Wishlist.objects.filter(share_token=token).exists():
                token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
            self.share_token = token
        super().save(*args, **kwargs)
    
    @property
    def item_count(self):
        return self.items.count()
    
    @property
    def total_value(self):
        return sum(item.product.price for item in self.items.all() if item.product.is_active)


class WishlistItem(models.Model):
    """
    Items in a wishlist
    """
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='wishlist_items')
    notes = models.TextField(blank=True, null=True)  # Personal notes about the item
    priority = models.PositiveIntegerField(default=0)  # Higher number = higher priority
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['wishlist', 'product']]
        ordering = ['-priority', '-added_at']
        indexes = [
            models.Index(fields=['wishlist', 'product']),
        ]
    
    def __str__(self):
        return f"{self.product.name} in {self.wishlist.name}"
    
    @property
    def price_changed(self):
        """Check if price has changed since added"""
        # This would need to track original price - for now return False
        # Could be enhanced with PriceHistory model
        return False


class PriceAlert(models.Model):
    """
    Price drop alerts for products
    """
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('TRIGGERED', 'Price Drop Triggered'),
        ('CANCELLED', 'Cancelled'),
        ('EXPIRED', 'Expired'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='price_alerts', limit_choices_to={'user_type': 'CUSTOMER'})
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='price_alerts')
    
    # Price tracking
    target_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Alert when price drops to this
    target_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Alert when price drops by this %
    original_price = models.DecimalField(max_digits=10, decimal_places=2)  # Price when alert was created
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    
    # Notification
    notified_at = models.DateTimeField(null=True, blank=True)
    notification_sent = models.BooleanField(default=False)
    
    # Expiry
    expires_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['customer', 'product']]
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['product', 'status']),
            models.Index(fields=['status', 'expires_at']),
        ]
    
    def __str__(self):
        return f"Price alert for {self.product.name} - {self.customer.username}"
    
    def check_price_drop(self):
        """Check if price has dropped and trigger alert if conditions met"""
        if self.status != 'ACTIVE':
            return False
        
        current_price = self.product.price
        
        # Check if expired
        if self.expires_at:
            if timezone.now() > self.expires_at:
                self.status = 'EXPIRED'
                self.save()
                return False
        
        # Check target price
        if self.target_price and current_price <= self.target_price:
            if current_price < self.original_price:
                self.status = 'TRIGGERED'
                self.save(update_fields=['status'])
                self.trigger_notification()
                return True
        
        # Check target percentage
        if self.target_percentage:
            price_drop = ((self.original_price - current_price) / self.original_price) * 100
            if price_drop >= float(self.target_percentage):
                if current_price < self.original_price:
                    self.status = 'TRIGGERED'
                    self.save(update_fields=['status'])
                    self.trigger_notification()
                    return True
        
        return False

    def trigger_notification(self):
        """Log notification for price drop"""
        if self.notification_sent:
            return
        
        NotificationLog.objects.create(
            customer=self.customer,
            notification_type='PRICE_DROP',
            title=f'Price drop for {self.product.name}',
            message=f'{self.product.name} has dropped in price from ${self.original_price} to ${self.product.price}.',
            product=self.product,
            price_alert=self
        )
        
        self.notification_sent = True
        self.notified_at = timezone.now()
        self.save(update_fields=['notification_sent', 'notified_at'])


class GiftRegistry(models.Model):
    """
    Gift registry for customers
    """
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gift_registries', limit_choices_to={'user_type': 'CUSTOMER'})
    name = models.CharField(max_length=200)  # e.g., "Wedding Registry", "Birthday Wishlist"
    description = models.TextField(blank=True, null=True)
    event_date = models.DateField(null=True, blank=True)  # Date of the event
    
    # Sharing
    is_public = models.BooleanField(default=True)
    share_token = models.CharField(max_length=50, unique=True, db_index=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['share_token']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.customer.username}"
    
    def save(self, *args, **kwargs):
        if not self.share_token:
            import secrets
            import string
            token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
            while GiftRegistry.objects.filter(share_token=token).exists():
                token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
            self.share_token = token
        super().save(*args, **kwargs)
    
    @property
    def item_count(self):
        return self.items.count()
    
    @property
    def total_value(self):
        return sum(item.product.price * item.quantity for item in self.items.all() if item.product.is_active)
    
    @property
    def purchased_count(self):
        return sum(item.quantity_purchased for item in self.items.all())
    
    @property
    def completion_percentage(self):
        total_needed = sum(item.quantity for item in self.items.all())
        if total_needed == 0:
            return 0
        return (self.purchased_count / total_needed) * 100


class GiftRegistryItem(models.Model):
    """
    Items in a gift registry
    """
    registry = models.ForeignKey(GiftRegistry, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='gift_registry_items')
    quantity = models.PositiveIntegerField(default=1)
    quantity_purchased = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True, null=True)  # Notes for gift givers
    priority = models.PositiveIntegerField(default=0)
    
    # Purchaser tracking (optional - for thank you notes)
    purchased_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='gift_purchases')
    purchase_order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='gift_registry_items')
    
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['registry', 'product']]
        ordering = ['-priority', '-added_at']
        indexes = [
            models.Index(fields=['registry', 'product']),
        ]
    
    def __str__(self):
        return f"{self.product.name} x{self.quantity} in {self.registry.name}"
    
    @property
    def remaining_quantity(self):
        return max(0, self.quantity - self.quantity_purchased)
    
    @property
    def is_fulfilled(self):
        return self.quantity_purchased >= self.quantity


class NotificationLog(models.Model):
    """
    Track notifications sent to customers
    """
    NOTIFICATION_TYPE_CHOICES = [
        ('PRICE_DROP', 'Price Drop'),
        ('BACK_IN_STOCK', 'Back in Stock'),
        ('NEW_PRODUCT', 'New Product'),
        ('PROJECT_MILESTONE', 'Project Milestone'),
        ('GENERAL', 'General'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', limit_choices_to={'user_type': 'CUSTOMER'})
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Related objects
    product = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    vendor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='vendor_notifications', limit_choices_to={'user_type': 'VENDOR'})
    project = models.ForeignKey('projects.CommunityProject', on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    milestone = models.ForeignKey('projects.ProjectMilestone', on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    price_alert = models.ForeignKey('PriceAlert', on_delete=models.SET_NULL, null=True, blank=True, related_name='notification_logs')
    
    # Delivery tracking
    sent_via_email = models.BooleanField(default=False)
    sent_via_in_app = models.BooleanField(default=True)
    is_read = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'notification_type']),
            models.Index(fields=['is_read', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.title}"
    
    def mark_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])


class BackInStockAlert(models.Model):
    """
    Alerts for when an out-of-stock product becomes available
    """
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('TRIGGERED', 'Triggered'),
        ('CANCELLED', 'Cancelled'),
        ('EXPIRED', 'Expired'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='back_in_stock_alerts', limit_choices_to={'user_type': 'CUSTOMER'})
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='back_in_stock_alerts')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    
    notified_at = models.DateTimeField(null=True, blank=True)
    notification_sent = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['customer', 'product']]
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['product', 'status']),
        ]
    
    def __str__(self):
        return f"Back in stock alert for {self.product.name} - {self.customer.username}"
    
    def mark_notified(self):
        self.status = 'TRIGGERED'
        self.notification_sent = True
        self.notified_at = timezone.now()
        self.save(update_fields=['status', 'notification_sent', 'notified_at'])


class VendorSubscription(models.Model):
    """
    Customer subscription to vendor updates (new products, promotions)
    """
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vendor_subscriptions', limit_choices_to={'user_type': 'CUSTOMER'})
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscribers', limit_choices_to={'user_type': 'VENDOR'})
    
    notify_new_products = models.BooleanField(default=True)
    notify_promotions = models.BooleanField(default=False)
    last_notified_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['customer', 'vendor']]
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['vendor']),
            models.Index(fields=['customer']),
        ]
    
    def __str__(self):
        return f"{self.customer.username} → {self.vendor.username}"


class ProjectNotificationSubscription(models.Model):
    """
    Customer subscription to project milestone notifications
    """
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_notification_subscriptions', limit_choices_to={'user_type': 'CUSTOMER'})
    project = models.ForeignKey('projects.CommunityProject', on_delete=models.CASCADE, related_name='notification_subscriptions')
    
    notify_milestones = models.BooleanField(default=True)
    notify_updates = models.BooleanField(default=True)
    
    last_notified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['customer', 'project']]
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project']),
        ]
    
    def __str__(self):
        return f"{self.customer.username} subscribed to {self.project.title}"


class ImpactLevel(models.Model):
    """
    Gamification impact levels (Bronze, Silver, etc.)
    """
    LEVEL_CHOICES = [
        ('BRONZE', 'Bronze'),
        ('SILVER', 'Silver'),
        ('GOLD', 'Gold'),
        ('PLATINUM', 'Platinum'),
        ('DIAMOND', 'Diamond'),
    ]
    
    name = models.CharField(max_length=50, choices=LEVEL_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    min_points = models.PositiveIntegerField()
    badge_icon = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=20, default='#be8400')
    perks = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['min_points']
    
    def __str__(self):
        return self.display_name


class AchievementBadge(models.Model):
    """
    Achievement badges that can be earned by customers
    """
    BADGE_CATEGORY_CHOICES = [
        ('SUPPORT', 'Support'),
        ('PURCHASE', 'Purchase'),
        ('PROJECT', 'Project'),
        ('COMMUNITY', 'Community'),
        ('CHALLENGE', 'Challenge'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    category = models.CharField(max_length=30, choices=BADGE_CATEGORY_CHOICES)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=20, default='#be8400')
    points_reward = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # Criteria (stored as informational text)
    criteria_text = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class CustomerAchievement(models.Model):
    """
    Tracks achievements earned by customers
    """
    STATUS_CHOICES = [
        ('IN_PROGRESS', 'In Progress'),
        ('EARNED', 'Earned'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements', limit_choices_to={'user_type': 'CUSTOMER'})
    badge = models.ForeignKey(AchievementBadge, on_delete=models.CASCADE, related_name='customer_achievements')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IN_PROGRESS')
    progress = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.0'))  # percentage completion
    progress_value = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.0'))
    target_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    earned_at = models.DateTimeField(null=True, blank=True)
    notify_user = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['customer', 'badge']]
        ordering = ['-earned_at', '-created_at']
        indexes = [
            models.Index(fields=['customer', 'status']),
        ]
    
    def __str__(self):
        return f"{self.customer.username} - {self.badge.name}"


class LeaderboardEntry(models.Model):
    """
    Leaderboard entries for gamification
    """
    LEADERBOARD_TYPE_CHOICES = [
        ('PROJECT_CONTRIBUTION', 'Project Contribution'),
        ('IMPACT_POINTS', 'Impact Points'),
        ('PURCHASES', 'Purchases'),
    ]
    
    PERIOD_CHOICES = [
        ('ALL_TIME', 'All Time'),
        ('MONTHLY', 'Monthly'),
        ('WEEKLY', 'Weekly'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leaderboard_entries', limit_choices_to={'user_type': 'CUSTOMER'})
    leaderboard_type = models.CharField(max_length=40, choices=LEADERBOARD_TYPE_CHOICES)
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, default='ALL_TIME')
    score = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.0'))
    rank = models.PositiveIntegerField(default=0)
    last_calculated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['customer', 'leaderboard_type', 'period']]
        ordering = ['leaderboard_type', 'period', 'rank']
        indexes = [
            models.Index(fields=['leaderboard_type', 'period', 'rank']),
        ]
    
    def __str__(self):
        return f"{self.customer.username} - {self.leaderboard_type} ({self.period})"


class CommunityChallenge(models.Model):
    """
    Collaborative community challenges
    """
    CHALLENGE_TYPE_CHOICES = [
        ('PROJECT', 'Project Contributions'),
        ('PURCHASE', 'Purchases'),
        ('COMMUNITY', 'Community'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField()
    challenge_type = models.CharField(max_length=30, choices=CHALLENGE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    target_value = models.DecimalField(max_digits=12, decimal_places=2)
    reward_badge = models.ForeignKey(AchievementBadge, on_delete=models.SET_NULL, null=True, blank=True, related_name='rewards_challenges')
    reward_points = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['challenge_type', 'is_active']),
        ]
    
    def __str__(self):
        return self.title


class CommunityChallengeParticipant(models.Model):
    """
    Participant progress for community challenges
    """
    challenge = models.ForeignKey(CommunityChallenge, on_delete=models.CASCADE, related_name='participants')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='challenge_participations', limit_choices_to={'user_type': 'CUSTOMER'})
    contribution_value = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.0'))
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.0'))
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = [['challenge', 'customer']]
        ordering = ['-contribution_value']
        indexes = [
            models.Index(fields=['challenge', 'completed']),
        ]
    
    def __str__(self):
        return f"{self.customer.username} - {self.challenge.title}"

