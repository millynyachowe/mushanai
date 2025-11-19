from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.social_media_dashboard, name='social_media_dashboard'),
    
    # Account management
    path('connect/<str:platform>/', views.connect_account, name='social_connect_account'),
    path('oauth/<str:platform>/callback/', views.oauth_callback, name='social_oauth_callback'),
    path('accounts/<int:account_id>/disconnect/', views.disconnect_account, name='social_disconnect_account'),
    path('accounts/<int:account_id>/settings/', views.account_settings, name='social_account_settings'),
    
    # Templates
    path('templates/', views.templates_list, name='social_templates_list'),
    path('templates/create/', views.template_create, name='social_template_create'),
    path('templates/<int:template_id>/edit/', views.template_edit, name='social_template_edit'),
    
    # Posting
    path('posts/', views.posts_list, name='social_posts_list'),
    path('post/<int:product_id>/', views.post_product, name='social_post_product'),
    path('preview/<int:product_id>/', views.post_preview, name='social_post_preview'),
    
    # Analytics
    path('analytics/', views.analytics_dashboard, name='social_analytics'),
]

