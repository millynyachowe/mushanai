# Vendor System - Quick Reference Card

## 🚀 Setup Commands

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Run migrations
python manage.py makemigrations vendors
python manage.py migrate

# 3. Create superuser (if needed)
python manage.py createsuperuser

# 4. Run development server
python manage.py runserver
```

## 🔗 Vendor URLs

### POS System
- **POS Interface**: http://127.0.0.1:8000/vendor/pos/
- **View All Receipts**: http://127.0.0.1:8000/vendor/receipts/
- **Receipt Detail**: http://127.0.0.1:8000/vendor/receipts/{id}/

### Accounting
- **Accounting Dashboard**: http://127.0.0.1:8000/vendor/accounting/
- **Expenses List**: http://127.0.0.1:8000/vendor/accounting/expenses/
- **Create Expense**: http://127.0.0.1:8000/vendor/accounting/expenses/create/

### Discussions
- **Forum Home**: http://127.0.0.1:8000/vendor/discussions/
- **Create Discussion**: http://127.0.0.1:8000/vendor/discussions/create/
- **View Discussion**: http://127.0.0.1:8000/vendor/discussions/{id}/

### General Vendor
- **Dashboard**: http://127.0.0.1:8000/vendor/dashboard/
- **Profile**: http://127.0.0.1:8000/vendor/profile/
- **Analytics**: http://127.0.0.1:8000/vendor/analytics/
- **Products**: http://127.0.0.1:8000/vendor/products/
- **Reviews**: http://127.0.0.1:8000/vendor/reviews/

### Admin
- **Django Admin**: http://127.0.0.1:8000/admin/

## 📋 Quick Shell Commands

### Create Discussion Categories
```python
python manage.py shell

from vendors.models import VendorDiscussionCategory

categories = [
    {'name': 'General Discussion', 'slug': 'general', 'icon': 'fas fa-comments', 'order': 1},
    {'name': 'Product Sourcing', 'slug': 'sourcing', 'icon': 'fas fa-shopping-cart', 'order': 2},
    {'name': 'Marketing & Sales', 'slug': 'marketing', 'icon': 'fas fa-chart-line', 'order': 3},
]

for cat in categories:
    VendorDiscussionCategory.objects.get_or_create(slug=cat['slug'], defaults=cat)
```

### Create Test Company
```python
python manage.py shell

from vendors.models import VendorCompany
from django.contrib.auth import get_user_model

User = get_user_model()
vendor = User.objects.filter(user_type='VENDOR').first()

VendorCompany.objects.create(
    vendor=vendor,
    name="Test Company",
    registration_number="REG001",
    is_active=True
)
```

### View Vendor Stats
```python
python manage.py shell

from vendors.models import SaleReceipt, VendorExpense
from django.contrib.auth import get_user_model

User = get_user_model()
vendor = User.objects.filter(user_type='VENDOR').first()

print(f"Total Receipts: {SaleReceipt.objects.filter(vendor=vendor).count()}")
print(f"Total Expenses: {VendorExpense.objects.filter(vendor=vendor).count()}")
```

## 🗂️ Model Reference

### SaleReceipt Fields
- `receipt_number` (auto-generated)
- `customer_name` (required)
- `customer_phone`, `customer_email` (optional)
- `payment_method` (CASH, ECOCASH, etc.)
- `subtotal`, `tax_amount`, `discount_amount`, `total_amount`
- `notes`, `is_walk_in`, `sale_date`

### VendorExpense Fields
- `description` (required)
- `category` (9 choices)
- `amount` (required)
- `expense_date` (required)
- `payment_method`, `reference_number` (optional)
- `receipt_image` (optional)
- `notes` (optional)

### VendorDiscussion Fields
- `title`, `content` (required)
- `category` (ForeignKey)
- `is_pinned`, `is_locked`, `is_announcement` (flags)
- `view_count`, `reply_count` (auto-tracked)

## 🎨 Template Locations

```
templates/vendors/
├── pos.html                    # POS interface
├── receipts_list.html          # Receipt history
├── receipt_detail.html         # Receipt view
├── receipt_print.html          # Print template
├── accounting_dashboard.html   # Accounting home
├── expenses_list.html          # Expense list
├── expense_create.html         # Create expense
├── discussions_list.html       # Forum home
├── discussion_detail.html      # Thread view
└── discussion_create.html      # Create thread
```

## 🔧 Common Customizations

### Change Receipt Branding
Edit: `templates/vendors/receipt_print.html`
- Lines 18-27: Company header
- Add logo, colors, additional info

### Add Payment Method
Edit: `vendors/models.py`
- Line 576: `PAYMENT_METHOD_CHOICES`
- Add: `('NEW_METHOD', 'Display Name'),`

### Add Expense Category
Edit: `vendors/models.py`
- Line 664: `EXPENSE_CATEGORY_CHOICES`
- Add: `('NEW_CATEGORY', 'Display Name'),`

### Customize Discussion Categories
Via Django Admin or Shell:
```python
VendorDiscussionCategory.objects.create(
    name='New Category',
    slug='new-category',
    icon='fas fa-icon-name',
    order=10,
    is_active=True
)
```

## 📊 Database Tables

New tables created:
- `vendors_salereceipt`
- `vendors_salereceiptitem`
- `vendors_vendorexpense`
- `vendors_vendorinvoice`
- `vendors_vendorinvoiceitem`
- `vendors_accountingjournalentry`
- `vendors_vendordiscussioncategory`
- `vendors_vendordiscussion`
- `vendors_vendordiscussionreply`

## 🐛 Troubleshooting

### No products in POS?
```python
# Check products exist and are active
from products.models import Product
Product.objects.filter(is_active=True, vendor=vendor).count()
```

### Receipt not printing?
- Check browser print settings
- Try Chrome/Firefox
- Ensure CSS is enabled

### No discussion categories?
```python
# Check categories exist
from vendors.models import VendorDiscussionCategory
VendorDiscussionCategory.objects.all()
```

### Can't access vendor URLs?
- Ensure user has `user_type='VENDOR'`
- Check if logged in
- Verify URLs in `mushanaicore/urls.py`

## 📱 Testing Checklist

- [ ] Create a vendor user
- [ ] Login as vendor
- [ ] Access POS
- [ ] Create a test sale
- [ ] Print/download receipt
- [ ] Create an expense
- [ ] View accounting dashboard
- [ ] Create discussion category
- [ ] Create a discussion
- [ ] Reply to discussion
- [ ] Test on mobile device

## 🎯 Admin Quick Access

### View All Vendor Data
- **Receipts**: Admin → Vendors → Sale receipts
- **Expenses**: Admin → Vendors → Vendor expenses
- **Discussions**: Admin → Vendors → Vendor discussions
- **Companies**: Admin → Vendors → Vendor Companies

### Bulk Actions
- Approve/reject discussions
- Export receipts to CSV
- Manage discussion categories
- Verify vendor companies

## 📞 Support Contacts

**Documentation:**
- `VENDOR_SYSTEM_GUIDE.md` - Full feature guide
- `MIGRATION_INSTRUCTIONS.md` - Setup steps
- `VENDOR_IMPLEMENTATION_SUMMARY.md` - Technical details

**Issues:**
- Check Django logs
- Check browser console
- Review server errors

## 🎉 Quick Start

```bash
# 1. Setup
source venv/bin/activate
python manage.py migrate

# 2. Create categories
python manage.py shell
# Run category creation code

# 3. Start server
python manage.py runserver

# 4. Login and test
# Go to: http://127.0.0.1:8000/vendor/pos/
```

---

**Tip**: Bookmark this file for quick reference during development!

**Version**: 1.0  
**Last Updated**: November 19, 2025

