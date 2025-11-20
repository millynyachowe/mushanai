from django.contrib import admin
from django.utils.html import format_html
from .models import Notification, NotificationPreference, NotificationBatch


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['icon_display', 'title', 'recipient', 'priority_badge', 'is_read', 
                    'created_at', 'action_button']
    list_filter = ['notification_type', 'priority', 'is_read', 'created_at', 'email_sent']
    search_fields = ['title', 'message', 'recipient__username', 'recipient__email']
    readonly_fields = ['icon_display', 'created_at', 'read_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Recipient', {
            'fields': ('recipient',)
        }),
        ('Notification', {
            'fields': ('notification_type', 'title', 'message', 'priority')
        }),
        ('Action', {
            'fields': ('action_url', 'action_text')
        }),
        ('Status', {
            'fields': ('is_read', 'read_at', 'email_sent')
        }),
        ('Related Object', {
            'fields': ('content_type', 'object_id'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'expires_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_unread', 'send_email_notifications']
    
    def icon_display(self, obj):
        return format_html(
            '<span style="font-size: 20px;">{}</span>',
            obj.icon
        )
    icon_display.short_description = 'Icon'
    
    def priority_badge(self, obj):
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            obj.color,
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'
    
    def action_button(self, obj):
        if obj.action_url:
            return format_html(
                '<a href="{}" class="button">View</a>',
                obj.action_url
            )
        return '-'
    action_button.short_description = 'Action'
    
    def mark_as_read(self, request, queryset):
        count = queryset.filter(is_read=False).count()
        for notif in queryset:
            notif.mark_as_read()
        self.message_user(request, f'{count} notification(s) marked as read.')
    mark_as_read.short_description = 'Mark as read'
    
    def mark_as_unread(self, request, queryset):
        count = queryset.filter(is_read=True).count()
        for notif in queryset:
            notif.mark_as_unread()
        self.message_user(request, f'{count} notification(s) marked as unread.')
    mark_as_unread.short_description = 'Mark as unread'
    
    def send_email_notifications(self, request, queryset):
        from .utils import send_email_notification
        count = 0
        for notif in queryset.filter(email_sent=False):
            send_email_notification(notif)
            count += 1
        self.message_user(request, f'{count} email notification(s) sent.')
    send_email_notifications.short_description = 'Send email notifications'


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'send_email_notifications', 'email_frequency', 
                    'enable_push_notifications', 'enable_quiet_hours']
    list_filter = ['send_email_notifications', 'email_frequency', 'enable_push_notifications', 
                   'enable_quiet_hours']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Vendor Notifications', {
            'fields': ('notify_new_order', 'notify_payment_received', 'notify_new_review',
                      'notify_low_stock', 'notify_new_supplier', 'notify_event_created',
                      'notify_promotion_ending', 'notify_discussion_reply', 'notify_manufacturing')
        }),
        ('Customer Notifications', {
            'fields': ('notify_order_status', 'notify_payment_status', 'notify_product_recommendations',
                      'notify_price_drops', 'notify_back_in_stock', 'notify_new_projects',
                      'notify_wishlist_sales', 'notify_loyalty_rewards')
        }),
        ('Email Settings', {
            'fields': ('send_email_notifications', 'email_frequency')
        }),
        ('Push Notifications', {
            'fields': ('enable_push_notifications',)
        }),
        ('Quiet Hours', {
            'fields': ('enable_quiet_hours', 'quiet_hours_start', 'quiet_hours_end')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_type(self, obj):
        return obj.user.user_type
    user_type.short_description = 'User Type'


@admin.register(NotificationBatch)
class NotificationBatchAdmin(admin.ModelAdmin):
    list_display = ['title', 'recipient_type', 'status', 'sent_count', 'total_recipients',
                    'scheduled_for', 'created_at']
    list_filter = ['status', 'recipient_type', 'created_at']
    search_fields = ['title', 'message_template']
    readonly_fields = ['sent_count', 'created_at', 'completed_at']
    filter_horizontal = ['specific_users']
    
    fieldsets = (
        ('Batch Details', {
            'fields': ('title', 'notification_type', 'message_template')
        }),
        ('Recipients', {
            'fields': ('recipient_type', 'specific_users')
        }),
        ('Status', {
            'fields': ('status', 'total_recipients', 'sent_count')
        }),
        ('Scheduling', {
            'fields': ('scheduled_for',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )

