from django.utils import timezone
from .models import (
    BackInStockAlert,
    VendorSubscription,
    ProjectNotificationSubscription,
    NotificationLog,
    PriceAlert
)


def send_back_in_stock_notifications(product):
    """Notify customers when a product is back in stock"""
    alerts = BackInStockAlert.objects.filter(
        product=product,
        status='ACTIVE'
    ).select_related('customer')
    
    notifications = []
    for alert in alerts:
        NotificationLog.objects.create(
            customer=alert.customer,
            notification_type='BACK_IN_STOCK',
            title=f'{product.name} is back in stock',
            message=f'Good news! {product.name} is available again.',
            product=product
        )
        alert.mark_notified()
        notifications.append(alert.customer)
    
    return notifications


def send_new_product_notifications(product):
    """Notify subscribers when a vendor adds a new product"""
    vendor = product.vendor
    if not vendor:
        return []
    subscriptions = VendorSubscription.objects.filter(
        vendor=vendor,
        notify_new_products=True
    ).select_related('customer')
    
    notified = []
    for subscription in subscriptions:
        NotificationLog.objects.create(
            customer=subscription.customer,
            notification_type='NEW_PRODUCT',
            title=f'New product from {vendor.username}',
            message=f'{product.name} has just been added by {vendor.username}. Check it out!',
            product=product,
            vendor=vendor
        )
        subscription.last_notified_at = timezone.now()
        subscription.save(update_fields=['last_notified_at'])
        notified.append(subscription.customer)
    
    return notified


def send_price_drop_notification(price_alert: PriceAlert):
    """Notify customer for a price drop (wrapper for price alert)"""
    if price_alert.notification_sent:
        return None
    price_alert.trigger_notification()
    return price_alert.customer


def send_project_milestone_notifications(milestone):
    """Notify subscribers when a project milestone is reached"""
    project = milestone.project
    subscriptions = ProjectNotificationSubscription.objects.filter(
        project=project,
        notify_milestones=True
    ).select_related('customer')
    
    notified = []
    for subscription in subscriptions:
        NotificationLog.objects.create(
            customer=subscription.customer,
            notification_type='PROJECT_MILESTONE',
            title=f'Project update: {project.title}',
            message=f'Milestone "{milestone.title}" has been reached for {project.title}.',
            project=project,
            milestone=milestone
        )
        subscription.last_notified_at = timezone.now()
        subscription.save(update_fields=['last_notified_at'])
        notified.append(subscription.customer)
    
    return notified
