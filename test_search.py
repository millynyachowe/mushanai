#!/usr/bin/env python
"""
Quick test script for search functionality
Run with: python manage.py shell < test_search.py
"""

from products.models import Product, Category, Brand, ProductReview
from accounts.models import User
from django.db.models import Count, Avg
from store.views import product_search, search_autocomplete
from django.test import RequestFactory

# Create test data
print("Creating test data...")

# Get or create a vendor
vendor, _ = User.objects.get_or_create(
    username='testvendor',
    defaults={
        'email': 'vendor@test.com',
        'user_type': 'VENDOR',
        'first_name': 'Test',
        'last_name': 'Vendor'
    }
)
vendor.set_password('testpass123')
vendor.save()

# Create category
category, _ = Category.objects.get_or_create(
    name='Test Category',
    defaults={'slug': 'test-category'}
)

# Create brand
brand, _ = Brand.objects.get_or_create(
    name='Test Brand',
    defaults={'slug': 'test-brand', 'is_local': True}
)

# Create products
products_data = [
    {
        'name': 'Test Product 1',
        'slug': 'test-product-1',
        'description': 'This is a test product',
        'short_description': 'Test product 1',
        'price': 10.00,
        'category': category,
        'brand': brand,
        'vendor': vendor,
        'is_active': True,
        'is_made_from_local_materials': True,
    },
    {
        'name': 'Test Product 2',
        'slug': 'test-product-2',
        'description': 'Another test product',
        'short_description': 'Test product 2',
        'price': 20.00,
        'category': category,
        'brand': brand,
        'vendor': vendor,
        'is_active': True,
        'is_made_from_local_materials': False,
    },
    {
        'name': 'Featured Product',
        'slug': 'featured-product',
        'description': 'A featured test product',
        'short_description': 'Featured product',
        'price': 30.00,
        'category': category,
        'brand': brand,
        'vendor': vendor,
        'is_active': True,
        'is_featured': True,
        'is_made_from_local_materials': True,
    },
]

for data in products_data:
    product, created = Product.objects.get_or_create(
        slug=data['slug'],
        defaults=data
    )
    if created:
        print(f"Created product: {product.name}")

# Create a customer for reviews
customer, _ = User.objects.get_or_create(
    username='testcustomer',
    defaults={
        'email': 'customer@test.com',
        'user_type': 'CUSTOMER',
        'first_name': 'Test',
        'last_name': 'Customer'
    }
)
customer.set_password('testpass123')
customer.save()

# Create a review
product = Product.objects.first()
if product:
    review, created = ProductReview.objects.get_or_create(
        product=product,
        customer=customer,
        defaults={
            'rating': 5,
            'comment': 'Great product!',
            'title': 'Excellent',
            'is_approved': True,
            'is_verified_purchase': True,
        }
    )
    if created:
        print(f"Created review for {product.name}")

# Test search
print("\nTesting search functionality...")
factory = RequestFactory()

# Test 1: Basic search
request = factory.get('/search/', {'q': 'test'})
request.user = customer
response = product_search(request)
print(f"✓ Search for 'test' returned {response.context_data['results_count']} results")

# Test 2: Search with filter
request = factory.get('/search/', {'q': 'test', 'local_materials': 'true'})
request.user = customer
response = product_search(request)
print(f"✓ Search with local materials filter returned {response.context_data['results_count']} results")

# Test 3: Search with price filter
request = factory.get('/search/', {'q': 'test', 'min_price': '15', 'max_price': '25'})
request.user = customer
response = product_search(request)
print(f"✓ Search with price filter returned {response.context_data['results_count']} results")

# Test 4: Autocomplete
request = factory.get('/search/autocomplete/', {'q': 'test'})
response = search_autocomplete(request)
print(f"✓ Autocomplete returned {len(response.json()['suggestions'])} suggestions")

# Test 5: Check ratings
product = Product.objects.annotate(
    avg_rating=Avg('reviews__rating'),
    review_count=Count('reviews')
).first()
if product:
    print(f"✓ Product '{product.name}' has rating: {product.avg_rating or 0} ({product.review_count} reviews)")

print("\n✅ All tests passed!")
print("\nYou can now:")
print("1. Visit http://127.0.0.1:8000/search/ to test the search page")
print("2. Visit http://127.0.0.1:8000/trending/ to see trending products")
print("3. Login as testcustomer/testpass123 or testvendor/testpass123")
print("4. Create more products and reviews in the admin panel")

