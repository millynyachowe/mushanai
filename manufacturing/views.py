from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import (
    BillOfMaterials, BOMItem, ManufacturingOrder,
    QualityCheck, ProductionWorker, ManufacturingAnalytics
)
from products.models import Product
from suppliers.models import RawMaterial


@login_required
def manufacturing_dashboard(request):
    """
    Simple Production Dashboard - Overview of everything
    """
    if request.user.user_type != 'VENDOR':
        messages.error(request, 'Manufacturing module is only available to vendors.')
        return redirect('home')
    
    # Today's production orders
    today = timezone.now().date()
    today_orders = ManufacturingOrder.objects.filter(
        vendor=request.user,
        scheduled_date=today
    )
    
    # Orders by status
    orders_ready = ManufacturingOrder.objects.filter(
        vendor=request.user,
        status='READY'
    ).count()
    
    orders_in_progress = ManufacturingOrder.objects.filter(
        vendor=request.user,
        status='IN_PROGRESS'
    ).count()
    
    orders_quality_check = ManufacturingOrder.objects.filter(
        vendor=request.user,
        status='QUALITY_CHECK'
    ).count()
    
    # Products with BOMs
    products_with_bom = BillOfMaterials.objects.filter(
        vendor=request.user,
        is_active=True
    ).count()
    
    # Recent completed orders
    recent_completed = ManufacturingOrder.objects.filter(
        vendor=request.user,
        status='COMPLETED'
    ).order_by('-completed_at')[:5]
    
    # This month's production
    first_day_of_month = today.replace(day=1)
    month_production = ManufacturingOrder.objects.filter(
        vendor=request.user,
        created_at__gte=first_day_of_month,
        status='COMPLETED'
    ).aggregate(
        total_units=Sum('quantity_produced'),
        total_orders=Count('id')
    )
    
    context = {
        'today_orders': today_orders,
        'orders_ready': orders_ready,
        'orders_in_progress': orders_in_progress,
        'orders_quality_check': orders_quality_check,
        'products_with_bom': products_with_bom,
        'recent_completed': recent_completed,
        'month_production': month_production,
    }
    
    return render(request, 'manufacturing/dashboard.html', context)


@login_required
def bom_list(request):
    """
    List all Bills of Materials (Product Recipes)
    """
    if request.user.user_type != 'VENDOR':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    boms = BillOfMaterials.objects.filter(
        vendor=request.user
    ).select_related('product').prefetch_related('items')
    
    # Products without BOM
    products_without_bom = Product.objects.filter(
        vendor=request.user
    ).exclude(bom__isnull=False)
    
    context = {
        'boms': boms,
        'products_without_bom': products_without_bom,
    }
    
    return render(request, 'manufacturing/bom_list.html', context)


@login_required
def bom_create(request, product_id):
    """
    Create a Bill of Materials for a product
    """
    if request.user.user_type != 'VENDOR':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    product = get_object_or_404(Product, id=product_id, vendor=request.user)
    
    if hasattr(product, 'bom'):
        messages.warning(request, 'This product already has a BOM.')
        return redirect('bom_detail', bom_id=product.bom.id)
    
    if request.method == 'POST':
        # Create BOM
        bom = BillOfMaterials.objects.create(
            product=product,
            vendor=request.user,
            batch_size=request.POST.get('batch_size', 1),
            production_time_hours=request.POST.get('production_time_hours') or None,
            labor_cost_per_unit=request.POST.get('labor_cost_per_unit', 0),
            overhead_cost_per_unit=request.POST.get('overhead_cost_per_unit', 0),
            markup_percentage=request.POST.get('markup_percentage', 50),
            instructions=request.POST.get('instructions', ''),
        )
        
        messages.success(request, f'BOM created for {product.name}. Now add materials.')
        return redirect('bom_detail', bom_id=bom.id)
    
    # Get available raw materials
    raw_materials = RawMaterial.objects.filter(
        approval_status='APPROVED',
        is_available=True
    )
    
    context = {
        'product': product,
        'raw_materials': raw_materials,
    }
    
    return render(request, 'manufacturing/bom_create.html', context)


@login_required
def bom_detail(request, bom_id):
    """
    View and manage a Bill of Materials
    """
    bom = get_object_or_404(BillOfMaterials, id=bom_id, vendor=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_item':
            # Add material to BOM
            material_id = request.POST.get('material_id')
            quantity = request.POST.get('quantity')
            unit = request.POST.get('unit')
            notes = request.POST.get('notes', '')
            
            if material_id and quantity:
                material = get_object_or_404(RawMaterial, id=material_id)
                BOMItem.objects.create(
                    bom=bom,
                    raw_material=material,
                    quantity=quantity,
                    unit=unit or material.unit,
                    notes=notes
                )
                bom.calculate_costs()
                messages.success(request, 'Material added to BOM.')
        
        elif action == 'remove_item':
            item_id = request.POST.get('item_id')
            BOMItem.objects.filter(id=item_id, bom=bom).delete()
            bom.calculate_costs()
            messages.success(request, 'Material removed from BOM.')
        
        return redirect('bom_detail', bom_id=bom.id)
    
    # Get available raw materials
    raw_materials = RawMaterial.objects.filter(
        approval_status='APPROVED',
        is_available=True
    )
    
    context = {
        'bom': bom,
        'raw_materials': raw_materials,
    }
    
    return render(request, 'manufacturing/bom_detail.html', context)


@login_required
def bom_edit(request, bom_id):
    """
    Edit BOM details
    """
    bom = get_object_or_404(BillOfMaterials, id=bom_id, vendor=request.user)
    
    if request.method == 'POST':
        bom.batch_size = request.POST.get('batch_size', 1)
        bom.production_time_hours = request.POST.get('production_time_hours') or None
        bom.labor_cost_per_unit = request.POST.get('labor_cost_per_unit', 0)
        bom.overhead_cost_per_unit = request.POST.get('overhead_cost_per_unit', 0)
        bom.markup_percentage = request.POST.get('markup_percentage', 50)
        bom.instructions = request.POST.get('instructions', '')
        bom.save()
        bom.calculate_costs()
        
        messages.success(request, 'BOM updated successfully.')
        return redirect('bom_detail', bom_id=bom.id)
    
    context = {'bom': bom}
    return render(request, 'manufacturing/bom_edit.html', context)


@login_required
def manufacturing_orders_list(request):
    """
    List all manufacturing orders
    """
    if request.user.user_type != 'VENDOR':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    orders = ManufacturingOrder.objects.filter(
        vendor=request.user
    ).select_related('product', 'bom').order_by('-created_at')
    
    # Filters
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    
    context = {
        'orders': orders,
        'selected_status': status,
    }
    
    return render(request, 'manufacturing/orders_list.html', context)


@login_required
def manufacturing_order_create(request):
    """
    Create a new manufacturing order
    """
    if request.user.user_type != 'VENDOR':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')
        scheduled_date = request.POST.get('scheduled_date') or None
        priority = request.POST.get('priority', 'NORMAL')
        notes = request.POST.get('notes', '')
        
        product = get_object_or_404(Product, id=product_id, vendor=request.user)
        
        if not hasattr(product, 'bom'):
            messages.error(request, 'This product does not have a BOM. Please create one first.')
            return redirect('bom_create', product_id=product.id)
        
        # Create manufacturing order
        mo = ManufacturingOrder.objects.create(
            vendor=request.user,
            product=product,
            bom=product.bom,
            quantity_to_produce=quantity,
            scheduled_date=scheduled_date,
            priority=priority,
            production_notes=notes,
            status='READY'
        )
        
        mo.calculate_local_percentage()
        
        messages.success(request, f'Manufacturing order {mo.mo_number} created!')
        return redirect('manufacturing_order_detail', mo_id=mo.id)
    
    # Get products with BOMs
    products_with_bom = Product.objects.filter(
        vendor=request.user,
        bom__isnull=False
    )
    
    context = {
        'products': products_with_bom,
    }
    
    return render(request, 'manufacturing/order_create.html', context)


@login_required
def manufacturing_order_detail(request, mo_id):
    """
    View manufacturing order details
    """
    mo = get_object_or_404(ManufacturingOrder, id=mo_id, vendor=request.user)
    
    context = {
        'mo': mo,
    }
    
    return render(request, 'manufacturing/order_detail.html', context)


@login_required
def manufacturing_order_start(request, mo_id):
    """
    Start a manufacturing order
    """
    mo = get_object_or_404(ManufacturingOrder, id=mo_id, vendor=request.user)
    
    if mo.status == 'READY':
        mo.start_production()
        messages.success(request, f'Production started for {mo.mo_number}')
    else:
        messages.warning(request, 'Order is not in READY status.')
    
    return redirect('manufacturing_order_detail', mo_id=mo.id)


@login_required
def manufacturing_order_complete(request, mo_id):
    """
    Complete a manufacturing order
    """
    mo = get_object_or_404(ManufacturingOrder, id=mo_id, vendor=request.user)
    
    if request.method == 'POST':
        quantity_produced = request.POST.get('quantity_produced')
        quantity_approved = request.POST.get('quantity_approved', quantity_produced)
        
        mo.quantity_produced = quantity_produced
        mo.quantity_approved = quantity_approved
        mo.complete_production()
        
        messages.success(request, f'Production completed! {quantity_approved} units added to inventory.')
        return redirect('manufacturing_order_detail', mo_id=mo.id)
    
    context = {'mo': mo}
    return render(request, 'manufacturing/order_complete.html', context)


@login_required
def manufacturing_materials(request):
    """
    View raw materials needed for production
    """
    if request.user.user_type != 'VENDOR':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # Get all materials used in vendor's BOMs
    boms = BillOfMaterials.objects.filter(vendor=request.user, is_active=True)
    
    materials_needed = {}
    for bom in boms:
        for item in bom.items.all():
            material = item.raw_material
            if material.id not in materials_needed:
                materials_needed[material.id] = {
                    'material': material,
                    'total_quantity': 0,
                    'products': []
                }
            materials_needed[material.id]['total_quantity'] += item.quantity
            materials_needed[material.id]['products'].append(bom.product.name)
    
    context = {
        'materials_needed': materials_needed.values(),
    }
    
    return render(request, 'manufacturing/materials.html', context)


@login_required
def request_materials(request):
    """
    Redirect to raw materials marketplace
    """
    messages.info(request, 'Browse and purchase raw materials from our marketplace.')
    return redirect('raw_materials')  # This will be created in vendors module


@login_required
def manufacturing_analytics(request):
    """
    Manufacturing analytics and community impact
    """
    if request.user.user_type != 'VENDOR':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # This month
    today = timezone.now().date()
    first_day = today.replace(day=1)
    
    orders_this_month = ManufacturingOrder.objects.filter(
        vendor=request.user,
        created_at__gte=first_day
    )
    
    completed_orders = orders_this_month.filter(status='COMPLETED')
    
    stats = completed_orders.aggregate(
        total_units=Sum('quantity_produced'),
        total_cost=Sum('actual_cost'),
        avg_local_percentage=Avg('local_materials_percentage')
    )
    
    # Workers
    workers = ProductionWorker.objects.filter(
        vendor=request.user,
        work_date__gte=first_day
    )
    
    worker_stats = workers.aggregate(
        total_workers=Count('worker_name', distinct=True),
        total_hours=Sum('hours_worked'),
        total_wages=Sum('total_payment')
    )
    
    # Community contribution (1% of production value)
    if stats['total_cost']:
        community_contribution = Decimal(str(stats['total_cost'])) * Decimal('0.01')
    else:
        community_contribution = 0
    
    context = {
        'stats': stats,
        'worker_stats': worker_stats,
        'community_contribution': community_contribution,
        'orders_this_month': orders_this_month,
        'completed_orders': completed_orders,
    }
    
    return render(request, 'manufacturing/analytics.html', context)

