"""
Test checkout flow
"""
import pytest
from decimal import Decimal
from django.urls import reverse
from orders.models import Order


@pytest.mark.critical
class TestCheckoutFlow:
    """Test complete checkout process"""
    
    def test_add_to_cart(self, customer_client, product):
        """Test adding product to cart"""
        url = reverse('add_to_cart', kwargs={'product_id': product.id})
        data = {'quantity': 2}
        
        response = customer_client.post(url, data)
        
        assert response.status_code in [200, 302]
        # Check cart session or cart model
    
    def test_view_cart(self, customer_client):
        """Test viewing cart"""
        url = reverse('cart')
        
        response = customer_client.get(url)
        
        assert response.status_code == 200
    
    def test_checkout_page(self, customer_client, product):
        """Test accessing checkout page"""
        # Add product to cart first
        add_url = reverse('add_to_cart', kwargs={'product_id': product.id})
        customer_client.post(add_url, {'quantity': 1})
        
        # Access checkout
        url = reverse('checkout')
        response = customer_client.get(url)
        
        assert response.status_code == 200
    
    def test_complete_order(self, customer_client, product, mock_stripe_payment):
        """Test completing an order"""
        # Add to cart
        add_url = reverse('add_to_cart', kwargs={'product_id': product.id})
        customer_client.post(add_url, {'quantity': 2})
        
        # Complete checkout
        checkout_url = reverse('checkout')
        data = {
            'shipping_address': '123 Test St',
            'payment_method': 'stripe',
        }
        
        response = customer_client.post(checkout_url, data)
        
        # Check order was created
        assert Order.objects.filter(customer__username='testcustomer').exists()
        order = Order.objects.get(customer__username='testcustomer')
        assert order.items.count() > 0
    
    def test_order_requires_authentication(self, client):
        """Test checkout requires login"""
        url = reverse('checkout')
        
        response = client.get(url)
        
        # Should redirect to login
        assert response.status_code == 302
        assert 'login' in response.url
    
    def test_empty_cart_checkout(self, customer_client):
        """Test checkout with empty cart"""
        url = reverse('checkout')
        
        response = customer_client.get(url)
        
        # Should handle empty cart gracefully
        assert response.status_code in [200, 302]

