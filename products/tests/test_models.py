"""
Test Product models
"""
import pytest
from decimal import Decimal
from products.models import Product, Category, Brand


@pytest.mark.critical
class TestProductModel:
    """Test Product model"""
    
    def test_create_product(self, db, vendor_user, category, brand):
        """Test creating a product"""
        product = Product.objects.create(
            name='New Product',
            slug='new-product',
            description='Product description',
            vendor=vendor_user,
            category=category,
            brand=brand,
            price=Decimal('49.99'),
            stock_quantity=50
        )
        
        assert product.name == 'New Product'
        assert product.price == Decimal('49.99')
        assert product.stock_quantity == 50
        assert product.vendor == vendor_user
    
    def test_product_str(self, product):
        """Test product string representation"""
        assert str(product) == 'Test Product'
    
    def test_product_is_in_stock(self, product):
        """Test is_in_stock property"""
        assert product.is_in_stock
        
        product.stock_quantity = 0
        product.save()
        
        assert not product.is_in_stock
    
    def test_product_has_active_promotion(self, product, promotion):
        """Test product with active promotion"""
        from vendors.models import ProductPromotion
        
        ProductPromotion.objects.create(
            promotion=promotion,
            product=product
        )
        
        assert product.has_active_promotion
        assert product.promotion_percentage == 25.0
    
    def test_product_promotion_price(self, product, promotion):
        """Test promotional pricing"""
        from vendors.models import ProductPromotion
        
        # Product price is 99.99
        ProductPromotion.objects.create(
            promotion=promotion,  # 25% off
            product=product
        )
        
        expected_price = Decimal('74.99')  # 99.99 - 25%
        assert abs(product.promotion_price - expected_price) < Decimal('0.02')
    
    def test_product_slug_unique(self, db, vendor_user, category):
        """Test product slug is unique"""
        Product.objects.create(
            name='Product 1',
            slug='test-slug',
            description='Test',
            vendor=vendor_user,
            category=category,
            price=Decimal('10.00')
        )
        
        with pytest.raises(Exception):
            Product.objects.create(
                name='Product 2',
                slug='test-slug',  # Duplicate slug
                description='Test',
                vendor=vendor_user,
                category=category,
                price=Decimal('10.00')
            )


@pytest.mark.unit
class TestCategoryModel:
    """Test Category model"""
    
    def test_create_category(self, db):
        """Test creating a category"""
        category = Category.objects.create(
            name='Electronics',
            slug='electronics',
            tier='PREMIUM'
        )
        
        assert category.name == 'Electronics'
        assert category.tier == 'PREMIUM'
    
    def test_category_str(self, category):
        """Test category string representation"""
        assert str(category) == 'Test Category'


@pytest.mark.unit
class TestBrandModel:
    """Test Brand model"""
    
    def test_create_brand(self, db):
        """Test creating a brand"""
        brand = Brand.objects.create(
            name='Local Brand',
            slug='local-brand',
            is_local=True
        )
        
        assert brand.name == 'Local Brand'
        assert brand.is_local
    
    def test_brand_str(self, brand):
        """Test brand string representation"""
        assert str(brand) == 'Test Brand'

