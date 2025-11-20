"""
Global pytest configuration and fixtures
"""
import pytest
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()


# ============================================================================
# USER FIXTURES
# ============================================================================

@pytest.fixture
def customer_user(db):
    """Create a customer user"""
    return User.objects.create_user(
        username='testcustomer',
        email='customer@test.com',
        password='testpass123',
        user_type='CUSTOMER',
        first_name='Test',
        last_name='Customer'
    )


@pytest.fixture
def vendor_user(db):
    """Create a vendor user"""
    return User.objects.create_user(
        username='testvendor',
        email='vendor@test.com',
        password='testpass123',
        user_type='VENDOR',
        first_name='Test',
        last_name='Vendor'
    )


@pytest.fixture
def admin_user(db):
    """Create an admin user"""
    return User.objects.create_superuser(
        username='testadmin',
        email='admin@test.com',
        password='testpass123',
        user_type='ADMIN'
    )


@pytest.fixture
def supplier_user(db):
    """Create a supplier user"""
    return User.objects.create_user(
        username='testsupplier',
        email='supplier@test.com',
        password='testpass123',
        user_type='SUPPLIER',
        first_name='Test',
        last_name='Supplier'
    )


# ============================================================================
# AUTHENTICATED CLIENTS
# ============================================================================

@pytest.fixture
def customer_client(client, customer_user):
    """Authenticated client as customer"""
    client.force_login(customer_user)
    return client


@pytest.fixture
def vendor_client(client, vendor_user):
    """Authenticated client as vendor"""
    client.force_login(vendor_user)
    return client


@pytest.fixture
def admin_client(client, admin_user):
    """Authenticated client as admin"""
    client.force_login(admin_user)
    return client


# ============================================================================
# PRODUCT FIXTURES
# ============================================================================

@pytest.fixture
def category(db):
    """Create a product category"""
    from products.models import Category
    return Category.objects.create(
        name='Test Category',
        slug='test-category',
        description='Test category description',
        tier='MID_TIER'
    )


@pytest.fixture
def brand(db):
    """Create a brand"""
    from products.models import Brand
    return Brand.objects.create(
        name='Test Brand',
        slug='test-brand',
        description='Test brand description',
        is_local=True
    )


@pytest.fixture
def product(db, vendor_user, category, brand):
    """Create a product"""
    from products.models import Product
    return Product.objects.create(
        name='Test Product',
        slug='test-product',
        description='Test product description',
        vendor=vendor_user,
        category=category,
        brand=brand,
        price=Decimal('99.99'),
        stock_quantity=100,
        is_active=True
    )


@pytest.fixture
def products(db, vendor_user, category, brand):
    """Create multiple products"""
    from products.models import Product
    return [
        Product.objects.create(
            name=f'Test Product {i}',
            slug=f'test-product-{i}',
            description=f'Test product {i} description',
            vendor=vendor_user,
            category=category,
            brand=brand,
            price=Decimal('10.00') * i,
            stock_quantity=50 + i,
            is_active=True
        )
        for i in range(1, 6)
    ]


# ============================================================================
# ORDER FIXTURES
# ============================================================================

@pytest.fixture
def order(db, customer_user, product):
    """Create an order"""
    from orders.models import Order, OrderItem
    
    order = Order.objects.create(
        customer=customer_user,
        vendor=product.vendor,
        status='PENDING',
        total_amount=product.price * 2
    )
    
    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=2,
        price=product.price
    )
    
    return order


# ============================================================================
# VENDOR FIXTURES
# ============================================================================

@pytest.fixture
def vendor_profile(db, vendor_user):
    """Create a vendor profile"""
    from vendors.models import VendorProfile
    return VendorProfile.objects.create(
        vendor=vendor_user,
        company_name='Test Company',
        business_type='RETAILER',
        description='Test company description',
        is_verified=True
    )


@pytest.fixture
def vendor_company(db, vendor_user):
    """Create a vendor company"""
    from vendors.models import VendorCompany
    return VendorCompany.objects.create(
        vendor=vendor_user,
        name='Test Company Ltd',
        description='Test company',
        is_active=True
    )


# ============================================================================
# NOTIFICATION FIXTURES
# ============================================================================

@pytest.fixture
def notification(db, customer_user):
    """Create a notification"""
    from notifications.models import Notification
    return Notification.objects.create(
        recipient=customer_user,
        notification_type='ORDER_CONFIRMED',
        title='Order Confirmed',
        message='Your order has been confirmed',
        priority='HIGH'
    )


@pytest.fixture
def notification_preferences(db, customer_user):
    """Create notification preferences"""
    from notifications.models import NotificationPreference
    return NotificationPreference.objects.create(
        user=customer_user
    )


# ============================================================================
# PROMOTION FIXTURES
# ============================================================================

@pytest.fixture
def promotion(db, vendor_user):
    """Create a promotion"""
    from vendors.models import Promotion
    from django.utils import timezone
    from datetime import timedelta
    
    return Promotion.objects.create(
        vendor=vendor_user,
        name='Test Promotion',
        description='Test promotion description',
        style='black-friday',
        discount_percentage=Decimal('25.00'),
        start_date=timezone.now(),
        end_date=timezone.now() + timedelta(days=7),
        is_active=True
    )


# ============================================================================
# HELPER FIXTURES
# ============================================================================

@pytest.fixture
def api_client():
    """DRF API client"""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_api_client(api_client, customer_user):
    """Authenticated API client"""
    api_client.force_authenticate(user=customer_user)
    return api_client


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Allow database access for all tests"""
    pass


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache before each test"""
    from django.core.cache import cache
    cache.clear()


# ============================================================================
# MOCK FIXTURES
# ============================================================================

@pytest.fixture
def mock_stripe_payment(mocker):
    """Mock Stripe payment processing"""
    mock = mocker.patch('stripe.PaymentIntent.create')
    mock.return_value = {
        'id': 'pi_test123',
        'status': 'succeeded',
        'amount': 10000
    }
    return mock


@pytest.fixture
def mock_email_send(mocker):
    """Mock email sending"""
    return mocker.patch('django.core.mail.send_mail')


@pytest.fixture
def mock_social_media_post(mocker):
    """Mock social media posting"""
    return mocker.patch('social_media.services.SocialMediaPoster.post')

