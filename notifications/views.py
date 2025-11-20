"""
Notification Views
Handle notification display, management, and API endpoints
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Notification, NotificationPreference
from .utils import mark_all_as_read, get_unread_count


@login_required
def notification_list(request):
    """
    Display list of notifications for user
    """
    notifications = Notification.objects.filter(recipient=request.user)
    
    # Filter by read status
    filter_type = request.GET.get('filter', 'all')
    if filter_type == 'unread':
        notifications = notifications.filter(is_read=False)
    elif filter_type == 'read':
        notifications = notifications.filter(is_read=True)
    
    # Filter by priority
    priority = request.GET.get('priority')
    if priority:
        notifications = notifications.filter(priority=priority)
    
    # Paginate
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'notifications': page_obj,
        'unread_count': get_unread_count(request.user),
        'filter_type': filter_type,
    }
    return render(request, 'notifications/list.html', context)


@login_required
@require_POST
def notification_mark_read(request, notification_id):
    """
    Mark a notification as read
    """
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.mark_as_read()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'unread_count': get_unread_count(request.user)
        })
    
    messages.success(request, 'Notification marked as read.')
    return redirect('notification_list')


@login_required
@require_POST
def notification_mark_unread(request, notification_id):
    """
    Mark a notification as unread
    """
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.mark_as_unread()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'unread_count': get_unread_count(request.user)
        })
    
    messages.success(request, 'Notification marked as unread.')
    return redirect('notification_list')


@login_required
@require_POST
def notification_mark_all_read(request):
    """
    Mark all notifications as read
    """
    count = mark_all_as_read(request.user)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'count': count,
            'unread_count': 0
        })
    
    messages.success(request, f'{count} notification(s) marked as read.')
    return redirect('notification_list')


@login_required
@require_POST
def notification_delete(request, notification_id):
    """
    Delete a notification
    """
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'unread_count': get_unread_count(request.user)
        })
    
    messages.success(request, 'Notification deleted.')
    return redirect('notification_list')


@login_required
def notification_preferences(request):
    """
    Manage notification preferences
    """
    prefs, created = NotificationPreference.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Update preferences
        if request.user.user_type == 'VENDOR':
            prefs.notify_new_order = request.POST.get('notify_new_order') == 'on'
            prefs.notify_payment_received = request.POST.get('notify_payment_received') == 'on'
            prefs.notify_new_review = request.POST.get('notify_new_review') == 'on'
            prefs.notify_low_stock = request.POST.get('notify_low_stock') == 'on'
            prefs.notify_new_supplier = request.POST.get('notify_new_supplier') == 'on'
            prefs.notify_event_created = request.POST.get('notify_event_created') == 'on'
            prefs.notify_promotion_ending = request.POST.get('notify_promotion_ending') == 'on'
            prefs.notify_discussion_reply = request.POST.get('notify_discussion_reply') == 'on'
            prefs.notify_manufacturing = request.POST.get('notify_manufacturing') == 'on'
        
        elif request.user.user_type == 'CUSTOMER':
            prefs.notify_order_status = request.POST.get('notify_order_status') == 'on'
            prefs.notify_payment_status = request.POST.get('notify_payment_status') == 'on'
            prefs.notify_product_recommendations = request.POST.get('notify_product_recommendations') == 'on'
            prefs.notify_price_drops = request.POST.get('notify_price_drops') == 'on'
            prefs.notify_back_in_stock = request.POST.get('notify_back_in_stock') == 'on'
            prefs.notify_new_projects = request.POST.get('notify_new_projects') == 'on'
            prefs.notify_wishlist_sales = request.POST.get('notify_wishlist_sales') == 'on'
            prefs.notify_loyalty_rewards = request.POST.get('notify_loyalty_rewards') == 'on'
        
        # Email preferences
        prefs.send_email_notifications = request.POST.get('send_email_notifications') == 'on'
        prefs.email_frequency = request.POST.get('email_frequency', 'INSTANT')
        prefs.enable_push_notifications = request.POST.get('enable_push_notifications') == 'on'
        
        # Quiet hours
        prefs.enable_quiet_hours = request.POST.get('enable_quiet_hours') == 'on'
        if prefs.enable_quiet_hours:
            prefs.quiet_hours_start = request.POST.get('quiet_hours_start')
            prefs.quiet_hours_end = request.POST.get('quiet_hours_end')
        
        prefs.save()
        messages.success(request, 'Notification preferences updated successfully!')
        return redirect('notification_preferences')
    
    context = {
        'prefs': prefs,
    }
    return render(request, 'notifications/preferences.html', context)


# API Endpoints (for AJAX/Mobile)

@login_required
def api_notification_list(request):
    """
    API endpoint to get notifications (JSON)
    """
    notifications = Notification.objects.filter(recipient=request.user)[:20]
    
    data = {
        'notifications': [
            {
                'id': notif.id,
                'type': notif.notification_type,
                'title': notif.title,
                'message': notif.message,
                'icon': notif.icon,
                'priority': notif.priority,
                'is_read': notif.is_read,
                'action_url': notif.action_url,
                'action_text': notif.action_text,
                'created_at': notif.created_at.isoformat(),
            }
            for notif in notifications
        ],
        'unread_count': get_unread_count(request.user),
    }
    
    return JsonResponse(data)


@login_required
def api_unread_count(request):
    """
    API endpoint to get unread notification count
    """
    return JsonResponse({
        'unread_count': get_unread_count(request.user)
    })


@login_required
def notification_dropdown(request):
    """
    Render notification dropdown for navbar
    """
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:10]
    unread_count = get_unread_count(request.user)
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
    }
    return render(request, 'notifications/dropdown.html', context)

