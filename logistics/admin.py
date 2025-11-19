from django.contrib import admin
from .models import DeliveryGroup, SharedDelivery, DeliveryRoute, LogisticsCostShare


class SharedDeliveryInline(admin.TabularInline):
    model = SharedDelivery
    extra = 0


@admin.register(DeliveryGroup)
class DeliveryGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'status', 'destination_city', 'total_logistics_cost', 'scheduled_date', 'created_at']
    list_filter = ['status', 'destination_country', 'created_at']
    search_fields = ['name', 'origin_address', 'destination_city']
    inlines = [SharedDeliveryInline]
    readonly_fields = ['created_at', 'updated_at', 'completed_at']


@admin.register(DeliveryRoute)
class DeliveryRouteAdmin(admin.ModelAdmin):
    list_display = ['delivery_group', 'total_distance_km', 'estimated_time_minutes', 'driver_name', 'created_at']
    search_fields = ['delivery_group__name', 'driver_name', 'driver_phone']
    raw_id_fields = ['delivery_group']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SharedDelivery)
class SharedDeliveryAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'delivery_group', 'allocated_cost', 'has_paid', 'is_confirmed', 'joined_at']
    list_filter = ['has_paid', 'is_confirmed', 'joined_at']
    search_fields = ['vendor__username', 'delivery_group__name', 'delivery_address']
    raw_id_fields = ['vendor', 'delivery_group', 'order']


@admin.register(LogisticsCostShare)
class LogisticsCostShareAdmin(admin.ModelAdmin):
    list_display = ['shared_delivery', 'total_allocated', 'calculation_method', 'created_at']
    list_filter = ['calculation_method', 'created_at']
    raw_id_fields = ['shared_delivery']
    readonly_fields = ['created_at']
