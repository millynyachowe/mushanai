"""
Product recommendation engine
"""
from django.db.models import Count, Q, Avg, F
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import Product, ProductView, ProductReview

User = get_user_model()


def get_customers_also_bought(product, limit=8):
    """
    Get products that customers who bought this product also bought
    Based on order history
    """
    from orders.models import OrderItem
    
    # Get customers who bought this product
    customers_who_bought = OrderItem.objects.filter(
        product=product,
        order__payment_status='PAID'
    ).values_list('order__customer', flat=True).distinct()
    
    if not customers_who_bought:
        return Product.objects.none()
    
    # Get other products bought by these customers (excluding the current product)
    also_bought = OrderItem.objects.filter(
        order__customer__in=customers_who_bought,
        order__payment_status='PAID'
    ).exclude(
        product=product
    ).values('product').annotate(
        purchase_count=Count('product')
    ).order_by('-purchase_count')[:limit]
    
    product_ids = [item['product'] for item in also_bought]
    
    # Return products ordered by purchase frequency
    products = Product.objects.filter(
        id__in=product_ids,
        is_active=True
    ).annotate(
        purchase_count=Count('order_items', filter=Q(order_items__order__customer__in=customers_who_bought))
    ).order_by('-purchase_count', '-created_at')
    
    return products


def get_similar_products(product, limit=8):
    """
    Get similar products based on category, brand, and attributes
    """
    from django.db.models import Case, When, IntegerField
    
    similar_products = Product.objects.filter(
        is_active=True
    ).exclude(id=product.id)
    
    # Build similarity query - prioritize by category, then brand, then vendor
    similarity_filters = Q()
    
    # Same category (highest priority)
    if product.category:
        similarity_filters |= Q(category=product.category)
    
    # Same brand
    if product.brand:
        similarity_filters |= Q(brand=product.brand)
    
    # Same vendor
    if product.vendor:
        similarity_filters |= Q(vendor=product.vendor)
    
    # Filter products that match similarity criteria
    if similarity_filters:
        similar = similar_products.filter(similarity_filters)
    else:
        # If no filters, just get other products from same vendor
        similar = similar_products.filter(vendor=product.vendor)
    
    # Annotate with ratings and sales
    similar = similar.annotate(
        avg_rating=Avg('reviews__rating'),
        annotated_review_count=Count('reviews', distinct=True),
        sales_count=Count('order_items', distinct=True)
    )
    
    # If no similar products found with filters, get products from same category or vendor
    if not similar.exists():
        fallback = Product.objects.filter(
            is_active=True
        ).exclude(id=product.id)
        if product.category:
            fallback = fallback.filter(category=product.category)
        elif product.vendor:
            fallback = fallback.filter(vendor=product.vendor)
        similar = fallback.annotate(
            avg_rating=Avg('reviews__rating'),
            annotated_review_count=Count('reviews', distinct=True),
            sales_count=Count('order_items', distinct=True)
        )
    
    # Order by ratings and popularity
    similar = similar.order_by('-avg_rating', '-annotated_review_count', '-sales_count', '-created_at')
    
    return similar[:limit]


def get_recently_viewed(customer=None, session_key=None, limit=8):
    """
    Get recently viewed products for a customer or session
    """
    if customer:
        views = ProductView.objects.filter(
            customer=customer
        ).order_by('-viewed_at').values_list('product_id', flat=True).distinct()[:limit]
    elif session_key:
        views = ProductView.objects.filter(
            session_key=session_key
        ).order_by('-viewed_at').values_list('product_id', flat=True).distinct()[:limit]
    else:
        return Product.objects.none()
    
    product_ids = list(views)
    
    # Preserve order of views
    products = Product.objects.filter(id__in=product_ids, is_active=True)
    # Create a mapping to preserve order
    product_dict = {p.id: p for p in products}
    return [product_dict[pid] for pid in product_ids if pid in product_dict]


def get_personalized_recommendations(customer, limit=12):
    """
    Get personalized product recommendations based on purchase history
    """
    from orders.models import OrderItem
    from django.db.models import Case, When, IntegerField, FloatField
    
    # Get customer's purchase history
    purchased_products = OrderItem.objects.filter(
        order__customer=customer,
        order__payment_status='PAID'
    ).values_list('product_id', flat=True).distinct()
    
    if not purchased_products:
        # No purchase history, return trending products
        return get_trending_products(limit=limit)
    
    # Get categories and brands from purchased products
    purchased_categories = list(Product.objects.filter(
        id__in=purchased_products
    ).values_list('category_id', flat=True).distinct())
    
    purchased_brands = list(Product.objects.filter(
        id__in=purchased_products
    ).values_list('brand_id', flat=True).distinct())
    
    # Get products in same categories/brands that customer hasn't bought
    recommendations = Product.objects.filter(
        is_active=True
    ).exclude(
        id__in=purchased_products
    )
    
    # Filter by categories or brands
    if purchased_categories or purchased_brands:
        category_filter = Q(category_id__in=purchased_categories) if purchased_categories else Q()
        brand_filter = Q(brand_id__in=purchased_brands) if purchased_brands else Q()
        recommendations = recommendations.filter(category_filter | brand_filter)
    
    # Annotate with scores (use unique names to avoid property conflicts)
    recommendations = recommendations.annotate(
        annotated_avg_rating=Avg('reviews__rating'),
        annotated_review_count=Count('reviews', distinct=True),
        annotated_sales_count=Count('order_items', distinct=True)
    )
    
    # Order by ratings, reviews, and sales
    recommendations = recommendations.order_by(
        '-annotated_avg_rating',
        '-annotated_review_count',
        '-annotated_sales_count',
        '-created_at'
    )
    
    return recommendations[:limit]


def get_trending_products(limit=12, days=30):
    """
    Get trending products based on recent activity (views, sales, reviews)
    """
    from orders.models import OrderItem
    from django.db.models import Count, Avg, F
    
    cutoff_date = timezone.now() - timedelta(days=days)
    
    trending = Product.objects.filter(
        is_active=True
    ).annotate(
        annotated_avg_rating=Avg('reviews__rating'),
        annotated_review_count=Count('reviews', distinct=True),
        annotated_recent_sales=Count('order_items', filter=Q(order_items__order__created_at__gte=cutoff_date), distinct=True),
        annotated_recent_views=Count('views', filter=Q(views__viewed_at__gte=cutoff_date), distinct=True)
    )
    
    # Calculate trending score (simplified - using popularity_score property)
    # Order by combination of factors
    trending = trending.order_by(
        '-annotated_recent_sales',
        '-annotated_recent_views', 
        '-annotated_review_count',
        '-annotated_avg_rating',
        '-view_count',
        '-created_at'
    )[:limit]
    
    return trending


def get_seasonal_suggestions(limit=8):
    """
    Get seasonal/trending product suggestions
    Currently returns featured and trending products
    Can be enhanced with actual seasonal logic
    """
    # Get featured products first
    featured = Product.objects.filter(
        is_featured=True,
        is_active=True
    ).annotate(
        featured_avg_rating=Avg('reviews__rating'),
        featured_review_count=Count('reviews', distinct=True)
    ).order_by('-featured_avg_rating', '-featured_review_count')[:limit // 2]
    
    # Fill with trending if needed
    remaining = limit - featured.count()
    if remaining > 0:
        trending = get_trending_products(limit=remaining)
        return list(featured) + list(trending)
    
    return featured


def track_product_view(product, customer=None, session_key=None, ip_address=None):
    """
    Track a product view for recommendations
    """
    from django.db.models import F
    
    ProductView.objects.create(
        product=product,
        customer=customer,
        session_key=session_key,
        ip_address=ip_address
    )
    
    # Update product view count
    Product.objects.filter(id=product.id).update(view_count=F('view_count') + 1)
    
    # Update customer dashboard's recently viewed (keep last 20)
    if customer:
        try:
            dashboard = customer.customer_dashboard
            dashboard.last_viewed_products.add(product)
            # Keep only last 20 viewed products (get most recent views)
            recent_views = ProductView.objects.filter(
                customer=customer
            ).order_by('-viewed_at').values_list('product_id', flat=True).distinct()[:20]
            dashboard.last_viewed_products.set(recent_views)
        except:
            # Dashboard doesn't exist yet, create it
            from customers.models import CustomerDashboard
            dashboard = CustomerDashboard.objects.create(customer=customer)
            dashboard.last_viewed_products.add(product)

