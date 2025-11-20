"""
Notification Utility Functions
Helper functions to create and send notifications
"""
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from .models import Notification, NotificationPreference
from datetime import timedelta
from django.utils import timezone

User = get_user_model()


def create_notification(
    recipient,
    notification_type,
    title,
    message,
    priority='MEDIUM',
    action_url=None,
    action_text=None,
    related_object=None,
    expires_in_days=30,
    send_email=False
):
    """
    Create a notification for a user
    
    Args:
        recipient: User object
        notification_type: Type of notification (from Notification.NOTIFICATION_TYPES)
        title: Notification title
        message: Notification message
        priority: Priority level (LOW, MEDIUM, HIGH, URGENT)
        action_url: URL for action button
        action_text: Text for action button
        related_object: Related Django model instance
        expires_in_days: Days until notification expires
        send_email: Whether to send email notification
    
    Returns:
        Notification object
    """
    # Get or create notification preferences
    prefs, created = NotificationPreference.objects.get_or_create(user=recipient)
    
    # Check if user wants this type of notification
    if not prefs.should_send_notification(notification_type):
        return None
    
    # Check quiet hours
    if prefs.is_quiet_hours() and priority not in ['HIGH', 'URGENT']:
        return None
    
    # Set expiration date
    expires_at = timezone.now() + timedelta(days=expires_in_days) if expires_in_days else None
    
    # Get content type for related object
    content_type = None
    object_id = None
    if related_object:
        content_type = ContentType.objects.get_for_model(related_object)
        object_id = related_object.pk
    
    # Create notification
    notification = Notification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        title=title,
        message=message,
        priority=priority,
        action_url=action_url,
        action_text=action_text,
        content_type=content_type,
        object_id=object_id,
        expires_at=expires_at,
    )
    
    # Send email if requested and user allows
    if send_email and prefs.send_email_notifications and prefs.email_frequency == 'INSTANT':
        send_email_notification(notification)
    
    return notification


def send_email_notification(notification):
    """
    Send email notification to user
    """
    from django.core.mail import send_mail
    from django.conf import settings
    
    if notification.email_sent:
        return
    
    subject = f"{notification.icon} {notification.title}"
    message = f"""
Hello {notification.recipient.get_full_name() or notification.recipient.username},

{notification.message}

{f'Take action: {settings.SITE_URL}{notification.action_url}' if notification.action_url else ''}

---
This is an automated notification from Mushanai.
To manage your notification preferences, visit: {settings.SITE_URL}/notifications/preferences/
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [notification.recipient.email],
            fail_silently=False,
        )
        notification.email_sent = True
        notification.save(update_fields=['email_sent'])
    except Exception as e:
        print(f"Failed to send email notification: {e}")


# Vendor Notification Helpers

def notify_vendor_new_order(vendor, order):
    """Notify vendor of new order"""
    return create_notification(
        recipient=vendor,
        notification_type='NEW_ORDER',
        title='New Order Received!',
        message=f'You have a new order #{order.id} for ${order.total_amount}',
        priority='HIGH',
        action_url=f'/vendor/orders/{order.id}/',
        action_text='View Order',
        related_object=order,
        send_email=True,
    )


def notify_vendor_payment_received(vendor, order):
    """Notify vendor of payment received"""
    return create_notification(
        recipient=vendor,
        notification_type='PAYMENT_RECEIVED',
        title='Payment Received',
        message=f'Payment of ${order.total_amount} received for order #{order.id}',
        priority='HIGH',
        action_url=f'/vendor/orders/{order.id}/',
        action_text='View Order',
        related_object=order,
        send_email=True,
    )


def notify_vendor_new_review(vendor, review):
    """Notify vendor of new review"""
    return create_notification(
        recipient=vendor,
        notification_type='NEW_REVIEW',
        title='New Review Received',
        message=f'You received a {review.rating}-star review on {review.product.name}',
        priority='MEDIUM',
        action_url=f'/vendor/reviews/',
        action_text='View Reviews',
        related_object=review,
    )


def notify_vendor_low_stock(vendor, product):
    """Notify vendor of low stock"""
    return create_notification(
        recipient=vendor,
        notification_type='LOW_STOCK',
        title='Low Stock Alert',
        message=f'{product.name} is running low on stock ({product.stock_quantity} remaining)',
        priority='MEDIUM',
        action_url=f'/vendor/products/{product.id}/',
        action_text='Update Stock',
        related_object=product,
    )


def notify_vendor_new_supplier(vendor, supplier):
    """Notify vendor of new supplier"""
    return create_notification(
        recipient=vendor,
        notification_type='NEW_SUPPLIER',
        title='New Supplier Available',
        message=f'A new supplier "{supplier.company_name}" is now available in the marketplace',
        priority='LOW',
        action_url='/vendor/suppliers/',
        action_text='View Suppliers',
        related_object=supplier,
    )


def notify_vendor_event_created(vendor, event):
    """Notify vendor of new event"""
    return create_notification(
        recipient=vendor,
        notification_type='EVENT_CREATED',
        title='New Event Created',
        message=f'New event: {event.title} on {event.start_datetime.strftime("%B %d, %Y")}',
        priority='MEDIUM',
        action_url=f'/vendor/events/{event.id}/',
        action_text='View Event',
        related_object=event,
    )


def notify_vendor_promotion_ending(vendor, promotion):
    """Notify vendor that promotion is ending soon"""
    return create_notification(
        recipient=vendor,
        notification_type='PROMOTION_ENDING',
        title='Promotion Ending Soon',
        message=f'Your promotion "{promotion.name}" ends in {promotion.days_remaining} days',
        priority='MEDIUM',
        action_url=f'/vendor/promotions/{promotion.id}/',
        action_text='View Promotion',
        related_object=promotion,
    )


def notify_vendor_manufacturing_complete(vendor, manufacturing_order):
    """Notify vendor that manufacturing is complete"""
    return create_notification(
        recipient=vendor,
        notification_type='MANUFACTURING_COMPLETE',
        title='Manufacturing Complete',
        message=f'Manufacturing order for {manufacturing_order.product.name} is complete',
        priority='HIGH',
        action_url=f'/vendor/manufacturing/{manufacturing_order.id}/',
        action_text='View Order',
        related_object=manufacturing_order,
    )


# Customer Notification Helpers

def notify_customer_order_confirmed(customer, order):
    """Notify customer that order is confirmed"""
    return create_notification(
        recipient=customer,
        notification_type='ORDER_CONFIRMED',
        title='Order Confirmed!',
        message=f'Your order #{order.id} has been confirmed and is being processed',
        priority='HIGH',
        action_url=f'/customer/orders/{order.id}/',
        action_text='Track Order',
        related_object=order,
        send_email=True,
    )


def notify_customer_order_shipped(customer, order):
    """Notify customer that order has shipped"""
    return create_notification(
        recipient=customer,
        notification_type='ORDER_SHIPPED',
        title='Order Shipped!',
        message=f'Your order #{order.id} has been shipped and is on its way',
        priority='HIGH',
        action_url=f'/customer/orders/{order.id}/',
        action_text='Track Shipment',
        related_object=order,
        send_email=True,
    )


def notify_customer_order_delivered(customer, order):
    """Notify customer that order is delivered"""
    return create_notification(
        recipient=customer,
        notification_type='ORDER_DELIVERED',
        title='Order Delivered!',
        message=f'Your order #{order.id} has been delivered. Enjoy your purchase!',
        priority='HIGH',
        action_url=f'/customer/orders/{order.id}/',
        action_text='Leave Review',
        related_object=order,
        send_email=True,
    )


def notify_customer_payment_processed(customer, order):
    """Notify customer that payment is processed"""
    return create_notification(
        recipient=customer,
        notification_type='PAYMENT_PROCESSED',
        title='Payment Successful',
        message=f'Your payment of ${order.total_amount} has been processed successfully',
        priority='HIGH',
        action_url=f'/customer/orders/{order.id}/',
        action_text='View Order',
        related_object=order,
        send_email=True,
    )


def notify_customer_new_product_recommendation(customer, product):
    """Notify customer of product recommendation"""
    return create_notification(
        recipient=customer,
        notification_type='NEW_PRODUCT_RECOMMENDATION',
        title='You Might Like This',
        message=f'Check out {product.name} - we think you\'ll love it!',
        priority='LOW',
        action_url=f'/products/{product.slug}/',
        action_text='View Product',
        related_object=product,
    )


def notify_customer_price_drop(customer, product, old_price, new_price):
    """Notify customer of price drop"""
    savings = old_price - new_price
    return create_notification(
        recipient=customer,
        notification_type='PRICE_DROP',
        title='Price Drop Alert!',
        message=f'{product.name} is now ${new_price} (was ${old_price}). Save ${savings}!',
        priority='MEDIUM',
        action_url=f'/products/{product.slug}/',
        action_text='Buy Now',
        related_object=product,
    )


def notify_customer_back_in_stock(customer, product):
    """Notify customer that product is back in stock"""
    return create_notification(
        recipient=customer,
        notification_type='BACK_IN_STOCK',
        title='Back in Stock!',
        message=f'{product.name} is back in stock. Order now before it sells out!',
        priority='MEDIUM',
        action_url=f'/products/{product.slug}/',
        action_text='Buy Now',
        related_object=product,
    )


def notify_customer_new_project(customer, project):
    """Notify customer of new community project"""
    return create_notification(
        recipient=customer,
        notification_type='NEW_PROJECT',
        title='New Community Project',
        message=f'New project: {project.name}. Your purchases contribute to making a difference!',
        priority='LOW',
        action_url=f'/projects/{project.slug}/',
        action_text='Learn More',
        related_object=project,
    )


def notify_customer_wishlist_sale(customer, product, promotion):
    """Notify customer that wishlist item is on sale"""
    return create_notification(
        recipient=customer,
        notification_type='WISHLIST_SALE',
        title='Wishlist Item on Sale!',
        message=f'{product.name} from your wishlist is now {promotion.discount_percentage}% off!',
        priority='HIGH',
        action_url=f'/products/{product.slug}/',
        action_text='Buy Now',
        related_object=product,
    )


def notify_customer_loyalty_reward(customer, reward):
    """Notify customer of loyalty reward"""
    return create_notification(
        recipient=customer,
        notification_type='LOYALTY_REWARD',
        title='Loyalty Reward Earned!',
        message=f'Congratulations! You\'ve earned a reward: {reward.title}',
        priority='MEDIUM',
        action_url='/customer/loyalty/',
        action_text='View Rewards',
        related_object=reward,
    )


# Bulk Notification Helpers

def notify_all_vendors(title, message, notification_type='NEW_MESSAGE', priority='MEDIUM', action_url=None):
    """Send notification to all vendors"""
    vendors = User.objects.filter(user_type='VENDOR')
    notifications = []
    
    for vendor in vendors:
        notif = create_notification(
            recipient=vendor,
            notification_type=notification_type,
            title=title,
            message=message,
            priority=priority,
            action_url=action_url,
        )
        if notif:
            notifications.append(notif)
    
    return notifications


def notify_all_customers(title, message, notification_type='NEW_MESSAGE', priority='MEDIUM', action_url=None):
    """Send notification to all customers"""
    customers = User.objects.filter(user_type='CUSTOMER')
    notifications = []
    
    for customer in customers:
        notif = create_notification(
            recipient=customer,
            notification_type=notification_type,
            title=title,
            message=message,
            priority=priority,
            action_url=action_url,
        )
        if notif:
            notifications.append(notif)
    
    return notifications


def get_unread_count(user):
    """Get count of unread notifications for user"""
    return Notification.objects.filter(recipient=user, is_read=False).count()


def mark_all_as_read(user):
    """Mark all notifications as read for user"""
    return Notification.objects.filter(recipient=user, is_read=False).update(
        is_read=True,
        read_at=timezone.now()
    )


def delete_old_notifications(days=30):
    """Delete notifications older than specified days"""
    cutoff = timezone.now() - timedelta(days=days)
    return Notification.objects.filter(created_at__lt=cutoff, is_read=True).delete()

