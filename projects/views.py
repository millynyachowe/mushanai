from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import CommunityProject, ProjectProposal, ProjectMilestone
from customers.models import ProjectNotificationSubscription
from store.social_sharing import get_project_share_data
import re


def project_list(request):
    """
    Display all approved and active projects
    """
    projects = CommunityProject.objects.filter(
        is_approved=True,
        status__in=['ACTIVE', 'IN_PROGRESS']
    ).order_by('-is_most_popular', '-total_votes', '-created_at')
    
    context = {
        'projects': projects,
    }
    return render(request, 'projects/project_list.html', context)


def project_detail(request, slug):
    """
    Display project details with milestones and progress
    """
    project = get_object_or_404(CommunityProject, slug=slug, is_approved=True)
    milestones = project.milestones.all().order_by('order')
    
    project_subscription = None
    if request.user.is_authenticated and request.user.user_type == 'CUSTOMER':
        project_subscription = ProjectNotificationSubscription.objects.filter(
            customer=request.user,
            project=project
        ).first()
    
    # Get social sharing data
    share_data = get_project_share_data(request, project)
    
    context = {
        'project': project,
        'milestones': milestones,
        'funding_percentage': project.funding_percentage,
        'share_data': share_data,
        'project_subscription': project_subscription,
    }
    return render(request, 'projects/project_detail.html', context)


@login_required
def propose_project(request):
    """
    Allow users to propose new projects
    """
    form_data = {
        'title': '',
        'short_description': '',
        'description': '',
        'target_amount': '',
        'expense_breakdown': '',
        'timeline': '',
    }
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        short_description = request.POST.get('short_description', '').strip()
        description = request.POST.get('description', '').strip()
        target_amount_input = request.POST.get('target_amount', '').strip()
        expense_breakdown = request.POST.get('expense_breakdown', '').strip()
        timeline = request.POST.get('timeline', '').strip()
        
        form_data.update({
            'title': title,
            'short_description': short_description,
            'description': description,
            'target_amount': target_amount_input,
            'expense_breakdown': expense_breakdown,
            'timeline': timeline,
        })
        
        errors = []
        
        if not title:
            errors.append('Please provide a project title.')
        if not description:
            errors.append('Please provide a detailed project description.')
        
        target_amount_decimal = None
        if not target_amount_input:
            errors.append('Please provide the target funding amount.')
        else:
            try:
                target_amount_decimal = Decimal(target_amount_input)
                if target_amount_decimal < 0:
                    errors.append('Target amount cannot be negative.')
            except InvalidOperation:
                errors.append('Please enter a valid number for the target amount.')
        
        if not expense_breakdown:
            errors.append('Please outline the expense breakdown to justify the project budget.')
        if not timeline:
            errors.append('Please provide the project timeline and major milestones.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'projects/propose_project.html', {'form_data': form_data})
        
        ProjectProposal.objects.create(
            proposer=request.user,
            title=title,
            description=description,
            short_description=short_description,
            target_amount=target_amount_decimal,
            expense_breakdown=expense_breakdown,
            timeline=timeline,
            status='PENDING'
        )
        messages.success(request, 'Your project proposal has been submitted and is pending admin approval.')
        return redirect('project_list')
    
    return render(request, 'projects/propose_project.html', {'form_data': form_data})


@login_required
def my_projects(request):
    """
    Show projects that the user has voted for or contributed to
    """
    if request.user.user_type != 'CUSTOMER':
        messages.error(request, 'This page is for customers only.')
        return redirect('home')
    
    # Get projects the customer has voted for
    from .models import ProjectVote
    voted_projects = CommunityProject.objects.filter(
        votes__customer=request.user
    ).distinct().order_by('-votes__created_at')
    
    context = {
        'voted_projects': voted_projects,
    }
    return render(request, 'projects/my_projects.html', context)
