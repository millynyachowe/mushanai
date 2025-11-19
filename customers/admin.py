from django.contrib import admin
from .models import (
    CustomerDashboard, CustomerImpactMetrics, VotingHistory, SearchHistory,
    ReferralProgram, Referral, CustomerTestimonial, SocialShare,
    Wishlist, WishlistItem, PriceAlert, GiftRegistry, GiftRegistryItem,
    BackInStockAlert, VendorSubscription, ProjectNotificationSubscription, NotificationLog,
    ImpactLevel, AchievementBadge, CustomerAchievement,
    LeaderboardEntry, CommunityChallenge, CommunityChallengeParticipant
)


@admin.register(CustomerDashboard)
class CustomerDashboardAdmin(admin.ModelAdmin):
    list_display = ['customer', 'default_project', 'show_abandoned_carts', 'updated_at']
    search_fields = ['customer__username', 'customer__email']
    raw_id_fields = ['customer', 'default_project']
    filter_horizontal = ['last_viewed_products']


@admin.register(CustomerImpactMetrics)
class CustomerImpactMetricsAdmin(admin.ModelAdmin):
    list_display = ['customer', 'impact_points', 'current_level', 'total_badges_earned', 'total_project_contributions', 'projects_supported_count', 'total_spent', 'total_orders', 'last_calculated']
    search_fields = ['customer__username', 'customer__email']
    raw_id_fields = ['customer']
    readonly_fields = ['total_project_contributions', 'projects_supported_count', 'total_votes_cast',
                      'total_spent', 'total_orders', 'total_items_purchased', 
                      'local_brand_purchases', 'local_material_product_purchases',
                      'impact_points', 'total_badges_earned', 'last_calculated']


@admin.register(VotingHistory)
class VotingHistoryAdmin(admin.ModelAdmin):
    list_display = ['customer', 'project', 'vote_amount', 'is_default_vote', 'order', 'created_at']
    list_filter = ['is_default_vote', 'created_at']
    search_fields = ['customer__username', 'project__title', 'order__order_number']
    raw_id_fields = ['customer', 'project', 'order']
    readonly_fields = ['created_at']


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ['query', 'customer', 'results_count', 'was_product_found', 'created_at']
    list_filter = ['was_product_found', 'created_at']
    search_fields = ['query', 'customer__username']
    raw_id_fields = ['customer']
    readonly_fields = ['created_at']


@admin.register(ReferralProgram)
class ReferralProgramAdmin(admin.ModelAdmin):
    list_display = ['referrer', 'referral_code', 'is_active', 'total_referrals', 'successful_signups', 'successful_purchases', 'total_points_earned', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['referrer__username', 'referrer__email', 'referral_code']
    raw_id_fields = ['referrer']
    readonly_fields = ['total_referrals', 'successful_signups', 'successful_purchases', 'total_points_earned', 'total_rewards_earned', 'created_at', 'updated_at']


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ['referral_program', 'referred_user', 'referral_code_used', 'status', 'referrer_points_awarded', 'referred_points_awarded', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['referral_program__referrer__username', 'referred_user__username', 'referral_code_used']
    raw_id_fields = ['referral_program', 'referred_user', 'first_order']
    readonly_fields = ['created_at', 'updated_at', 'signed_up_at', 'first_purchase_at']


@admin.register(CustomerTestimonial)
class CustomerTestimonialAdmin(admin.ModelAdmin):
    list_display = ['customer', 'vendor', 'rating', 'status', 'is_featured', 'is_verified_purchase', 'created_at']
    list_filter = ['status', 'is_featured', 'is_verified_purchase', 'rating', 'created_at']
    search_fields = ['customer__username', 'vendor__username', 'testimonial', 'title']
    raw_id_fields = ['customer', 'vendor', 'order', 'reviewed_by']
    readonly_fields = ['created_at', 'updated_at', 'reviewed_at']
    
    actions = ['approve_testimonials', 'reject_testimonials', 'feature_testimonials']
    
    def approve_testimonials(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='APPROVED', reviewed_by=request.user, reviewed_at=timezone.now())
        self.message_user(request, f'{updated} testimonial(s) approved.')
    approve_testimonials.short_description = 'Approve selected testimonials'
    
    def reject_testimonials(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='REJECTED', reviewed_by=request.user, reviewed_at=timezone.now())
        self.message_user(request, f'{updated} testimonial(s) rejected.')
    reject_testimonials.short_description = 'Reject selected testimonials'
    
    def feature_testimonials(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} testimonial(s) featured.')
    feature_testimonials.short_description = 'Feature selected testimonials'


@admin.register(SocialShare)
class SocialShareAdmin(admin.ModelAdmin):
    list_display = ['share_type', 'platform', 'user', 'product', 'project', 'vendor', 'created_at']
    list_filter = ['share_type', 'platform', 'created_at']
    search_fields = ['user__username', 'product__name', 'project__title', 'vendor__username']
    raw_id_fields = ['user', 'product', 'project', 'vendor']
    readonly_fields = ['created_at']


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['name', 'customer', 'is_default', 'is_public', 'item_count', 'total_value', 'created_at']
    list_filter = ['is_default', 'is_public', 'created_at']
    search_fields = ['name', 'customer__username', 'customer__email', 'share_token']
    raw_id_fields = ['customer']
    readonly_fields = ['share_token', 'created_at', 'updated_at', 'item_count', 'total_value']


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'wishlist', 'priority', 'added_at']
    list_filter = ['added_at', 'priority']
    search_fields = ['product__name', 'wishlist__name', 'wishlist__customer__username']
    raw_id_fields = ['wishlist', 'product']
    readonly_fields = ['added_at', 'updated_at']


@admin.register(PriceAlert)
class PriceAlertAdmin(admin.ModelAdmin):
    list_display = ['product', 'customer', 'status', 'original_price', 'target_price', 'target_percentage', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['product__name', 'customer__username', 'customer__email']
    raw_id_fields = ['customer', 'product']
    readonly_fields = ['created_at', 'updated_at', 'notified_at']
    
    actions = ['check_price_drops']
    
    def check_price_drops(self, request, queryset):
        """Manually check for price drops"""
        triggered = 0
        for alert in queryset.filter(status='ACTIVE'):
            if alert.check_price_drop():
                triggered += 1
        self.message_user(request, f'{triggered} price alert(s) triggered.')
    check_price_drops.short_description = 'Check for price drops on selected alerts'


@admin.register(GiftRegistry)
class GiftRegistryAdmin(admin.ModelAdmin):
    list_display = ['name', 'customer', 'status', 'event_date', 'item_count', 'completion_percentage', 'created_at']
    list_filter = ['status', 'is_public', 'created_at', 'event_date']
    search_fields = ['name', 'customer__username', 'customer__email', 'share_token']
    raw_id_fields = ['customer']
    readonly_fields = ['share_token', 'created_at', 'updated_at', 'item_count', 'total_value', 'purchased_count', 'completion_percentage']


@admin.register(GiftRegistryItem)
class GiftRegistryItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'registry', 'quantity', 'quantity_purchased', 'remaining_quantity', 'is_fulfilled', 'added_at']
    list_filter = ['added_at', 'priority']
    search_fields = ['product__name', 'registry__name', 'registry__customer__username']
    raw_id_fields = ['registry', 'product', 'purchased_by', 'purchase_order']
    readonly_fields = ['added_at', 'updated_at', 'remaining_quantity', 'is_fulfilled']


@admin.register(BackInStockAlert)
class BackInStockAlertAdmin(admin.ModelAdmin):
    list_display = ['product', 'customer', 'status', 'notification_sent', 'created_at']
    list_filter = ['status', 'notification_sent', 'created_at']
    search_fields = ['product__name', 'customer__username', 'customer__email']
    raw_id_fields = ['customer', 'product']
    readonly_fields = ['created_at', 'updated_at', 'notified_at']


@admin.register(VendorSubscription)
class VendorSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['customer', 'vendor', 'notify_new_products', 'notify_promotions', 'created_at']
    list_filter = ['notify_new_products', 'notify_promotions', 'created_at']
    search_fields = ['customer__username', 'vendor__username']
    raw_id_fields = ['customer', 'vendor']
    readonly_fields = ['created_at', 'updated_at', 'last_notified_at']


@admin.register(ProjectNotificationSubscription)
class ProjectNotificationSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['customer', 'project', 'notify_milestones', 'notify_updates', 'created_at']
    list_filter = ['notify_milestones', 'notify_updates', 'created_at']
    search_fields = ['customer__username', 'project__title']
    raw_id_fields = ['customer', 'project']
    readonly_fields = ['created_at', 'updated_at', 'last_notified_at']


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ['customer', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'customer__username', 'message']
    raw_id_fields = ['customer', 'product', 'vendor', 'project', 'milestone', 'price_alert']
    readonly_fields = ['created_at', 'read_at']


@admin.register(ImpactLevel)
class ImpactLevelAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'min_points', 'color']
    search_fields = ['display_name', 'name']
    ordering = ['min_points']


@admin.register(AchievementBadge)
class AchievementBadgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'points_reward', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'description', 'criteria_text']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(CustomerAchievement)
class CustomerAchievementAdmin(admin.ModelAdmin):
    list_display = ['customer', 'badge', 'status', 'progress', 'earned_at']
    list_filter = ['status', 'earned_at']
    search_fields = ['customer__username', 'badge__name']
    raw_id_fields = ['customer', 'badge']


@admin.register(LeaderboardEntry)
class LeaderboardEntryAdmin(admin.ModelAdmin):
    list_display = ['customer', 'leaderboard_type', 'period', 'score', 'rank']
    list_filter = ['leaderboard_type', 'period']
    search_fields = ['customer__username']
    raw_id_fields = ['customer']


@admin.register(CommunityChallenge)
class CommunityChallengeAdmin(admin.ModelAdmin):
    list_display = ['title', 'challenge_type', 'start_date', 'end_date', 'target_value', 'is_active']
    list_filter = ['challenge_type', 'is_active', 'start_date']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['reward_badge']


@admin.register(CommunityChallengeParticipant)
class CommunityChallengeParticipantAdmin(admin.ModelAdmin):
    list_display = ['challenge', 'customer', 'contribution_value', 'progress_percentage', 'completed']
    list_filter = ['completed']
    search_fields = ['challenge__title', 'customer__username']
    raw_id_fields = ['challenge', 'customer']
