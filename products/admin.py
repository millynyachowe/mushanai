from django.contrib import admin
from .models import Category, Brand, Product, ProductImage, ProductReview, ProductView, ReviewPhoto, ReviewHelpfulVote, ProductTag, CategoryDisplaySchedule


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'tier', 'display_header', 'is_active', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description', 'display_header', 'display_tagline']
    list_filter = ['tier', 'is_active', 'created_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'image', 'is_active')
        }),
        ('Display Customization', {
            'fields': ('display_header', 'display_tagline', 'tier'),
            'description': 'Customize how this category appears on the homepage'
        }),
    )


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_local', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['is_local', 'created_at']
    search_fields = ['name', 'description']


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'vendor', 'offline_vendor_name', 'category', 'price', 'stock_quantity', 'is_featured', 'is_active', 'is_made_from_local_materials', 'search_count', 'view_count', 'created_at']
    list_filter = ['is_featured', 'is_active', 'is_made_from_local_materials', 'category', 'vendor', 'created_at']
    search_fields = ['name', 'description', 'sku', 'vendor__username', 'offline_vendor_name']
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ['vendor']
    inlines = [ProductImageInline]
    readonly_fields = ['search_count', 'unavailable_requests', 'view_count']
    
    filter_horizontal = ['tags']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'short_description', 'vendor', 'category', 'brand', 'tags')
        }),
        ('Offline Vendor (for admin-managed brands without accounts)', {
            'fields': ('offline_vendor_name', 'offline_vendor_phone', 'offline_vendor_address'),
            'classes': ('collapse',),
        }),
        ('Pricing', {
            'fields': ('price', 'compare_at_price')
        }),
        ('Inventory', {
            'fields': ('sku', 'stock_quantity', 'track_inventory')
        }),
        ('Display', {
            'fields': ('is_featured', 'is_active', 'is_made_from_local_materials', 'primary_image')
        }),
        ('Analytics', {
            'fields': ('search_count', 'unavailable_requests', 'view_count')
        }),
    )


class ReviewPhotoInline(admin.TabularInline):
    model = ReviewPhoto
    extra = 1
    fields = ['image', 'alt_text', 'order']


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'customer', 'rating', 'is_verified_purchase', 'is_approved', 'has_vendor_response', 'helpful_count', 'created_at']
    list_filter = ['rating', 'is_approved', 'is_verified_purchase', 'created_at']
    search_fields = ['product__name', 'customer__username', 'comment', 'title']
    raw_id_fields = ['product', 'customer']
    readonly_fields = ['created_at', 'updated_at', 'vendor_response_date']
    inlines = [ReviewPhotoInline]
    
    fieldsets = (
        ('Review Information', {
            'fields': ('product', 'customer', 'rating', 'title', 'comment')
        }),
        ('Status', {
            'fields': ('is_verified_purchase', 'is_approved')
        }),
        ('Vendor Response', {
            'fields': ('vendor_response', 'vendor_response_date')
        }),
        ('Engagement', {
            'fields': ('helpful_count',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['approve_reviews', 'reject_reviews', 'mark_verified_purchase']
    
    def has_vendor_response(self, obj):
        return bool(obj.vendor_response)
    has_vendor_response.boolean = True
    has_vendor_response.short_description = 'Has Response'
    
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        
        # Update vendor ratings and badges when reviews are approved
        from vendors.models import VendorProfile
        vendors_to_update = set()
        for review in queryset:
            vendor = review.product.vendor
            try:
                vendor_profile = vendor.vendor_profile
                vendors_to_update.add(vendor_profile)
            except:
                pass
        
        # Update metrics for all affected vendors
        for vendor_profile in vendors_to_update:
            vendor_profile.update_metrics()
        
        self.message_user(request, f"{queryset.count()} reviews approved.")
    approve_reviews.short_description = "Approve selected reviews"
    
    def reject_reviews(self, request, queryset):
        queryset.update(is_approved=False)
        
        # Update vendor ratings when reviews are rejected
        from vendors.models import VendorProfile
        vendors_to_update = set()
        for review in queryset:
            vendor = review.product.vendor
            try:
                vendor_profile = vendor.vendor_profile
                vendors_to_update.add(vendor_profile)
            except:
                pass
        
        # Update metrics for all affected vendors
        for vendor_profile in vendors_to_update:
            vendor_profile.update_metrics()
        
        self.message_user(request, f"{queryset.count()} reviews rejected.")
    
    def mark_verified_purchase(self, request, queryset):
        queryset.update(is_verified_purchase=True)
        self.message_user(request, f"{queryset.count()} reviews marked as verified purchase.")


@admin.register(ReviewPhoto)
class ReviewPhotoAdmin(admin.ModelAdmin):
    list_display = ['review', 'order', 'created_at']
    list_filter = ['created_at']
    search_fields = ['review__product__name', 'review__customer__username']
    raw_id_fields = ['review']


@admin.register(ReviewHelpfulVote)
class ReviewHelpfulVoteAdmin(admin.ModelAdmin):
    list_display = ['review', 'customer', 'session_key', 'created_at']
    list_filter = ['created_at']
    search_fields = ['review__product__name', 'review__customer__username', 'customer__username']
    raw_id_fields = ['review', 'customer']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        return False  # Votes are created automatically


@admin.register(ProductView)
class ProductViewAdmin(admin.ModelAdmin):
    list_display = ['product', 'customer', 'session_key', 'ip_address', 'viewed_at']
    list_filter = ['viewed_at']
    search_fields = ['product__name', 'customer__username', 'session_key', 'ip_address']
    raw_id_fields = ['product', 'customer']
    readonly_fields = ['viewed_at']
    date_hierarchy = 'viewed_at'
    
    def has_add_permission(self, request):
        return False  # Views are created automatically


@admin.register(ProductTag)
class ProductTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color', 'is_active', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'color', 'is_active')
        }),
    )


@admin.register(CategoryDisplaySchedule)
class CategoryDisplayScheduleAdmin(admin.ModelAdmin):
    list_display = ['category', 'period', 'start_date', 'end_date', 'display_order', 'is_active', 'is_current_display']
    list_filter = ['period', 'is_active', 'start_date', 'end_date']
    search_fields = ['category__name', 'category__display_header']
    date_hierarchy = 'start_date'
    fieldsets = (
        ('Schedule Information', {
            'fields': ('category', 'period', 'start_date', 'end_date', 'display_order', 'is_active')
        }),
    )
    
    def is_current_display(self, obj):
        return obj.is_current()
    is_current_display.boolean = True
    is_current_display.short_description = 'Currently Active'
