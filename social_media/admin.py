from django.contrib import admin
from django.contrib import messages
from .models import (
    SocialMediaAccount, ProductSocialPost, SocialMediaTemplate,
    SocialMediaAnalytics, ScheduledPost
)


@admin.register(SocialMediaAccount)
class SocialMediaAccountAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'platform', 'account_name', 'status', 'auto_post', 'total_posts', 'last_post_at', 'connected_at']
    list_filter = ['platform', 'status', 'auto_post', 'connected_at']
    search_fields = ['vendor__username', 'account_name', 'account_username']
    raw_id_fields = ['vendor']
    readonly_fields = ['total_posts', 'last_post_at', 'connected_at', 'updated_at']
    
    fieldsets = (
        ('Account Information', {
            'fields': ('vendor', 'platform', 'account_name', 'account_id', 'account_username')
        }),
        ('Authentication', {
            'fields': ('access_token', 'token_expires_at', 'refresh_token'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('auto_post', 'status')
        }),
        ('Statistics', {
            'fields': ('total_posts', 'last_post_at')
        }),
        ('Timestamps', {
            'fields': ('connected_at', 'updated_at')
        }),
    )
    
    actions = ['mark_active', 'mark_expired', 'disable_auto_post']
    
    def mark_active(self, request, queryset):
        updated = queryset.update(status='ACTIVE')
        self.message_user(request, f'{updated} account(s) marked as active.', messages.SUCCESS)
    mark_active.short_description = "Mark as active"
    
    def mark_expired(self, request, queryset):
        updated = queryset.update(status='EXPIRED')
        self.message_user(request, f'{updated} account(s) marked as expired.', messages.WARNING)
    mark_expired.short_description = "Mark as expired"
    
    def disable_auto_post(self, request, queryset):
        updated = queryset.update(auto_post=False)
        self.message_user(request, f'Auto-post disabled for {updated} account(s).', messages.INFO)
    disable_auto_post.short_description = "Disable auto-post"


@admin.register(ProductSocialPost)
class ProductSocialPostAdmin(admin.ModelAdmin):
    list_display = ['product', 'vendor', 'social_account', 'status', 'likes_count', 'comments_count', 'reach', 'posted_at']
    list_filter = ['status', 'social_account__platform', 'posted_at', 'created_at']
    search_fields = ['product__name', 'vendor__username', 'post_text']
    raw_id_fields = ['product', 'vendor', 'social_account']
    readonly_fields = ['posted_at', 'created_at', 'updated_at']
    date_hierarchy = 'posted_at'
    
    fieldsets = (
        ('Post Information', {
            'fields': ('product', 'vendor', 'social_account')
        }),
        ('Post Content', {
            'fields': ('post_text', 'post_id', 'post_url')
        }),
        ('Status', {
            'fields': ('status', 'error_message')
        }),
        ('Engagement', {
            'fields': ('likes_count', 'comments_count', 'shares_count', 'reach')
        }),
        ('Timestamps', {
            'fields': ('posted_at', 'created_at', 'updated_at')
        }),
    )
    
    actions = ['mark_as_posted', 'retry_failed']
    
    def mark_as_posted(self, request, queryset):
        updated = queryset.update(status='POSTED')
        self.message_user(request, f'{updated} post(s) marked as posted.', messages.SUCCESS)
    mark_as_posted.short_description = "Mark as posted"
    
    def retry_failed(self, request, queryset):
        count = queryset.filter(status='FAILED').update(status='PENDING')
        self.message_user(request, f'{count} failed post(s) reset to pending for retry.', messages.INFO)
    retry_failed.short_description = "Retry failed posts"


@admin.register(SocialMediaTemplate)
class SocialMediaTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'vendor', 'platform', 'is_default', 'created_at']
    list_filter = ['platform', 'is_default', 'created_at']
    search_fields = ['name', 'template_text', 'vendor__username']
    raw_id_fields = ['vendor']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Template Information', {
            'fields': ('vendor', 'platform', 'name', 'is_default')
        }),
        ('Template Content', {
            'fields': ('template_text', 'hashtags'),
            'description': 'Use {product_name}, {price}, {description}, {url}, {brand}, {category} as placeholders'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(SocialMediaAnalytics)
class SocialMediaAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'social_account', 'month', 'total_posts', 'successful_posts', 'total_likes', 'total_reach']
    list_filter = ['month', 'social_account__platform']
    search_fields = ['vendor__username']
    raw_id_fields = ['vendor', 'social_account']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'month'


@admin.register(ScheduledPost)
class ScheduledPostAdmin(admin.ModelAdmin):
    list_display = ['product', 'vendor', 'social_account', 'scheduled_for', 'status', 'posted_at']
    list_filter = ['status', 'social_account__platform', 'scheduled_for']
    search_fields = ['product__name', 'vendor__username', 'post_text']
    raw_id_fields = ['product', 'vendor', 'social_account']
    readonly_fields = ['posted_at', 'created_at', 'updated_at']
    date_hierarchy = 'scheduled_for'
    
    fieldsets = (
        ('Post Information', {
            'fields': ('product', 'vendor', 'social_account')
        }),
        ('Schedule', {
            'fields': ('scheduled_for', 'status')
        }),
        ('Content', {
            'fields': ('post_text',)
        }),
        ('Result', {
            'fields': ('post_id', 'error_message', 'posted_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['cancel_posts', 'reschedule_failed']
    
    def cancel_posts(self, request, queryset):
        updated = queryset.filter(status='SCHEDULED').update(status='CANCELLED')
        self.message_user(request, f'{updated} scheduled post(s) cancelled.', messages.WARNING)
    cancel_posts.short_description = "Cancel scheduled posts"
    
    def reschedule_failed(self, request, queryset):
        from django.utils import timezone
        from datetime import timedelta
        
        failed = queryset.filter(status='FAILED')
        for post in failed:
            post.scheduled_for = timezone.now() + timedelta(hours=1)
            post.status = 'SCHEDULED'
            post.save()
        
        self.message_user(request, f'{failed.count()} failed post(s) rescheduled for 1 hour from now.', messages.INFO)
    reschedule_failed.short_description = "Reschedule failed posts"

