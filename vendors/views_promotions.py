"""
Vendor Promotion Management Views
Allows vendors to create and manage product promotions
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from decimal import Decimal

from .models import Promotion, ProductPromotion, PromotionAnalytics
from products.models import Product


@login_required
def vendor_promotions_list(request):
    """
    List all promotions for the vendor
    """
    if request.user.user_type != 'VENDOR':
        messages.error(request, 'Access denied. Vendors only.')
        return redirect('home')
    
    promotions = Promotion.objects.filter(vendor=request.user).select_related('company')
    
    # Update statuses
    for promo in promotions:
        promo.update_status()
        promo.save()
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        promotions = promotions.filter(status=status_filter)
    
    # Calculate statistics
    stats = {
        'total': Promotion.objects.filter(vendor=request.user).count(),
        'active': Promotion.objects.filter(vendor=request.user, status='ACTIVE').count(),
        'scheduled': Promotion.objects.filter(vendor=request.user, status='SCHEDULED').count(),
        'expired': Promotion.objects.filter(vendor=request.user, status='EXPIRED').count(),
        'total_revenue': Promotion.objects.filter(vendor=request.user).aggregate(
            total=Sum('total_revenue'))['total'] or 0,
    }
    
    context = {
        'promotions': promotions,
        'stats': stats,
        'status_filter': status_filter,
    }
    return render(request, 'vendors/promotions/list.html', context)


@login_required
def vendor_promotion_create(request):
    """
    Create a new promotion
    """
    if request.user.user_type != 'VENDOR':
        messages.error(request, 'Access denied. Vendors only.')
        return redirect('home')
    
    if request.method == 'POST':
        try:
            # Create promotion
            promotion = Promotion.objects.create(
                vendor=request.user,
                name=request.POST.get('name'),
                description=request.POST.get('description', ''),
                style=request.POST.get('style'),
                discount_percentage=Decimal(request.POST.get('discount_percentage')),
                start_date=request.POST.get('start_date'),
                end_date=request.POST.get('end_date'),
                show_badge=request.POST.get('show_badge') == 'on',
                show_countdown=request.POST.get('show_countdown') == 'on',
                featured=request.POST.get('featured') == 'on',
                terms=request.POST.get('terms', ''),
            )
            
            # Add selected products
            product_ids = request.POST.getlist('products')
            if product_ids:
                for product_id in product_ids:
                    product = Product.objects.get(id=product_id, vendor=request.user)
                    ProductPromotion.objects.create(
                        promotion=promotion,
                        product=product
                    )
            
            messages.success(request, f'Promotion "{promotion.name}" created successfully!')
            return redirect('vendor_promotion_detail', promotion_id=promotion.id)
        
        except Exception as e:
            messages.error(request, f'Error creating promotion: {str(e)}')
    
    # Get vendor's products
    products = Product.objects.filter(vendor=request.user, is_active=True)
    
    context = {
        'products': products,
        'style_choices': Promotion.STYLE_CHOICES,
    }
    return render(request, 'vendors/promotions/create.html', context)


@login_required
def vendor_promotion_detail(request, promotion_id):
    """
    View promotion details and analytics
    """
    promotion = get_object_or_404(Promotion, id=promotion_id, vendor=request.user)
    
    # Update status
    promotion.update_status()
    promotion.save()
    
    # Get products in promotion
    product_promotions = ProductPromotion.objects.filter(
        promotion=promotion
    ).select_related('product')
    
    # Get analytics
    analytics = PromotionAnalytics.objects.filter(promotion=promotion).order_by('-date')[:30]
    
    # Calculate performance metrics
    metrics = {
        'total_views': promotion.view_count,
        'total_clicks': promotion.click_count,
        'total_sales': promotion.conversion_count,
        'total_revenue': promotion.total_revenue,
        'conversion_rate': promotion.conversion_rate,
        'avg_order_value': promotion.total_revenue / promotion.conversion_count if promotion.conversion_count > 0 else 0,
        'products_count': product_promotions.count(),
    }
    
    context = {
        'promotion': promotion,
        'product_promotions': product_promotions,
        'analytics': analytics,
        'metrics': metrics,
    }
    return render(request, 'vendors/promotions/detail.html', context)


@login_required
def vendor_promotion_edit(request, promotion_id):
    """
    Edit an existing promotion
    """
    promotion = get_object_or_404(Promotion, id=promotion_id, vendor=request.user)
    
    if request.method == 'POST':
        try:
            promotion.name = request.POST.get('name')
            promotion.description = request.POST.get('description', '')
            promotion.style = request.POST.get('style')
            promotion.discount_percentage = Decimal(request.POST.get('discount_percentage'))
            promotion.start_date = request.POST.get('start_date')
            promotion.end_date = request.POST.get('end_date')
            promotion.show_badge = request.POST.get('show_badge') == 'on'
            promotion.show_countdown = request.POST.get('show_countdown') == 'on'
            promotion.featured = request.POST.get('featured') == 'on'
            promotion.terms = request.POST.get('terms', '')
            promotion.save()
            
            # Update products
            new_product_ids = set(request.POST.getlist('products'))
            existing_product_ids = set(
                ProductPromotion.objects.filter(promotion=promotion).values_list('product_id', flat=True)
            )
            
            # Remove products not in new list
            to_remove = existing_product_ids - new_product_ids
            ProductPromotion.objects.filter(promotion=promotion, product_id__in=to_remove).delete()
            
            # Add new products
            to_add = new_product_ids - existing_product_ids
            for product_id in to_add:
                product = Product.objects.get(id=product_id, vendor=request.user)
                ProductPromotion.objects.create(
                    promotion=promotion,
                    product=product
                )
            
            messages.success(request, f'Promotion "{promotion.name}" updated successfully!')
            return redirect('vendor_promotion_detail', promotion_id=promotion.id)
        
        except Exception as e:
            messages.error(request, f'Error updating promotion: {str(e)}')
    
    # Get vendor's products and selected products
    products = Product.objects.filter(vendor=request.user, is_active=True)
    selected_products = ProductPromotion.objects.filter(promotion=promotion).values_list('product_id', flat=True)
    
    context = {
        'promotion': promotion,
        'products': products,
        'selected_products': list(selected_products),
        'style_choices': Promotion.STYLE_CHOICES,
    }
    return render(request, 'vendors/promotions/edit.html', context)


@login_required
def vendor_promotion_toggle(request, promotion_id):
    """
    Toggle promotion active status
    """
    promotion = get_object_or_404(Promotion, id=promotion_id, vendor=request.user)
    
    promotion.is_active = not promotion.is_active
    promotion.save()
    
    status = 'activated' if promotion.is_active else 'paused'
    messages.success(request, f'Promotion "{promotion.name}" {status}!')
    
    return redirect('vendor_promotion_detail', promotion_id=promotion.id)


@login_required
def vendor_promotion_delete(request, promotion_id):
    """
    Delete a promotion
    """
    promotion = get_object_or_404(Promotion, id=promotion_id, vendor=request.user)
    
    if request.method == 'POST':
        name = promotion.name
        promotion.delete()
        messages.success(request, f'Promotion "{name}" deleted successfully!')
        return redirect('vendor_promotions_list')
    
    context = {'promotion': promotion}
    return render(request, 'vendors/promotions/delete.html', context)


@login_required
def vendor_promotion_add_products(request, promotion_id):
    """
    Add products to an existing promotion
    """
    promotion = get_object_or_404(Promotion, id=promotion_id, vendor=request.user)
    
    if request.method == 'POST':
        product_ids = request.POST.getlist('products')
        added_count = 0
        
        for product_id in product_ids:
            try:
                product = Product.objects.get(id=product_id, vendor=request.user)
                ProductPromotion.objects.get_or_create(
                    promotion=promotion,
                    product=product
                )
                added_count += 1
            except Product.DoesNotExist:
                continue
        
        messages.success(request, f'{added_count} product(s) added to promotion!')
        return redirect('vendor_promotion_detail', promotion_id=promotion.id)
    
    # Get products not already in promotion
    existing_product_ids = ProductPromotion.objects.filter(
        promotion=promotion
    ).values_list('product_id', flat=True)
    
    products = Product.objects.filter(
        vendor=request.user, 
        is_active=True
    ).exclude(id__in=existing_product_ids)
    
    context = {
        'promotion': promotion,
        'products': products,
    }
    return render(request, 'vendors/promotions/add_products.html', context)


@login_required
def vendor_promotion_remove_product(request, promotion_id, product_id):
    """
    Remove a product from promotion
    """
    promotion = get_object_or_404(Promotion, id=promotion_id, vendor=request.user)
    
    ProductPromotion.objects.filter(
        promotion=promotion,
        product_id=product_id
    ).delete()
    
    messages.success(request, 'Product removed from promotion!')
    return redirect('vendor_promotion_detail', promotion_id=promotion.id)


@login_required
def vendor_promotion_duplicate(request, promotion_id):
    """
    Duplicate an existing promotion
    """
    original = get_object_or_404(Promotion, id=promotion_id, vendor=request.user)
    
    # Create duplicate
    duplicate = Promotion.objects.create(
        vendor=original.vendor,
        company=original.company,
        name=f"{original.name} (Copy)",
        description=original.description,
        style=original.style,
        discount_percentage=original.discount_percentage,
        start_date=timezone.now(),
        end_date=original.end_date,
        status='DRAFT',
        is_active=False,
        show_badge=original.show_badge,
        show_countdown=original.show_countdown,
        featured=False,
        terms=original.terms,
    )
    
    # Copy products
    for pp in ProductPromotion.objects.filter(promotion=original):
        ProductPromotion.objects.create(
            promotion=duplicate,
            product=pp.product
        )
    
    messages.success(request, f'Promotion duplicated! Edit the details and activate when ready.')
    return redirect('vendor_promotion_edit', promotion_id=duplicate.id)

