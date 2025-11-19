# Raw Materials Suppliers - Quick Start Guide

## ✅ What's Complete

### Backend (100% Ready)
- ✅ All database models
- ✅ Migrations applied
- ✅ Admin interface configured
- ✅ Email system for credentials
- ✅ Approval workflow
- ✅ Purchase tracking
- ✅ Inquiry system
- ✅ Business intelligence data collection

## 🚀 How to Use Right Now

### Step 1: Create Material Categories

```bash
python manage.py shell
```

```python
from suppliers.models import RawMaterialCategory

categories = [
    {'name': 'Textiles & Fabrics', 'slug': 'textiles'},
    {'name': 'Wood & Timber', 'slug': 'wood'},
    {'name': 'Metals & Alloys', 'slug': 'metals'},
    {'name': 'Leather & Hides', 'slug': 'leather'},
    {'name': 'Beads & Jewelry', 'slug': 'beads'},
    {'name': 'Clay & Ceramics', 'slug': 'clay'},
    {'name': 'Natural Fibers', 'slug': 'fibers'},
    {'name': 'Dyes & Pigments', 'slug': 'dyes'},
    {'name': 'Packaging Materials', 'slug': 'packaging'},
]

for cat in categories:
    RawMaterialCategory.objects.get_or_create(
        slug=cat['slug'],
        defaults=cat
    )

print("✅ Categories created!")
exit()
```

### Step 2: Create a Supplier Account

**Via Django Admin:**

1. Go to: `http://127.0.0.1:8000/admin/`
2. Navigate to: **Authentication and Authorization** → **Users**
3. Click **Add User**
4. Create account:
   - Username: `supplier1`
   - Password: Set a password
   - **Important:** User type: `SUPPLIER`
5. Save

6. Go to: **Suppliers** → **Supplier Profiles**
7. Click **Add Supplier Profile**
8. Fill in:
   - Supplier: Select the user you just created
   - Company name: "Example Raw Materials Co."
   - Contact number: "+263771234567"
   - Email: "supplier@example.com"
   - Address: "123 Main St, Harare"
   - Is verified: ✓ Check
9. Save

### Step 3: Send Login Credentials

1. In **Supplier Profiles** list
2. Check the box next to your supplier
3. Actions dropdown → **Send login credentials to selected suppliers**
4. Click **Go**
5. ✅ Supplier receives email with login details!

### Step 4: Supplier Adds Material (Manual for Now)

**As Admin (temporarily):**

1. Go to: **Suppliers** → **Raw Materials**
2. Click **Add Raw Material**
3. Fill in:
   - Name: "Cotton Fabric - White"
   - Slug: "cotton-fabric-white"
   - Description: "High-quality cotton fabric..."
   - Supplier: Select your supplier
   - Category: "Textiles & Fabrics"
   - **Unit price**: 15.00
   - **Unit**: "meter"
   - **Min order quantity**: 5
   - Approval status: PENDING
   - Is locally sourced: ✓
   - Is available: ✓
4. Save

### Step 5: Approve Materials

1. In **Raw Materials** list
2. Filter by: **Approval status** → **Pending**
3. Select materials to approve
4. Actions → **Approve selected materials**
5. Click **Go**
6. ✅ Materials now visible to vendors!

## 📊 View Transactions

### Check Purchases
```
Admin → Suppliers → Raw Material Purchases
```

### Check Inquiries
```
Admin → Suppliers → Raw Material Inquiries
```

### View Analytics
```python
python manage.py shell
```

```python
from suppliers.models import RawMaterial, RawMaterialPurchase
from django.db.models import Sum, Count

# Total materials
print(f"Total materials: {RawMaterial.objects.count()}")
print(f"Approved: {RawMaterial.objects.filter(approval_status='APPROVED').count()}")
print(f"Pending: {RawMaterial.objects.filter(approval_status='PENDING').count()}")

# Purchases
purchases = RawMaterialPurchase.objects.all()
print(f"\nTotal purchases: {purchases.count()}")

if purchases.exists():
    total_revenue = purchases.aggregate(
        total=Sum('total_amount')
    )['total']
    print(f"Total revenue: ${total_revenue}")

exit()
```

## 🔗 Key URLs

### Admin
- **All Suppliers**: `/admin/suppliers/supplierprofile/`
- **All Materials**: `/admin/suppliers/rawmaterial/`
- **Pending Approvals**: `/admin/suppliers/rawmaterial/?approval_status=PENDING`
- **All Purchases**: `/admin/suppliers/rawmaterialpurchase/`
- **All Inquiries**: `/admin/suppliers/rawmaterialinquiry/`

## 📧 Email Template

**When you send credentials, suppliers receive:**

```
Subject: Welcome to Mushanai - Supplier Portal Access

Dear [Company Name],

Welcome to the Mushanai Supplier Portal!

Your account has been created. Here are your login details:

Username: [username]
Email: [email]

Login URL: [your-site]/accounts/login/

After logging in, you can:
- Add raw materials to your catalog
- Manage your inventory
- View and respond to inquiries from vendors
- Track your sales

Best regards,
The Mushanai Team
```

## 💡 Admin Actions Available

### Supplier Profiles
- ✅ Verify suppliers
- ✅ Send credentials email

### Raw Materials
- ✅ Approve materials
- ✅ Reject materials
- ✅ Mark available
- ✅ Mark unavailable

### Purchases
- ✅ Mark confirmed
- ✅ Mark shipped
- ✅ Mark delivered

### Inquiries
- ✅ Mark read
- ✅ Close inquiries

## 🎯 Testing Workflow

### Complete Test Run:

```bash
# 1. Start server
python manage.py runserver

# 2. Open admin
http://127.0.0.1:8000/admin/

# 3. Create supplier (as shown above)

# 4. Add material (as shown above)

# 5. Approve material

# 6. Check it's visible:
python manage.py shell
```

```python
from suppliers.models import RawMaterial

# Should show your material
approved = RawMaterial.objects.filter(
    approval_status='APPROVED',
    is_available=True
)

for material in approved:
    print(f"✅ {material.name} - ${material.unit_price}/{material.unit}")

exit()
```

## 📚 Full Documentation

- **Complete Guide**: `SUPPLIERS_MODULE_COMPLETE_GUIDE.md`
- **Implementation Details**: See guide for views/templates needed
- **Business Intelligence**: See guide for BI integration

## ✨ What Works NOW

1. ✅ Create suppliers via admin
2. ✅ Send email credentials
3. ✅ Add materials (via admin temporarily)
4. ✅ Approve/reject materials
5. ✅ Track all purchases
6. ✅ View inquiries
7. ✅ Update statuses
8. ✅ View analytics data

## 🚧 What Needs Frontend

- Supplier portal (add materials, view sales)
- Vendor marketplace (browse, buy, inquire)
- Business intelligence dashboard

**Estimated Time**: 2-3 days

## 🎊 Success!

Your Raw Materials Suppliers module is **ready for use**. You can:
- Create supplier accounts NOW
- Approve materials NOW
- Track transactions NOW
- Monitor everything NOW

The system is fully functional for admin use. Frontend portals can be added as needed!

---

**Status**: ✅ Production Ready (Admin Side)  
**Next**: Build supplier/vendor frontends  
**Last Updated**: November 19, 2025

