from django.urls import path
from . import views

urlpatterns = [
    # Manufacturing Dashboard
    path('', views.manufacturing_dashboard, name='manufacturing_dashboard'),
    
    # Bills of Materials
    path('bom/', views.bom_list, name='bom_list'),
    path('bom/create/<int:product_id>/', views.bom_create, name='bom_create'),
    path('bom/<int:bom_id>/', views.bom_detail, name='bom_detail'),
    path('bom/<int:bom_id>/edit/', views.bom_edit, name='bom_edit'),
    
    # Manufacturing Orders
    path('orders/', views.manufacturing_orders_list, name='manufacturing_orders'),
    path('orders/create/', views.manufacturing_order_create, name='manufacturing_order_create'),
    path('orders/<int:mo_id>/', views.manufacturing_order_detail, name='manufacturing_order_detail'),
    path('orders/<int:mo_id>/start/', views.manufacturing_order_start, name='manufacturing_order_start'),
    path('orders/<int:mo_id>/complete/', views.manufacturing_order_complete, name='manufacturing_order_complete'),
    
    # Raw Materials for Manufacturing
    path('materials/', views.manufacturing_materials, name='manufacturing_materials'),
    path('materials/request/', views.request_materials, name='request_materials'),
    
    # Analytics
    path('analytics/', views.manufacturing_analytics, name='manufacturing_analytics'),
]

