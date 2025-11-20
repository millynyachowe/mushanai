"""
Test Vendor views
"""
import pytest
from django.urls import reverse


@pytest.mark.integration
class TestVendorViews:
    """Test vendor dashboard and features"""
    
    def test_vendor_dashboard(self, vendor_client):
        """Test vendor can access dashboard"""
        url = reverse('vendor_dashboard')
        
        response = vendor_client.get(url)
        
        assert response.status_code == 200
    
    def test_customer_cannot_access_vendor_dashboard(self, customer_client):
        """Test customer cannot access vendor dashboard"""
        url = reverse('vendor_dashboard')
        
        response = customer_client.get(url)
        
        # Should be denied or redirected
        assert response.status_code in [302, 403]
    
    def test_vendor_promotions_list(self, vendor_client):
        """Test vendor can view promotions"""
        url = reverse('vendor_promotions_list')
        
        response = vendor_client.get(url)
        
        assert response.status_code == 200
    
    def test_vendor_create_promotion(self, vendor_client, product):
        """Test vendor can create promotion"""
        url = reverse('vendor_promotion_create')
        data = {
            'name': 'Test Sale',
            'style': 'hot-deal',
            'discount_percentage': '20.00',
            'start_date': timezone.now().isoformat(),
            'end_date': (timezone.now() + timedelta(days=7)).isoformat(),
            'products': [product.id],
        }
        
        response = vendor_client.post(url, data)
        
        assert response.status_code in [200, 201, 302]
        assert Promotion.objects.filter(name='Test Sale').exists()
    
    def test_vendor_pos_system(self, vendor_client):
        """Test vendor POS page"""
        url = reverse('vendor_pos')
        
        response = vendor_client.get(url)
        
        assert response.status_code == 200
    
    def test_vendor_expenses_list(self, vendor_client):
        """Test vendor can view expenses"""
        url = reverse('vendor_expenses_list')
        
        response = vendor_client.get(url)
        
        assert response.status_code == 200

