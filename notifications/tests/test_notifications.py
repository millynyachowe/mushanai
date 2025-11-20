"""
Test Notification system
"""
import pytest
from notifications.models import Notification, NotificationPreference
from notifications.utils import (
    create_notification,
    notify_vendor_new_order,
    notify_customer_order_confirmed,
    get_unread_count
)


@pytest.mark.critical
class TestNotificationModel:
    """Test Notification model"""
    
    def test_create_notification(self, db, customer_user):
        """Test creating a notification"""
        notif = Notification.objects.create(
            recipient=customer_user,
            notification_type='ORDER_CONFIRMED',
            title='Order Confirmed',
            message='Your order has been confirmed',
            priority='HIGH'
        )
        
        assert notif.title == 'Order Confirmed'
        assert notif.priority == 'HIGH'
        assert not notif.is_read
    
    def test_mark_as_read(self, notification):
        """Test marking notification as read"""
        assert not notification.is_read
        
        notification.mark_as_read()
        
        assert notification.is_read
        assert notification.read_at is not None
    
    def test_notification_icon(self, notification):
        """Test notification icon property"""
        assert notification.icon == '✅'  # ORDER_CONFIRMED
    
    def test_get_unread_count(self, customer_user):
        """Test getting unread count"""
        # Create 3 notifications
        for i in range(3):
            Notification.objects.create(
                recipient=customer_user,
                notification_type='NEW_MESSAGE',
                title=f'Message {i}',
                message='Test'
            )
        
        count = get_unread_count(customer_user)
        
        assert count == 3


@pytest.mark.critical
class TestNotificationUtils:
    """Test notification utility functions"""
    
    def test_create_notification_util(self, customer_user):
        """Test create_notification utility"""
        notif = create_notification(
            recipient=customer_user,
            notification_type='PAYMENT_PROCESSED',
            title='Payment Successful',
            message='Your payment was processed',
            priority='HIGH'
        )
        
        assert notif is not None
        assert notif.title == 'Payment Successful'
    
    def test_notify_vendor_new_order(self, vendor_user, order):
        """Test vendor order notification"""
        notif = notify_vendor_new_order(vendor_user, order)
        
        assert notif is not None
        assert notif.notification_type == 'NEW_ORDER'
        assert notif.recipient == vendor_user
    
    def test_notify_customer_order_confirmed(self, customer_user, order):
        """Test customer order confirmation"""
        notif = notify_customer_order_confirmed(customer_user, order)
        
        assert notif is not None
        assert notif.notification_type == 'ORDER_CONFIRMED'
        assert notif.recipient == customer_user
    
    def test_notification_respects_preferences(self, customer_user):
        """Test notifications respect user preferences"""
        # Disable order notifications
        prefs = NotificationPreference.objects.create(
            user=customer_user,
            notify_order_status=False
        )
        
        notif = create_notification(
            recipient=customer_user,
            notification_type='ORDER_CONFIRMED',
            title='Order Confirmed',
            message='Test'
        )
        
        # Should return None because preference is disabled
        assert notif is None
    
    def test_email_notification_sent(self, customer_user, mock_email_send):
        """Test email notification is sent"""
        notif = create_notification(
            recipient=customer_user,
            notification_type='PAYMENT_PROCESSED',
            title='Payment Successful',
            message='Test',
            send_email=True
        )
        
        # Check email was attempted
        assert mock_email_send.called


@pytest.mark.integration
class TestNotificationSignals:
    """Test notification signals"""
    
    def test_order_creates_notifications(self, db, customer_user, product):
        """Test creating order triggers notifications"""
        from orders.models import Order, OrderItem
        
        # Clear existing notifications
        Notification.objects.all().delete()
        
        # Create order (should trigger signal)
        order = Order.objects.create(
            customer=customer_user,
            vendor=product.vendor,
            status='PENDING'
        )
        
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=1,
            price=product.price
        )
        
        # Check notifications were created
        customer_notifs = Notification.objects.filter(recipient=customer_user)
        vendor_notifs = Notification.objects.filter(recipient=product.vendor)
        
        assert customer_notifs.exists()
        assert vendor_notifs.exists()

