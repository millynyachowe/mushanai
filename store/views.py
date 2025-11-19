from decimal import Decimal, InvalidOperation
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count, Avg, F, Min, Max
from django.db import models
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from products.models import Product, Brand, Category, ProductReview, ReviewPhoto, ReviewHelpfulVote
from products.recommendations import (
    get_customers_also_bought,
    get_similar_products,
    get_recently_viewed,
    get_personalized_recommendations,
    get_trending_products,
    get_seasonal_suggestions,
    track_product_view
)
from vendors.models import VendorProfile, VendorPaymentOption, VendorDeliveryZone
from projects.models import CommunityProject
from customers.models import SearchHistory, SocialShare, BackInStockAlert, VendorSubscription
from django.contrib.auth import get_user_model
from .social_sharing import (
    get_product_share_data,
    get_project_share_data,
    get_vendor_share_data
)
from orders.models import Cart, CartItem, Order, OrderItem, OrderPaymentSubmission

User = get_user_model()


def home(request):
    from products.models import CategoryDisplaySchedule
    from customers.models import CustomerTestimonial
    from projects.models import CommunityProject
    from django.utils import timezone
    
    # Get scheduled categories for homepage
    today = timezone.now().date()
    active_schedules = CategoryDisplaySchedule.objects.filter(
        is_active=True,
        start_date__lte=today
    ).filter(
        models.Q(end_date__isnull=True) | models.Q(end_date__gte=today)
    ).select_related('category').order_by('display_order', 'category__name')
    
    # Group by period and get current schedules
    category_sections = []
    for schedule in active_schedules:
        if schedule.is_current():
            category = schedule.category
            if not category.is_active:
                continue
            
            # Get products for this category
            products = Product.objects.filter(
                category=category,
                is_active=True
            ).annotate(
                avg_rating=Avg('reviews__rating'),
                review_total=Count('reviews', distinct=True)
            ).order_by('-created_at')[:12]
            
            if products.exists():
                category_sections.append({
                    'category': category,
                    'schedule': schedule,
                    'products': products,
                    'header': category.display_header or category.name,
                    'tagline': category.display_tagline or category.description or '',
                })
    
    # If no scheduled categories, show all active categories with products
    if not category_sections:
        categories = Category.objects.filter(is_active=True).order_by('tier', 'name')
        for category in categories:
            products = Product.objects.filter(
                category=category,
                is_active=True
            ).annotate(
                avg_rating=Avg('reviews__rating'),
                review_total=Count('reviews', distinct=True)
            ).order_by('-created_at')[:12]
            
            if products.exists():
                category_sections.append({
                    'category': category,
                    'schedule': None,
                    'products': products,
                    'header': category.display_header or category.name,
                    'tagline': category.display_tagline or category.description or '',
                })
    
    # Premium Picks - Get premium tier products
    premium_products = Product.objects.filter(
        category__tier='PREMIUM',
        is_active=True
    ).annotate(
        avg_rating=Avg('reviews__rating'),
        review_total=Count('reviews', distinct=True)
    ).order_by('-is_featured', '-created_at')[:4]
    
    # Trending products
    trending_products = get_trending_products(limit=8)
    
    # Featured vendors/brands
    featured_vendors = VendorProfile.objects.filter(
        is_verified=True,
        vendor__products__is_active=True
    ).distinct().annotate(
        product_count=Count('vendor__products', filter=Q(vendor__products__is_active=True))
    ).filter(product_count__gt=0).order_by('-overall_rating', '-total_reviews')[:6]
    
    # All categories for "Shop by Category"
    all_categories = Category.objects.filter(
        is_active=True,
        products__is_active=True
    ).distinct().annotate(
        product_count=Count('products', filter=Q(products__is_active=True))
    ).filter(product_count__gt=0).order_by('tier', 'name')
    
    # Featured testimonials
    featured_testimonials = CustomerTestimonial.objects.filter(
        status='APPROVED',
        is_featured=True
    ).select_related('customer', 'vendor').order_by('-created_at')[:3]
    
    # If not enough featured, get recent approved ones
    if featured_testimonials.count() < 3:
        additional = CustomerTestimonial.objects.filter(
            status='APPROVED'
        ).exclude(id__in=[t.id for t in featured_testimonials]).select_related('customer', 'vendor').order_by('-created_at')[:3-featured_testimonials.count()]
        featured_testimonials = list(featured_testimonials) + list(additional)
    
    # Community projects for impact section
    active_projects = CommunityProject.objects.filter(
        is_approved=True,
        status__in=['ACTIVE', 'IN_PROGRESS']
    ).order_by('-created_at')[:1]
    
    context = {
        'category_sections': category_sections,
        'premium_products': premium_products,
        'trending_products': trending_products,
        'featured_vendors': featured_vendors,
        'all_categories': all_categories,
        'featured_testimonials': featured_testimonials,
        'active_projects': active_projects,
    }
    return render(request, 'store/index.html', context)


def brand_stories(request):
    # Get vendor profiles that have published brand stories (description published)
    brands = VendorProfile.objects.filter(
        description__isnull=False
    ).exclude(description='').order_by('-created_at')
    
    context = {
        'brands': brands,
    }
    return render(request, 'store/brand_stories.html', context)


def product_detail(request, slug):
    """
    Product detail page with recommendations
    """
    product = get_object_or_404(Product, slug=slug, is_active=True)
    
    # Track product view
    customer = request.user if request.user.is_authenticated and request.user.user_type == 'CUSTOMER' else None
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    
    ip_address = request.META.get('REMOTE_ADDR')
    track_product_view(product, customer=customer, session_key=session_key, ip_address=ip_address)
    
    # Get product with annotations
    product = Product.objects.filter(id=product.id).annotate(
        avg_rating=Avg('reviews__rating'),
        review_total=Count('reviews', distinct=True)
    ).first()
    
    # Get vendor profile with badges
    vendor_profile = None
    offline_vendor_details = None
    if product.vendor:
        try:
            vendor_profile = VendorProfile.objects.select_related('vendor').prefetch_related('badges').get(vendor=product.vendor)
            # Ensure vendor metrics are up to date (lazy update - only if not calculated recently)
            if not vendor_profile.ratings_last_calculated or (timezone.now() - vendor_profile.ratings_last_calculated) > timedelta(hours=1):
                vendor_profile.update_metrics()
        except VendorProfile.DoesNotExist:
            pass
    else:
        offline_vendor_details = {
            'name': product.vendor_display_name,
            'phone': product.vendor_contact_phone,
            'address': product.vendor_contact_address,
        }
    
    # Get approved reviews with photos and vendor responses
    reviews = ProductReview.objects.filter(
        product=product,
        is_approved=True
    ).select_related('customer', 'product__vendor').prefetch_related('photos').order_by('-created_at')[:20]
    
    # Check if customer has already reviewed this product
    user_review = None
    has_purchased = False
    can_review = False
    if customer:
        try:
            user_review = ProductReview.objects.get(product=product, customer=customer)
        except ProductReview.DoesNotExist:
            pass
        
        # Check if customer has purchased this product (for verified purchase badge)
        has_purchased = product.customer_has_purchased(customer)
        # Allow all customers to review (not just those who purchased)
        can_review = user_review is None
    
    # Get recommendations
    customers_also_bought = get_customers_also_bought(product, limit=8)
    similar_products = get_similar_products(product, limit=8)
    
    # Get recently viewed (for authenticated users)
    recently_viewed = []
    if customer:
        recently_viewed = get_recently_viewed(customer=customer, limit=8)
    
    # Get social sharing data
    share_data = get_product_share_data(request, product)
    
    # Back in stock alert status
    back_in_stock_alert = None
    show_back_in_stock = False
    if customer and not product.is_in_stock:
        back_in_stock_alert = BackInStockAlert.objects.filter(
            customer=customer,
            product=product,
        ).first()
        show_back_in_stock = True
    
    context = {
        'product': product,
        'vendor_profile': vendor_profile,
        'offline_vendor': offline_vendor_details,
        'reviews': reviews,
        'user_review': user_review,
        'can_review': can_review,
        'has_purchased': has_purchased,
        'customers_also_bought': customers_also_bought,
        'similar_products': similar_products,
        'recently_viewed': recently_viewed,
        'share_data': share_data,
        'back_in_stock_alert': back_in_stock_alert,
        'show_back_in_stock': show_back_in_stock,
    }
    
    return render(request, 'store/product_detail.html', context)


def vendor_profile_public(request, vendor_id):
    """
    Public vendor profile page showing ratings, badges, and products
    """
    vendor = get_object_or_404(User, id=vendor_id, user_type='VENDOR')
    
    try:
        vendor_profile = VendorProfile.objects.select_related('vendor').prefetch_related('badges').get(vendor=vendor)
        # Update metrics if needed
        if not vendor_profile.ratings_last_calculated or (timezone.now() - vendor_profile.ratings_last_calculated) > timedelta(hours=1):
            vendor_profile.update_metrics()
    except VendorProfile.DoesNotExist:
        messages.error(request, 'Vendor profile not found.')
        return redirect('home')
    
    # Get vendor's products
    products = Product.objects.filter(
        vendor=vendor,
        is_active=True
    ).annotate(
        avg_rating=Avg('reviews__rating'),
        review_total=Count('reviews', distinct=True)
    ).order_by('-created_at')[:20]
    
    # Get vendor's reviews
    reviews = ProductReview.objects.filter(
        product__vendor=vendor,
        is_approved=True
    ).select_related('product', 'customer').order_by('-created_at')[:10]
    
    # Get social sharing data
    share_data = get_vendor_share_data(request, vendor)
    
    # Get approved testimonials
    from customers.models import CustomerTestimonial
    testimonials = CustomerTestimonial.objects.filter(
        vendor=vendor,
        status='APPROVED'
    ).select_related('customer').order_by('-is_featured', '-created_at')[:10]
    
    is_vendor_subscribed = False
    if request.user.is_authenticated and request.user.user_type == 'CUSTOMER':
        is_vendor_subscribed = VendorSubscription.objects.filter(
            customer=request.user,
            vendor=vendor
        ).exists()
    
    context = {
        'vendor': vendor,
        'vendor_profile': vendor_profile,
        'products': products,
        'reviews': reviews,
        'testimonials': testimonials,
        'share_data': share_data,
        'is_vendor_subscribed': is_vendor_subscribed,
    }
    
    return render(request, 'store/vendor_profile.html', context)


def _calculate_delivery_fee(vendor_profile, city, distance):
    """
    Calculate delivery fee based on vendor delivery settings.
    """
    if not vendor_profile:
        return Decimal('0.00')
    
    try:
        distance_decimal = Decimal(distance) if distance is not None else None
    except InvalidOperation:
        distance_decimal = None
    
    free_city = vendor_profile.delivery_free_city
    free_radius = vendor_profile.delivery_free_radius_km
    base_fee = vendor_profile.delivery_base_fee or Decimal('0.00')
    per_km = vendor_profile.delivery_per_km_fee or Decimal('0.00')
    
    if free_city and city and city.strip().lower() == free_city.strip().lower():
        return Decimal('0.00')
    
    if distance_decimal is not None and free_radius and distance_decimal <= free_radius:
        return Decimal('0.00')
    
    fee = base_fee
    if per_km and distance_decimal is not None:
        extra_distance = distance_decimal
        if free_radius:
            extra_distance = max(distance_decimal - free_radius, Decimal('0.00'))
        fee += per_km * extra_distance
    
    return fee


@login_required
def checkout(request):
    """
    Custom checkout flow for customers to submit payments to vendors.
    """
    if request.user.user_type != 'CUSTOMER':
        messages.error(request, 'Checkout is available to customers only.')
        return redirect('home')
    
    cart, _ = Cart.objects.get_or_create(customer=request.user)
    cart_items = cart.items.select_related('product', 'product__vendor')
    
    if not cart_items.exists():
        messages.info(request, 'Your cart is empty.')
        return redirect('home')
    
    # Group items by vendor/offline vendor
    vendor_groups = {}
    for item in cart_items:
        product = item.product
        vendor = product.vendor
        if vendor:
            key = f"vendor-{vendor.id}"
        else:
            key = f"offline-{(product.offline_vendor_name or product.id)}"
        
        group = vendor_groups.setdefault(key, {
            'key': key,
            'vendor': vendor,
            'offline_details': {
                'name': product.vendor_display_name,
                'phone': product.vendor_contact_phone,
                'address': product.vendor_contact_address,
            } if not vendor else None,
            'items': [],
            'subtotal': Decimal('0.00'),
        })
        group['items'].append({
            'product': product,
            'quantity': item.quantity,
            'price': product.price,
            'subtotal': product.price * item.quantity,
        })
        group['subtotal'] += product.price * item.quantity
    
    # Attach payment options and delivery settings
    for key, group in vendor_groups.items():
        vendor = group['vendor']
        payment_options = []
        if vendor:
            options_qs = VendorPaymentOption.objects.filter(vendor=vendor, is_enabled=True)
            if not options_qs.exists():
                # Fallback to COD if vendor has not configured options
                options_qs = VendorPaymentOption.objects.filter(vendor=vendor, payment_type='CASH_ON_DELIVERY')
                if not options_qs.exists():
                    VendorPaymentOption.objects.update_or_create(
                        vendor=vendor,
                        payment_type='CASH_ON_DELIVERY',
                        defaults={'is_enabled': True}
                    )
                    options_qs = VendorPaymentOption.objects.filter(vendor=vendor, payment_type='CASH_ON_DELIVERY')
            for option in options_qs:
                payment_options.append({
                    'code': option.payment_type,
                    'label': option.get_payment_type_display(),
                    'phone': option.phone_number,
                    'merchant_name': option.merchant_name,
                    'instructions': option.instructions,
                })
            vendor_profile = VendorProfile.objects.filter(vendor=vendor).first()
        else:
            payment_options.append({
                'code': 'CASH_ON_DELIVERY',
                'label': 'Cash on Delivery',
                'phone': group['offline_details']['phone'],
                'instructions': 'Pay when your order is delivered.',
            })
            vendor_profile = None
        
        group['payment_options'] = payment_options
        group['vendor_profile'] = vendor_profile
        # Add vendor location for distance calculation
        if vendor_profile:
            group['vendor_location'] = {
                'address': vendor_profile.location_address,
                'latitude': float(vendor_profile.location_latitude) if vendor_profile.location_latitude else None,
                'longitude': float(vendor_profile.location_longitude) if vendor_profile.location_longitude else None,
                'per_km_fee': float(vendor_profile.delivery_per_km_fee) if vendor_profile.delivery_per_km_fee else None,
                'base_fee': float(vendor_profile.delivery_base_fee) if vendor_profile.delivery_base_fee else 0,
                'free_radius': float(vendor_profile.delivery_free_radius_km) if vendor_profile.delivery_free_radius_km else None,
            }
        else:
            group['vendor_location'] = {
                'address': None,
                'latitude': None,
                'longitude': None,
                'per_km_fee': None,
                'base_fee': 0,
                'free_radius': None,
            }
        
        # Delivery options (Harare + city-specific + custom)
        delivery_options = []
        if vendor_profile:
            harare_radius = vendor_profile.harare_radius_km or Decimal('10.00')
            if vendor_profile.harare_within_radius_fee is not None:
                delivery_options.append({
                    'code': 'HARARE_WITHIN',
                    'label': f'Harare (within {harare_radius} km)',
                    'fee': vendor_profile.harare_within_radius_fee,
                    'description': 'Fixed fee for deliveries within Harare radius',
                    'requires_custom': False,
                    'requires_map': False,
                })
            if vendor_profile.harare_beyond_radius_fee is not None:
                delivery_options.append({
                    'code': 'HARARE_OUTSIDE',
                    'label': 'Harare (outside radius)',
                    'fee': vendor_profile.harare_beyond_radius_fee,
                    'description': 'Fixed fee for Harare deliveries beyond radius',
                    'requires_custom': False,
                    'requires_map': False,
                })
            city_zones = VendorDeliveryZone.objects.filter(
                vendor=vendor,
                is_active=True,
                fee__isnull=False
            ).order_by('city')
            for zone in city_zones:
                delivery_options.append({
                    'code': f'CITY_{zone.city}',
                    'label': zone.get_city_display(),
                    'fee': zone.fee,
                    'description': f'Deliveries to {zone.get_city_display()}',
                    'requires_custom': False,
                    'requires_map': False,
                })
        # Custom option fallback
        custom_requires_map = bool(
            group['vendor_location'] and group['vendor_location']['latitude'] and group['vendor_location']['longitude']
        )
        delivery_options.append({
            'code': 'CUSTOM',
            'label': 'Other location (distance-based)',
            'fee': None,
            'description': 'Calculate delivery fee based on distance',
            'requires_custom': True,
            'requires_map': custom_requires_map,
        })
        group['delivery_options'] = delivery_options
    
    form_data = {
        'shipping_address': '',
        'shipping_city': '',
        'shipping_country': 'Zimbabwe',
        'shipping_phone': '',
        'delivery_details': {},
    }
    for key, group in vendor_groups.items():
        first_option = group['payment_options'][0] if group['payment_options'] else {'code': 'CASH_ON_DELIVERY'}
        form_data['delivery_details'][key] = {
            'payment_method': first_option['code'],
            'payer_name': '',
            'delivery_city': form_data['shipping_city'],
            'delivery_address': form_data['shipping_address'],
            'delivery_distance': '',
            'delivery_option': group['delivery_options'][0]['code'] if group['delivery_options'] else 'CUSTOM',
        }
        group['form_defaults'] = form_data['delivery_details'][key]
    
    if request.method == 'POST':
        shipping_address = request.POST.get('shipping_address', '').strip()
        shipping_city = request.POST.get('shipping_city', '').strip()
        shipping_country = request.POST.get('shipping_country', 'Zimbabwe').strip()
        shipping_phone = request.POST.get('shipping_phone', '').strip()
        
        form_data.update({
            'shipping_address': shipping_address,
            'shipping_city': shipping_city,
            'shipping_country': shipping_country,
            'shipping_phone': shipping_phone,
        })
        
        errors = []
        if not shipping_address:
            errors.append('Please provide a shipping address.')
        if not shipping_city:
            errors.append('Please provide the delivery city or town.')
        if not shipping_phone:
            errors.append('Please provide a contact phone number.')
        
        vendor_checkout_data = {}
        total_delivery_fee = Decimal('0.00')
        
        for key, group in vendor_groups.items():
            payment_method = request.POST.get(f'payment_method_{key}')
            payer_name = request.POST.get(f'payer_name_{key}', '').strip()
            delivery_city = request.POST.get(f'delivery_city_{key}', shipping_city).strip()
            delivery_address = request.POST.get(f'delivery_address_{key}', '').strip()
            delivery_distance_raw = request.POST.get(f'delivery_distance_{key}', '').strip()
            delivery_option = request.POST.get(f'delivery_option_{key}', '').strip()
            proof_file = request.FILES.get(f'proof_{key}')
            
            form_data['delivery_details'][key] = {
                'payment_method': payment_method,
                'payer_name': payer_name,
                'delivery_city': delivery_city,
                'delivery_address': delivery_address,
                'delivery_distance': delivery_distance_raw,
                'delivery_option': delivery_option,
            }
            group['form_defaults'] = form_data['delivery_details'][key]
            
            option_codes = [opt['code'] for opt in group['payment_options']]
            if payment_method not in option_codes:
                errors.append(f'Please select a payment option for {group["offline_details"]["name"] if group["vendor"] is None else group["vendor"].get_full_name() or group["vendor"].username}.')
            
            if not payer_name:
                errors.append('Please provide the name that will appear as the sender of the payment.')
            
            delivery_option_codes = [opt['code'] for opt in group['delivery_options']]
            if not delivery_option or delivery_option not in delivery_option_codes:
                errors.append(f'Please select a delivery option for {group["vendor"].get_full_name() if group["vendor"] else group["offline_details"]["name"]}.')
            
            distance_value = None
            selected_delivery_option = next((opt for opt in group['delivery_options'] if opt['code'] == delivery_option), None)
            if delivery_option == 'CUSTOM':
                if not delivery_address:
                    errors.append('Please provide the delivery address for custom delivery.')
                if delivery_distance_raw:
                    try:
                        distance_value = Decimal(delivery_distance_raw)
                        if distance_value < 0:
                            raise InvalidOperation
                    except (InvalidOperation, TypeError):
                        errors.append('Please provide a valid delivery distance (in km).')
                else:
                    errors.append('Please provide the delivery distance for custom delivery.')
                delivery_fee = _calculate_delivery_fee(group.get('vendor_profile'), delivery_city, distance_value)
            else:
                fee_value = selected_delivery_option['fee'] if selected_delivery_option else Decimal('0.00')
                delivery_fee = Decimal(fee_value or 0)
            
            total_delivery_fee += delivery_fee
            
            selected_option = next((opt for opt in group['payment_options'] if opt['code'] == payment_method), None)
            require_proof = payment_method != 'CASH_ON_DELIVERY'
            if require_proof and not proof_file:
                errors.append('Please upload proof of payment for mobile wallet transactions.')
            
            vendor_checkout_data[key] = {
                'payment_method': payment_method,
                'payer_name': payer_name,
                'proof': proof_file,
                'delivery_city': delivery_city,
                'delivery_address': delivery_address,
                'delivery_distance': distance_value,
                'delivery_fee': delivery_fee,
                'delivery_option': delivery_option,
                'payment_phone': selected_option['phone'] if selected_option else None,
                'instructions': selected_option['instructions'] if selected_option else '',
            }
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'store/checkout.html', {
                'cart_items': cart_items,
                'vendor_groups': vendor_groups,
                'form_data': form_data,
            })
        
        # Create order
        order_subtotal = sum((item.product.price * item.quantity for item in cart_items), Decimal('0.00'))
        order_total = order_subtotal + total_delivery_fee
        
        order = Order.objects.create(
            customer=request.user,
            shipping_address=shipping_address,
            shipping_city=shipping_city,
            shipping_country=shipping_country,
            shipping_phone=shipping_phone,
            subtotal=order_subtotal,
            shipping_cost=total_delivery_fee,
            total=order_total,
            payment_method='MANUAL',
            payment_status='PENDING',
        )
        
        # Create order items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                vendor=item.product.vendor,
                product_name=item.product.name,
                product_sku=item.product.sku,
                quantity=item.quantity,
                price=item.product.price,
                subtotal=item.product.price * item.quantity
            )
        
        # Create payment submissions per vendor
        for key, group in vendor_groups.items():
            vendor_data = vendor_checkout_data[key]
            OrderPaymentSubmission.objects.create(
                order=order,
                vendor=group['vendor'],
                payment_type=vendor_data['payment_method'],
                payment_phone=vendor_data['payment_phone'],
                payer_name=vendor_data['payer_name'],
                amount=group['subtotal'] + vendor_data['delivery_fee'],
                proof_of_payment=vendor_data['proof'],
            )
        
        # Clear cart
        cart.items.all().delete()
        
        messages.success(request, 'Thank you! Your order has been placed. Vendors will confirm your payment soon.')
        return redirect('checkout_success', order_id=order.id)
    
    return render(request, 'store/checkout.html', {
        'cart_items': cart_items,
        'vendor_groups': vendor_groups,
        'form_data': form_data,
    })


@login_required
def checkout_success(request, order_id):
    """
    Confirmation page after checkout.
    """
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    payment_submissions = order.payment_submissions.select_related('vendor')
    
    return render(request, 'store/checkout_success.html', {
        'order': order,
        'payment_submissions': payment_submissions,
    })


@login_required
def submit_review(request, slug):
    """
    Submit a product review
    """
    if request.user.user_type != 'CUSTOMER':
        messages.error(request, 'Only customers can submit reviews.')
        return redirect('product_detail', slug=slug)
    
    product = get_object_or_404(Product, slug=slug, is_active=True)
    customer = request.user
    
    # Check if customer has already reviewed this product
    existing_review = ProductReview.objects.filter(product=product, customer=customer).first()
    if existing_review:
        messages.error(request, 'You have already reviewed this product.')
        return redirect('product_detail', slug=slug)
    
    # Check if customer has purchased this product (optional - can be enabled/disabled)
    # For now, allow all customers to review, but mark verified purchase if they bought it
    has_purchased = product.customer_has_purchased(customer)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        title = request.POST.get('title', '').strip()
        comment = request.POST.get('comment', '').strip()
        
        if not rating or not comment:
            messages.error(request, 'Please provide a rating and comment.')
            return redirect('product_detail', slug=slug)
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError("Invalid rating")
        except (ValueError, TypeError):
            messages.error(request, 'Invalid rating. Please select a rating from 1 to 5 stars.')
            return redirect('product_detail', slug=slug)
        
        # Create review
        review = ProductReview.objects.create(
            product=product,
            customer=customer,
            rating=rating,
            title=title if title else None,
            comment=comment,
            is_verified_purchase=has_purchased,
            is_approved=False  # Requires admin approval
        )
        
        # Handle uploaded photos
        photos = request.FILES.getlist('photos')
        for i, photo in enumerate(photos[:5]):  # Limit to 5 photos
            ReviewPhoto.objects.create(
                review=review,
                image=photo,
                order=i
            )
        
        # Note: Vendor rating will be updated when review is approved by admin
        # This is handled in the ProductReviewAdmin's approve_reviews action
        
        messages.success(request, 'Your review has been submitted and is pending approval. Thank you for your feedback!')
        return redirect('product_detail', slug=slug)
    
    return redirect('product_detail', slug=slug)


@login_required
def vendor_response(request, review_id):
    """
    Vendor response to a review
    """
    review = get_object_or_404(ProductReview, id=review_id)
    
    # Check if user is the vendor for this product
    if request.user != review.product.vendor or request.user.user_type != 'VENDOR':
        messages.error(request, 'You can only respond to reviews for your own products.')
        return redirect('product_detail', slug=review.product.slug)
    
    if request.method == 'POST':
        response_text = request.POST.get('response', '').strip()
        
        if not response_text:
            messages.error(request, 'Please provide a response.')
            return redirect('product_detail', slug=review.product.slug)
        
        review.vendor_response = response_text
        review.vendor_response_date = timezone.now()
        review.save()
        
        # Update vendor response time metrics
        try:
            vendor_profile = request.user.vendor_profile
            vendor_profile.calculate_response_time()
            vendor_profile.assign_badges()
        except:
            pass
        
        messages.success(request, 'Your response has been added to the review.')
        return redirect('product_detail', slug=review.product.slug)
    
    return redirect('product_detail', slug=review.product.slug)


@require_POST
def mark_review_helpful(request, review_id):
    """
    Mark a review as helpful
    """
    review = get_object_or_404(ProductReview, id=review_id, is_approved=True)
    
    customer = request.user if request.user.is_authenticated and request.user.user_type == 'CUSTOMER' else None
    session_key = request.session.session_key
    
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    
    # Check if already voted
    if customer:
        # For authenticated customers, check by customer
        vote_exists = ReviewHelpfulVote.objects.filter(
            review=review,
            customer=customer
        ).exists()
    else:
        # For anonymous users, check by session_key
        vote_exists = ReviewHelpfulVote.objects.filter(
            review=review,
            session_key=session_key,
            customer__isnull=True
        ).exists()
    
    if vote_exists:
        return JsonResponse({'error': 'You have already marked this review as helpful.'}, status=400)
    
    # Create vote
    ReviewHelpfulVote.objects.create(
        review=review,
        customer=customer,
        session_key=session_key if not customer else None
    )
    
    # Update helpful count
    review.helpful_count = review.helpful_votes.count()
    review.save()
    
    return JsonResponse({
        'success': True,
        'helpful_count': review.helpful_count
    })


def product_search(request):
    """
    Advanced product search with filters and sorting
    """
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '')
    vendor_id = request.GET.get('vendor', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    local_materials = request.GET.get('local_materials', '')
    min_rating = request.GET.get('min_rating', '')
    sort_by = request.GET.get('sort', 'newest')  # newest, price_low, price_high, popularity, rating
    
    # Start with active products and annotate with ratings and counts
    from orders.models import OrderItem
    products = Product.objects.filter(is_active=True).select_related('vendor', 'category', 'brand').annotate(
        avg_rating=Avg('reviews__rating'),
        review_total=Count('reviews', distinct=True),
        sales_count=Count('order_items', distinct=True)
    )
    
    # Track search for analytics and filter by query
    if query:
        # Increment search count for matching active products (before filtering)
        search_q = Q(name__icontains=query) | Q(description__icontains=query) | Q(short_description__icontains=query)
        Product.objects.filter(is_active=True).filter(search_q).update(search_count=F('search_count') + 1)
        
        # Filter products by search query
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(short_description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(vendor__username__icontains=query)
        )
    
    # Apply filters
    if category_id:
        products = products.filter(category_id=category_id)
    
    if vendor_id:
        products = products.filter(vendor_id=vendor_id)
    
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass
    
    if local_materials == 'true':
        products = products.filter(is_made_from_local_materials=True)
    
    if min_rating:
        try:
            min_rating_float = float(min_rating)
            products = products.filter(avg_rating__gte=min_rating_float)
        except ValueError:
            pass
    
    # Apply sorting
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'popularity':
        # Sort by search_count + review_count + sales
        products = products.extra(
            select={'popularity_score': 'search_count + (review_total * 2) + COALESCE(sales_count, 0)'}
        ).order_by('-popularity_score', '-created_at')
    elif sort_by == 'rating':
        products = products.order_by('-avg_rating', '-review_total', '-created_at')
    else:  # newest (default)
        products = products.order_by('-created_at')
    
    # Get filter options
    categories = Category.objects.all().order_by('name')
    vendors = User.objects.filter(
        user_type='VENDOR',
        products__is_active=True
    ).distinct().order_by('username')
    
    # Calculate price range for filter (from all active products, not filtered)
    all_products = Product.objects.filter(is_active=True)
    price_range = all_products.aggregate(
        min_price=Min('price'),
        max_price=Max('price')
    )
    
    # Get results count before pagination
    results_count = products.count()
    
    # Track search in analytics
    if query:
        was_found = results_count > 0
        if request.user.is_authenticated and request.user.user_type == 'CUSTOMER':
            SearchHistory.objects.create(
                customer=request.user,
                query=query,
                results_count=results_count,
                was_product_found=was_found
            )
        else:
            # Track anonymous searches
            SearchHistory.objects.create(
                query=query,
                results_count=results_count,
                was_product_found=was_found
            )
    
    context = {
        'products': products,
        'query': query,
        'categories': categories,
        'vendors': vendors,
        'selected_category': category_id,
        'selected_vendor': vendor_id,
        'min_price_filter': min_price,
        'max_price_filter': max_price,
        'local_materials_filter': local_materials,
        'min_rating_filter': min_rating,
        'sort_by': sort_by,
        'price_range': price_range,
        'results_count': results_count,
    }
    
    return render(request, 'store/search.html', context)


@require_http_methods(["GET"])
def search_autocomplete(request):
    """
    Autocomplete API endpoint for search suggestions
    """
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    # Get product name suggestions
    products = Product.objects.filter(
        is_active=True,
        name__icontains=query
    ).values_list('name', flat=True).distinct()[:5]
    
    # Get category suggestions
    categories = Category.objects.filter(
        name__icontains=query
    ).values_list('name', flat=True).distinct()[:3]
    
    suggestions = list(products) + list(categories)
    
    return JsonResponse({
        'suggestions': suggestions[:8]  # Limit to 8 total suggestions
    })


def trending_products(request):
    """
    Get trending products based on search analytics
    """
    from orders.models import OrderItem
    # Get products with highest search count and reviews
    trending = get_trending_products(limit=20)
    
    context = {
        'trending_products': trending,
    }
    return render(request, 'store/trending.html', context)


@require_POST
def track_social_share(request):
    """
    Track social media shares for analytics
    """
    share_type = request.POST.get('share_type')  # PRODUCT, PROJECT, VENDOR
    platform = request.POST.get('platform')  # FACEBOOK, TWITTER, etc.
    object_id = request.POST.get('object_id')
    
    if not share_type or not platform or not object_id:
        return JsonResponse({'error': 'Missing required parameters'}, status=400)
    
    user = request.user if request.user.is_authenticated else None
    session_key = request.session.session_key
    ip_address = request.META.get('REMOTE_ADDR')
    
    # Create share tracking record
    share = SocialShare.objects.create(
        user=user,
        share_type=share_type,
        platform=platform,
        session_key=session_key if not user else None,
        ip_address=ip_address,
    )
    
    # Link to the appropriate object
    if share_type == 'PRODUCT':
        try:
            from products.models import Product
            product = Product.objects.get(id=object_id)
            share.product = product
            share.save()
        except Product.DoesNotExist:
            pass
    elif share_type == 'PROJECT':
        try:
            project = CommunityProject.objects.get(id=object_id)
            share.project = project
            share.save()
        except CommunityProject.DoesNotExist:
            pass
    elif share_type == 'VENDOR':
        try:
            vendor = User.objects.get(id=object_id, user_type='VENDOR')
            share.vendor = vendor
            share.save()
        except User.DoesNotExist:
            pass
    
    return JsonResponse({'success': True, 'share_id': share.id})


@login_required
@require_POST
def add_to_cart(request, product_id):
    """
    Add a product to the customer's cart
    """
    if request.user.user_type != 'CUSTOMER':
        return JsonResponse({'error': 'Only customers can add items to cart'}, status=403)
    
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    # Check stock availability
    if product.track_inventory and product.stock_quantity <= 0:
        return JsonResponse({'error': 'Product is out of stock'}, status=400)
    
    # Get or create cart
    cart, created = Cart.objects.get_or_create(customer=request.user)
    
    # Get quantity from request (default to 1)
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            quantity = 1
    except (ValueError, TypeError):
        quantity = 1
    
    # Check if item already in cart
    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not item_created:
        # Update quantity if item already exists
        new_quantity = cart_item.quantity + quantity
        if product.track_inventory and new_quantity > product.stock_quantity:
            return JsonResponse({
                'error': f'Only {product.stock_quantity} items available in stock'
            }, status=400)
        cart_item.quantity = new_quantity
        cart_item.save()
    
    return JsonResponse({
        'success': True,
        'message': f'{product.name} added to cart',
        'cart_item_count': cart.item_count,
        'cart_total': str(cart.total)
    })


@login_required
def view_cart(request):
    """
    View the customer's shopping cart
    """
    if request.user.user_type != 'CUSTOMER':
        messages.error(request, 'Only customers can view their cart.')
        return redirect('home')
    
    cart, created = Cart.objects.get_or_create(customer=request.user)
    cart_items = cart.items.select_related('product', 'product__vendor', 'product__category').all()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'store/cart.html', context)


@login_required
@require_POST
def remove_from_cart(request, item_id):
    """
    Remove an item from the cart
    """
    if request.user.user_type != 'CUSTOMER':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    cart_item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    
    cart = Cart.objects.get(customer=request.user)
    return JsonResponse({
        'success': True,
        'message': f'{product_name} removed from cart',
        'cart_item_count': cart.item_count,
        'cart_total': str(cart.total)
    })


@login_required
@require_POST
def update_cart_item(request, item_id):
    """
    Update the quantity of a cart item
    """
    if request.user.user_type != 'CUSTOMER':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    cart_item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user)
    
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            quantity = 1
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid quantity'}, status=400)
    
    # Check stock availability
    if cart_item.product.track_inventory and quantity > cart_item.product.stock_quantity:
        return JsonResponse({
            'error': f'Only {cart_item.product.stock_quantity} items available in stock'
        }, status=400)
    
    cart_item.quantity = quantity
    cart_item.save()
    
    cart = Cart.objects.get(customer=request.user)
    return JsonResponse({
        'success': True,
        'message': 'Cart updated',
        'cart_item_count': cart.item_count,
        'cart_total': str(cart.total),
        'item_subtotal': str(cart_item.subtotal)
    })
