from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Q, Avg, F
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from .models import VendorProfile, VendorAnalytics, VendorPaymentOption, VendorDeliveryZone, VendorEvent
from .forms import (
    VendorPaymentOptionFormSet,
    VendorDeliverySettingsForm,
    VendorDeliveryZoneFormSet,
)
from products.models import Product, ProductReview, ProductView
from orders.models import CartItem, OrderItem, Order, OrderPaymentSubmission
from projects.models import CommunityProject
from accounts.models import UserProfile

User = get_user_model()


@login_required
def vendor_dashboard(request):
    if request.user.user_type != 'VENDOR':
        messages.error(request, 'Access denied. Vendor access required.')
        return redirect('home')
    
    vendor = request.user
    
    # Get or create vendor profile
    vendor_profile, created = VendorProfile.objects.get_or_create(vendor=vendor)
    
    # Get vendor products
    products = Product.objects.filter(vendor=vendor)
    
    # Calculate analytics
    total_products = products.count()
    active_products = products.filter(is_active=True).count()
    
    # Get cart items for vendor products (cart abandonment tracking)
    vendor_product_ids = products.values_list('id', flat=True)
    cart_items = CartItem.objects.filter(product_id__in=vendor_product_ids)
    abandoned_carts_count = cart_items.filter(cart__is_abandoned=True).count()
    
    # Calculate total views/clicks (using search_count as proxy for now)
    total_clicks = products.aggregate(total=Sum('search_count'))['total'] or 0
    
    # Get or create analytics
    analytics, _ = VendorAnalytics.objects.get_or_create(vendor=vendor)
    
    # Calculate revenue from orders
    order_items = OrderItem.objects.filter(
        vendor=vendor,
        order__payment_status='PAID'
    )
    total_revenue = order_items.aggregate(
        total=Sum('subtotal')
    )['total'] or 0
    total_orders = order_items.values('order').distinct().count()
    
    # Update analytics
    analytics.total_products = total_products
    analytics.active_products = active_products
    analytics.total_abandoned_carts = abandoned_carts_count
    analytics.total_revenue = total_revenue
    analytics.total_orders = total_orders
    analytics.save()
    
    # Get recent reviews for vendor's products
    recent_reviews = ProductReview.objects.filter(
        product__vendor=vendor
    ).select_related('product', 'customer').order_by('-created_at')[:5]
    
    # Get pending reviews (not approved yet)
    pending_reviews_count = ProductReview.objects.filter(
        product__vendor=vendor,
        is_approved=False
    ).count()
    
    # Get reviews needing response
    reviews_needing_response = ProductReview.objects.filter(
        product__vendor=vendor,
        is_approved=True,
        vendor_response__isnull=True
    ).count()
    
    # Update vendor metrics if needed (lazy update)
    from django.utils import timezone
    from datetime import timedelta
    try:
        if not vendor_profile.ratings_last_calculated or (timezone.now() - vendor_profile.ratings_last_calculated) > timedelta(hours=1):
            vendor_profile.update_metrics()
    except AttributeError:
        # For new vendors, metrics methods might not be available yet
        pass
    
    # Get selected project
    selected_project = vendor_profile.selected_project
    
    # Upcoming events for vendor
    upcoming_events = VendorEvent.objects.filter(
        Q(is_global=True) | Q(vendors=vendor),
        start_datetime__gte=timezone.now()
    ).distinct().order_by('start_datetime')[:5]
    
    context = {
        'vendor_profile': vendor_profile,
        'products': products[:10],  # Latest 10 products
        'total_products': total_products,
        'active_products': active_products,
        'abandoned_carts_count': abandoned_carts_count,
        'total_clicks': total_clicks,
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'recent_reviews': recent_reviews,
        'pending_reviews_count': pending_reviews_count,
        'reviews_needing_response': reviews_needing_response,
        'avg_rating': round(vendor_profile.overall_rating, 1) if vendor_profile.overall_rating else 0,
        'selected_project': selected_project,
        'upcoming_events': upcoming_events,
    }
    
    return render(request, 'vendors/dashboard.html', context)


@login_required
def vendor_analytics_dashboard(request):
    """
    Advanced analytics dashboard for vendors
    """
    if request.user.user_type != 'VENDOR':
        messages.error(request, 'Access denied. Vendor access required.')
        return redirect('home')
    
    vendor = request.user
    vendor_profile, _ = VendorProfile.objects.get_or_create(vendor=vendor)
    
    order_items = OrderItem.objects.filter(
        vendor=vendor,
        order__payment_status='PAID'
    ).select_related('order', 'product')
    
    # Date ranges
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    last_12_weeks = today - timedelta(weeks=12)
    last_6_months = today - timedelta(days=180)
    
    # Sales trends
    sales_daily_qs = order_items.filter(order__created_at__date__gte=last_30_days).annotate(
        day=TruncDay('order__created_at')
    ).values('day').annotate(
        revenue=Sum('subtotal'),
        orders=Count('order', distinct=True)
    ).order_by('day')
    sales_daily = [
        {
            'date': entry['day'].strftime('%Y-%m-%d'),
            'revenue': float(entry['revenue'] or 0),
            'orders': entry['orders']
        }
        for entry in sales_daily_qs
    ]
    
    sales_weekly_qs = order_items.filter(order__created_at__date__gte=last_12_weeks).annotate(
        week=TruncWeek('order__created_at')
    ).values('week').annotate(
        revenue=Sum('subtotal'),
        orders=Count('order', distinct=True)
    ).order_by('week')
    sales_weekly = [
        {
            'date': entry['week'].strftime('%Y-%m-%d'),
            'revenue': float(entry['revenue'] or 0),
            'orders': entry['orders']
        }
        for entry in sales_weekly_qs
    ]
    
    sales_monthly_qs = order_items.filter(order__created_at__date__gte=last_6_months).annotate(
        month=TruncMonth('order__created_at')
    ).values('month').annotate(
        revenue=Sum('subtotal'),
        orders=Count('order', distinct=True)
    ).order_by('month')
    sales_monthly = [
        {
            'date': entry['month'].strftime('%Y-%m'),
            'revenue': float(entry['revenue'] or 0),
            'orders': entry['orders']
        }
        for entry in sales_monthly_qs
    ]
    
    # Product performance
    product_performance_raw = order_items.values(
        'product_id',
        'product_name'
    ).annotate(
        revenue=Sum('subtotal'),
        units_sold=Sum('quantity'),
        avg_price=Avg('price')
    ).order_by('-revenue')[:10]
    
    product_ids = [entry['product_id'] for entry in product_performance_raw if entry['product_id']]
    products_map = {
        product.id: product
        for product in Product.objects.filter(id__in=product_ids).annotate(
            avg_rating=Avg('reviews__rating')
        )
    }
    product_performance = []
    for entry in product_performance_raw:
        product = products_map.get(entry['product_id'])
        product_performance.append({
            'product_id': entry['product_id'],
            'product_name': entry['product_name'],
            'revenue': float(entry['revenue'] or 0),
            'units_sold': entry['units_sold'],
            'avg_price': float(entry['avg_price'] or 0),
            'avg_rating': round(product.avg_rating, 1) if product and product.avg_rating else None,
            'view_count': product.view_count if product else None,
            'slug': product.slug if product else None,
        })
    
    # Customer demographics
    vendor_orders = Order.objects.filter(
        items__vendor=vendor,
        payment_status='PAID'
    ).distinct()
    
    city_distribution_qs = vendor_orders.values('shipping_city').annotate(
        total=Count('id')
    ).order_by('-total')[:10]
    
    city_distribution = [
        {
            'city': entry['shipping_city'] or 'Unknown',
            'total': entry['total']
        }
        for entry in city_distribution_qs
    ]
    
    country_distribution_qs = vendor_orders.values('shipping_country').annotate(
        total=Count('id')
    ).order_by('-total')
    country_distribution = [
        {
            'country': entry['shipping_country'] or 'Unknown',
            'total': entry['total']
        }
        for entry in country_distribution_qs
    ]
    
    customer_profiles_qs = UserProfile.objects.filter(
        user__orders__items__vendor=vendor
    ).values('country', 'city').annotate(
        total=Count('user', distinct=True)
    ).order_by('-total')[:10]
    customer_location_breakdown = [
        {
            'country': entry['country'] or 'Unknown',
            'city': entry['city'] or 'Unknown',
            'total': entry['total']
        }
        for entry in customer_profiles_qs
    ]
    
    customer_orders = vendor_orders.values('customer').annotate(
        order_count=Count('id')
    )
    new_customers = sum(1 for entry in customer_orders if entry['order_count'] == 1)
    returning_customers = sum(1 for entry in customer_orders if entry['order_count'] > 1)
    
    # Conversion funnel
    product_views = ProductView.objects.filter(product__vendor=vendor).count()
    cart_adds = CartItem.objects.filter(product__vendor=vendor).count()
    completed_orders = order_items.count()
    
    conversion_funnel = {
        'views': product_views,
        'cart_adds': cart_adds,
        'orders': completed_orders,
        'view_to_cart': round((cart_adds / product_views) * 100, 2) if product_views else None,
        'cart_to_order': round((completed_orders / cart_adds) * 100, 2) if cart_adds else None,
        'view_to_order': round((completed_orders / product_views) * 100, 2) if product_views else None,
    }
    
    # Revenue forecasting
    last_30_revenue = order_items.filter(
        order__created_at__date__gte=last_30_days
    ).aggregate(total=Sum('subtotal'))['total'] or 0
    
    prev_30_revenue = order_items.filter(
        order__created_at__date__gte=last_30_days - timedelta(days=30),
        order__created_at__date__lt=last_30_days
    ).aggregate(total=Sum('subtotal'))['total'] or 0
    
    avg_daily_revenue = (last_30_revenue / 30) if last_30_revenue else 0
    forecast_next_30 = avg_daily_revenue * 30
    growth_rate = None
    if prev_30_revenue:
        growth_rate = ((last_30_revenue - prev_30_revenue) / prev_30_revenue) * 100
    
    revenue_forecast = {
        'last_30_days': float(last_30_revenue),
        'prev_30_days': float(prev_30_revenue),
        'growth_rate': round(growth_rate, 2) if growth_rate is not None else None,
        'forecast_next_30': round(float(forecast_next_30), 2),
        'avg_daily_revenue': round(float(avg_daily_revenue), 2),
    }
    
    # Top customers
    top_customers_qs = vendor_orders.values(
        'customer__id',
        'customer__username'
    ).annotate(
        revenue=Sum('items__subtotal'),
        orders=Count('id')
    ).order_by('-revenue')[:10]
    top_customers = [
        {
            'customer_id': entry['customer__id'],
            'customer': entry['customer__username'],
            'revenue': float(entry['revenue'] or 0),
            'orders': entry['orders'],
        } for entry in top_customers_qs
    ]
    
    context = {
        'vendor_profile': vendor_profile,
        'sales_daily': sales_daily,
        'sales_weekly': sales_weekly,
        'sales_monthly': sales_monthly,
        'product_performance': product_performance,
        'city_distribution': city_distribution,
        'country_distribution': country_distribution,
        'customer_location_breakdown': customer_location_breakdown,
        'new_customers': new_customers,
        'returning_customers': returning_customers,
        'conversion_funnel': conversion_funnel,
        'revenue_forecast': revenue_forecast,
        'top_customers': top_customers,
    }
    
    return render(request, 'vendors/analytics_dashboard.html', context)


@login_required
def vendor_payment_settings(request):
    """
    Allow vendors to configure payment options and delivery rules
    """
    if request.user.user_type != 'VENDOR':
        messages.error(request, 'Access denied. Vendor access required.')
        return redirect('home')
    
    vendor = request.user
    vendor_profile, _ = VendorProfile.objects.get_or_create(vendor=vendor)
    
    # Ensure all payment types exist for this vendor
    for payment_type, _ in VendorPaymentOption.PAYMENT_TYPE_CHOICES:
        VendorPaymentOption.objects.get_or_create(
            vendor=vendor,
            payment_type=payment_type,
            defaults={
                'is_enabled': payment_type == 'CASH_ON_DELIVERY',
            }
        )
    
    # Ensure delivery zones exist for all supported cities
    for city_code, _ in VendorDeliveryZone.CITY_CHOICES:
        VendorDeliveryZone.objects.get_or_create(vendor=vendor, city=city_code)
    
    payment_queryset = VendorPaymentOption.objects.filter(vendor=vendor).order_by('payment_type')
    delivery_zone_queryset = VendorDeliveryZone.objects.filter(vendor=vendor).order_by('city')
    
    if request.method == 'POST':
        formset = VendorPaymentOptionFormSet(request.POST, queryset=payment_queryset, prefix='payments')
        delivery_form = VendorDeliverySettingsForm(request.POST, instance=vendor_profile, prefix='delivery')
        zone_formset = VendorDeliveryZoneFormSet(request.POST, queryset=delivery_zone_queryset, prefix='zones')
        
        if formset.is_valid() and delivery_form.is_valid() and zone_formset.is_valid():
            options = formset.save(commit=False)
            for option in options:
                option.vendor = vendor
                option.save()
            # Save delivery settings
            delivery_form.save()
            zone_formset.save()
            
            messages.success(request, 'Payment options and delivery settings updated successfully.')
            return redirect('vendor_payment_settings')
    else:
        formset = VendorPaymentOptionFormSet(queryset=payment_queryset, prefix='payments')
        delivery_form = VendorDeliverySettingsForm(instance=vendor_profile, prefix='delivery')
        zone_formset = VendorDeliveryZoneFormSet(queryset=delivery_zone_queryset, prefix='zones')
    
    from django.conf import settings
    
    if request.method != 'POST':
        zone_formset = VendorDeliveryZoneFormSet(queryset=delivery_zone_queryset, prefix='zones')
    
    context = {
        'formset': formset,
        'delivery_form': delivery_form,
        'zone_formset': zone_formset,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
        'vendor_location': {
            'address': vendor_profile.location_address or '',
            'latitude': float(vendor_profile.location_latitude) if vendor_profile.location_latitude else None,
            'longitude': float(vendor_profile.location_longitude) if vendor_profile.location_longitude else None,
        },
    }
    return render(request, 'vendors/payment_settings.html', context)


@login_required
def vendor_payment_inbox(request):
    """
    Vendors review payment submissions from customers and acknowledge receipt.
    """
    if request.user.user_type != 'VENDOR':
        messages.error(request, 'Access denied. Vendor access required.')
        return redirect('home')
    
    vendor = request.user
    submissions = OrderPaymentSubmission.objects.filter(
        vendor=vendor
    ).select_related('order', 'order__customer').order_by('status', '-submitted_at')
    
    if request.method == 'POST':
        submission_id = request.POST.get('submission_id')
        submission = get_object_or_404(OrderPaymentSubmission, id=submission_id, vendor=vendor)
        
        if submission.status == 'ACKNOWLEDGED':
            messages.info(request, 'This payment has already been acknowledged.')
            return redirect('vendor_payment_inbox')
        
        submission.status = 'ACKNOWLEDGED'
        submission.acknowledged_at = timezone.now()
        submission.save()
        
        # Update order payment status if all vendor payments acknowledged
        order = submission.order
        if not order.payment_submissions.filter(status='PENDING').exists():
            order.payment_status = 'PAID'
            order.status = 'PROCESSING'
            order.save(update_fields=['payment_status', 'status', 'updated_at'])
        else:
            order.payment_status = 'PARTIAL'
            order.save(update_fields=['payment_status', 'updated_at'])
        
        messages.success(request, 'Payment acknowledged. Contact the customer immediately if there is any issue.')
        return redirect('vendor_payment_inbox')
    
    return render(request, 'vendors/payment_inbox.html', {
        'submissions': submissions,
    })


@login_required
def vendor_profile(request):
    if request.user.user_type != 'VENDOR':
        messages.error(request, 'Access denied. Vendor access required.')
        return redirect('home')
    
    vendor_profile, created = VendorProfile.objects.get_or_create(vendor=request.user)
    
    from projects.models import CommunityProject
    approved_projects = CommunityProject.objects.filter(is_approved=True, status__in=['ACTIVE', 'IN_PROGRESS'])
    
    if request.method == 'POST':
        # Update vendor profile
        vendor_profile.company_name = request.POST.get('company_name', vendor_profile.company_name)
        vendor_profile.description = request.POST.get('description', vendor_profile.description)
        vendor_profile.business_type = request.POST.get('business_type', vendor_profile.business_type)
        vendor_profile.website = request.POST.get('website', vendor_profile.website)
        vendor_profile.phone = request.POST.get('phone', vendor_profile.phone)
        vendor_profile.address = request.POST.get('address', vendor_profile.address)
        
        # Logo upload
        if 'logo' in request.FILES:
            vendor_profile.logo = request.FILES['logo']
        
        # Project participation
        vendor_profile.participate_in_projects = request.POST.get('participate_in_projects') == 'on'
        project_id = request.POST.get('selected_project')
        if project_id:
            vendor_profile.selected_project_id = project_id
        else:
            vendor_profile.selected_project = None
        
        vendor_profile.save()
        
        # Update user information
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.phone_number = request.POST.get('phone_number', user.phone_number)
        user.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('vendor_profile')
    
    return render(request, 'vendors/profile.html', {
        'vendor_profile': vendor_profile,
        'approved_projects': approved_projects,
    })


@login_required
def vendor_reviews(request):
    """
    Vendor view to see and respond to reviews for their products
    """
    if request.user.user_type != 'VENDOR':
        messages.error(request, 'Access denied. Vendor access required.')
        return redirect('home')
    
    vendor = request.user
    
    # Get all reviews for vendor's products
    reviews = ProductReview.objects.filter(
        product__vendor=vendor
    ).select_related('product', 'customer').prefetch_related('photos').order_by('-created_at')
    
    # Filter options
    filter_status = request.GET.get('status', 'all')  # all, approved, pending, responded, not_responded
    filter_rating = request.GET.get('rating', 'all')  # all, 1, 2, 3, 4, 5
    
    if filter_status == 'approved':
        reviews = reviews.filter(is_approved=True)
    elif filter_status == 'pending':
        reviews = reviews.filter(is_approved=False)
    elif filter_status == 'responded':
        reviews = reviews.filter(vendor_response__isnull=False)
    elif filter_status == 'not_responded':
        reviews = reviews.filter(vendor_response__isnull=True, is_approved=True)
    
    if filter_rating != 'all':
        try:
            reviews = reviews.filter(rating=int(filter_rating))
        except ValueError:
            pass
    
    context = {
        'reviews': reviews,
        'filter_status': filter_status,
        'filter_rating': filter_rating,
    }
    
    return render(request, 'vendors/reviews.html', context)


@login_required
def product_list(request):
    if request.user.user_type != 'VENDOR':
        messages.error(request, 'Access denied. Vendor access required.')
        return redirect('home')
    
    products = Product.objects.filter(vendor=request.user).order_by('-created_at')
    
    context = {
        'products': products,
    }
    return render(request, 'vendors/product_list.html', context)


@login_required
def product_create(request):
    if request.user.user_type != 'VENDOR':
        messages.error(request, 'Access denied. Vendor access required.')
        return redirect('home')
    
    from products.models import Category, Brand, ProductTag
    
    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        
        if not category_id:
            messages.error(request, 'Category is required. Please select a category for your product.')
            categories = Category.objects.filter(is_active=True).order_by('name')
            brands = Brand.objects.filter(is_local=True).order_by('name')
            tags = ProductTag.objects.filter(is_active=True).order_by('name')
            context = {
                'categories': categories,
                'brands': brands,
                'tags': tags,
            }
            return render(request, 'vendors/product_create.html', context)
        
        slug_input = request.POST.get('slug', '').strip()
        
        # Generate slug if not provided
        if not slug_input:
            import re
            slug_input = re.sub(r'[^\w\s-]', '', name.lower())
            slug_input = re.sub(r'[-\s]+', '-', slug_input)
        
        # Ensure slug is unique
        base_slug = slug_input
        counter = 1
        while Product.objects.filter(slug=slug_input).exists():
            slug_input = f"{base_slug}-{counter}"
            counter += 1
        
        product = Product.objects.create(
            name=name,
            slug=slug_input,
            description=request.POST.get('description', ''),
            short_description=request.POST.get('short_description', ''),
            vendor=request.user,
            category_id=category_id,
            brand_id=request.POST.get('brand') or None,
            price=request.POST.get('price'),
            compare_at_price=request.POST.get('compare_at_price') or None,
            sku=request.POST.get('sku') or None,
            stock_quantity=request.POST.get('stock_quantity', 0),
            track_inventory=request.POST.get('track_inventory') == 'on',
            is_featured=request.POST.get('is_featured') == 'on',
            is_active=request.POST.get('is_active', 'on') == 'on',
            is_made_from_local_materials=request.POST.get('is_made_from_local_materials') == 'on',
        )
        
        # Handle tags
        tag_ids = request.POST.getlist('tags')
        if tag_ids:
            product.tags.set(tag_ids)
        
        # Handle primary image
        if 'primary_image' in request.FILES:
            product.primary_image = request.FILES['primary_image']
            product.save()
        
        messages.success(request, f'Product "{product.name}" created successfully!')
        return redirect('vendor_product_list')
    
    categories = Category.objects.filter(is_active=True).order_by('name')
    brands = Brand.objects.filter(is_local=True).order_by('name')
    tags = ProductTag.objects.filter(is_active=True).order_by('name')
    
    context = {
        'categories': categories,
        'brands': brands,
        'tags': tags,
    }
    return render(request, 'vendors/product_create.html', context)


@login_required
def product_detail(request, pk):
    if request.user.user_type != 'VENDOR':
        messages.error(request, 'Access denied. Vendor access required.')
        return redirect('home')
    
    product = get_object_or_404(Product, pk=pk, vendor=request.user)
    
    context = {
        'product': product,
    }
    return render(request, 'vendors/product_detail.html', context)


# ============================================
# POS (POINT OF SALE) VIEWS
# ============================================

@login_required
def vendor_pos(request):
    """
    Point of Sale interface for vendors
    """
    if request.user.user_type != 'VENDOR':
        messages.error(request, 'Access denied. Vendor access required.')
        return redirect('home')
    
    vendor = request.user
    vendor_profile, _ = VendorProfile.objects.get_or_create(vendor=vendor)
    
    # Get vendor's products for POS
    products = Product.objects.filter(
        vendor=vendor,
        is_active=True
    ).order_by('name')
    
    # Get vendor companies for multi-company support
    from .models import VendorCompany
    companies = VendorCompany.objects.filter(vendor=vendor, is_active=True)
    
    context = {
        'vendor_profile': vendor_profile,
        'products': products,
        'companies': companies,
    }
    
    return render(request, 'vendors/pos.html', context)


@login_required
def vendor_pos_create_receipt(request):
    """
    Create a new POS receipt (AJAX endpoint)
    """
    if request.user.user_type != 'VENDOR':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    import json
    from decimal import Decimal
    from .models import SaleReceipt, SaleReceiptItem, VendorCompany
    
    try:
        data = json.loads(request.body)
        
        # Validate data
        if not data.get('customer_name'):
            return JsonResponse({'error': 'Customer name is required'}, status=400)
        
        if not data.get('items') or len(data['items']) == 0:
            return JsonResponse({'error': 'At least one item is required'}, status=400)
        
        # Create receipt
        receipt = SaleReceipt()
        receipt.vendor = request.user
        
        # Handle company selection
        company_id = data.get('company_id')
        if company_id:
            try:
                receipt.company = VendorCompany.objects.get(id=company_id, vendor=request.user)
            except VendorCompany.DoesNotExist:
                pass
        
        receipt.customer_name = data['customer_name']
        receipt.customer_phone = data.get('customer_phone', '')
        receipt.customer_email = data.get('customer_email', '')
        receipt.payment_method = data.get('payment_method', 'CASH')
        receipt.notes = data.get('notes', '')
        receipt.is_walk_in = data.get('is_walk_in', True)
        
        # Calculate totals
        subtotal = Decimal('0')
        for item_data in data['items']:
            quantity = Decimal(str(item_data['quantity']))
            unit_price = Decimal(str(item_data['unit_price']))
            subtotal += quantity * unit_price
        
        receipt.subtotal = subtotal
        receipt.tax_amount = Decimal(data.get('tax_amount', '0'))
        receipt.discount_amount = Decimal(data.get('discount_amount', '0'))
        receipt.total_amount = subtotal + receipt.tax_amount - receipt.discount_amount
        receipt.sale_date = timezone.now()
        
        receipt.save()
        
        # Create receipt items
        for item_data in data['items']:
            item = SaleReceiptItem()
            item.receipt = receipt
            
            # Try to link to product
            product_id = item_data.get('product_id')
            if product_id:
                try:
                    product = Product.objects.get(id=product_id, vendor=request.user)
                    item.product = product
                    item.product_name = product.name
                    item.product_sku = product.sku
                except Product.DoesNotExist:
                    item.product_name = item_data['product_name']
            else:
                item.product_name = item_data['product_name']
            
            item.quantity = Decimal(str(item_data['quantity']))
            item.unit_price = Decimal(str(item_data['unit_price']))
            item.save()
        
        return JsonResponse({
            'success': True,
            'receipt_id': receipt.id,
            'receipt_number': receipt.receipt_number,
            'message': 'Receipt created successfully'
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


from django.http import JsonResponse


@login_required
def vendor_receipts_list(request):
    """
    List all receipts created by vendor
    """
    if request.user.user_type != 'VENDOR':
        messages.error(request, 'Access denied. Vendor access required.')
        return redirect('home')
    
    vendor = request.user
    from .models import SaleReceipt
    
    receipts = SaleReceipt.objects.filter(
        vendor=vendor
    ).prefetch_related('items').order_by('-sale_date')
    
    # Filter by date range
    from datetime import datetime
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            receipts = receipts.filter(sale_date__date__gte=start)
        except ValueError:
            pass
    
    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            receipts = receipts.filter(sale_date__date__lte=end)
        except ValueError:
            pass
    
    context = {
        'receipts': receipts,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'vendors/receipts_list.html', context)


@login_required
def vendor_receipt_detail(request, receipt_id):
    """
    View and print a specific receipt
    """
    if request.user.user_type != 'VENDOR':
        messages.error(request, 'Access denied. Vendor access required.')
        return redirect('home')
    
    from .models import SaleReceipt
    receipt = get_object_or_404(SaleReceipt, id=receipt_id, vendor=request.user)
    
    vendor_profile, _ = VendorProfile.objects.get_or_create(vendor=request.user)
    
    context = {
        'receipt': receipt,
        'vendor_profile': vendor_profile,
    }
    
    # Check if print mode
    if request.GET.get('print') == '1':
        return render(request, 'vendors/receipt_print.html', context)
    
    return render(request, 'vendors/receipt_detail.html', context)


# ============================================
# ACCOUNTING MODULE VIEWS
# ============================================

@login_required
def vendor_accounting_dashboard(request):
    """
    Accounting module dashboard
    """
    if request.user.user_type != 'VENDOR':
        messages.error(request, 'Access denied. Vendor access required.')
        return redirect('home')
    
    vendor = request.user
    from .models import SaleReceipt, VendorExpense, VendorInvoice
    
    # Get financial summary
    from datetime import date
    today = date.today()
    first_day_of_month = today.replace(day=1)
    
    # Revenue this month (from receipts)
    revenue_this_month = SaleReceipt.objects.filter(
        vendor=vendor,
        sale_date__date__gte=first_day_of_month
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Expenses this month
    expenses_this_month = VendorExpense.objects.filter(
        vendor=vendor,
        expense_date__gte=first_day_of_month
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Outstanding invoices
    outstanding_invoices = VendorInvoice.objects.filter(
        vendor=vendor,
        status__in=['SENT', 'OVERDUE']
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Recent transactions
    recent_receipts = SaleReceipt.objects.filter(vendor=vendor).order_by('-sale_date')[:10]
    recent_expenses = VendorExpense.objects.filter(vendor=vendor).order_by('-expense_date')[:10]
    
    context = {
        'revenue_this_month': revenue_this_month,
        'expenses_this_month': expenses_this_month,
        'profit_this_month': revenue_this_month - expenses_this_month,
        'outstanding_invoices': outstanding_invoices,
        'recent_receipts': recent_receipts,
        'recent_expenses': recent_expenses,
    }
    
    return render(request, 'vendors/accounting_dashboard.html', context)


@login_required
def vendor_expenses_list(request):
    """
    List and manage expenses with filtering
    """
    if request.user.user_type != 'VENDOR':
        messages.error(request, 'Access denied. Vendor access required.')
        return redirect('home')
    
    from .models import VendorExpense
    from datetime import datetime
    from django.db.models import Sum
    
    expenses = VendorExpense.objects.filter(
        vendor=request.user
    ).select_related('company').order_by('-expense_date')
    
    # Filtering
    category = request.GET.get('category')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    search = request.GET.get('search')
    
    if category:
        expenses = expenses.filter(category=category)
    
    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            expenses = expenses.filter(expense_date__gte=start)
        except ValueError:
            pass
    
    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            expenses = expenses.filter(expense_date__lte=end)
        except ValueError:
            pass
    
    if search:
        expenses = expenses.filter(
            Q(description__icontains=search) |
            Q(notes__icontains=search) |
            Q(reference_number__icontains=search)
        )
    
    # Calculate totals
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
    
    # Category breakdown
    category_breakdown = expenses.values('category').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    context = {
        'expenses': expenses,
        'total_expenses': total_expenses,
        'category_breakdown': category_breakdown,
        'selected_category': category,
        'start_date': start_date,
        'end_date': end_date,
        'search': search,
        'expense_categories': VendorExpense.EXPENSE_CATEGORY_CHOICES,
    }
    
    return render(request, 'vendors/expenses_list.html', context)


@login_required
def vendor_expense_create(request):
    """
    Create a new expense
    """
    if request.user.user_type != 'VENDOR':
        messages.error(request, 'Access denied. Vendor access required.')
        return redirect('home')
    
    from .models import VendorExpense, VendorCompany
    
    if request.method == 'POST':
        expense = VendorExpense()
        expense.vendor = request.user
        
        # Handle company selection
        company_id = request.POST.get('company_id')
        if company_id:
            try:
                expense.company = VendorCompany.objects.get(id=company_id, vendor=request.user)
            except VendorCompany.DoesNotExist:
                pass
        
        expense.description = request.POST.get('description')
        expense.category = request.POST.get('category')
        expense.amount = request.POST.get('amount')
        expense.expense_date = request.POST.get('expense_date')
        expense.payment_method = request.POST.get('payment_method', '')
        expense.reference_number = request.POST.get('reference_number', '')
        expense.notes = request.POST.get('notes', '')
        
        if 'receipt_image' in request.FILES:
            expense.receipt_image = request.FILES['receipt_image']
        
        expense.save()
        
        messages.success(request, 'Expense recorded successfully.')
        return redirect('vendor_expenses_list')
    
    companies = VendorCompany.objects.filter(vendor=request.user, is_active=True)
    
    context = {
        'companies': companies,
    }
    
    return render(request, 'vendors/expense_create.html', context)


@login_required
def vendor_expense_detail(request, expense_id):
    """
    View expense details
    """
    if request.user.user_type != 'VENDOR':
        messages.error(request, 'Access denied. Vendor access required.')
        return redirect('home')
    
    from .models import VendorExpense
    
    expense = get_object_or_404(VendorExpense, id=expense_id, vendor=request.user)
    
    context = {
        'expense': expense,
    }
    
    return render(request, 'vendors/expense_detail.html', context)


@login_required
def vendor_expense_edit(request, expense_id):
    """
    Edit an existing expense
    """
    if request.user.user_type != 'VENDOR':
        messages.error(request, 'Access denied. Vendor access required.')
        return redirect('home')
    
    from .models import VendorExpense, VendorCompany
    
    expense = get_object_or_404(VendorExpense, id=expense_id, vendor=request.user)
    
    if request.method == 'POST':
        # Handle company selection
        company_id = request.POST.get('company_id')
        if company_id:
            try:
                expense.company = VendorCompany.objects.get(id=company_id, vendor=request.user)
            except VendorCompany.DoesNotExist:
                expense.company = None
        else:
            expense.company = None
        
        expense.description = request.POST.get('description')
        expense.category = request.POST.get('category')
        expense.amount = request.POST.get('amount')
        expense.expense_date = request.POST.get('expense_date')
        expense.payment_method = request.POST.get('payment_method', '')
        expense.reference_number = request.POST.get('reference_number', '')
        expense.notes = request.POST.get('notes', '')
        
        if 'receipt_image' in request.FILES:
            expense.receipt_image = request.FILES['receipt_image']
        
        expense.save()
        
        messages.success(request, 'Expense updated successfully.')
        return redirect('vendor_expense_detail', expense_id=expense.id)
    
    companies = VendorCompany.objects.filter(vendor=request.user, is_active=True)
    
    context = {
        'expense': expense,
        'companies': companies,
    }
    
    return render(request, 'vendors/expense_edit.html', context)


@login_required
def vendor_expense_delete(request, expense_id):
    """
    Delete an expense
    """
    if request.user.user_type != 'VENDOR':
        messages.error(request, 'Access denied. Vendor access required.')
        return redirect('home')
    
    from .models import VendorExpense
    
    expense = get_object_or_404(VendorExpense, id=expense_id, vendor=request.user)
    
    if request.method == 'POST':
        expense_desc = expense.description
        expense.delete()
        messages.success(request, f'Expense "{expense_desc}" deleted successfully.')
        return redirect('vendor_expenses_list')
    
    context = {
        'expense': expense,
    }
    
    return render(request, 'vendors/expense_delete.html', context)


@login_required
def vendor_expenses_export(request):
    """
    Export expenses to CSV
    """
    if request.user.user_type != 'VENDOR':
        messages.error(request, 'Access denied. Vendor access required.')
        return redirect('home')
    
    import csv
    from django.http import HttpResponse
    from .models import VendorExpense
    from datetime import datetime
    
    # Get filtered expenses
    expenses = VendorExpense.objects.filter(vendor=request.user).order_by('-expense_date')
    
    # Apply filters from query params
    category = request.GET.get('category')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if category:
        expenses = expenses.filter(category=category)
    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            expenses = expenses.filter(expense_date__gte=start)
        except ValueError:
            pass
    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            expenses = expenses.filter(expense_date__lte=end)
        except ValueError:
            pass
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="expenses_{timezone.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Description', 'Category', 'Amount', 'Payment Method', 'Reference', 'Notes', 'Company'])
    
    for expense in expenses:
        writer.writerow([
            expense.expense_date.strftime('%Y-%m-%d'),
            expense.description,
            expense.get_category_display(),
            f'${expense.amount}',
            expense.payment_method or '',
            expense.reference_number or '',
            expense.notes or '',
            expense.company.name if expense.company else '',
        ])
    
    return response


# ============================================
# VENDOR DISCUSSIONS/FORUM VIEWS
# ============================================

@login_required
def vendor_discussions(request):
    """
    List all vendor discussions/forum
    """
    if request.user.user_type != 'VENDOR':
        messages.error(request, 'Access denied. Vendor access required.')
        return redirect('home')
    
    from .models import VendorDiscussion, VendorDiscussionCategory
    
    # Get category filter
    category_slug = request.GET.get('category')
    
    discussions = VendorDiscussion.objects.select_related(
        'author', 'category'
    ).prefetch_related('replies').order_by('-is_pinned', '-last_activity_at')
    
    if category_slug:
        discussions = discussions.filter(category__slug=category_slug)
    
    categories = VendorDiscussionCategory.objects.filter(is_active=True)
    
    context = {
        'discussions': discussions,
        'categories': categories,
        'selected_category': category_slug,
    }
    
    return render(request, 'vendors/discussions_list.html', context)


@login_required
def vendor_discussion_detail(request, discussion_id):
    """
    View a discussion and its replies
    """
    if request.user.user_type != 'VENDOR':
        messages.error(request, 'Access denied. Vendor access required.')
        return redirect('home')
    
    from .models import VendorDiscussion, VendorDiscussionReply
    
    discussion = get_object_or_404(
        VendorDiscussion.objects.select_related('author', 'category'),
        id=discussion_id
    )
    
    # Increment view count
    discussion.view_count += 1
    discussion.save(update_fields=['view_count'])
    
    # Handle reply submission
    if request.method == 'POST' and not discussion.is_locked:
        content = request.POST.get('content')
        if content:
            reply = VendorDiscussionReply.objects.create(
                discussion=discussion,
                author=request.user,
                content=content
            )
            messages.success(request, 'Reply posted successfully.')
            return redirect('vendor_discussion_detail', discussion_id=discussion.id)
    
    replies = discussion.replies.select_related('author').order_by('created_at')
    
    context = {
        'discussion': discussion,
        'replies': replies,
    }
    
    return render(request, 'vendors/discussion_detail.html', context)


@login_required
def vendor_discussion_create(request):
    """
    Create a new discussion
    """
    if request.user.user_type != 'VENDOR':
        messages.error(request, 'Access denied. Vendor access required.')
        return redirect('home')
    
    from .models import VendorDiscussion, VendorDiscussionCategory
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        
        if not title or not content or not category_id:
            messages.error(request, 'Please fill in all required fields.')
        else:
            try:
                category = VendorDiscussionCategory.objects.get(id=category_id, is_active=True)
                discussion = VendorDiscussion.objects.create(
                    category=category,
                    author=request.user,
                    title=title,
                    content=content
                )
                messages.success(request, 'Discussion created successfully.')
                return redirect('vendor_discussion_detail', discussion_id=discussion.id)
            except VendorDiscussionCategory.DoesNotExist:
                messages.error(request, 'Invalid category selected.')
    
    categories = VendorDiscussionCategory.objects.filter(is_active=True)
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'vendors/discussion_create.html', context)
