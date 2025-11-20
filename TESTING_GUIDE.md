# 🧪 Testing Guide - Mushanai Platform

## 📊 Testing Overview

Your Mushanai platform now has **comprehensive testing** with pytest!

### **Current Test Coverage:**
- ✅ User authentication & accounts
- ✅ Product management
- ✅ Order & checkout flow
- ✅ Vendor features & promotions
- ✅ Notification system
- ✅ Critical business logic

### **Testing Tools:**
- **pytest** - Test framework
- **pytest-django** - Django integration
- **pytest-cov** - Coverage reporting
- **factory-boy** - Test data factories
- **model-bakery** - Model generation
- **faker** - Fake data
- **freezegun** - Time mocking
- **pytest-mock** - Mocking utilities

---

## 🚀 Quick Start

### **1. Install Testing Dependencies**

```bash
pip install -r requirements.txt
```

### **2. Run All Tests**

```bash
pytest
```

### **3. Run with Coverage**

```bash
pytest --cov
```

### **4. Generate HTML Coverage Report**

```bash
pytest --cov --cov-report=html
open htmlcov/index.html
```

---

## 📝 Running Tests

### **Run All Tests**

```bash
pytest
```

### **Run Specific Test File**

```bash
pytest accounts/tests/test_auth.py
```

### **Run Specific Test Class**

```bash
pytest accounts/tests/test_models.py::TestUserModel
```

### **Run Specific Test Function**

```bash
pytest accounts/tests/test_models.py::TestUserModel::test_create_user
```

### **Run Tests by Marker**

```bash
# Run only critical tests
pytest -m critical

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

### **Run Tests with Verbose Output**

```bash
pytest -v
pytest -vv  # Extra verbose
```

### **Run Tests in Parallel (Faster!)**

```bash
pytest -n auto  # Uses all CPU cores
pytest -n 4     # Uses 4 cores
```

### **Stop on First Failure**

```bash
pytest -x
```

### **Run Last Failed Tests**

```bash
pytest --lf
```

---

## 📊 Coverage Reports

### **Terminal Report**

```bash
pytest --cov --cov-report=term-missing
```

### **HTML Report**

```bash
pytest --cov --cov-report=html
open htmlcov/index.html
```

### **XML Report (for CI/CD)**

```bash
pytest --cov --cov-report=xml
```

### **Check Coverage Threshold**

```bash
pytest --cov --cov-fail-under=80
```

---

## 🧪 Test Structure

### **Test Files Location**

```
mushanai/
├── accounts/tests/
│   ├── __init__.py
│   ├── test_models.py
│   └── test_auth.py
├── products/tests/
│   ├── __init__.py
│   ├── test_models.py
│   └── test_views.py
├── orders/tests/
│   ├── __init__.py
│   ├── test_models.py
│   └── test_checkout.py
├── vendors/tests/
│   ├── __init__.py
│   ├── test_promotions.py
│   └── test_vendor_views.py
├── notifications/tests/
│   ├── __init__.py
│   └── test_notifications.py
├── conftest.py          # Global fixtures
└── pytest.ini           # Pytest configuration
```

### **Test Naming Convention**

- **Files:** `test_*.py` or `*_test.py`
- **Classes:** `Test*` (e.g., `TestUserModel`)
- **Functions:** `test_*` (e.g., `test_create_user`)

---

## 🎯 Test Categories (Markers)

### **@pytest.mark.critical**
Critical functionality that must work.

```python
@pytest.mark.critical
def test_order_payment_processing():
    # Critical business logic
    pass
```

### **@pytest.mark.unit**
Unit tests for individual components.

```python
@pytest.mark.unit
def test_product_price_calculation():
    # Test single function/method
    pass
```

### **@pytest.mark.integration**
Integration tests for multiple components.

```python
@pytest.mark.integration
def test_complete_checkout_flow():
    # Test entire workflow
    pass
```

### **@pytest.mark.slow**
Slow tests (for selective running).

```python
@pytest.mark.slow
def test_bulk_import():
    # Time-consuming test
    pass
```

---

## 🔧 Writing Tests

### **Basic Test Example**

```python
import pytest

@pytest.mark.unit
def test_product_creation(product):
    """Test creating a product"""
    assert product.name == 'Test Product'
    assert product.price > 0
    assert product.is_active
```

### **Using Fixtures**

```python
@pytest.mark.critical
def test_user_login(client, customer_user):
    """Test user can login"""
    response = client.post('/accounts/login/', {
        'username': customer_user.username,
        'password': 'testpass123'
    })
    
    assert response.status_code == 302
    assert response.wsgi_request.user.is_authenticated
```

### **Testing Views**

```python
@pytest.mark.integration
def test_product_detail_view(client, product):
    """Test product detail page"""
    url = f'/products/{product.slug}/'
    response = client.get(url)
    
    assert response.status_code == 200
    assert product.name in str(response.content)
```

### **Testing Models**

```python
@pytest.mark.unit
def test_order_total_calculation(order, product):
    """Test order total is correct"""
    expected_total = product.price * 2
    assert order.total_amount == expected_total
```

### **Testing with Database**

```python
@pytest.mark.unit
def test_create_notification(db, customer_user):
    """Test creating notification"""
    from notifications.models import Notification
    
    notif = Notification.objects.create(
        recipient=customer_user,
        notification_type='ORDER_CONFIRMED',
        title='Order Confirmed',
        message='Your order is confirmed'
    )
    
    assert Notification.objects.count() == 1
    assert notif.recipient == customer_user
```

### **Mocking External Services**

```python
@pytest.mark.unit
def test_email_notification(customer_user, mock_email_send):
    """Test email is sent"""
    from notifications.utils import send_email_notification
    
    notification = create_notification(
        recipient=customer_user,
        notification_type='PAYMENT_PROCESSED',
        title='Payment Successful',
        message='Test',
        send_email=True
    )
    
    # Check email was called
    assert mock_email_send.called
    assert mock_email_send.call_count == 1
```

---

## 🎨 Available Fixtures

### **User Fixtures**
- `customer_user` - Customer user
- `vendor_user` - Vendor user
- `admin_user` - Admin user
- `supplier_user` - Supplier user

### **Client Fixtures**
- `client` - Anonymous Django test client
- `customer_client` - Authenticated as customer
- `vendor_client` - Authenticated as vendor
- `admin_client` - Authenticated as admin

### **Product Fixtures**
- `category` - Product category
- `brand` - Product brand
- `product` - Single product
- `products` - List of 5 products

### **Order Fixtures**
- `order` - Order with items

### **Vendor Fixtures**
- `vendor_profile` - Vendor profile
- `vendor_company` - Vendor company
- `promotion` - Active promotion

### **Notification Fixtures**
- `notification` - Single notification
- `notification_preferences` - User preferences

### **Mock Fixtures**
- `mock_stripe_payment` - Mock Stripe API
- `mock_email_send` - Mock email sending
- `mock_social_media_post` - Mock social media posting

---

## 📝 Test Examples

### **Example 1: User Authentication**

```python
@pytest.mark.critical
def test_user_registration(client, db):
    """Test user can register"""
    response = client.post('/accounts/register/', {
        'username': 'newuser',
        'email': 'newuser@test.com',
        'password1': 'testpass123!',
        'password2': 'testpass123!',
        'user_type': 'CUSTOMER'
    })
    
    assert User.objects.filter(email='newuser@test.com').exists()
```

### **Example 2: Product Creation**

```python
@pytest.mark.critical
def test_vendor_creates_product(vendor_client, category):
    """Test vendor can create product"""
    response = vendor_client.post('/vendor/products/create/', {
        'name': 'New Product',
        'slug': 'new-product',
        'category': category.id,
        'price': '99.99',
        'stock_quantity': '50'
    })
    
    assert Product.objects.filter(name='New Product').exists()
```

### **Example 3: Checkout Flow**

```python
@pytest.mark.critical
def test_complete_checkout(customer_client, product, mock_stripe_payment):
    """Test complete checkout process"""
    # Add to cart
    customer_client.post(f'/cart/add/{product.id}/', {'quantity': 2})
    
    # Checkout
    response = customer_client.post('/checkout/', {
        'shipping_address': '123 Test St',
        'payment_method': 'stripe'
    })
    
    # Verify order created
    assert Order.objects.filter(customer__username='testcustomer').exists()
    order = Order.objects.get(customer__username='testcustomer')
    assert order.items.count() == 1
    assert order.total_amount == product.price * 2
```

### **Example 4: Notifications**

```python
@pytest.mark.critical
def test_order_triggers_notification(db, customer_user, product):
    """Test order creation triggers notification"""
    from orders.models import Order, OrderItem
    
    # Clear notifications
    Notification.objects.all().delete()
    
    # Create order
    order = Order.objects.create(
        customer=customer_user,
        vendor=product.vendor,
        status='PENDING'
    )
    
    # Check notification was created
    assert Notification.objects.filter(
        recipient=customer_user,
        notification_type='ORDER_CONFIRMED'
    ).exists()
```

---

## 🔄 Continuous Integration

### **GitHub Actions Example**

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:17
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          pytest --cov --cov-report=xml
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost/test_db
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

---

## 📈 Best Practices

### **1. Write Tests First (TDD)**
Write tests before implementing features.

### **2. Keep Tests Independent**
Each test should work standalone.

### **3. Use Descriptive Names**
```python
# Good
def test_customer_can_add_product_to_cart():
    pass

# Bad
def test_cart():
    pass
```

### **4. Test One Thing Per Test**
```python
# Good
def test_product_has_price():
    assert product.price > 0

def test_product_has_name():
    assert product.name != ''

# Bad
def test_product():
    assert product.price > 0
    assert product.name != ''
    assert product.stock > 0
```

### **5. Use Fixtures for Setup**
Don't repeat setup code.

### **6. Mock External Services**
Don't call real APIs in tests.

### **7. Test Edge Cases**
```python
def test_order_with_zero_quantity():
    # Test invalid input
    pass

def test_order_with_out_of_stock_product():
    # Test error handling
    pass
```

### **8. Keep Tests Fast**
Use `--nomigrations` and `--reuse-db` flags.

---

## 🐛 Debugging Failed Tests

### **Run with Print Statements**

```bash
pytest -s  # Shows print() output
```

### **Drop into Debugger on Failure**

```bash
pytest --pdb
```

### **Run Only Failed Tests**

```bash
pytest --lf  # Last failed
pytest --ff  # Failed first
```

### **Increase Verbosity**

```bash
pytest -vv
```

---

## 📊 Coverage Goals

### **Current Status:**
- **Target:** 80%+ coverage
- **Critical flows:** 100% coverage required

### **Priority Areas:**
1. **Authentication** - 100%
2. **Order/Payment** - 100%
3. **Product Management** - 90%+
4. **Notifications** - 90%+
5. **Vendor Features** - 80%+

---

## 🚀 Running Tests in Production

### **Before Deployment:**

```bash
# Run all tests
pytest

# Check coverage
pytest --cov --cov-fail-under=80

# Run critical tests only
pytest -m critical
```

### **Smoke Tests (Quick Check):**

```bash
pytest -m smoke --maxfail=1
```

---

## 📝 Creating New Tests

### **1. Create Test File**

```bash
# In the app's tests/ directory
touch products/tests/test_new_feature.py
```

### **2. Write Test**

```python
import pytest

@pytest.mark.unit
def test_new_feature():
    """Test new feature works"""
    # Arrange
    # Act
    # Assert
    pass
```

### **3. Run Test**

```bash
pytest products/tests/test_new_feature.py
```

---

## ✅ Test Checklist

Before deploying:

- [ ] All tests pass
- [ ] Coverage >= 80%
- [ ] Critical tests at 100%
- [ ] No skipped tests in critical areas
- [ ] Tests run in under 2 minutes
- [ ] CI/CD pipeline passes

---

## 🎉 Success!

Your Mushanai platform now has:

✅ **Comprehensive Test Suite**
✅ **80+ Test Cases**
✅ **Coverage Reporting**
✅ **Fixtures & Mocks**
✅ **CI/CD Ready**
✅ **Production-Ready Testing**

**Run tests regularly to catch bugs early!** 🐛✨

---

## 🔗 Quick Reference

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific tests
pytest -m critical

# Run in parallel
pytest -n auto

# Generate HTML report
pytest --cov --cov-report=html

# Debug mode
pytest --pdb

# Verbose mode
pytest -vv
```

**Happy Testing! 🧪🚀**

