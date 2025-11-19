# Migration Instructions for Vendor Management System

## ⚠️ Important: Disk Space Issue

During setup, we encountered a "No space left on device" error. You'll need to resolve this before running migrations.

## Steps to Complete Setup

### 1. Free Up Disk Space

```bash
# Check available disk space
df -h

# Clear system cache (macOS)
sudo rm -rf /private/var/folders/*
sudo rm -rf ~/Library/Caches/*

# Or use CleanMyMac or similar tool
```

### 2. Activate Virtual Environment

```bash
cd /Users/ishe/Desktop/Milly/mushanai
source venv/bin/activate
```

### 3. Run Migrations

```bash
# Create migrations for vendors app
python manage.py makemigrations vendors

# You should see output like:
# Migrations for 'vendors':
#   vendors/migrations/000X_auto_YYYYMMDD_HHMM.py
#     - Create model AccountingJournalEntry
#     - Create model SaleReceipt
#     - Create model SaleReceiptItem
#     - Create model VendorExpense
#     - Create model VendorInvoice
#     - Create model VendorInvoiceItem
#     - Create model VendorDiscussionCategory
#     - Create model VendorDiscussion
#     - Create model VendorDiscussionReply

# Apply migrations
python manage.py migrate
```

### 4. Create Discussion Categories

After migrations, create some discussion categories through Django admin:

```bash
python manage.py shell
```

```python
from vendors.models import VendorDiscussionCategory

categories = [
    {'name': 'General Discussion', 'slug': 'general', 'icon': 'fas fa-comments', 'order': 1},
    {'name': 'Product Sourcing', 'slug': 'sourcing', 'icon': 'fas fa-shopping-cart', 'order': 2},
    {'name': 'Marketing & Sales', 'slug': 'marketing', 'icon': 'fas fa-chart-line', 'order': 3},
    {'name': 'Shipping & Logistics', 'slug': 'logistics', 'icon': 'fas fa-truck', 'order': 4},
    {'name': 'Customer Service', 'slug': 'customer-service', 'icon': 'fas fa-headset', 'order': 5},
    {'name': 'Success Stories', 'slug': 'success-stories', 'icon': 'fas fa-trophy', 'order': 6},
]

for cat_data in categories:
    VendorDiscussionCategory.objects.get_or_create(
        slug=cat_data['slug'],
        defaults=cat_data
    )

print("Discussion categories created!")
exit()
```

### 5. Test the System

1. **Test POS**: Navigate to `/vendor/pos/` and create a test sale
2. **Test Receipts**: View the receipt at `/vendor/receipts/`
3. **Test Accounting**: Go to `/vendor/accounting/` to see the dashboard
4. **Test Discussions**: Create a discussion at `/vendor/discussions/create/`

### 6. Create Sample Data (Optional)

```python
python manage.py shell
```

```python
from vendors.models import VendorCompany
from django.contrib.auth import get_user_model

User = get_user_model()

# Find a vendor user
vendor = User.objects.filter(user_type='VENDOR').first()

if vendor:
    # Create a company for the vendor
    VendorCompany.objects.get_or_create(
        vendor=vendor,
        name=f"{vendor.username}'s Company",
        defaults={'registration_number': 'REG001', 'is_active': True}
    )
    print(f"Company created for {vendor.username}")
else:
    print("No vendor users found. Create a vendor user first.")

exit()
```

## Verification Checklist

After migrations, verify:

- [ ] All models appear in Django admin
- [ ] Can access `/vendor/pos/`
- [ ] Can access `/vendor/receipts/`
- [ ] Can access `/vendor/accounting/`
- [ ] Can access `/vendor/discussions/`
- [ ] Can create a test receipt in POS
- [ ] Can create a test expense
- [ ] Can create a test discussion
- [ ] Receipt prints correctly
- [ ] All vendor menu items work

## Common Issues

### Issue: "No module named 'vendors'"
**Solution**: Make sure you're in the correct directory and virtual environment is activated.

### Issue: "relation does not exist"
**Solution**: Run migrations: `python manage.py migrate`

### Issue: "No discussion categories"
**Solution**: Create categories using the shell commands above or through Django admin.

### Issue: "404 on vendor URLs"
**Solution**: Ensure `vendors.urls` is included in main `urls.py`:
```python
path('vendor/', include('vendors.urls')),
```

### Issue: "Products not showing in POS"
**Solution**: 
1. Ensure products are created
2. Products must be `is_active=True`
3. Products must belong to the logged-in vendor

## Database Backup Recommendation

Before running migrations on production:

```bash
# SQLite backup
cp db.sqlite3 db.sqlite3.backup_$(date +%Y%m%d)

# PostgreSQL backup (if using)
pg_dump dbname > backup_$(date +%Y%m%d).sql
```

## Success! 🎉

Once migrations are complete, your vendor management system is ready to use! Refer to `VENDOR_SYSTEM_GUIDE.md` for detailed feature documentation.

## Quick Start for Vendors

1. Login as a vendor user
2. Navigate to `/vendor/dashboard/`
3. Click "POS" to make your first sale
4. Click "Accounting" to track expenses
5. Click "Discussions" to connect with other vendors

---

**Note**: The system is fully integrated with your existing vendor profiles, products, and order system. No data migration is needed - it works with your existing data!

