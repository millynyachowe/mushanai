from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q, Avg
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from .models import (
    CustomerDashboard, CustomerImpactMetrics, VotingHistory, SearchHistory,
    ReferralProgram, Referral, CustomerTestimonial,
    Wishlist, WishlistItem, PriceAlert, GiftRegistry, GiftRegistryItem,
    BackInStockAlert, VendorSubscription, ProjectNotificationSubscription,
    NotificationLog, AchievementBadge, CustomerAchievement,
    ImpactLevel, LeaderboardEntry, CommunityChallenge, CommunityChallengeParticipant
)
from .gamification import (
    update_impact_level,
    award_badge,
    recalc_leaderboard_ranks,
    update_challenge_progress
)
from orders.models import Order, OrderItem
from products.models import Product
from products.recommendations import (
    get_personalized_recommendations,
    get_recently_viewed,
    get_trending_products,
    get_seasonal_suggestions
)
from projects.models import CommunityProject, ProjectVote
from vendors.models import VendorProfile
from loyalty.models import LoyaltyAccount
import secrets
import string

User = get_user_model()


@login_required
def customer_portal(request):
    """
    Main customer portal dashboard
    """
    if request.user.user_type != 'CUSTOMER':
        messages.error(request, 'Access denied. Customer access required.')
        return redirect('home')
    
    customer = request.user
    
    # Get or create customer dashboard
    dashboard, created = CustomerDashboard.objects.get_or_create(customer=customer)
    
    # Get customer orders
    orders = Order.objects.filter(customer=customer).order_by('-created_at')[:10]
    
    # Get projects customer has voted for
    voted_projects = CommunityProject.objects.filter(
        votes__customer=customer
    ).distinct().order_by('-votes__created_at')[:5]
    
    # Get impact metrics
    impact_metrics, created = CustomerImpactMetrics.objects.get_or_create(customer=customer)
    
    # Calculate metrics if needed
    if created or True:  # Always recalculate for now
        total_spent = Order.objects.filter(
            customer=customer,
            payment_status='PAID'
        ).aggregate(total=Sum('total'))['total'] or 0
        
        total_orders = Order.objects.filter(customer=customer).count()
        total_items = OrderItem.objects.filter(
            order__customer=customer
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        # Project contributions
        total_contributions = ProjectVote.objects.filter(
            customer=customer
        ).aggregate(total=Sum('vote_amount'))['total'] or 0
        
        projects_supported = ProjectVote.objects.filter(
            customer=customer
        ).values('project').distinct().count()
        
        # Local brand purchases
        local_brand_purchases = OrderItem.objects.filter(
            order__customer=customer,
            product__is_made_from_local_materials=True
        ).count()
        
        impact_metrics.total_spent = total_spent
        impact_metrics.total_orders = total_orders
        impact_metrics.total_items_purchased = total_items or 0
        impact_metrics.total_project_contributions = total_contributions
        impact_metrics.projects_supported_count = projects_supported
        impact_metrics.total_votes_cast = ProjectVote.objects.filter(customer=customer).count()
        impact_metrics.local_brand_purchases = local_brand_purchases
        impact_metrics.local_material_product_purchases = local_brand_purchases
        impact_metrics.save()
    
    current_level = update_impact_level(impact_metrics)
    next_level = ImpactLevel.objects.filter(min_points__gt=impact_metrics.impact_points).order_by('min_points').first()
    
    # Calculate points needed for next level
    points_to_next_level = None
    if next_level:
        points_to_next_level = next_level.min_points - impact_metrics.impact_points
    
    recent_achievements = CustomerAchievement.objects.filter(
        customer=customer,
        status='EARNED'
    ).select_related('badge').order_by('-earned_at')[:3]
    
    # Get personalized recommendations
    personalized_recommendations = get_personalized_recommendations(customer, limit=12)
    
    # Get recently viewed products
    recently_viewed = get_recently_viewed(customer=customer, limit=8)
    
    # Get trending products
    trending_products = get_trending_products(limit=8)
    
    # Get seasonal suggestions
    seasonal_products = get_seasonal_suggestions(limit=8)
    
    # Get brand stories
    brands = VendorProfile.objects.filter(
        description__isnull=False
    ).exclude(description='').order_by('-created_at')[:6]
    
    context = {
        'dashboard': dashboard,
        'orders': orders,
        'voted_projects': voted_projects,
        'impact_metrics': impact_metrics,
        'current_level': current_level,
        'next_level': next_level,
        'points_to_next_level': points_to_next_level,
        'recent_achievements': recent_achievements,
        'personalized_recommendations': personalized_recommendations,
        'recently_viewed': recently_viewed,
        'trending_products': trending_products,
        'seasonal_products': seasonal_products,
        'brands': brands,
    }
    
    return render(request, 'customers/portal.html', context)


@login_required
def my_orders(request):
    """
    Display all customer orders
    """
    if request.user.user_type != 'CUSTOMER':
        messages.error(request, 'Access denied. Customer access required.')
        return redirect('home')
    
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    
    return render(request, 'customers/my_orders.html', context)


@login_required
def my_projects(request):
    """
    Display projects customer has contributed to
    """
    if request.user.user_type != 'CUSTOMER':
        messages.error(request, 'Access denied. Customer access required.')
        return redirect('home')
    
    # Get projects with customer's votes
    project_votes = ProjectVote.objects.filter(
        customer=request.user
    ).select_related('project').order_by('-created_at')
    
    context = {
        'project_votes': project_votes,
    }
    
    return render(request, 'customers/my_projects.html', context)


@login_required
def referral_program(request):
    """
    Customer referral program page
    """
    if request.user.user_type != 'CUSTOMER':
        messages.error(request, 'Access denied. Customer access required.')
        return redirect('home')
    
    customer = request.user
    
    # Get or create referral program
    referral_program, created = ReferralProgram.objects.get_or_create(
        referrer=customer,
        defaults={'referral_code': generate_referral_code(customer)}
    )
    
    # Get referral statistics
    referrals = Referral.objects.filter(referral_program=referral_program).order_by('-created_at')
    
    # Get referral URL
    referral_url = get_referral_url(request, referral_program.referral_code)
    
    context = {
        'referral_program': referral_program,
        'referrals': referrals,
        'referral_url': referral_url,
    }
    
    return render(request, 'customers/referral_program.html', context)


def generate_referral_code(customer):
    """Generate a unique referral code"""
    # Use customer username + random string
    base = customer.username.upper()[:6]
    random_part = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
    code = f"{base}{random_part}"
    
    # Ensure uniqueness
    while ReferralProgram.objects.filter(referral_code=code).exists():
        random_part = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
        code = f"{base}{random_part}"
    
    return code


def get_referral_url(request, referral_code):
    """Get referral URL"""
    if hasattr(settings, 'SITE_URL'):
        base_url = settings.SITE_URL
    else:
        scheme = 'https' if request.is_secure() else 'http'
        base_url = f"{scheme}://{request.get_host()}"
    
    from django.urls import reverse
    signup_url = reverse('customer_signup')
    return f"{base_url}{signup_url}?ref={referral_code}"


@login_required
@require_http_methods(["GET", "POST"])
def submit_testimonial(request, vendor_id):
    """
    Submit a testimonial for a vendor
    """
    if request.user.user_type != 'CUSTOMER':
        messages.error(request, 'Only customers can submit testimonials.')
        return redirect('home')
    
    vendor = get_object_or_404(User, id=vendor_id, user_type='VENDOR')
    customer = request.user
    
    # Check if customer has already submitted a testimonial for this vendor
    existing_testimonial = CustomerTestimonial.objects.filter(
        customer=customer,
        vendor=vendor
    ).first()
    
    if request.method == 'POST':
        testimonial_text = request.POST.get('testimonial', '').strip()
        title = request.POST.get('title', '').strip()
        rating = request.POST.get('rating', '5')
        display_name = request.POST.get('display_name', '').strip()
        
        if not testimonial_text:
            messages.error(request, 'Please provide a testimonial.')
            return redirect('vendor_profile_public', vendor_id=vendor_id)
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError("Invalid rating")
        except (ValueError, TypeError):
            rating = 5
        
        # Check if customer has purchased from this vendor
        has_purchased = Order.objects.filter(
            customer=customer,
            order_items__vendor=vendor,
            payment_status='PAID'
        ).exists()
        
        # Get the most recent order if exists
        order = None
        if has_purchased:
            order = Order.objects.filter(
                customer=customer,
                order_items__vendor=vendor,
                payment_status='PAID'
            ).order_by('-created_at').first()
        
        if existing_testimonial:
            # Update existing testimonial
            existing_testimonial.testimonial = testimonial_text
            existing_testimonial.title = title if title else None
            existing_testimonial.rating = rating
            existing_testimonial.display_name = display_name if display_name else None
            existing_testimonial.is_verified_purchase = has_purchased
            existing_testimonial.order = order
            existing_testimonial.status = 'PENDING'  # Reset to pending for re-approval
            existing_testimonial.save()
            messages.success(request, 'Your testimonial has been updated and is pending approval.')
        else:
            # Create new testimonial
            CustomerTestimonial.objects.create(
                customer=customer,
                vendor=vendor,
                testimonial=testimonial_text,
                title=title if title else None,
                rating=rating,
                display_name=display_name if display_name else None,
                is_verified_purchase=has_purchased,
                order=order,
                status='PENDING'
            )
            messages.success(request, 'Your testimonial has been submitted and is pending approval. Thank you!')
        
        return redirect('vendor_profile_public', vendor_id=vendor_id)
    
    # GET request - show form
    context = {
        'vendor': vendor,
        'existing_testimonial': existing_testimonial,
    }
    return render(request, 'customers/submit_testimonial.html', context)


# ============ NOTIFICATION VIEWS ============

@login_required
def notifications_dashboard(request):
    """
    Dashboard to manage notification subscriptions and history
    """
    if request.user.user_type != 'CUSTOMER':
        messages.error(request, 'Access denied. Customer access required.')
        return redirect('home')
    
    customer = request.user
    notifications = NotificationLog.objects.filter(customer=customer).select_related('product', 'vendor', 'project')[:50]
    back_in_stock_alerts = BackInStockAlert.objects.filter(customer=customer).select_related('product')
    vendor_subscriptions = VendorSubscription.objects.filter(customer=customer).select_related('vendor')
    project_subscriptions = ProjectNotificationSubscription.objects.filter(customer=customer).select_related('project')
    price_alerts = PriceAlert.objects.filter(customer=customer).select_related('product')
    
    context = {
        'notifications': notifications,
        'back_in_stock_alerts': back_in_stock_alerts,
        'vendor_subscriptions': vendor_subscriptions,
        'project_subscriptions': project_subscriptions,
        'price_alerts': price_alerts,
    }
    return render(request, 'customers/notifications_dashboard.html', context)


@login_required
def gamification_dashboard(request):
    """
    Show gamification status, achievements, leaderboards, and challenges
    """
    if request.user.user_type != 'CUSTOMER':
        messages.error(request, 'Access denied. Customer access required.')
        return redirect('home')
    
    customer = request.user
    impact_metrics, _ = CustomerImpactMetrics.objects.get_or_create(customer=customer)
    current_level = update_impact_level(impact_metrics)
    
    achievements = CustomerAchievement.objects.filter(
        customer=customer
    ).select_related('badge').order_by('-earned_at', '-updated_at')
    
    active_badges = AchievementBadge.objects.filter(is_active=True).order_by('name')
    impact_levels = ImpactLevel.objects.all().order_by('min_points')
    
    # Leaderboards
    project_leaderboard = LeaderboardEntry.objects.filter(
        leaderboard_type='PROJECT_CONTRIBUTION',
        period='ALL_TIME'
    ).select_related('customer').order_by('rank')[:10]
    
    impact_leaderboard = LeaderboardEntry.objects.filter(
        leaderboard_type='IMPACT_POINTS',
        period='ALL_TIME'
    ).select_related('customer').order_by('rank')[:10]
    
    # Community challenges
    today = timezone.now().date()
    active_challenges = CommunityChallenge.objects.filter(
        is_active=True,
        start_date__lte=today,
        end_date__gte=today
    ).order_by('-start_date')
    
    challenge_participations = CommunityChallengeParticipant.objects.filter(
        challenge__in=active_challenges,
        customer=customer
    ).select_related('challenge')
    
    participations_map = {p.challenge_id: p for p in challenge_participations}
    for challenge in active_challenges:
        challenge.participation = participations_map.get(challenge.id)
    
    context = {
        'impact_metrics': impact_metrics,
        'current_level': current_level,
        'impact_levels': impact_levels,
        'achievements': achievements,
        'active_badges': active_badges,
        'project_leaderboard': project_leaderboard,
        'impact_leaderboard': impact_leaderboard,
        'active_challenges': active_challenges,
    }
    
    return render(request, 'customers/gamification_dashboard.html', context)


@login_required
@require_POST
def join_challenge(request, challenge_id):
    """
    Join a community challenge
    """
    if request.user.user_type != 'CUSTOMER':
        messages.error(request, 'Access denied. Customer access required.')
        return redirect('home')
    
    challenge = get_object_or_404(CommunityChallenge, id=challenge_id, is_active=True)
    participant, created = CommunityChallengeParticipant.objects.get_or_create(
        challenge=challenge,
        customer=request.user
    )
    
    if created:
        messages.success(request, f'You joined the challenge "{challenge.title}".')
    else:
        messages.info(request, f'You are already participating in "{challenge.title}".')
    
    return redirect('gamification_dashboard')


@login_required
@require_POST
def mark_notification_read(request, notification_id):
    """
    Mark a notification as read
    """
    notification = get_object_or_404(NotificationLog, id=notification_id, customer=request.user)
    notification.mark_read()
    return JsonResponse({'success': True})


@login_required
@require_POST
def subscribe_back_in_stock(request, product_id):
    """
    Subscribe to back-in-stock alert for a product
    """
    if request.user.user_type != 'CUSTOMER':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Access denied'}, status=403)
        messages.error(request, 'Access denied. Customer access required.')
        return redirect('product_detail', slug=get_object_or_404(Product, id=product_id).slug)
    
    product = get_object_or_404(Product, id=product_id)
    if product.is_in_stock:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Product is currently in stock.'}, status=400)
        messages.info(request, f'{product.name} is currently in stock.')
        return redirect('product_detail', slug=product.slug)
    
    alert, created = BackInStockAlert.objects.get_or_create(
        customer=request.user,
        product=product
    )
    
    if created:
        if not alert.expires_at:
            alert.expires_at = timezone.now() + timedelta(days=30)
            alert.save(update_fields=['expires_at'])
        message = f'You will be notified when {product.name} is back in stock.'
    else:
        alert.status = 'ACTIVE'
        alert.notification_sent = False
        alert.notified_at = None
        alert.save(update_fields=['status', 'notification_sent', 'notified_at'])
        message = f'Back-in-stock alert refreshed for {product.name}.'
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': message})
    
    messages.success(request, message)
    return redirect('product_detail', slug=product.slug)


@login_required
@require_POST
def cancel_back_in_stock(request, alert_id):
    """
    Cancel a back-in-stock alert
    """
    alert = get_object_or_404(BackInStockAlert, id=alert_id, customer=request.user)
    alert.status = 'CANCELLED'
    alert.save(update_fields=['status'])
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': 'Alert cancelled.'})
    
    messages.success(request, 'Back-in-stock alert cancelled.')
    return redirect('notifications_dashboard')


@login_required
@require_POST
def toggle_vendor_subscription(request, vendor_id):
    """
    Follow or unfollow a vendor for new product notifications
    """
    if request.user.user_type != 'CUSTOMER':
        messages.error(request, 'Access denied. Customer access required.')
        return redirect('home')
    
    vendor = get_object_or_404(User, id=vendor_id, user_type='VENDOR')
    subscription = VendorSubscription.objects.filter(customer=request.user, vendor=vendor).first()
    
    if subscription:
        subscription.delete()
        messages.success(request, f'You will no longer receive updates from {vendor.username}.')
    else:
        VendorSubscription.objects.create(customer=request.user, vendor=vendor)
        messages.success(request, f'You will receive updates when {vendor.username} adds new products.')
    
    return redirect('vendor_profile_public', vendor_id=vendor_id)


@login_required
@require_POST
def toggle_project_notification(request, project_id):
    """
    Subscribe or unsubscribe from project milestone notifications
    """
    if request.user.user_type != 'CUSTOMER':
        messages.error(request, 'Access denied. Customer access required.')
        return redirect('home')
    
    project = get_object_or_404(CommunityProject, id=project_id, is_approved=True)
    subscription = ProjectNotificationSubscription.objects.filter(customer=request.user, project=project).first()
    
    if subscription:
        subscription.delete()
        messages.success(request, f'You will no longer receive milestone notifications for {project.title}.')
    else:
        ProjectNotificationSubscription.objects.create(
            customer=request.user,
            project=project
        )
        messages.success(request, f'You will receive notifications for milestones in {project.title}.')
    
    return redirect('project_detail', slug=project.slug)


# ============ WISHLIST VIEWS ============

@login_required
def wishlist_list(request):
    """
    List all wishlists for the customer
    """
    if request.user.user_type != 'CUSTOMER':
        messages.error(request, 'Access denied. Customer access required.')
        return redirect('home')
    
    wishlists = Wishlist.objects.filter(customer=request.user).order_by('-is_default', '-created_at')
    
    # Get or create default wishlist
    default_wishlist = wishlists.filter(is_default=True).first()
    if not default_wishlist:
        default_wishlist = Wishlist.objects.create(
            customer=request.user,
            name='My Wishlist',
            is_default=True
        )
        wishlists = Wishlist.objects.filter(customer=request.user).order_by('-is_default', '-created_at')
    
    context = {
        'wishlists': wishlists,
        'default_wishlist': default_wishlist,
    }
    return render(request, 'customers/wishlist_list.html', context)


@login_required
def wishlist_detail(request, wishlist_id):
    """
    View a specific wishlist
    """
    if request.user.user_type != 'CUSTOMER':
        messages.error(request, 'Access denied. Customer access required.')
        return redirect('home')
    
    wishlist = get_object_or_404(Wishlist, id=wishlist_id, customer=request.user)
    items = WishlistItem.objects.filter(wishlist=wishlist).select_related('product', 'product__vendor').order_by('-priority', '-added_at')
    
    context = {
        'wishlist': wishlist,
        'items': items,
    }
    return render(request, 'customers/wishlist_detail.html', context)


@login_required
@require_POST
def wishlist_add_product(request, product_id):
    """
    Add a product to wishlist (AJAX)
    """
    if request.user.user_type != 'CUSTOMER':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    product = get_object_or_404(Product, id=product_id, is_active=True)
    wishlist_id = request.POST.get('wishlist_id')
    
    # Get or create default wishlist
    if wishlist_id:
        wishlist = get_object_or_404(Wishlist, id=wishlist_id, customer=request.user)
    else:
        wishlist, created = Wishlist.objects.get_or_create(
            customer=request.user,
            is_default=True,
            defaults={'name': 'My Wishlist'}
        )
    
    # Check if already in wishlist
    item, created = WishlistItem.objects.get_or_create(
        wishlist=wishlist,
        product=product
    )
    
    if created:
        return JsonResponse({
            'success': True,
            'message': f'{product.name} added to {wishlist.name}',
            'wishlist_id': wishlist.id,
            'wishlist_name': wishlist.name
        })
    else:
        return JsonResponse({
            'success': False,
            'message': f'{product.name} is already in {wishlist.name}'
        }, status=400)


@login_required
@require_POST
def wishlist_remove_product(request, item_id):
    """
    Remove a product from wishlist (AJAX)
    """
    if request.user.user_type != 'CUSTOMER':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    item = get_object_or_404(WishlistItem, id=item_id, wishlist__customer=request.user)
    product_name = item.product.name
    item.delete()
    
    return JsonResponse({
        'success': True,
        'message': f'{product_name} removed from wishlist'
    })


@login_required
@require_http_methods(["GET", "POST"])
def wishlist_create(request):
    """
    Create a new wishlist
    """
    if request.user.user_type != 'CUSTOMER':
        messages.error(request, 'Access denied. Customer access required.')
        return redirect('home')
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        is_public = request.POST.get('is_public') == 'on'
        
        if not name:
            messages.error(request, 'Please provide a name for your wishlist.')
            return redirect('wishlist_create')
        
        wishlist = Wishlist.objects.create(
            customer=request.user,
            name=name,
            description=description if description else None,
            is_public=is_public
        )
        
        messages.success(request, f'Wishlist "{name}" created successfully!')
        return redirect('wishlist_detail', wishlist_id=wishlist.id)
    
    return render(request, 'customers/wishlist_create.html')


@login_required
@require_POST
def wishlist_delete(request, wishlist_id):
    """
    Delete a wishlist
    """
    if request.user.user_type != 'CUSTOMER':
        messages.error(request, 'Access denied. Customer access required.')
        return redirect('home')
    
    wishlist = get_object_or_404(Wishlist, id=wishlist_id, customer=request.user)
    
    if wishlist.is_default:
        messages.error(request, 'Cannot delete your default wishlist.')
        return redirect('wishlist_list')
    
    wishlist_name = wishlist.name
    wishlist.delete()
    messages.success(request, f'Wishlist "{wishlist_name}" deleted successfully.')
    return redirect('wishlist_list')


def wishlist_share(request, share_token):
    """
    Public view of a shared wishlist
    """
    wishlist = get_object_or_404(Wishlist, share_token=share_token, is_public=True)
    items = WishlistItem.objects.filter(wishlist=wishlist).select_related('product', 'product__vendor').order_by('-priority', '-added_at')
    
    context = {
        'wishlist': wishlist,
        'items': items,
        'is_shared': True,
    }
    return render(request, 'customers/wishlist_detail.html', context)


# ============ PRICE ALERT VIEWS ============

@login_required
def price_alerts_list(request):
    """
    List all price alerts for the customer
    """
    if request.user.user_type != 'CUSTOMER':
        messages.error(request, 'Access denied. Customer access required.')
        return redirect('home')
    
    alerts = PriceAlert.objects.filter(customer=request.user).select_related('product').order_by('-created_at')
    
    context = {
        'alerts': alerts,
    }
    return render(request, 'customers/price_alerts_list.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def price_alert_create(request, product_id):
    """
    Create a price alert for a product
    """
    if request.user.user_type != 'CUSTOMER':
        messages.error(request, 'Access denied. Customer access required.')
        return redirect('home')
    
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    # Check if alert already exists
    existing_alert = PriceAlert.objects.filter(customer=request.user, product=product, status='ACTIVE').first()
    
    if request.method == 'POST':
        if existing_alert:
            messages.info(request, 'You already have an active price alert for this product.')
            return redirect('price_alerts_list')
        
        target_price = request.POST.get('target_price', '').strip()
        target_percentage = request.POST.get('target_percentage', '').strip()
        
        if not target_price and not target_percentage:
            messages.error(request, 'Please provide either a target price or target percentage.')
            return redirect('price_alert_create', product_id=product_id)
        
        alert = PriceAlert.objects.create(
            customer=request.user,
            product=product,
            original_price=product.price,
            target_price=float(target_price) if target_price else None,
            target_percentage=float(target_percentage) if target_percentage else None,
        )
        
        messages.success(request, f'Price alert created for {product.name}!')
        return redirect('price_alerts_list')
    
    context = {
        'product': product,
        'existing_alert': existing_alert,
    }
    return render(request, 'customers/price_alert_create.html', context)


@login_required
@require_POST
def price_alert_delete(request, alert_id):
    """
    Delete/cancel a price alert
    """
    if request.user.user_type != 'CUSTOMER':
        messages.error(request, 'Access denied. Customer access required.')
        return redirect('home')
    
    alert = get_object_or_404(PriceAlert, id=alert_id, customer=request.user)
    alert.status = 'CANCELLED'
    alert.save()
    
    messages.success(request, 'Price alert cancelled.')
    return redirect('price_alerts_list')


# ============ GIFT REGISTRY VIEWS ============

@login_required
def gift_registry_list(request):
    """
    List all gift registries for the customer
    """
    if request.user.user_type != 'CUSTOMER':
        messages.error(request, 'Access denied. Customer access required.')
        return redirect('home')
    
    registries = GiftRegistry.objects.filter(customer=request.user).order_by('-created_at')
    
    context = {
        'registries': registries,
    }
    return render(request, 'customers/gift_registry_list.html', context)


@login_required
def gift_registry_detail(request, registry_id):
    """
    View a specific gift registry
    """
    if request.user.user_type != 'CUSTOMER':
        messages.error(request, 'Access denied. Customer access required.')
        return redirect('home')
    
    registry = get_object_or_404(GiftRegistry, id=registry_id, customer=request.user)
    items = GiftRegistryItem.objects.filter(registry=registry).select_related('product', 'product__vendor', 'purchased_by').order_by('-priority', '-added_at')
    
    context = {
        'registry': registry,
        'items': items,
    }
    return render(request, 'customers/gift_registry_detail.html', context)


def gift_registry_public(request, share_token):
    """
    Public view of a shared gift registry
    """
    registry = get_object_or_404(GiftRegistry, share_token=share_token, is_public=True, status='ACTIVE')
    items = GiftRegistryItem.objects.filter(registry=registry).select_related('product', 'product__vendor').order_by('-priority', '-added_at')
    
    context = {
        'registry': registry,
        'items': items,
        'is_public': True,
    }
    return render(request, 'customers/gift_registry_detail.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def gift_registry_create(request):
    """
    Create a new gift registry
    """
    if request.user.user_type != 'CUSTOMER':
        messages.error(request, 'Access denied. Customer access required.')
        return redirect('home')
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        event_date = request.POST.get('event_date', '').strip()
        is_public = request.POST.get('is_public') == 'on'
        
        if not name:
            messages.error(request, 'Please provide a name for your gift registry.')
            return redirect('gift_registry_create')
        
        registry = GiftRegistry.objects.create(
            customer=request.user,
            name=name,
            description=description if description else None,
            event_date=event_date if event_date else None,
            is_public=is_public
        )
        
        messages.success(request, f'Gift registry "{name}" created successfully!')
        return redirect('gift_registry_detail', registry_id=registry.id)
    
    return render(request, 'customers/gift_registry_create.html')


@login_required
@require_POST
def gift_registry_add_product(request, registry_id, product_id):
    """
    Add a product to gift registry
    """
    if request.user.user_type != 'CUSTOMER':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    registry = get_object_or_404(GiftRegistry, id=registry_id, customer=request.user)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = int(request.POST.get('quantity', 1))
    
    item, created = GiftRegistryItem.objects.get_or_create(
        registry=registry,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        item.quantity += quantity
        item.save()
    
    return JsonResponse({
        'success': True,
        'message': f'{product.name} added to {registry.name}',
        'registry_id': registry.id
    })


@login_required
@require_POST
def gift_registry_remove_product(request, item_id):
    """
    Remove a product from gift registry
    """
    if request.user.user_type != 'CUSTOMER':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    item = get_object_or_404(GiftRegistryItem, id=item_id, registry__customer=request.user)
    product_name = item.product.name
    item.delete()
    
    return JsonResponse({
        'success': True,
        'message': f'{product_name} removed from gift registry'
    })
