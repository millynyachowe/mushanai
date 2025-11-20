"""
Test User and Account models
"""
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.unit
class TestUserModel:
    """Test User model"""
    
    def test_create_user(self, db):
        """Test creating a user"""
        user = User.objects.create_user(
            username='newuser',
            email='newuser@test.com',
            password='testpass123'
        )
        
        assert user.username == 'newuser'
        assert user.email == 'newuser@test.com'
        assert user.check_password('testpass123')
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser
    
    def test_create_superuser(self, db):
        """Test creating a superuser"""
        user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='testpass123'
        )
        
        assert user.is_staff
        assert user.is_superuser
        assert user.user_type == 'ADMIN'
    
    def test_user_types(self, customer_user, vendor_user, admin_user):
        """Test user type choices"""
        assert customer_user.user_type == 'CUSTOMER'
        assert vendor_user.user_type == 'VENDOR'
        assert admin_user.user_type == 'ADMIN'
    
    def test_user_str(self, customer_user):
        """Test user string representation"""
        assert str(customer_user) == 'testcustomer'
    
    def test_get_full_name(self, customer_user):
        """Test get_full_name method"""
        assert customer_user.get_full_name() == 'Test Customer'
    
    def test_user_email_unique(self, db, customer_user):
        """Test email uniqueness"""
        with pytest.raises(Exception):
            User.objects.create_user(
                username='another',
                email=customer_user.email,  # Duplicate email
                password='test'
            )

