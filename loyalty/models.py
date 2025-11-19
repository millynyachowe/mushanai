from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()


class LoyaltyAccount(models.Model):
    """
    Loyalty account for customers to track points
    """
    customer = models.OneToOneField(User, on_delete=models.CASCADE, related_name='loyalty_account', limit_choices_to={'user_type': 'CUSTOMER'})
    total_points = models.PositiveIntegerField(default=0)
    available_points = models.PositiveIntegerField(default=0)
    lifetime_points = models.PositiveIntegerField(default=0)  # Total points ever earned
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-total_points']
    
    def __str__(self):
        return f"Loyalty Account for {self.customer.username} - {self.available_points} points"


class SocialMediaPost(models.Model):
    """
    Customer social media posts for earning points
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_posts', limit_choices_to={'user_type': 'CUSTOMER'})
    post_url = models.URLField()  # Link to social media post
    platform = models.CharField(max_length=50)  # Facebook, Instagram, Twitter, etc.
    description = models.TextField(blank=True, null=True)
    
    # Approval
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_posts', limit_choices_to={'user_type': 'ADMIN'})
    reviewed_at = models.DateTimeField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    # Points
    points_awarded = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.customer.username} - {self.platform} post - {self.status}"


class LoyaltyPointsTransaction(models.Model):
    """
    Track all loyalty points transactions (earned, redeemed, expired)
    """
    TRANSACTION_TYPE_CHOICES = [
        ('EARNED', 'Earned'),
        ('REDEEMED', 'Redeemed'),
        ('EXPIRED', 'Expired'),
        ('ADJUSTED', 'Adjusted'),
    ]
    
    SOURCE_CHOICES = [
        ('PURCHASE', 'Purchase'),
        ('SOCIAL_POST', 'Social Media Post'),
        ('REFERRAL', 'Referral'),
        ('REDEMPTION', 'Reward Redemption'),
        ('ADMIN', 'Admin Adjustment'),
        ('EXPIRATION', 'Point Expiration'),
    ]
    
    loyalty_account = models.ForeignKey(LoyaltyAccount, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    points = models.IntegerField()  # Can be negative for redemptions
    balance_after = models.PositiveIntegerField()
    
    # Related objects
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='loyalty_transactions')
    social_post = models.ForeignKey(SocialMediaPost, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    reward_redemption = models.ForeignKey('RewardRedemption', on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['loyalty_account', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.loyalty_account.customer.username} - {self.transaction_type} {abs(self.points)} points"


class Reward(models.Model):
    """
    Rewards available for redemption with loyalty points
    """
    REWARD_TYPE_CHOICES = [
        ('DISCOUNT', 'Discount'),
        ('PRODUCT', 'Special Product'),
        ('PROJECT', 'Project Contribution'),
        ('OTHER', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    reward_type = models.CharField(max_length=20, choices=REWARD_TYPE_CHOICES)
    
    # Points required
    points_required = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    
    # Reward details
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    special_product = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True, blank=True, related_name='rewards')
    project = models.ForeignKey('projects.CommunityProject', on_delete=models.SET_NULL, null=True, blank=True, related_name='rewards')
    
    # Availability
    is_active = models.BooleanField(default=True)
    stock_quantity = models.PositiveIntegerField(null=True, blank=True)  # For limited rewards
    track_stock = models.BooleanField(default=False)
    
    # Display
    image = models.ImageField(upload_to='rewards/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    
    # Usage limits
    max_redemptions_per_user = models.PositiveIntegerField(null=True, blank=True)
    total_redemptions = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['points_required', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.points_required} points"
    
    @property
    def is_available(self):
        if not self.is_active:
            return False
        if self.track_stock and self.stock_quantity is not None:
            return self.stock_quantity > 0
        return True


class RewardRedemption(models.Model):
    """
    Customer reward redemptions
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('FULFILLED', 'Fulfilled'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reward_redemptions', limit_choices_to={'user_type': 'CUSTOMER'})
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE, related_name='redemptions')
    points_used = models.PositiveIntegerField()
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Fulfillment
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='reward_redemptions')
    fulfillment_notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    fulfilled_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.customer.username} redeemed {self.reward.name}"
