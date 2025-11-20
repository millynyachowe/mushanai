from django.urls import path
from . import views

urlpatterns = [
    # Notification management
    path('', views.notification_list, name='notification_list'),
    path('<int:notification_id>/read/', views.notification_mark_read, name='notification_mark_read'),
    path('<int:notification_id>/unread/', views.notification_mark_unread, name='notification_mark_unread'),
    path('mark-all-read/', views.notification_mark_all_read, name='notification_mark_all_read'),
    path('<int:notification_id>/delete/', views.notification_delete, name='notification_delete'),
    
    # Preferences
    path('preferences/', views.notification_preferences, name='notification_preferences'),
    
    # API endpoints
    path('api/list/', views.api_notification_list, name='api_notification_list'),
    path('api/unread-count/', views.api_unread_count, name='api_unread_count'),
    path('dropdown/', views.notification_dropdown, name='notification_dropdown'),
]

