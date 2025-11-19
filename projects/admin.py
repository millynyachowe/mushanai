from django.contrib import admin
from django.utils import timezone
import re
from .models import CommunityProject, ProjectMilestone, ProjectVote, ProjectProposal


class ProjectMilestoneInline(admin.TabularInline):
    model = ProjectMilestone
    extra = 1
    ordering = ['order']


@admin.register(CommunityProject)
class CommunityProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'is_approved', 'current_funding', 'target_amount', 'funding_percentage', 'total_votes', 'is_most_popular', 'is_featured', 'created_at']
    list_filter = ['status', 'is_approved', 'is_featured', 'is_most_popular', 'created_at']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['current_funding', 'total_votes', 'funding_percentage', 'approved_at']
    inlines = [ProjectMilestoneInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'short_description', 'image')
        }),
        ('Funding', {
            'fields': ('target_amount', 'current_funding', 'total_votes')
        }),
        ('Status & Dates', {
            'fields': ('status', 'start_date', 'expected_completion_date', 'actual_completion_date')
        }),
        ('Display', {
            'fields': ('is_featured', 'is_most_popular')
        }),
        ('Approval', {
            'fields': ('is_approved', 'approved_by', 'approved_at')
        }),
    )
    
    actions = ['approve_projects', 'reject_projects']
    
    def approve_projects(self, request, queryset):
        for project in queryset:
            project.is_approved = True
            project.approved_by = request.user
            project.approved_at = timezone.now()
            project.save()
        self.message_user(request, f"{queryset.count()} projects approved.")
    approve_projects.short_description = "Approve selected projects"
    
    def reject_projects(self, request, queryset):
        queryset.update(is_approved=False, approved_by=request.user, approved_at=timezone.now())
        self.message_user(request, f"{queryset.count()} projects rejected.")


@admin.register(ProjectProposal)
class ProjectProposalAdmin(admin.ModelAdmin):
    list_display = ['title', 'proposer', 'status', 'target_amount', 'reviewed_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'description', 'proposer__username']
    raw_id_fields = ['proposer', 'reviewed_by', 'approved_project']
    readonly_fields = ['created_at', 'updated_at', 'reviewed_at']
    
    fieldsets = (
        ('Proposal Information', {
            'fields': ('proposer', 'title', 'description', 'short_description', 'target_amount')
        }),
        ('Review', {
            'fields': ('status', 'reviewed_by', 'reviewed_at', 'rejection_reason', 'approved_project')
        }),
    )
    
    actions = ['approve_proposals', 'reject_proposals']
    
    def approve_proposals(self, request, queryset):
        for proposal in queryset.filter(status='PENDING'):
            # Create slug from title
            slug = re.sub(r'[^\w\s-]', '', proposal.title.lower())
            slug = re.sub(r'[-\s]+', '-', slug)
            base_slug = slug
            counter = 1
            while CommunityProject.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            # Create project from proposal
            project = CommunityProject.objects.create(
                title=proposal.title,
                slug=slug,
                description=proposal.description,
                short_description=proposal.short_description,
                target_amount=proposal.target_amount,
                status='ACTIVE',
                is_approved=True,
                approved_by=request.user,
                approved_at=timezone.now()
            )
            
            proposal.status = 'APPROVED'
            proposal.reviewed_by = request.user
            proposal.reviewed_at = timezone.now()
            proposal.approved_project = project
            proposal.save()
        
        self.message_user(request, f"{queryset.count()} proposals approved and projects created.")
    approve_proposals.short_description = "Approve selected proposals"
    
    def reject_proposals(self, request, queryset):
        queryset.update(status='REJECTED', reviewed_by=request.user, reviewed_at=timezone.now())
        self.message_user(request, f"{queryset.count()} proposals rejected.")


@admin.register(ProjectVote)
class ProjectVoteAdmin(admin.ModelAdmin):
    list_display = ['customer', 'project', 'vote_amount', 'is_default_vote', 'order', 'created_at']
    list_filter = ['is_default_vote', 'created_at', 'project']
    search_fields = ['customer__username', 'project__title', 'order__order_number']
    raw_id_fields = ['customer', 'project', 'order']
    readonly_fields = ['created_at']
