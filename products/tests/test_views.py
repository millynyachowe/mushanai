"""
Test Product views
"""
import pytest
from django.urls import reverse


@pytest.mark.integration
class TestProductViews:
    """Test product-related views"""
    
    def test_product_list_view(self, client, products):
        """Test product list page"""
        url = reverse('product_list')  # Adjust based on your URL
        
        response = client.get(url)
        
        assert response.status_code == 200
        assert len(response.context['products']) >= 5
    
    def test_product_detail_view(self, client, product):
        """Test product detail page"""
        url = reverse('product_detail', kwargs={'slug': product.slug})
        
        response = client.get(url)
        
        assert response.status_code == 200
        assert response.context['product'] == product
        assert 'Test Product' in str(response.content)
    
    def test_product_search(self, client, product):
        """Test product search functionality"""
        url = reverse('product_search')  # Adjust based on your URL
        
        response = client.get(url, {'q': 'Test'})
        
        assert response.status_code == 200
        assert product in response.context['products']
    
    def test_product_filter_by_category(self, client, product, category):
        """Test filtering products by category"""
        url = reverse('product_list')
        
        response = client.get(url, {'category': category.slug})
        
        assert response.status_code == 200
        assert product in response.context['products']
    
    def test_vendor_product_create(self, vendor_client, category):
        """Test vendor can create product"""
        url = reverse('vendor_product_create')
        data = {
            'name': 'New Product',
            'slug': 'new-product',
            'description': 'Product description',
            'category': category.id,
            'price': '99.99',
            'stock_quantity': '50',
        }
        
        response = vendor_client.post(url, data)
        
        assert response.status_code in [200, 201, 302]
        assert Product.objects.filter(name='New Product').exists()

