"""
Notification System Models
Handles in-app notifications for vendors and customers
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


class Notification(models.Model):
    """
    Store notifications for users (vendors and customers)
    """
    
    # Notification Types for Vendors
    VENDOR_NOTIFICATION_TYPES = [
        ('NEW_ORDER', '🛒 New Order'),
        ('ORDER_CANCELLED', '❌ Order Cancelled'),
        ('PAYMENT_RECEIVED', '💰 Payment Received'),
        ('NEW_REVIEW', '⭐ New Review'),
        ('LOW_STOCK', '📦 Low Stock Alert'),
        ('NEW_SUPPLIER', '🏭 New Supplier Available'),
        ('SUPPLIER_APPROVED', '✅ Supplier Material Approved'),
        ('EVENT_CREATED', '📅 New Event Created'),
        ('PROMOTION_ENDING', '⏰ Promotion Ending Soon'),
        ('NEW_MESSAGE', '💬 New Message'),
        ('DISCUSSION_REPLY', '💭 Discussion Reply'),
        ('ACCOUNT_VERIFIED', '✅ Account Verified'),
        ('BADGE_EARNED', '🏆 Badge Earned'),
        ('MANUFACTURING_COMPLETE', '🏭 Manufacturing Complete'),
        ('QUALITY_CHECK_FAILED', '⚠️ Quality Check Failed'),
    ]
    
    # Notification Types for Customers
    CUSTOMER_NOTIFICATION_TYPES = [
        ('ORDER_CONFIRMED', '✅ Order Confirmed'),
        ('ORDER_SHIPPED', '🚚 Order Shipped'),
        ('ORDER_DELIVERED', '📦 Order Delivered'),
        ('PAYMENT_PROCESSED', '💳 Payment Processed'),
        ('NEW_PRODUCT_RECOMMENDATION', '✨ New Product You May Like'),
        ('PRICE_DROP', '💰 Price Drop Alert'),
        ('BACK_IN_STOCK', '📦 Back in Stock'),
        ('NEW_PROJECT', '🌍 New Community Project'),
        ('WISHLIST_SALE', '🎉 Wishlist Item on Sale'),
        ('LOYALTY_REWARD', '🎁 Loyalty Reward Earned'),
        ('VENDOR_RESPONSE', '💬 Vendor Responded'),
        ('REVIEW_HELPFUL', '👍 Review Marked Helpful'),
        ('NEW_FOLLOWER', '👤 New Follower'),
    ]
    
    # Combine all types
    NOTIFICATION_TYPES = VENDOR_NOTIFICATION_TYPES + CUSTOMER_NOTIFICATION_TYPES
    
    # Priority Levels
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]
    
    # Recipient
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    
    # Notification Details
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Priority
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Action Link (optional)
    action_url = models.CharField(max_length=500, blank=True, null=True, 
                                   help_text='URL to redirect when notification is clicked')
    action_text = models.CharField(max_length=100, blank=True, null=True,
                                    help_text='Text for action button (e.g., "View Order")')
    
    # Generic Foreign Key for related object
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object = GenericForeignKey('content_type', 'object_id')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True, 
                                      help_text='When notification should be auto-deleted')
    
    # Email sent flag
    email_sent = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['recipient', 'created_at']),
            models.Index(fields=['notification_type', 'recipient']),
        ]
    
    def __str__(self):
        return f"{self.get_notification_type_display()} for {self.recipient.username}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    def mark_as_unread(self):
        """Mark notification as unread"""
        if self.is_read:
            self.is_read = False
            self.read_at = None
            self.save(update_fields=['is_read', 'read_at'])
    
    @property
    def is_expired(self):
        """Check if notification has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    @property
    def icon(self):
        """Get emoji icon based on notification type"""
        icons = {
            'NEW_ORDER': '🛒',
            'ORDER_CANCELLED': '❌',
            'PAYMENT_RECEIVED': '💰',
            'NEW_REVIEW': '⭐',
            'LOW_STOCK': '📦',
            'NEW_SUPPLIER': '🏭',
            'SUPPLIER_APPROVED': '✅',
            'EVENT_CREATED': '📅',
            'PROMOTION_ENDING': '⏰',
            'NEW_MESSAGE': '💬',
            'DISCUSSION_REPLY': '💭',
            'ACCOUNT_VERIFIED': '✅',
            'BADGE_EARNED': '🏆',
            'MANUFACTURING_COMPLETE': '🏭',
            'QUALITY_CHECK_FAILED': '⚠️',
            'ORDER_CONFIRMED': '✅',
            'ORDER_SHIPPED': '🚚',
            'ORDER_DELIVERED': '📦',
            'PAYMENT_PROCESSED': '💳',
            'NEW_PRODUCT_RECOMMENDATION': '✨',
            'PRICE_DROP': '💰',
            'BACK_IN_STOCK': '📦',
            'NEW_PROJECT': '🌍',
            'WISHLIST_SALE': '🎉',
            'LOYALTY_REWARD': '🎁',
            'VENDOR_RESPONSE': '💬',
            'REVIEW_HELPFUL': '👍',
            'NEW_FOLLOWER': '👤',
        }
        return icons.get(self.notification_type, '🔔')
    
    @property
    def color(self):
        """Get color based on priority"""
        colors = {
            'LOW': '#6c757d',
            'MEDIUM': '#0dcaf0',
            'HIGH': '#ffc107',
            'URGENT': '#dc3545',
        }
        return colors.get(self.priority, '#0dcaf0')


class NotificationPreference(models.Model):
    """
    User preferences for notifications
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Vendor Preferences
    notify_new_order = models.BooleanField(default=True)
    notify_payment_received = models.BooleanField(default=True)
    notify_new_review = models.BooleanField(default=True)
    notify_low_stock = models.BooleanField(default=True)
    notify_new_supplier = models.BooleanField(default=True)
    notify_event_created = models.BooleanField(default=True)
    notify_promotion_ending = models.BooleanField(default=True)
    notify_discussion_reply = models.BooleanField(default=True)
    notify_manufacturing = models.BooleanField(default=True)
    
    # Customer Preferences
    notify_order_status = models.BooleanField(default=True)
    notify_payment_status = models.BooleanField(default=True)
    notify_product_recommendations = models.BooleanField(default=True)
    notify_price_drops = models.BooleanField(default=True)
    notify_back_in_stock = models.BooleanField(default=True)
    notify_new_projects = models.BooleanField(default=True)
    notify_wishlist_sales = models.BooleanField(default=True)
    notify_loyalty_rewards = models.BooleanField(default=True)
    
    # Email Preferences
    send_email_notifications = models.BooleanField(default=True)
    email_frequency = models.CharField(
        max_length=20,
        choices=[
            ('INSTANT', 'Instant'),
            ('DAILY', 'Daily Digest'),
            ('WEEKLY', 'Weekly Summary'),
            ('NEVER', 'Never'),
        ],
        default='INSTANT'
    )
    
    # Push Notification Preferences
    enable_push_notifications = models.BooleanField(default=True)
    
    # Quiet Hours
    enable_quiet_hours = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(null=True, blank=True, help_text='e.g., 22:00')
    quiet_hours_end = models.TimeField(null=True, blank=True, help_text='e.g., 08:00')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'
    
    def __str__(self):
        return f"Notification Preferences for {self.user.username}"
    
    def should_send_notification(self, notification_type):
        """Check if notification should be sent based on user preferences"""
        type_to_preference = {
            'NEW_ORDER': self.notify_new_order,
            'PAYMENT_RECEIVED': self.notify_payment_received,
            'NEW_REVIEW': self.notify_new_review,
            'LOW_STOCK': self.notify_low_stock,
            'NEW_SUPPLIER': self.notify_new_supplier,
            'EVENT_CREATED': self.notify_event_created,
            'PROMOTION_ENDING': self.notify_promotion_ending,
            'DISCUSSION_REPLY': self.notify_discussion_reply,
            'MANUFACTURING_COMPLETE': self.notify_manufacturing,
            'ORDER_CONFIRMED': self.notify_order_status,
            'ORDER_SHIPPED': self.notify_order_status,
            'ORDER_DELIVERED': self.notify_order_status,
            'PAYMENT_PROCESSED': self.notify_payment_status,
            'NEW_PRODUCT_RECOMMENDATION': self.notify_product_recommendations,
            'PRICE_DROP': self.notify_price_drops,
            'BACK_IN_STOCK': self.notify_back_in_stock,
            'NEW_PROJECT': self.notify_new_projects,
            'WISHLIST_SALE': self.notify_wishlist_sales,
            'LOYALTY_REWARD': self.notify_loyalty_rewards,
        }
        return type_to_preference.get(notification_type, True)
    
    def is_quiet_hours(self):
        """Check if current time is within quiet hours"""
        if not self.enable_quiet_hours or not self.quiet_hours_start or not self.quiet_hours_end:
            return False
        
        from datetime import datetime
        now = datetime.now().time()
        
        if self.quiet_hours_start < self.quiet_hours_end:
            return self.quiet_hours_start <= now <= self.quiet_hours_end
        else:
            # Quiet hours span midnight
            return now >= self.quiet_hours_start or now <= self.quiet_hours_end


class NotificationBatch(models.Model):
    """
    Group notifications for batch operations
    """
    title = models.CharField(max_length=200)
    notification_type = models.CharField(max_length=50, choices=Notification.NOTIFICATION_TYPES)
    message_template = models.TextField()
    
    # Recipients
    recipient_type = models.CharField(
        max_length=20,
        choices=[
            ('ALL_VENDORS', 'All Vendors'),
            ('ALL_CUSTOMERS', 'All Customers'),
            ('SPECIFIC_USERS', 'Specific Users'),
        ]
    )
    specific_users = models.ManyToManyField(User, blank=True, related_name='batch_notifications')
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('SENDING', 'Sending'),
            ('COMPLETED', 'Completed'),
            ('FAILED', 'Failed'),
        ],
        default='PENDING'
    )
    
    total_recipients = models.PositiveIntegerField(default=0)
    sent_count = models.PositiveIntegerField(default=0)
    
    # Scheduling
    scheduled_for = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_notification_batches')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification Batch'
        verbose_name_plural = 'Notification Batches'
    
    def __str__(self):
        return f"{self.title} ({self.recipient_type})"

