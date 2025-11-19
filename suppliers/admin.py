from django.contrib import admin
from django.contrib import messages
from django.utils import timezone
from .models import (
    SupplierProfile, RawMaterialCategory, RawMaterial, MaterialUsage,
    RawMaterialPurchase, RawMaterialInquiry
)


@admin.register(SupplierProfile)
class SupplierProfileAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'brand_name', 'supplier', 'contact_number', 'is_verified', 'added_by', 'added_at']
    list_filter = ['is_verified', 'added_at']
    search_fields = ['company_name', 'brand_name', 'supplier__username', 'contact_number', 'email']
    raw_id_fields = ['supplier', 'added_by']
    readonly_fields = ['added_at', 'updated_at']
    
    fieldsets = (
        ('Company Information', {
            'fields': ('company_name', 'brand_name', 'description')
        }),
        ('Contact Details', {
            'fields': ('contact_number', 'email', 'address')
        }),
        ('User Account', {
            'fields': ('supplier', 'is_verified')
        }),
        ('Admin Tracking', {
            'fields': ('added_by', 'added_at', 'updated_at')
        }),
    )
    
    actions = ['verify_suppliers', 'send_credentials_email']
    
    def verify_suppliers(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} supplier(s) verified successfully.', messages.SUCCESS)
    verify_suppliers.short_description = "Verify selected suppliers"
    
    def send_credentials_email(self, request, queryset):
        """Send login credentials to suppliers"""
        from django.core.mail import send_mail
        from django.conf import settings
        
        count = 0
        for supplier_profile in queryset:
            supplier_user = supplier_profile.supplier
            try:
                # Send email with login instructions
                subject = 'Welcome to Mushanai - Supplier Portal Access'
                message = f"""
Dear {supplier_profile.company_name},

Welcome to the Mushanai Supplier Portal!

Your account has been created. Here are your login details:

Username: {supplier_user.username}
Email: {supplier_user.email}

Login URL: {settings.SITE_URL}/accounts/login/

After logging in, you can:
- Add raw materials to your catalog
- Manage your inventory
- View and respond to inquiries from vendors
- Track your sales

If you have any questions, please contact us at {settings.DEFAULT_FROM_EMAIL}

Best regards,
The Mushanai Team
                """
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [supplier_profile.email or supplier_user.email],
                    fail_silently=False,
                )
                count += 1
            except Exception as e:
                self.message_user(request, f'Error sending email to {supplier_profile.company_name}: {str(e)}', messages.ERROR)
        
        if count > 0:
            self.message_user(request, f'Credentials sent to {count} supplier(s).', messages.SUCCESS)
    send_credentials_email.short_description = "Send login credentials to selected suppliers"


@admin.register(RawMaterialCategory)
class RawMaterialCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']


@admin.register(RawMaterial)
class RawMaterialAdmin(admin.ModelAdmin):
    list_display = ['name', 'supplier', 'category', 'unit_price', 'approval_status', 'is_locally_sourced', 'is_available', 'purchase_count', 'created_at']
    list_filter = ['approval_status', 'is_locally_sourced', 'is_available', 'is_hidden', 'category', 'created_at']
    search_fields = ['name', 'description', 'supplier__company_name', 'origin']
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ['supplier', 'category', 'approved_by']
    readonly_fields = ['usage_count', 'purchase_count', 'total_revenue', 'created_at', 'updated_at', 'approved_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'detailed_description', 'image')
        }),
        ('Classification', {
            'fields': ('supplier', 'category', 'is_featured', 'is_hidden')
        }),
        ('Pricing & Availability', {
            'fields': ('unit_price', 'unit', 'min_order_quantity', 'stock_quantity', 'is_available')
        }),
        ('Approval Status', {
            'fields': ('approval_status', 'approved_by', 'approved_at', 'rejection_reason')
        }),
        ('Origin & Sustainability', {
            'fields': ('origin', 'is_locally_sourced', 'sustainability_info', 'environmental_impact')
        }),
        ('Analytics', {
            'fields': ('usage_count', 'purchase_count', 'total_revenue')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['approve_materials', 'reject_materials', 'mark_available', 'mark_unavailable']
    
    def approve_materials(self, request, queryset):
        updated = queryset.filter(approval_status='PENDING').update(
            approval_status='APPROVED',
            approved_by=request.user,
            approved_at=timezone.now()
        )
        self.message_user(request, f'{updated} material(s) approved successfully.', messages.SUCCESS)
    approve_materials.short_description = "Approve selected materials"
    
    def reject_materials(self, request, queryset):
        updated = queryset.filter(approval_status='PENDING').update(
            approval_status='REJECTED',
            approved_by=request.user,
            approved_at=timezone.now()
        )
        self.message_user(request, f'{updated} material(s) rejected.', messages.WARNING)
    reject_materials.short_description = "Reject selected materials"
    
    def mark_available(self, request, queryset):
        updated = queryset.update(is_available=True)
        self.message_user(request, f'{updated} material(s) marked as available.', messages.SUCCESS)
    mark_available.short_description = "Mark as available"
    
    def mark_unavailable(self, request, queryset):
        updated = queryset.update(is_available=False)
        self.message_user(request, f'{updated} material(s) marked as unavailable.', messages.INFO)
    mark_unavailable.short_description = "Mark as unavailable"


@admin.register(MaterialUsage)
class MaterialUsageAdmin(admin.ModelAdmin):
    list_display = ['material', 'product', 'quantity', 'unit', 'created_at']
    search_fields = ['material__name', 'product__name']
    raw_id_fields = ['material', 'product']
    readonly_fields = ['created_at']


@admin.register(RawMaterialPurchase)
class RawMaterialPurchaseAdmin(admin.ModelAdmin):
    list_display = ['purchase_number', 'vendor', 'material', 'supplier', 'quantity', 'total_amount', 'status', 'payment_status', 'ordered_at']
    list_filter = ['status', 'payment_status', 'ordered_at']
    search_fields = ['purchase_number', 'vendor__username', 'material__name', 'supplier__company_name']
    raw_id_fields = ['vendor', 'material', 'supplier']
    readonly_fields = ['purchase_number', 'ordered_at', 'confirmed_at', 'delivered_at', 'updated_at']
    date_hierarchy = 'ordered_at'
    
    fieldsets = (
        ('Purchase Information', {
            'fields': ('purchase_number', 'vendor', 'material', 'supplier')
        }),
        ('Order Details', {
            'fields': ('quantity', 'unit', 'unit_price', 'total_amount')
        }),
        ('Status', {
            'fields': ('status', 'payment_status')
        }),
        ('Delivery', {
            'fields': ('delivery_address', 'delivery_city', 'delivery_phone')
        }),
        ('Notes', {
            'fields': ('vendor_notes', 'supplier_notes', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('ordered_at', 'confirmed_at', 'delivered_at', 'updated_at')
        }),
    )
    
    actions = ['mark_confirmed', 'mark_shipped', 'mark_delivered']
    
    def mark_confirmed(self, request, queryset):
        updated = queryset.filter(status='PENDING').update(
            status='CONFIRMED',
            confirmed_at=timezone.now()
        )
        self.message_user(request, f'{updated} purchase(s) confirmed.', messages.SUCCESS)
    mark_confirmed.short_description = "Mark as confirmed"
    
    def mark_shipped(self, request, queryset):
        updated = queryset.update(status='SHIPPED')
        self.message_user(request, f'{updated} purchase(s) marked as shipped.', messages.SUCCESS)
    mark_shipped.short_description = "Mark as shipped"
    
    def mark_delivered(self, request, queryset):
        updated = queryset.update(
            status='DELIVERED',
            delivered_at=timezone.now()
        )
        self.message_user(request, f'{updated} purchase(s) marked as delivered.', messages.SUCCESS)
    mark_delivered.short_description = "Mark as delivered"


@admin.register(RawMaterialInquiry)
class RawMaterialInquiryAdmin(admin.ModelAdmin):
    list_display = ['subject', 'vendor', 'material', 'supplier', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['subject', 'message', 'vendor__username', 'material__name', 'supplier__company_name']
    raw_id_fields = ['vendor', 'material', 'supplier']
    readonly_fields = ['created_at', 'updated_at', 'responded_at']
    
    fieldsets = (
        ('Inquiry Details', {
            'fields': ('vendor', 'material', 'supplier', 'subject', 'message')
        }),
        ('Contact Information', {
            'fields': ('vendor_email', 'vendor_phone')
        }),
        ('Response', {
            'fields': ('status', 'supplier_response', 'responded_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['mark_read', 'mark_closed']
    
    def mark_read(self, request, queryset):
        updated = queryset.filter(status='NEW').update(status='READ')
        self.message_user(request, f'{updated} inquiry(ies) marked as read.', messages.SUCCESS)
    mark_read.short_description = "Mark as read"
    
    def mark_closed(self, request, queryset):
        updated = queryset.update(status='CLOSED')
        self.message_user(request, f'{updated} inquiry(ies) closed.', messages.SUCCESS)
    mark_closed.short_description = "Close inquiries"
