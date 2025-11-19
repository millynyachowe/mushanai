from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class SocialMediaAccount(models.Model):
    """
    Vendor's connected social media accounts
    """
    PLATFORM_CHOICES = [
        ('FACEBOOK', 'Facebook'),
        ('INSTAGRAM', 'Instagram'),
        ('TWITTER', 'Twitter'),
        ('WHATSAPP_BUSINESS', 'WhatsApp Business'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('EXPIRED', 'Token Expired'),
        ('DISCONNECTED', 'Disconnected'),
        ('ERROR', 'Error'),
    ]
    
    vendor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='social_media_accounts',
        limit_choices_to={'user_type': 'VENDOR'}
    )
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    
    # Account details
    account_name = models.CharField(max_length=200, help_text='Page/Account name')
    account_id = models.CharField(max_length=200, help_text='Platform account ID')
    account_username = models.CharField(max_length=200, blank=True, null=True)
    
    # Authentication
    access_token = models.TextField(help_text='OAuth access token')
    token_expires_at = models.DateTimeField(null=True, blank=True)
    refresh_token = models.TextField(blank=True, null=True)
    
    # Settings
    auto_post = models.BooleanField(default=False, help_text='Auto-post new products')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    
    # Tracking
    total_posts = models.PositiveIntegerField(default=0)
    last_post_at = models.DateTimeField(null=True, blank=True)
    
    connected_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['vendor', 'platform', 'account_id']
        ordering = ['-connected_at']
        verbose_name = 'Social Media Account'
        verbose_name_plural = 'Social Media Accounts'
    
    def __str__(self):
        return f"{self.vendor.username} - {self.platform} ({self.account_name})"
    
    def is_token_valid(self):
        """Check if access token is still valid"""
        if not self.token_expires_at:
            return True  # No expiry set
        return timezone.now() < self.token_expires_at
    
    def mark_expired(self):
        """Mark token as expired"""
        self.status = 'EXPIRED'
        self.save()


class ProductSocialPost(models.Model):
    """
    Track products posted to social media
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('POSTED', 'Posted Successfully'),
        ('FAILED', 'Failed'),
        ('DELETED', 'Deleted'),
    ]
    
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='product_social_posts')
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vendor_social_posts')
    social_account = models.ForeignKey(SocialMediaAccount, on_delete=models.CASCADE, related_name='platform_posts')
    
    # Post details
    post_id = models.CharField(max_length=200, blank=True, null=True, help_text='Platform post ID')
    post_url = models.URLField(blank=True, null=True, help_text='Link to post')
    post_text = models.TextField(help_text='Post caption/text')
    
    # Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    error_message = models.TextField(blank=True, null=True)
    
    # Engagement (if available from API)
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    shares_count = models.PositiveIntegerField(default=0)
    reach = models.PositiveIntegerField(default=0, help_text='Number of people reached')
    
    posted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['vendor', 'status']),
            models.Index(fields=['product', 'social_account']),
        ]
    
    def __str__(self):
        return f"{self.product.name} → {self.social_account.platform}"


class SocialMediaTemplate(models.Model):
    """
    Templates for social media posts
    """
    vendor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='social_templates',
        limit_choices_to={'user_type': 'VENDOR'}
    )
    platform = models.CharField(max_length=20, choices=SocialMediaAccount.PLATFORM_CHOICES)
    
    name = models.CharField(max_length=100, help_text='Template name for reference')
    template_text = models.TextField(
        help_text='Use {product_name}, {price}, {description}, {url} as placeholders'
    )
    
    # Hashtags
    hashtags = models.TextField(
        blank=True, 
        null=True,
        help_text='Comma-separated hashtags (without #)'
    )
    
    is_default = models.BooleanField(default=False, help_text='Use as default for this platform')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_default', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.platform})"
    
    def get_hashtags_list(self):
        """Get hashtags as list"""
        if not self.hashtags:
            return []
        return [f"#{tag.strip()}" for tag in self.hashtags.split(',') if tag.strip()]
    
    def render(self, product):
        """Render template with product data"""
        from django.conf import settings
        
        text = self.template_text
        replacements = {
            '{product_name}': product.name,
            '{price}': f"${product.price}",
            '{description}': product.description[:200] if product.description else '',
            '{url}': f"{settings.SITE_URL}/products/{product.slug}/",
            '{brand}': product.brand or '',
            '{category}': product.category.name if product.category else '',
        }
        
        for key, value in replacements.items():
            text = text.replace(key, str(value))
        
        # Add hashtags
        hashtags = self.get_hashtags_list()
        if hashtags:
            text += '\n\n' + ' '.join(hashtags)
        
        return text


class SocialMediaAnalytics(models.Model):
    """
    Monthly analytics for social media performance
    """
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_analytics')
    social_account = models.ForeignKey(SocialMediaAccount, on_delete=models.CASCADE, related_name='analytics')
    month = models.DateField()
    
    # Posting activity
    total_posts = models.PositiveIntegerField(default=0)
    successful_posts = models.PositiveIntegerField(default=0)
    failed_posts = models.PositiveIntegerField(default=0)
    
    # Engagement
    total_likes = models.PositiveIntegerField(default=0)
    total_comments = models.PositiveIntegerField(default=0)
    total_shares = models.PositiveIntegerField(default=0)
    total_reach = models.PositiveIntegerField(default=0)
    
    # Click-through (if trackable)
    clicks_to_website = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['vendor', 'social_account', 'month']
        ordering = ['-month']
        verbose_name = 'Social Media Analytics'
        verbose_name_plural = 'Social Media Analytics'
    
    def __str__(self):
        return f"{self.vendor.username} - {self.social_account.platform} ({self.month.strftime('%B %Y')})"


class ScheduledPost(models.Model):
    """
    Schedule posts for future publishing
    """
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('POSTED', 'Posted'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='scheduled_posts')
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scheduled_posts')
    social_account = models.ForeignKey(SocialMediaAccount, on_delete=models.CASCADE, related_name='scheduled_posts')
    
    post_text = models.TextField()
    scheduled_for = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    
    # Result
    post_id = models.CharField(max_length=200, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    posted_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['scheduled_for']
        indexes = [
            models.Index(fields=['status', 'scheduled_for']),
        ]
    
    def __str__(self):
        return f"{self.product.name} → {self.social_account.platform} @ {self.scheduled_for}"

