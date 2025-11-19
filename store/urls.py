from django.urls import path
from .views import (
    home, brand_stories, product_search, search_autocomplete, trending_products, 
    product_detail, submit_review, vendor_response, mark_review_helpful, vendor_profile_public,
    track_social_share, checkout, checkout_success, add_to_cart, view_cart, remove_from_cart, update_cart_item
)

urlpatterns = [
    path('', home, name='home'),
    path('brand-stories/', brand_stories, name='brand_stories'),
    path('search/', product_search, name='product_search'),
    path('search/autocomplete/', search_autocomplete, name='search_autocomplete'),
    path('trending/', trending_products, name='trending_products'),
    path('product/<slug:slug>/', product_detail, name='product_detail'),
    path('product/<slug:slug>/review/', submit_review, name='submit_review'),
    path('review/<int:review_id>/response/', vendor_response, name='vendor_response'),
    path('review/<int:review_id>/helpful/', mark_review_helpful, name='mark_review_helpful'),
    path('vendor/<int:vendor_id>/', vendor_profile_public, name='vendor_profile_public'),
    path('share/track/', track_social_share, name='track_social_share'),
    path('checkout/', checkout, name='checkout'),
    path('checkout/success/<int:order_id>/', checkout_success, name='checkout_success'),
    path('cart/', view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', update_cart_item, name='update_cart_item'),
]
