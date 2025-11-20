from django.contrib import admin
from django import forms
from .models import (
    VendorProfile,
    VendorCompany,
    VendorAnalytics,
    CashReceipt,
    JobPosting,
    VendorBadge,
    VendorPaymentOption,
    VendorDeliveryZone,
    VendorEvent,
)

# Import promotion admin classes
from .admin_promotions import PromotionAdmin, ProductPromotionAdmin, PromotionAnalyticsAdmin


@admin.register(VendorBadge)
class VendorBadgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'badge_type', 'is_active', 'min_rating', 'min_reviews', 'min_sales', 'created_at']
    list_filter = ['is_active', 'badge_type', 'created_at']
    search_fields = ['name', 'description']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'badge_type', 'description', 'icon', 'color', 'is_active')
        }),
        ('Auto-Assignment Criteria', {
            'fields': ('min_rating', 'min_reviews', 'min_sales', 'min_revenue', 
                      'max_response_time_hours', 'min_local_products', 'min_eco_products'),
            'description': 'Set criteria for automatic badge assignment. Leave blank to assign manually.'
        }),
    )
    
    actions = ['assign_badges_to_all_vendors']
    
    def assign_badges_to_all_vendors(self, request, queryset):
        """Admin action to reassign badges to all vendors"""
        from .models import VendorProfile
        vendors = VendorProfile.objects.all()
        count = 0
        for vendor in vendors:
            vendor.update_metrics()
            count += 1
        self.message_user(request, f"Badges reassigned to {count} vendors.")
    assign_badges_to_all_vendors.short_description = "Reassign badges to all vendors"


@admin.register(VendorProfile)
class VendorProfileAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'vendor', 'is_verified', 'overall_rating', 'total_reviews', 'has_advanced_dashboard', 'accepts_shared_logistics', 'created_at']
    list_filter = ['is_verified', 'has_advanced_dashboard', 'accepts_shared_logistics', 'badges', 'created_at']
    search_fields = ['company_name', 'vendor__username', 'vendor__email', 'registration_number']
    raw_id_fields = ['vendor']
    filter_horizontal = ['badges']
    readonly_fields = ['overall_rating', 'total_reviews', 'average_response_time_hours', 'ratings_last_calculated']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('vendor', 'company_name', 'registration_number', 'tax_id')
        }),
        ('Business Information', {
            'fields': ('business_type', 'description', 'logo', 'business_phone', 'business_email', 'business_address')
        }),
        ('Status & Features', {
            'fields': ('is_verified', 'has_advanced_dashboard', 'accepts_shared_logistics', 'auto_approve_orders')
        }),
        ('Projects', {
            'fields': ('participate_in_projects', 'selected_project')
        }),
        ('Delivery Settings', {
            'fields': ('delivery_free_city', 'delivery_free_radius_km', 'delivery_base_fee', 'delivery_per_km_fee'),
        }),
        ('Ratings & Badges', {
            'fields': ('overall_rating', 'total_reviews', 'average_response_time_hours', 'ratings_last_calculated', 'badges')
        }),
    )
    
    actions = ['update_ratings', 'reassign_badges', 'verify_vendors', 'unverify_vendors']
    
    def update_ratings(self, request, queryset):
        """Update ratings for selected vendors"""
        for vendor in queryset:
            vendor.calculate_rating()
        self.message_user(request, f"Ratings updated for {queryset.count()} vendors.")
    update_ratings.short_description = "Update ratings for selected vendors"
    
    def reassign_badges(self, request, queryset):
        """Reassign badges for selected vendors"""
        for vendor in queryset:
            vendor.update_metrics()
        self.message_user(request, f"Badges reassigned for {queryset.count()} vendors.")
    reassign_badges.short_description = "Reassign badges for selected vendors"
    
    def verify_vendors(self, request, queryset):
        """Verify selected vendors"""
        queryset.update(is_verified=True)
        # Reassign badges to update verified badge
        for vendor in queryset:
            vendor.assign_badges()
        self.message_user(request, f"{queryset.count()} vendors verified.")
    verify_vendors.short_description = "Verify selected vendors"
    
    def unverify_vendors(self, request, queryset):
        """Unverify selected vendors"""
        queryset.update(is_verified=False)
        # Reassign badges to remove verified badge
        for vendor in queryset:
            vendor.assign_badges()
        self.message_user(request, f"{queryset.count()} vendors unverified.")
    unverify_vendors.short_description = "Unverify selected vendors"


@admin.register(VendorCompany)
class VendorCompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'vendor', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'vendor__username']
    raw_id_fields = ['vendor']


@admin.register(VendorAnalytics)
class VendorAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'total_revenue', 'total_orders', 'total_products', 'last_calculated']
    list_filter = ['last_calculated']
    search_fields = ['vendor__username']
    raw_id_fields = ['vendor']
    readonly_fields = ['last_calculated', 'created_at']


@admin.register(CashReceipt)
class CashReceiptAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'vendor', 'amount', 'customer_name', 'is_walk_in', 'receipt_date']
    list_filter = ['is_walk_in', 'receipt_date']
    search_fields = ['receipt_number', 'vendor__username', 'customer_name']
    raw_id_fields = ['vendor']
    date_hierarchy = 'receipt_date'


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ['title', 'vendor', 'job_type', 'location', 'status', 'posted_date']
    list_filter = ['status', 'job_type', 'posted_date']
    search_fields = ['title', 'vendor__username', 'description']
    raw_id_fields = ['vendor']
    date_hierarchy = 'posted_date'


@admin.register(VendorPaymentOption)
class VendorPaymentOptionAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'payment_type', 'phone_number', 'merchant_name', 'is_enabled', 'created_at']
    list_filter = ['payment_type', 'is_enabled', 'created_at']
    search_fields = ['vendor__username', 'vendor__email', 'phone_number', 'merchant_name']
    raw_id_fields = ['vendor']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(VendorDeliveryZone)
class VendorDeliveryZoneAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'city', 'fee', 'is_active', 'updated_at']
    list_filter = ['city', 'is_active', 'updated_at']
    search_fields = ['vendor__username', 'vendor__email', 'city']
    raw_id_fields = ['vendor']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(VendorEvent)
class VendorEventAdmin(admin.ModelAdmin):
    class VendorEventAdminForm(forms.ModelForm):
        payment_methods = forms.MultipleChoiceField(
            choices=VendorEvent.PAYMENT_METHOD_CHOICES,
            widget=forms.CheckboxSelectMultiple,
            required=False
        )
        
        class Meta:
            model = VendorEvent
            fields = '__all__'
    
    form = VendorEventAdminForm
    list_display = ['title', 'location', 'start_datetime', 'price', 'is_global', 'created_at']
    list_filter = ['is_global', 'start_datetime', 'payment_methods']
    search_fields = ['title', 'location', 'description']
    filter_horizontal = ['vendors']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Event Details', {
            'fields': ('title', 'description', 'image', 'location', ('start_datetime', 'end_datetime'))
        }),
        ('Pricing', {
            'fields': ('price', 'early_bird_price', 'early_bird_deadline')
        }),
        ('Audience & Payments', {
            'fields': ('is_global', 'vendors', 'payment_methods')
        }),
    )
