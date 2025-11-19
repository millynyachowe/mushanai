from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class MinistryDashboard(models.Model):
    """
    Ministry dashboard configuration and preferences
    """
    ministry = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ministry_dashboard', limit_choices_to={'user_type': 'MINISTRY'})
    
    # Dashboard preferences
    show_job_postings = models.BooleanField(default=True)
    show_project_progress = models.BooleanField(default=True)
    show_material_analytics = models.BooleanField(default=True)
    show_search_trends = models.BooleanField(default=True)
    show_skill_gaps = models.BooleanField(default=True)
    show_brand_growth = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ministry_dashboards'
    
    def __str__(self):
        return f"Dashboard for {self.ministry.username}"


class MaterialUsageAnalytics(models.Model):
    """
    Analytics on raw material usage in manufacturing
    """
    material = models.ForeignKey('suppliers.RawMaterial', on_delete=models.CASCADE, related_name='usage_analytics')
    
    # Usage metrics
    times_used = models.PositiveIntegerField(default=0)
    total_quantity_used = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    products_using = models.PositiveIntegerField(default=0)
    
    # Time period
    period_start = models.DateField()
    period_end = models.DateField()
    period_type = models.CharField(max_length=20, default='monthly')  # daily, weekly, monthly, yearly
    
    # Trends
    usage_trend = models.CharField(max_length=20, blank=True, null=True)  # increasing, decreasing, stable
    growth_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    
    last_calculated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Material Usage Analytics'
        ordering = ['-times_used']
        unique_together = ['material', 'period_start', 'period_end']
    
    def __str__(self):
        return f"Analytics for {self.material.name} - {self.period_start} to {self.period_end}"


class SearchTrendAnalytics(models.Model):
    """
    Analytics on search trends to identify skill gaps and unavailable items
    """
    # Search data
    search_query = models.CharField(max_length=500)
    search_count = models.PositiveIntegerField(default=0)
    
    # Results
    results_returned = models.PositiveIntegerField(default=0)
    is_product_available = models.BooleanField(default=False)
    unavailable_count = models.PositiveIntegerField(default=0)  # Times searched but no results
    
    # Time period
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Skill gap indicator
    potential_skill_gap = models.BooleanField(default=False)
    skill_gap_reason = models.TextField(blank=True, null=True)
    
    last_calculated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Search Trend Analytics'
        ordering = ['-unavailable_count', '-search_count']
        indexes = [
            models.Index(fields=['potential_skill_gap', 'unavailable_count']),
        ]
    
    def __str__(self):
        return f"Search: {self.search_query} - {self.unavailable_count} unavailable"


class SkillGapAnalysis(models.Model):
    """
    Skill gap analysis based on unavailable items and job postings
    """
    SEVERITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    category = models.ForeignKey('products.Category', on_delete=models.SET_NULL, null=True, blank=True, related_name='skill_gaps')
    skill_name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    # Indicators
    unavailable_product_count = models.PositiveIntegerField(default=0)
    job_posting_count = models.PositiveIntegerField(default=0)
    search_demand_count = models.PositiveIntegerField(default=0)
    
    # Assessment
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='MEDIUM')
    estimated_impact = models.TextField(blank=True, null=True)
    
    # Recommendations
    recommended_actions = models.TextField(blank=True, null=True)
    
    # Status
    is_resolved = models.BooleanField(default=False)
    resolved_date = models.DateField(blank=True, null=True)
    
    last_analyzed = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Skill Gap Analyses'
        ordering = ['-severity', '-unavailable_product_count']
    
    def __str__(self):
        return f"Skill Gap: {self.skill_name} - {self.get_severity_display()}"


class LocalBrandGrowth(models.Model):
    """
    Track growth metrics for local brands
    """
    brand = models.ForeignKey('products.Brand', on_delete=models.CASCADE, related_name='growth_metrics')
    
    # Growth metrics
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    revenue_growth_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Sales metrics
    total_orders = models.PositiveIntegerField(default=0)
    order_growth_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Product metrics
    active_products = models.PositiveIntegerField(default=0)
    new_products_count = models.PositiveIntegerField(default=0)
    
    # Time period
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Vendor growth
    vendor_count = models.PositiveIntegerField(default=0)
    
    last_calculated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Local Brand Growth Metrics'
        ordering = ['-revenue_growth_percentage']
        unique_together = ['brand', 'period_start', 'period_end']
    
    def __str__(self):
        return f"Growth: {self.brand.name} - {self.revenue_growth_percentage}%"


class MinistryReport(models.Model):
    """
    Generated reports for ministries
    """
    REPORT_TYPE_CHOICES = [
        ('JOB_POSTINGS', 'Job Postings Summary'),
        ('PROJECT_PROGRESS', 'Project Progress'),
        ('MATERIAL_USAGE', 'Material Usage Analysis'),
        ('SEARCH_TRENDS', 'Search Trends'),
        ('SKILL_GAPS', 'Skill Gap Analysis'),
        ('BRAND_GROWTH', 'Local Brand Growth'),
        ('COMPREHENSIVE', 'Comprehensive Report'),
    ]
    
    ministry = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports', limit_choices_to={'user_type': 'MINISTRY'})
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    
    # Report data
    report_data = models.JSONField()  # Store report data
    summary = models.TextField(blank=True, null=True)
    
    # Time period
    period_start = models.DateField(blank=True, null=True)
    period_end = models.DateField(blank=True, null=True)
    
    # File generation
    pdf_file = models.FileField(upload_to='ministry_reports/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.ministry.username}"
