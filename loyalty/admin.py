from django.contrib import admin
from .models import LoyaltyAccount, SocialMediaPost, LoyaltyPointsTransaction, Reward, RewardRedemption


@admin.register(LoyaltyAccount)
class LoyaltyAccountAdmin(admin.ModelAdmin):
    list_display = ['customer', 'total_points', 'available_points', 'lifetime_points', 'created_at']
    search_fields = ['customer__username', 'customer__email']
    raw_id_fields = ['customer']
    readonly_fields = ['total_points', 'available_points', 'lifetime_points']


@admin.register(SocialMediaPost)
class SocialMediaPostAdmin(admin.ModelAdmin):
    list_display = ['customer', 'platform', 'status', 'points_awarded', 'reviewed_by', 'created_at']
    list_filter = ['status', 'platform', 'created_at']
    search_fields = ['customer__username', 'post_url', 'description']
    raw_id_fields = ['customer', 'reviewed_by']
    readonly_fields = ['created_at', 'reviewed_at']
    
    actions = ['approve_posts', 'reject_posts']
    
    def approve_posts(self, request, queryset):
        for post in queryset.filter(status='PENDING'):
            post.status = 'APPROVED'
            post.reviewed_by = request.user
            from django.utils import timezone
            post.reviewed_at = timezone.now()
            post.save()
        self.message_user(request, f"{queryset.count()} posts approved.")
    approve_posts.short_description = "Approve selected posts"
    
    def reject_posts(self, request, queryset):
        queryset.update(status='REJECTED', reviewed_by=request.user)
        from django.utils import timezone
        queryset.update(reviewed_at=timezone.now())
        self.message_user(request, f"{queryset.count()} posts rejected.")


@admin.register(LoyaltyPointsTransaction)
class LoyaltyPointsTransactionAdmin(admin.ModelAdmin):
    list_display = ['loyalty_account', 'transaction_type', 'source', 'points', 'balance_after', 'created_at']
    list_filter = ['transaction_type', 'source', 'created_at']
    search_fields = ['loyalty_account__customer__username']
    raw_id_fields = ['loyalty_account', 'order', 'social_post', 'reward_redemption']
    readonly_fields = ['created_at']


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ['name', 'reward_type', 'points_required', 'is_active', 'stock_quantity', 'total_redemptions', 'created_at']
    list_filter = ['reward_type', 'is_active', 'is_featured', 'created_at']
    search_fields = ['name', 'description']
    raw_id_fields = ['special_product', 'project']


@admin.register(RewardRedemption)
class RewardRedemptionAdmin(admin.ModelAdmin):
    list_display = ['customer', 'reward', 'points_used', 'status', 'created_at', 'fulfilled_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer__username', 'reward__name']
    raw_id_fields = ['customer', 'reward', 'order']
    readonly_fields = ['created_at', 'updated_at']
