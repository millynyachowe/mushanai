"""
Notification Signals
Automatically create notifications when events occur
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .utils import *

User = get_user_model()


# Order Signals

@receiver(post_save, sender='orders.Order')
def on_order_created(sender, instance, created, **kwargs):
    """Notify vendor when new order is created"""
    if created:
        # Notify vendor
        if instance.vendor:
            notify_vendor_new_order(instance.vendor, instance)
        
        # Notify customer
        notify_customer_order_confirmed(instance.customer, instance)


@receiver(post_save, sender='orders.Order')
def on_order_status_changed(sender, instance, **kwargs):
    """Notify customer when order status changes"""
    if not instance.pk:
        return
    
    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    
    # Check if status changed
    if hasattr(old_instance, 'status') and old_instance.status != instance.status:
        if instance.status == 'SHIPPED':
            notify_customer_order_shipped(instance.customer, instance)
        elif instance.status == 'DELIVERED':
            notify_customer_order_delivered(instance.customer, instance)


# Payment Signals

@receiver(post_save, sender='payments.PaymentTransaction')
def on_payment_processed(sender, instance, created, **kwargs):
    """Notify vendor and customer when payment is processed"""
    if created and instance.status == 'COMPLETED':
        # Notify vendor
        if hasattr(instance.order, 'vendor') and instance.order.vendor:
            notify_vendor_payment_received(instance.order.vendor, instance.order)
        
        # Notify customer
        notify_customer_payment_processed(instance.order.customer, instance.order)


# Review Signals

@receiver(post_save, sender='products.ProductReview')
def on_review_created(sender, instance, created, **kwargs):
    """Notify vendor when new review is created"""
    if created and instance.product.vendor:
        notify_vendor_new_review(instance.product.vendor, instance)


# Product Signals

@receiver(post_save, sender='products.Product')
def on_product_stock_low(sender, instance, **kwargs):
    """Notify vendor when product stock is low"""
    if instance.track_inventory and instance.stock_quantity <= 5 and instance.stock_quantity > 0:
        if instance.vendor:
            notify_vendor_low_stock(instance.vendor, instance)


# Supplier Signals

@receiver(post_save, sender='suppliers.SupplierProfile')
def on_supplier_created(sender, instance, created, **kwargs):
    """Notify all vendors when new supplier is available"""
    if created and instance.is_verified:
        vendors = User.objects.filter(user_type='VENDOR')
        for vendor in vendors:
            notify_vendor_new_supplier(vendor, instance)


# Event Signals

@receiver(post_save, sender='vendors.VendorEvent')
def on_event_created(sender, instance, created, **kwargs):
    """Notify vendors when new event is created"""
    if created:
        if instance.is_global:
            # Notify all vendors
            vendors = User.objects.filter(user_type='VENDOR')
            for vendor in vendors:
                notify_vendor_event_created(vendor, instance)
        else:
            # Notify specific vendors
            for vendor in instance.vendors.all():
                notify_vendor_event_created(vendor, instance)


# Promotion Signals

@receiver(post_save, sender='vendors.Promotion')
def on_promotion_ending_soon(sender, instance, **kwargs):
    """Notify vendor when promotion is ending soon"""
    if instance.is_currently_active and instance.days_remaining <= 3 and instance.days_remaining > 0:
        notify_vendor_promotion_ending(instance.vendor, instance)


# Manufacturing Signals

@receiver(post_save, sender='manufacturing.ManufacturingOrder')
def on_manufacturing_complete(sender, instance, **kwargs):
    """Notify vendor when manufacturing is complete"""
    if not instance.pk:
        return
    
    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    
    # Check if status changed to COMPLETED
    if old_instance.status != 'COMPLETED' and instance.status == 'COMPLETED':
        notify_vendor_manufacturing_complete(instance.vendor, instance)


# Project Signals

@receiver(post_save, sender='projects.CommunityProject')
def on_project_created(sender, instance, created, **kwargs):
    """Notify customers when new community project is created"""
    if created:
        # Notify customers who want project notifications
        customers = User.objects.filter(
            user_type='CUSTOMER',
            notification_preferences__notify_new_projects=True
        )
        for customer in customers[:100]:  # Limit to avoid overwhelming the system
            notify_customer_new_project(customer, instance)


# User Signals - Create default notification preferences

@receiver(post_save, sender=User)
def create_notification_preferences(sender, instance, created, **kwargs):
    """Create default notification preferences for new users"""
    if created:
        from .models import NotificationPreference
        NotificationPreference.objects.get_or_create(user=instance)

