from django.contrib import admin
from .models import MinistryDashboard, MaterialUsageAnalytics, SearchTrendAnalytics, SkillGapAnalysis, LocalBrandGrowth, MinistryReport


@admin.register(MinistryDashboard)
class MinistryDashboardAdmin(admin.ModelAdmin):
    list_display = ['ministry', 'show_job_postings', 'show_project_progress', 'show_material_analytics', 'updated_at']
    search_fields = ['ministry__username', 'ministry__email']
    raw_id_fields = ['ministry']


@admin.register(MaterialUsageAnalytics)
class MaterialUsageAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['material', 'times_used', 'total_quantity_used', 'products_using', 'usage_trend', 'period_start', 'period_end']
    list_filter = ['usage_trend', 'period_type', 'period_start', 'period_end']
    search_fields = ['material__name', 'material__supplier__company_name']
    raw_id_fields = ['material']
    readonly_fields = ['last_calculated']


@admin.register(SearchTrendAnalytics)
class SearchTrendAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['search_query', 'search_count', 'unavailable_count', 'is_product_available', 'potential_skill_gap', 'period_start']
    list_filter = ['is_product_available', 'potential_skill_gap', 'period_start', 'period_end']
    search_fields = ['search_query']
    readonly_fields = ['last_calculated']
    ordering = ['-unavailable_count', '-search_count']


@admin.register(SkillGapAnalysis)
class SkillGapAnalysisAdmin(admin.ModelAdmin):
    list_display = ['skill_name', 'category', 'severity', 'unavailable_product_count', 'job_posting_count', 'is_resolved', 'created_at']
    list_filter = ['severity', 'is_resolved', 'category', 'created_at']
    search_fields = ['skill_name', 'description', 'category__name']
    raw_id_fields = ['category']
    readonly_fields = ['last_analyzed']


@admin.register(LocalBrandGrowth)
class LocalBrandGrowthAdmin(admin.ModelAdmin):
    list_display = ['brand', 'total_revenue', 'revenue_growth_percentage', 'total_orders', 'order_growth_percentage', 'period_start', 'period_end']
    list_filter = ['period_start', 'period_end']
    search_fields = ['brand__name']
    raw_id_fields = ['brand']
    readonly_fields = ['last_calculated']
    ordering = ['-revenue_growth_percentage']


@admin.register(MinistryReport)
class MinistryReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'ministry', 'report_type', 'period_start', 'period_end', 'created_at']
    list_filter = ['report_type', 'created_at', 'period_start']
    search_fields = ['title', 'ministry__username', 'summary']
    raw_id_fields = ['ministry']
    readonly_fields = ['created_at']
