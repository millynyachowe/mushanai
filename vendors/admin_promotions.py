"""
Admin interface for vendor promotions
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Promotion, ProductPromotion, PromotionAnalytics


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ['name', 'vendor_name', 'discount_badge', 'style_badge', 'status_badge', 
                    'date_range', 'product_count', 'revenue', 'conversion_rate_display', 'is_active']
    list_filter = ['status', 'style', 'is_active', 'created_at', 'start_date']
    search_fields = ['name', 'vendor__username', 'vendor__email', 'description']
    readonly_fields = ['view_count', 'click_count', 'conversion_count', 'total_revenue', 
                       'created_at', 'updated_at', 'conversion_rate_display']
    filter_horizontal = []
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('vendor', 'company', 'name', 'description', 'style')
        }),
        ('Discount Settings', {
            'fields': ('discount_percentage',)
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date', 'status', 'is_active')
        }),
        ('Display Options', {
            'fields': ('show_badge', 'show_countdown', 'featured')
        }),
        ('Terms & Conditions', {
            'fields': ('terms',),
            'classes': ('collapse',)
        }),
        ('Analytics', {
            'fields': ('view_count', 'click_count', 'conversion_count', 'total_revenue', 'conversion_rate_display'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_promotions', 'pause_promotions', 'update_statuses']
    
    def vendor_name(self, obj):
        return obj.vendor.get_full_name() or obj.vendor.username
    vendor_name.short_description = 'Vendor'
    
    def discount_badge(self, obj):
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{:.0f}% OFF</span>',
            obj.get_badge_color(),
            obj.discount_percentage
        )
    discount_badge.short_description = 'Discount'
    
    def style_badge(self, obj):
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            obj.get_badge_color(),
            obj.get_style_display_name()
        )
    style_badge.short_description = 'Style'
    
    def status_badge(self, obj):
        colors = {
            'DRAFT': '#9e9e9e',
            'SCHEDULED': '#2196f3',
            'ACTIVE': '#4caf50',
            'EXPIRED': '#f44336',
            'PAUSED': '#ff9800',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#9e9e9e'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def date_range(self, obj):
        return format_html(
            '{}<br><small style="color: #666;">to {}</small>',
            obj.start_date.strftime('%b %d, %Y'),
            obj.end_date.strftime('%b %d, %Y')
        )
    date_range.short_description = 'Date Range'
    
    def product_count(self, obj):
        count = obj.product_count
        return format_html('<strong>{}</strong> products', count)
    product_count.short_description = 'Products'
    
    def revenue(self, obj):
        return f'${obj.total_revenue:,.2f}'
    revenue.short_description = 'Revenue'
    
    def conversion_rate_display(self, obj):
        rate = obj.conversion_rate
        return f'{rate:.1f}%'
    conversion_rate_display.short_description = 'Conversion Rate'
    
    def activate_promotions(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} promotion(s) activated.')
    activate_promotions.short_description = 'Activate selected promotions'
    
    def pause_promotions(self, request, queryset):
        queryset.update(is_active=False, status='PAUSED')
        self.message_user(request, f'{queryset.count()} promotion(s) paused.')
    pause_promotions.short_description = 'Pause selected promotions'
    
    def update_statuses(self, request, queryset):
        for promo in queryset:
            promo.update_status()
            promo.save()
        self.message_user(request, f'{queryset.count()} promotion(s) status updated.')
    update_statuses.short_description = 'Update statuses based on dates'


@admin.register(ProductPromotion)
class ProductPromotionAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'promotion_name', 'original_price', 'discounted_price_display', 
                    'savings_display', 'is_active', 'sales_count']
    list_filter = ['promotion__status', 'promotion__style', 'added_at']
    search_fields = ['product__name', 'promotion__name']
    readonly_fields = ['original_price', 'discounted_price', 'savings_amount', 
                       'view_count', 'click_count', 'sales_count', 'revenue', 'added_at', 'updated_at']
    raw_id_fields = ['promotion', 'product']
    
    fieldsets = (
        ('Link', {
            'fields': ('promotion', 'product')
        }),
        ('Pricing', {
            'fields': ('original_price', 'discounted_price', 'savings_amount')
        }),
        ('Analytics', {
            'fields': ('view_count', 'click_count', 'sales_count', 'revenue'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('added_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def product_name(self, obj):
        return obj.product.name
    product_name.short_description = 'Product'
    
    def promotion_name(self, obj):
        return obj.promotion.name
    promotion_name.short_description = 'Promotion'
    
    def discounted_price_display(self, obj):
        return format_html(
            '<strong style="color: #4caf50;">${:.2f}</strong>',
            obj.discounted_price
        )
    discounted_price_display.short_description = 'Discounted Price'
    
    def savings_display(self, obj):
        return format_html(
            '<span style="color: #f44336;">-${:.2f} ({:.0f}%)</span>',
            obj.savings_amount,
            obj.savings_percentage
        )
    savings_display.short_description = 'Savings'
    
    def is_active(self, obj):
        return obj.is_active
    is_active.boolean = True
    is_active.short_description = 'Active'


@admin.register(PromotionAnalytics)
class PromotionAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['promotion_name', 'date', 'views', 'clicks', 'sales', 
                    'revenue_display', 'conversion_rate']
    list_filter = ['date', 'promotion']
    search_fields = ['promotion__name']
    readonly_fields = ['promotion', 'date', 'views', 'clicks', 'sales', 'revenue', 
                       'unique_visitors', 'created_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Promotion', {
            'fields': ('promotion', 'date')
        }),
        ('Traffic', {
            'fields': ('views', 'unique_visitors', 'clicks')
        }),
        ('Sales', {
            'fields': ('sales', 'revenue')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def promotion_name(self, obj):
        return obj.promotion.name
    promotion_name.short_description = 'Promotion'
    
    def revenue_display(self, obj):
        return f'${obj.revenue:,.2f}'
    revenue_display.short_description = 'Revenue'
    
    def conversion_rate(self, obj):
        if obj.clicks == 0:
            return '0%'
        rate = (obj.sales / obj.clicks) * 100
        return f'{rate:.1f}%'
    conversion_rate.short_description = 'Conversion'
    
    def has_add_permission(self, request):
        # Analytics are created automatically
        return False

