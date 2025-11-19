from django.contrib import admin
from django.contrib import messages
from .models import (
    BillOfMaterials, BOMItem, ManufacturingOrder,
    QualityCheck, ProductionWorker, ManufacturingAnalytics
)


class BOMItemInline(admin.TabularInline):
    model = BOMItem
    extra = 1
    raw_id_fields = ['raw_material']
    readonly_fields = ['cost']
    fields = ['raw_material', 'quantity', 'unit', 'notes', 'cost']


@admin.register(BillOfMaterials)
class BillOfMaterialsAdmin(admin.ModelAdmin):
    list_display = ['product', 'vendor', 'batch_size', 'total_cost_per_unit', 'suggested_selling_price', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['product__name', 'vendor__username']
    raw_id_fields = ['product', 'vendor']
    readonly_fields = ['total_material_cost', 'total_cost_per_unit', 'suggested_selling_price', 'created_at', 'updated_at']
    inlines = [BOMItemInline]
    
    fieldsets = (
        ('Product', {
            'fields': ('product', 'vendor', 'is_active')
        }),
        ('Production', {
            'fields': ('batch_size', 'production_time_hours', 'instructions')
        }),
        ('Costing (Auto-calculated)', {
            'fields': ('total_material_cost', 'labor_cost_per_unit', 'overhead_cost_per_unit', 'total_cost_per_unit')
        }),
        ('Pricing', {
            'fields': ('markup_percentage', 'suggested_selling_price')
        }),
    )
    
    actions = ['recalculate_costs']
    
    def recalculate_costs(self, request, queryset):
        count = 0
        for bom in queryset:
            bom.calculate_costs()
            count += 1
        self.message_user(request, f'Costs recalculated for {count} BOM(s).', messages.SUCCESS)
    recalculate_costs.short_description = "Recalculate costs for selected BOMs"


class ProductionWorkerInline(admin.TabularInline):
    model = ProductionWorker
    extra = 0
    fields = ['worker_name', 'role', 'hours_worked', 'hourly_rate', 'total_payment', 'work_date']
    readonly_fields = ['total_payment']


class QualityCheckInline(admin.TabularInline):
    model = QualityCheck
    extra = 0
    readonly_fields = ['checked_at']


@admin.register(ManufacturingOrder)
class ManufacturingOrderAdmin(admin.ModelAdmin):
    list_display = ['mo_number', 'vendor', 'product', 'quantity_to_produce', 'quantity_produced', 'status', 'priority', 'scheduled_date', 'created_at']
    list_filter = ['status', 'priority', 'scheduled_date', 'created_at']
    search_fields = ['mo_number', 'vendor__username', 'product__name']
    raw_id_fields = ['vendor', 'product', 'bom']
    readonly_fields = ['mo_number', 'estimated_cost', 'local_materials_percentage', 'created_at', 'updated_at', 'started_at', 'completed_at']
    date_hierarchy = 'created_at'
    inlines = [QualityCheckInline, ProductionWorkerInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('mo_number', 'vendor', 'product', 'bom')
        }),
        ('Production', {
            'fields': ('quantity_to_produce', 'quantity_produced', 'quantity_approved', 'quantity_rejected')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority', 'scheduled_date')
        }),
        ('Costing', {
            'fields': ('estimated_cost', 'actual_cost')
        }),
        ('Impact', {
            'fields': ('local_materials_percentage',)
        }),
        ('Notes', {
            'fields': ('production_notes',)
        }),
        ('Timestamps', {
            'fields': ('started_at', 'completed_at', 'created_at', 'updated_at')
        }),
    )
    
    actions = ['start_orders', 'complete_orders', 'calculate_local_percentage']
    
    def start_orders(self, request, queryset):
        count = 0
        for order in queryset.filter(status='READY'):
            order.start_production()
            count += 1
        self.message_user(request, f'{count} order(s) started.', messages.SUCCESS)
    start_orders.short_description = "Start selected orders"
    
    def complete_orders(self, request, queryset):
        count = 0
        for order in queryset.filter(status='IN_PROGRESS'):
            order.complete_production()
            count += 1
        self.message_user(request, f'{count} order(s) completed and inventory updated.', messages.SUCCESS)
    complete_orders.short_description = "Complete selected orders"
    
    def calculate_local_percentage(self, request, queryset):
        for order in queryset:
            order.calculate_local_percentage()
        self.message_user(request, f'Local percentage calculated for {queryset.count()} order(s).', messages.SUCCESS)
    calculate_local_percentage.short_description = "Calculate local materials %"


@admin.register(QualityCheck)
class QualityCheckAdmin(admin.ModelAdmin):
    list_display = ['manufacturing_order', 'checked_by', 'quantity_checked', 'quantity_approved', 'quantity_rejected', 'status', 'checked_at']
    list_filter = ['status', 'checked_at']
    search_fields = ['manufacturing_order__mo_number']
    raw_id_fields = ['manufacturing_order', 'checked_by']
    readonly_fields = ['checked_at']


@admin.register(ProductionWorker)
class ProductionWorkerAdmin(admin.ModelAdmin):
    list_display = ['worker_name', 'manufacturing_order', 'role', 'hours_worked', 'total_payment', 'work_date']
    list_filter = ['role', 'work_date']
    search_fields = ['worker_name', 'manufacturing_order__mo_number']
    raw_id_fields = ['manufacturing_order', 'vendor']
    readonly_fields = ['total_payment', 'created_at']
    date_hierarchy = 'work_date'


@admin.register(ManufacturingAnalytics)
class ManufacturingAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'month', 'total_orders', 'total_units_produced', 'local_materials_percentage', 'total_workers', 'community_contribution']
    list_filter = ['month']
    search_fields = ['vendor__username']
    raw_id_fields = ['vendor']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'month'

