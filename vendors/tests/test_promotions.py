"""
Test Vendor Promotions
"""
import pytest
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from vendors.models import Promotion, ProductPromotion


@pytest.mark.critical
class TestPromotionModel:
    """Test Promotion model"""
    
    def test_create_promotion(self, db, vendor_user):
        """Test creating a promotion"""
        promotion = Promotion.objects.create(
            vendor=vendor_user,
            name='Black Friday Sale',
            style='black-friday',
            discount_percentage=Decimal('30.00'),
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=7),
            is_active=True
        )
        
        assert promotion.name == 'Black Friday Sale'
        assert promotion.discount_percentage == Decimal('30.00')
    
    def test_promotion_is_active(self, promotion):
        """Test promotion active status"""
        assert promotion.is_currently_active
    
    def test_promotion_expired(self, db, vendor_user):
        """Test expired promotion"""
        promotion = Promotion.objects.create(
            vendor=vendor_user,
            name='Expired Sale',
            style='flash-sale',
            discount_percentage=Decimal('50.00'),
            start_date=timezone.now() - timedelta(days=10),
            end_date=timezone.now() - timedelta(days=1),  # Expired
            is_active=True
        )
        
        promotion.update_status()
        
        assert promotion.status == 'EXPIRED'
        assert not promotion.is_currently_active
    
    def test_product_promotion_price_calculation(self, db, product, promotion):
        """Test automatic price calculation"""
        prod_promo = ProductPromotion.objects.create(
            promotion=promotion,
            product=product
        )
        
        # Product is 99.99, discount is 25%
        expected_discounted = Decimal('74.99')
        expected_savings = Decimal('25.00')
        
        assert abs(prod_promo.discounted_price - expected_discounted) < Decimal('0.02')
        assert abs(prod_promo.savings_amount - expected_savings) < Decimal('0.02')
    
    def test_promotion_days_remaining(self, promotion):
        """Test days remaining calculation"""
        days = promotion.days_remaining
        
        assert days >= 0
        assert days <= 7

