"""
Test authentication flows
"""
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.critical
class TestAuthentication:
    """Test user authentication"""
    
    def test_user_registration(self, client, db):
        """Test user can register"""
        url = reverse('register')  # Adjust based on your URL name
        data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password1': 'testpass123!@#',
            'password2': 'testpass123!@#',
            'user_type': 'CUSTOMER'
        }
        
        response = client.post(url, data)
        
        # Check user was created
        assert User.objects.filter(email='newuser@test.com').exists()
        user = User.objects.get(email='newuser@test.com')
        assert user.username == 'newuser'
        assert user.user_type == 'CUSTOMER'
    
    def test_user_login(self, client, customer_user):
        """Test user can login"""
        url = reverse('account_login')
        data = {
            'login': customer_user.email,
            'password': 'testpass123'
        }
        
        response = client.post(url, data)
        
        # Check user is logged in
        assert response.wsgi_request.user.is_authenticated
    
    def test_user_logout(self, customer_client):
        """Test user can logout"""
        url = reverse('account_logout')
        
        response = customer_client.post(url)
        
        # Check user is logged out
        assert not response.wsgi_request.user.is_authenticated
    
    def test_login_with_wrong_password(self, client, customer_user):
        """Test login fails with wrong password"""
        url = reverse('account_login')
        data = {
            'login': customer_user.email,
            'password': 'wrongpassword'
        }
        
        response = client.post(url, data)
        
        # Check user is not logged in
        assert not response.wsgi_request.user.is_authenticated
    
    def test_google_oauth_redirect(self, client):
        """Test Google OAuth redirect"""
        url = reverse('google_login')  # django-allauth URL
        
        response = client.get(url)
        
        # Should redirect to Google
        assert response.status_code in [302, 301]
        assert 'google' in response.url.lower()

