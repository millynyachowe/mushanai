from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta

from .models import (
    SocialMediaAccount, ProductSocialPost, SocialMediaTemplate,
    SocialMediaAnalytics, ScheduledPost
)
from products.models import Product
from .services import SocialMediaPoster


@login_required
def social_media_dashboard(request):
    """
    Social media dashboard for vendors
    """
    if request.user.user_type != 'VENDOR':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # Get connected accounts
    accounts = SocialMediaAccount.objects.filter(vendor=request.user)
    
    # Recent posts
    recent_posts = ProductSocialPost.objects.filter(
        vendor=request.user
    ).select_related('product', 'social_account').order_by('-created_at')[:10]
    
    # This month's stats
    first_day = timezone.now().replace(day=1).date()
    month_posts = ProductSocialPost.objects.filter(
        vendor=request.user,
        posted_at__gte=first_day
    )
    
    stats = {
        'total_accounts': accounts.count(),
        'active_accounts': accounts.filter(status='ACTIVE').count(),
        'month_posts': month_posts.filter(status='POSTED').count(),
        'failed_posts': month_posts.filter(status='FAILED').count(),
    }
    
    context = {
        'accounts': accounts,
        'recent_posts': recent_posts,
        'stats': stats,
    }
    
    return render(request, 'social_media/dashboard.html', context)


@login_required
def connect_account(request, platform):
    """
    Initialize OAuth flow to connect a social media account
    """
    if request.user.user_type != 'VENDOR':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # This would typically redirect to OAuth provider
    # For now, show instruction page
    context = {
        'platform': platform,
    }
    
    return render(request, 'social_media/connect_account.html', context)


@login_required
def oauth_callback(request, platform):
    """
    OAuth callback to complete account connection
    """
    if request.user.user_type != 'VENDOR':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # This would process OAuth callback
    # Get code, exchange for token, save account
    
    # For now, show manual setup
    messages.info(request, f'{platform} account connection in progress. Please complete manual setup.')
    return redirect('social_media_dashboard')


@login_required
def disconnect_account(request, account_id):
    """
    Disconnect a social media account
    """
    account = get_object_or_404(SocialMediaAccount, id=account_id, vendor=request.user)
    
    if request.method == 'POST':
        account.status = 'DISCONNECTED'
        account.save()
        messages.success(request, f'{account.platform} account disconnected.')
        return redirect('social_media_dashboard')
    
    context = {'account': account}
    return render(request, 'social_media/disconnect_confirm.html', context)


@login_required
def account_settings(request, account_id):
    """
    Manage social media account settings
    """
    account = get_object_or_404(SocialMediaAccount, id=account_id, vendor=request.user)
    
    if request.method == 'POST':
        account.auto_post = request.POST.get('auto_post') == 'on'
        account.save()
        messages.success(request, 'Settings updated.')
        return redirect('social_media_dashboard')
    
    context = {'account': account}
    return render(request, 'social_media/account_settings.html', context)


@login_required
def templates_list(request):
    """
    List all posting templates
    """
    if request.user.user_type != 'VENDOR':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    templates = SocialMediaTemplate.objects.filter(vendor=request.user)
    
    context = {'templates': templates}
    return render(request, 'social_media/templates_list.html', context)


@login_required
def template_create(request):
    """
    Create a new posting template
    """
    if request.user.user_type != 'VENDOR':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if request.method == 'POST':
        template = SocialMediaTemplate.objects.create(
            vendor=request.user,
            platform=request.POST.get('platform'),
            name=request.POST.get('name'),
            template_text=request.POST.get('template_text'),
            hashtags=request.POST.get('hashtags', ''),
            is_default=request.POST.get('is_default') == 'on'
        )
        
        # If set as default, unset other defaults for this platform
        if template.is_default:
            SocialMediaTemplate.objects.filter(
                vendor=request.user,
                platform=template.platform
            ).exclude(id=template.id).update(is_default=False)
        
        messages.success(request, 'Template created successfully.')
        return redirect('social_templates_list')
    
    context = {
        'platforms': SocialMediaAccount.PLATFORM_CHOICES,
    }
    return render(request, 'social_media/template_form.html', context)


@login_required
def template_edit(request, template_id):
    """
    Edit a posting template
    """
    template = get_object_or_404(SocialMediaTemplate, id=template_id, vendor=request.user)
    
    if request.method == 'POST':
        template.name = request.POST.get('name')
        template.template_text = request.POST.get('template_text')
        template.hashtags = request.POST.get('hashtags', '')
        template.is_default = request.POST.get('is_default') == 'on'
        template.save()
        
        # If set as default, unset other defaults
        if template.is_default:
            SocialMediaTemplate.objects.filter(
                vendor=request.user,
                platform=template.platform
            ).exclude(id=template.id).update(is_default=False)
        
        messages.success(request, 'Template updated successfully.')
        return redirect('social_templates_list')
    
    context = {
        'template': template,
        'platforms': SocialMediaAccount.PLATFORM_CHOICES,
    }
    return render(request, 'social_media/template_form.html', context)


@login_required
def posts_list(request):
    """
    List all social media posts
    """
    if request.user.user_type != 'VENDOR':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    posts = ProductSocialPost.objects.filter(
        vendor=request.user
    ).select_related('product', 'social_account').order_by('-created_at')
    
    # Filters
    status = request.GET.get('status')
    platform = request.GET.get('platform')
    
    if status:
        posts = posts.filter(status=status)
    if platform:
        posts = posts.filter(social_account__platform=platform)
    
    context = {
        'posts': posts,
        'selected_status': status,
        'selected_platform': platform,
    }
    
    return render(request, 'social_media/posts_list.html', context)


@login_required
@require_POST
def post_product(request, product_id):
    """
    Post a product to selected social media accounts
    """
    product = get_object_or_404(Product, id=product_id, vendor=request.user)
    
    # Get selected accounts
    account_ids = request.POST.getlist('accounts')
    custom_text = request.POST.get('custom_text', '')
    
    if not account_ids:
        return JsonResponse({'success': False, 'error': 'No accounts selected'})
    
    accounts = SocialMediaAccount.objects.filter(
        id__in=account_ids,
        vendor=request.user,
        status='ACTIVE'
    )
    
    results = []
    for account in accounts:
        # Get image path if available
        image_path = None
        if hasattr(product, 'image') and product.image:
            try:
                image_path = product.image.path
            except:
                pass
        
        # Post
        post_text = custom_text if custom_text else None
        social_post = SocialMediaPoster.post_product(
            product, account, post_text=post_text, image_path=image_path
        )
        
        results.append({
            'platform': account.platform,
            'success': social_post.status == 'POSTED',
            'error': social_post.error_message
        })
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'results': results})
    else:
        for result in results:
            if result['success']:
                messages.success(request, f"Posted to {result['platform']}")
            else:
                messages.error(request, f"{result['platform']}: {result['error']}")
        return redirect('product_detail', product_id=product.id)


@login_required
def post_preview(request, product_id):
    """
    Preview how a product will look on social media
    """
    product = get_object_or_404(Product, id=product_id, vendor=request.user)
    
    # Get accounts
    accounts = SocialMediaAccount.objects.filter(
        vendor=request.user,
        status='ACTIVE'
    )
    
    # Generate preview for each platform
    previews = {}
    for account in accounts:
        template = SocialMediaTemplate.objects.filter(
            vendor=request.user,
            platform=account.platform,
            is_default=True
        ).first()
        
        if template:
            post_text = template.render(product)
        else:
            from django.conf import settings
            post_text = f"{product.name}\n\n{product.description[:200]}"
            if hasattr(settings, 'SITE_URL'):
                post_text += f"\n\n{settings.SITE_URL}/products/{product.slug}/"
        
        previews[account.platform] = {
            'account': account,
            'text': post_text
        }
    
    context = {
        'product': product,
        'previews': previews,
    }
    
    return render(request, 'social_media/post_preview.html', context)


@login_required
def analytics_dashboard(request):
    """
    Social media analytics dashboard
    """
    if request.user.user_type != 'VENDOR':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # Get all posts
    posts = ProductSocialPost.objects.filter(
        vendor=request.user,
        status='POSTED'
    ).select_related('social_account')
    
    # Overall stats
    total_posts = posts.count()
    total_likes = sum(post.likes_count for post in posts)
    total_comments = sum(post.comments_count for post in posts)
    total_shares = sum(post.shares_count for post in posts)
    total_reach = sum(post.reach for post in posts)
    
    # By platform
    platform_stats = {}
    for post in posts:
        platform = post.social_account.platform
        if platform not in platform_stats:
            platform_stats[platform] = {
                'posts': 0,
                'likes': 0,
                'comments': 0,
                'shares': 0,
                'reach': 0
            }
        platform_stats[platform]['posts'] += 1
        platform_stats[platform]['likes'] += post.likes_count
        platform_stats[platform]['comments'] += post.comments_count
        platform_stats[platform]['shares'] += post.shares_count
        platform_stats[platform]['reach'] += post.reach
    
    # Top performing posts
    top_posts = posts.order_by('-likes_count')[:10]
    
    context = {
        'total_posts': total_posts,
        'total_likes': total_likes,
        'total_comments': total_comments,
        'total_shares': total_shares,
        'total_reach': total_reach,
        'platform_stats': platform_stats,
        'top_posts': top_posts,
    }
    
    return render(request, 'social_media/analytics.html', context)

