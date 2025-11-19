from django.shortcuts import render
from products.models import Product, Brand
from vendors.models import VendorProfile
from projects.models import CommunityProject


def home(request):
    # Get featured products
    featured_products = Product.objects.filter(is_featured=True, is_active=True)[:8]
    
    # Get all active products
    products = Product.objects.filter(is_active=True).order_by('-created_at')[:12]
    
    context = {
        'featured_products': featured_products,
        'products': products,
    }
    return render(request, 'home/index.html', context)


def brand_stories(request):
    # Get vendor profiles that have published brand stories (description published)
    brands = VendorProfile.objects.filter(
        description__isnull=False
    ).exclude(description='').order_by('-created_at')
    
    context = {
        'brands': brands,
    }
    return render(request, 'home/brand_stories.html', context)
