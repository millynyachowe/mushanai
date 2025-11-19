from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()


class CommunityProject(models.Model):
    """
    Community development projects that customers can vote to fund
    """
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('ACTIVE', 'Active'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True, null=True)
    
    # Funding
    target_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    current_funding = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    
    # Status and dates
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    start_date = models.DateField(blank=True, null=True)
    expected_completion_date = models.DateField(blank=True, null=True)
    actual_completion_date = models.DateField(blank=True, null=True)
    
    # Display
    image = models.ImageField(upload_to='projects/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_most_popular = models.BooleanField(default=False)  # For default voting logic
    
    # Approval
    is_approved = models.BooleanField(default=False)  # Admin approval required
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_projects', limit_choices_to={'user_type': 'ADMIN'})
    approved_at = models.DateTimeField(blank=True, null=True)
    
    # Tracking
    total_votes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_most_popular', '-total_votes', '-created_at']
        indexes = [
            models.Index(fields=['status', 'is_featured', 'is_approved']),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def funding_percentage(self):
        if self.target_amount == 0:
            return 0
        return (self.current_funding / self.target_amount) * 100
    
    @property
    def is_active(self):
        return self.status in ['ACTIVE', 'IN_PROGRESS'] and self.is_approved


class ProjectMilestone(models.Model):
    """
    Milestones for tracking project progress
    """
    project = models.ForeignKey(CommunityProject, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    target_date = models.DateField(blank=True, null=True)
    completed_date = models.DateField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.project.title} - {self.title}"


class ProjectProposal(models.Model):
    """
    Project proposals submitted by users (need admin approval)
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    proposer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_proposals')
    title = models.CharField(max_length=200)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True, null=True)
    expense_breakdown = models.TextField(blank=True, null=True)
    timeline = models.TextField(blank=True, null=True)
    
    # Funding goal
    target_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_proposals', limit_choices_to={'user_type': 'ADMIN'})
    reviewed_at = models.DateTimeField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    # If approved, link to created project
    approved_project = models.OneToOneField(CommunityProject, on_delete=models.SET_NULL, null=True, blank=True, related_name='proposal')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"


class ProjectVote(models.Model):
    """
    Customer votes for projects (allocated during checkout)
    """
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_votes', limit_choices_to={'user_type': 'CUSTOMER'})
    project = models.ForeignKey(CommunityProject, on_delete=models.CASCADE, related_name='votes')
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='project_votes', null=True, blank=True)
    vote_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    is_default_vote = models.BooleanField(default=False)  # Whether this was the default vote
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['customer', 'order']  # One vote per customer per order
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.customer.username} voted {self.vote_amount} for {self.project.title}"
