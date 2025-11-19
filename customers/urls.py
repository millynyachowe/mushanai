from django.urls import path
from .views import (
    customer_portal, my_orders, my_projects, referral_program, submit_testimonial,
    notifications_dashboard, mark_notification_read,
    subscribe_back_in_stock, cancel_back_in_stock,
    toggle_vendor_subscription, toggle_project_notification,
    gamification_dashboard, join_challenge,
    wishlist_list, wishlist_detail, wishlist_create, wishlist_delete,
    wishlist_add_product, wishlist_remove_product, wishlist_share,
    price_alerts_list, price_alert_create, price_alert_delete,
    gift_registry_list, gift_registry_detail, gift_registry_create,
    gift_registry_add_product, gift_registry_remove_product, gift_registry_public
)

urlpatterns = [
    path('portal/', customer_portal, name='customer_portal'),
    path('orders/', my_orders, name='customer_orders'),
    path('projects/', my_projects, name='customer_my_projects'),
    path('referrals/', referral_program, name='referral_program'),
    path('testimonial/<int:vendor_id>/', submit_testimonial, name='submit_testimonial'),
    path('notifications/', notifications_dashboard, name='notifications_dashboard'),
    path('notifications/<int:notification_id>/read/', mark_notification_read, name='mark_notification_read'),
    path('notifications/back-in-stock/<int:product_id>/', subscribe_back_in_stock, name='subscribe_back_in_stock'),
    path('notifications/back-in-stock/cancel/<int:alert_id>/', cancel_back_in_stock, name='cancel_back_in_stock'),
    path('notifications/vendor/<int:vendor_id>/toggle/', toggle_vendor_subscription, name='toggle_vendor_subscription'),
    path('notifications/project/<int:project_id>/toggle/', toggle_project_notification, name='toggle_project_notification'),
    path('gamification/', gamification_dashboard, name='gamification_dashboard'),
    path('gamification/challenge/<int:challenge_id>/join/', join_challenge, name='join_challenge'),
    
    # Wishlist URLs
    path('wishlists/', wishlist_list, name='wishlist_list'),
    path('wishlist/create/', wishlist_create, name='wishlist_create'),
    path('wishlist/<int:wishlist_id>/', wishlist_detail, name='wishlist_detail'),
    path('wishlist/<int:wishlist_id>/delete/', wishlist_delete, name='wishlist_delete'),
    path('wishlist/add/<int:product_id>/', wishlist_add_product, name='wishlist_add_product'),
    path('wishlist/remove/<int:item_id>/', wishlist_remove_product, name='wishlist_remove_product'),
    path('wishlist/share/<str:share_token>/', wishlist_share, name='wishlist_share'),
    
    # Price Alert URLs
    path('price-alerts/', price_alerts_list, name='price_alerts_list'),
    path('price-alert/create/<int:product_id>/', price_alert_create, name='price_alert_create'),
    path('price-alert/<int:alert_id>/delete/', price_alert_delete, name='price_alert_delete'),
    
    # Gift Registry URLs
    path('gift-registries/', gift_registry_list, name='gift_registry_list'),
    path('gift-registry/create/', gift_registry_create, name='gift_registry_create'),
    path('gift-registry/<int:registry_id>/', gift_registry_detail, name='gift_registry_detail'),
    path('gift-registry/<int:registry_id>/add/<int:product_id>/', gift_registry_add_product, name='gift_registry_add_product'),
    path('gift-registry/remove/<int:item_id>/', gift_registry_remove_product, name='gift_registry_remove_product'),
    path('gift-registry/share/<str:share_token>/', gift_registry_public, name='gift_registry_public'),
]

