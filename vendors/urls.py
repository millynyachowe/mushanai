from django.urls import path
from .views import (
    vendor_dashboard,
    vendor_profile,
    product_list,
    product_create,
    product_detail,
    vendor_reviews,
    vendor_analytics_dashboard,
    vendor_payment_settings,
    vendor_payment_inbox,
    # POS views
    vendor_pos,
    vendor_pos_create_receipt,
    vendor_receipts_list,
    vendor_receipt_detail,
    # Accounting views
    vendor_accounting_dashboard,
    vendor_expenses_list,
    vendor_expense_create,
    vendor_expense_detail,
    vendor_expense_edit,
    vendor_expense_delete,
    vendor_expenses_export,
    # Discussion views
    vendor_discussions,
    vendor_discussion_detail,
    vendor_discussion_create,
)

# Import promotion views
from .views_promotions import (
    vendor_promotions_list,
    vendor_promotion_create,
    vendor_promotion_detail,
    vendor_promotion_edit,
    vendor_promotion_toggle,
    vendor_promotion_delete,
    vendor_promotion_add_products,
    vendor_promotion_remove_product,
    vendor_promotion_duplicate,
)

urlpatterns = [
    # Dashboard & Profile
    path('dashboard/', vendor_dashboard, name='vendor_dashboard'),
    path('profile/', vendor_profile, name='vendor_profile'),
    
    # Analytics
    path('analytics/', vendor_analytics_dashboard, name='vendor_analytics_dashboard'),
    
    # Payments
    path('payments/', vendor_payment_settings, name='vendor_payment_settings'),
    path('payments/inbox/', vendor_payment_inbox, name='vendor_payment_inbox'),
    
    # Products
    path('products/', product_list, name='vendor_product_list'),
    path('products/create/', product_create, name='vendor_product_create'),
    path('products/<int:pk>/', product_detail, name='vendor_product_detail'),
    
    # Reviews
    path('reviews/', vendor_reviews, name='vendor_reviews'),
    
    # POS (Point of Sale)
    path('pos/', vendor_pos, name='vendor_pos'),
    path('pos/create-receipt/', vendor_pos_create_receipt, name='vendor_pos_create_receipt'),
    path('receipts/', vendor_receipts_list, name='vendor_receipts_list'),
    path('receipts/<int:receipt_id>/', vendor_receipt_detail, name='vendor_receipt_detail'),
    
    # Accounting
    path('accounting/', vendor_accounting_dashboard, name='vendor_accounting_dashboard'),
    path('accounting/expenses/', vendor_expenses_list, name='vendor_expenses_list'),
    path('accounting/expenses/create/', vendor_expense_create, name='vendor_expense_create'),
    path('accounting/expenses/<int:expense_id>/', vendor_expense_detail, name='vendor_expense_detail'),
    path('accounting/expenses/<int:expense_id>/edit/', vendor_expense_edit, name='vendor_expense_edit'),
    path('accounting/expenses/<int:expense_id>/delete/', vendor_expense_delete, name='vendor_expense_delete'),
    path('accounting/expenses/export/', vendor_expenses_export, name='vendor_expenses_export'),
    
    # Discussions/Forum
    path('discussions/', vendor_discussions, name='vendor_discussions'),
    path('discussions/create/', vendor_discussion_create, name='vendor_discussion_create'),
    path('discussions/<int:discussion_id>/', vendor_discussion_detail, name='vendor_discussion_detail'),
    
    # Promotions
    path('promotions/', vendor_promotions_list, name='vendor_promotions_list'),
    path('promotions/create/', vendor_promotion_create, name='vendor_promotion_create'),
    path('promotions/<int:promotion_id>/', vendor_promotion_detail, name='vendor_promotion_detail'),
    path('promotions/<int:promotion_id>/edit/', vendor_promotion_edit, name='vendor_promotion_edit'),
    path('promotions/<int:promotion_id>/toggle/', vendor_promotion_toggle, name='vendor_promotion_toggle'),
    path('promotions/<int:promotion_id>/delete/', vendor_promotion_delete, name='vendor_promotion_delete'),
    path('promotions/<int:promotion_id>/add-products/', vendor_promotion_add_products, name='vendor_promotion_add_products'),
    path('promotions/<int:promotion_id>/remove-product/<int:product_id>/', vendor_promotion_remove_product, name='vendor_promotion_remove_product'),
    path('promotions/<int:promotion_id>/duplicate/', vendor_promotion_duplicate, name='vendor_promotion_duplicate'),
]
