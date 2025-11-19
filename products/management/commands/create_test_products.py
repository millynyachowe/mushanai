"""
Management command to create test products for checkout testing
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from products.models import Category, Brand, Product
from vendors.models import VendorProfile, VendorPaymentOption
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Create test products, categories, and brands for testing checkout'

    def handle(self, *args, **options):
        self.stdout.write('Creating test data...')
        
        # Create categories
        categories = {}
        category_data = [
            ('handmade-crafts', 'Handmade Crafts', 'Beautiful locally made crafts and artisanal products'),
            ('local-food', 'Local Food Products', 'Traditional and locally sourced food items'),
            ('textiles', 'Textiles & Clothing', 'Handwoven fabrics and traditional clothing'),
            ('home-decor', 'Home Decor', 'Decorative items for your home'),
        ]
        
        for slug, name, desc in category_data:
            category, created = Category.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'description': desc}
            )
            categories[slug] = category
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {name}'))
        
        # Create brands
        brands = {}
        brand_data = [
            ('zimbabwe-handmade', 'Zimbabwe Handmade', 'Local artisans creating unique products'),
            ('african-heritage', 'African Heritage', 'Traditional African products'),
            ('local-farmers', 'Local Farmers Co-op', 'Fresh produce from local farmers'),
        ]
        
        for slug, name, desc in brand_data:
            brand, created = Brand.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'description': desc, 'is_local': True}
            )
            brands[slug] = brand
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created brand: {name}'))
        
        # Get or create vendors
        vendors = User.objects.filter(user_type='VENDOR')
        vendor_list = list(vendors)
        
        if not vendor_list:
            self.stdout.write(self.style.WARNING('No vendors found. Creating test vendor...'))
            vendor = User.objects.create_user(
                username='testvendor',
                email='vendor@test.com',
                password='testpass123',
                user_type='VENDOR',
                first_name='Test',
                last_name='Vendor'
            )
            vendor_list = [vendor]
            self.stdout.write(self.style.SUCCESS(f'Created vendor: {vendor.username}'))
        
        # Ensure vendor profiles and payment options exist
        for vendor in vendor_list:
            profile, _ = VendorProfile.objects.get_or_create(
                vendor=vendor,
                defaults={
                    'company_name': f'{vendor.get_full_name() or vendor.username} Store',
                    'delivery_free_city': 'Harare',
                    'delivery_free_radius_km': Decimal('10.00'),
                    'delivery_base_fee': Decimal('5.00'),
                    'delivery_per_km_fee': Decimal('2.00'),
                }
            )
            
            # Create payment options for vendor
            payment_types = [
                ('CASH_ON_DELIVERY', 'Cash on Delivery', None, 'Pay when your order is delivered.'),
                ('ECOCASH', 'EcoCash', '0771234567', 'Send payment to the number above. Use your exact name as it appears on your EcoCash account.'),
                ('ONEMONEY', 'OneMoney', '0712345678', 'Send payment to the number above. Use your exact name as it appears on your OneMoney account.'),
            ]
            
            for ptype, label, phone, instructions in payment_types:
                VendorPaymentOption.objects.get_or_create(
                    vendor=vendor,
                    payment_type=ptype,
                    defaults={
                        'phone_number': phone,
                        'instructions': instructions,
                        'is_enabled': True,
                    }
                )
        
        # Create test products
        test_products = [
            {
                'name': 'Handwoven Basket Set',
                'slug': 'handwoven-basket-set',
                'description': 'Beautiful handwoven baskets made from local materials. Perfect for home storage and decoration. Each set includes 3 baskets of different sizes.',
                'short_description': 'Set of 3 handwoven baskets made from local materials',
                'category': categories['handmade-crafts'],
                'brand': brands['zimbabwe-handmade'],
                'vendor': vendor_list[0] if vendor_list else None,
                'price': Decimal('45.00'),
                'compare_at_price': Decimal('55.00'),
                'stock_quantity': 15,
                'is_featured': True,
                'is_active': True,
                'is_made_from_local_materials': True,
                'sku': 'BASKET-001',
            },
            {
                'name': 'Traditional Maize Meal',
                'slug': 'traditional-maize-meal',
                'description': 'Freshly ground maize meal from local farmers. 5kg bag. Perfect for making traditional sadza.',
                'short_description': '5kg bag of freshly ground maize meal',
                'category': categories['local-food'],
                'brand': brands['local-farmers'],
                'vendor': vendor_list[0] if vendor_list else None,
                'price': Decimal('12.50'),
                'stock_quantity': 50,
                'is_featured': True,
                'is_active': True,
                'is_made_from_local_materials': True,
                'sku': 'MAIZE-001',
            },
            {
                'name': 'African Print Fabric',
                'slug': 'african-print-fabric',
                'description': 'Beautiful African print fabric, 2 meters. Perfect for making traditional clothing or home decor items.',
                'short_description': '2 meters of African print fabric',
                'category': categories['textiles'],
                'brand': brands['african-heritage'],
                'vendor': vendor_list[1] if len(vendor_list) > 1 else vendor_list[0] if vendor_list else None,
                'price': Decimal('28.00'),
                'compare_at_price': Decimal('35.00'),
                'stock_quantity': 30,
                'is_featured': False,
                'is_active': True,
                'is_made_from_local_materials': True,
                'sku': 'FABRIC-001',
            },
            {
                'name': 'Wooden Carved Bowl',
                'slug': 'wooden-carved-bowl',
                'description': 'Hand-carved wooden bowl made from local timber. Unique design, perfect for serving or decoration.',
                'short_description': 'Hand-carved wooden bowl from local timber',
                'category': categories['home-decor'],
                'brand': brands['zimbabwe-handmade'],
                'vendor': vendor_list[0] if vendor_list else None,
                'price': Decimal('35.00'),
                'stock_quantity': 8,
                'is_featured': True,
                'is_active': True,
                'is_made_from_local_materials': True,
                'sku': 'BOWL-001',
            },
            {
                'name': 'Local Honey - 500ml',
                'slug': 'local-honey-500ml',
                'description': 'Pure, natural honey from local beekeepers. 500ml jar. No additives or preservatives.',
                'short_description': '500ml jar of pure local honey',
                'category': categories['local-food'],
                'brand': brands['local-farmers'],
                'vendor': None,  # Offline vendor product
                'offline_vendor_name': 'Mashonaland Beekeepers',
                'offline_vendor_phone': '0779123456',
                'offline_vendor_address': '123 Farm Road, Harare',
                'price': Decimal('18.00'),
                'stock_quantity': 25,
                'is_featured': False,
                'is_active': True,
                'is_made_from_local_materials': True,
                'sku': 'HONEY-001',
            },
            {
                'name': 'Traditional Pottery Vase',
                'slug': 'traditional-pottery-vase',
                'description': 'Handcrafted pottery vase with traditional patterns. Made using age-old techniques passed down through generations.',
                'short_description': 'Handcrafted traditional pottery vase',
                'category': categories['home-decor'],
                'brand': brands['african-heritage'],
                'vendor': vendor_list[1] if len(vendor_list) > 1 else vendor_list[0] if vendor_list else None,
                'price': Decimal('42.00'),
                'compare_at_price': Decimal('50.00'),
                'stock_quantity': 12,
                'is_featured': True,
                'is_active': True,
                'is_made_from_local_materials': True,
                'sku': 'VASE-001',
            },
        ]
        
        created_count = 0
        for product_data in test_products:
            product, created = Product.objects.get_or_create(
                slug=product_data['slug'],
                defaults=product_data
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created product: {product.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Product already exists: {product.name}'))
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Successfully created {created_count} test products!\n'
            f'Total products: {Product.objects.count()}\n'
            f'Total categories: {Category.objects.count()}\n'
            f'Total brands: {Brand.objects.count()}\n'
            f'Total vendors: {User.objects.filter(user_type="VENDOR").count()}\n'
        ))
        
        self.stdout.write(self.style.SUCCESS(
            '\n📝 Next steps:\n'
            '1. Visit http://127.0.0.1:8000/ to see the products\n'
            '2. Log in as a customer and add products to cart\n'
            '3. Go to checkout to test the payment flow\n'
            '4. Log in as a vendor to see payment submissions in the Payment Inbox\n'
        ))

