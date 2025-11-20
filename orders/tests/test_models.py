"""
Test Order models
"""
import pytest
from decimal import Decimal
from orders.models import Order, OrderItem


@pytest.mark.critical
class TestOrderModel:
    """Test Order model"""
    
    def test_create_order(self, db, customer_user, vendor_user):
        """Test creating an order"""
        order = Order.objects.create(
            customer=customer_user,
            vendor=vendor_user,
            status='PENDING',
            total_amount=Decimal('199.99')
        )
        
        assert order.customer == customer_user
        assert order.vendor == vendor_user
        assert order.status == 'PENDING'
        assert order.total_amount == Decimal('199.99')
    
    def test_order_with_items(self, order, product):
        """Test order with items"""
        items = order.items.all()
        
        assert items.count() == 1
        assert items[0].product == product
        assert items[0].quantity == 2
    
    def test_order_total_calculation(self, db, customer_user, vendor_user, product):
        """Test order total is calculated correctly"""
        order = Order.objects.create(
            customer=customer_user,
            vendor=vendor_user,
            status='PENDING'
        )
        
        # Add 2 items
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=2,
            price=product.price
        )
        
        expected_total = product.price * 2
        assert abs(order.total_amount - expected_total) < Decimal('0.01')
    
    def test_order_status_changes(self, order):
        """Test changing order status"""
        assert order.status == 'PENDING'
        
        order.status = 'CONFIRMED'
        order.save()
        
        assert order.status == 'CONFIRMED'
    
    def test_order_str(self, order):
        """Test order string representation"""
        assert 'Order' in str(order)
        assert str(order.id) in str(order)


@pytest.mark.unit
class TestOrderItemModel:
    """Test OrderItem model"""
    
    def test_create_order_item(self, db, order, product):
        """Test creating an order item"""
        item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=3,
            price=product.price
        )
        
        assert item.quantity == 3
        assert item.price == product.price
    
    def test_order_item_subtotal(self, order):
        """Test order item subtotal calculation"""
        item = order.items.first()
        
        expected_subtotal = item.price * item.quantity
        assert item.subtotal == expected_subtotal

