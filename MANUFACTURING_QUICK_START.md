# 🏭 Manufacturing Module - Quick Start Guide

## ✅ What's Ready NOW

- ✅ All database tables created
- ✅ Admin interface fully configured
- ✅ Auto-cost calculations working
- ✅ Inventory sync ready
- ✅ Analytics tracking ready
- ✅ Local materials % tracking
- ✅ Job/worker tracking

## 🚀 Quick Test Workflow (5 Minutes)

### Step 1: Create a Product (If You Don't Have One)

```bash
1. Go to /admin/products/product/
2. Click "Add Product"
3. Create a simple product:
   - Name: "Woven Basket"
   - Vendor: Select a vendor
   - Price: $20
   - Track inventory: ✓
   - Stock: 0
4. Save
```

### Step 2: Create a Bill of Materials (Recipe)

```bash
1. Go to /admin/manufacturing/billofmaterials/
2. Click "Add Bill of Materials"
3. Fill in:
   - Product: "Woven Basket"
   - Vendor: Same vendor
   - Batch size: 1
   - Production time: 3 (hours)
   - Labor cost per unit: 5.00
   - Overhead cost per unit: 2.00
   - Markup percentage: 50
4. Save and continue editing
```

### Step 3: Add Materials to BOM

```bash
Still in the BOM edit page:

1. Scroll to "BOM Items" section
2. Click "Add another BOM Item"
3. Select a raw material (you need approved materials first!)
4. Enter quantity: 0.5
5. Unit: kg
6. Notes: "High quality only"
7. Add 2-3 more materials
8. Click "Save"

✅ System automatically calculates:
   - Total material cost
   - Total cost per unit
   - Suggested selling price
```

### Step 4: Create a Manufacturing Order

```bash
1. Go to /admin/manufacturing/manufacturingorder/
2. Click "Add Manufacturing Order"
3. Fill in:
   - Vendor: Same vendor
   - Product: "Woven Basket"
   - BOM: Select the BOM you created
   - Quantity to produce: 10
   - Status: READY
   - Priority: NORMAL
   - Scheduled date: Today
4. Save

✅ System generates MO number: MO-[VENDOR]-[TIMESTAMP]
✅ Calculates estimated cost automatically
✅ Calculates local materials percentage
```

### Step 5: Start Production

```bash
Option A: Via Admin
1. In Manufacturing Orders list
2. Select your order
3. Actions → "Start selected orders"
4. Click "Go"
✅ Status changes to IN_PROGRESS
✅ Started_at timestamp recorded

Option B: Direct Edit
1. Click on the order
2. Change status to: IN_PROGRESS
3. Started at: Auto-filled with now
4. Save
```

### Step 6: Complete Production

```bash
1. Open your manufacturing order
2. Set:
   - Quantity produced: 10
   - Quantity approved: 9
   - Quantity rejected: 1
   - Status: COMPLETED
3. Save

✅ Product inventory updated: +9 units
✅ Completed_at timestamp recorded
✅ Ready to sell on marketplace!
```

## 📊 View Analytics

### Option 1: Admin Analytics

```bash
1. Go to /admin/manufacturing/manufacturinganalytics/
2. See monthly summaries for each vendor
```

### Option 2: Direct Query

```bash
python manage.py shell
```

```python
from manufacturing.models import ManufacturingOrder, BillOfMaterials
from django.db.models import Sum, Count, Avg

# Total production
total = ManufacturingOrder.objects.filter(
    status='COMPLETED'
).aggregate(
    units=Sum('quantity_produced'),
    orders=Count('id')
)
print(f"Total: {total['units']} units from {total['orders']} orders")

# By vendor
from accounts.models import User
vendor = User.objects.filter(user_type='VENDOR').first()

vendor_production = ManufacturingOrder.objects.filter(
    vendor=vendor,
    status='COMPLETED'
).aggregate(
    units=Sum('quantity_produced'),
    cost=Sum('actual_cost')
)
print(f"Vendor produced: {vendor_production['units']} units")
print(f"Total cost: ${vendor_production['cost']}")

# Local materials average
local_avg = ManufacturingOrder.objects.aggregate(
    avg=Avg('local_materials_percentage')
)
print(f"Average local materials: {local_avg['avg']}%")

exit()
```

## 🎯 Complete Example Workflow

### Example: Basket Maker

**Product: Traditional Woven Basket**

#### Step 1: Create BOM
```
Product: Traditional Woven Basket
Batch size: 1 basket
Production time: 3 hours

Materials:
1. Reed grass: 0.5 kg @ $10/kg = $5.00
2. Natural dye: 0.05 L @ $50/L = $2.50
3. Cotton thread: 20 m @ $0.10/m = $2.00

Labor: $5.00
Overhead: $1.50

Total Cost: $16.00
Markup: 50%
Suggested Price: $24.00
```

#### Step 2: Create Manufacturing Order
```
Product: Traditional Woven Basket
Quantity: 20 baskets
Scheduled: Tomorrow
Priority: NORMAL

Estimated Cost: $320 (20 × $16)
```

#### Step 3: Production
```
Status: READY
↓
[Start Production]
↓
Status: IN_PROGRESS
↓
[Complete Production]
↓
Status: COMPLETED

Produced: 20 baskets
Approved: 18 baskets (90%)
Rejected: 2 baskets (quality issues)

✅ Inventory: +18 baskets
✅ Ready to sell!
```

#### Step 4: Track Impact
```
Local materials: 66% (2 of 3 materials local)
Jobs: 2 workers, 15 hours
Community contribution: $3.20 (1% of $320)
```

## 🔗 Key Admin URLs

```
BOMs:
/admin/manufacturing/billofmaterials/

Manufacturing Orders:
/admin/manufacturing/manufacturingorder/

Quality Checks:
/admin/manufacturing/qualitycheck/

Workers:
/admin/manufacturing/productionworker/

Analytics:
/admin/manufacturing/manufacturinganalytics/
```

## 💡 Tips & Tricks

### Auto-Calculate Costs

```bash
1. Go to BOMs list
2. Select one or more BOMs
3. Actions → "Recalculate costs for selected BOMs"
4. Click "Go"

✅ All costs updated based on current material prices
```

### Bulk Start Orders

```bash
1. Go to Manufacturing Orders
2. Filter: Status = READY
3. Select multiple orders
4. Actions → "Start selected orders"
5. Click "Go"

✅ All selected orders start at once
```

### Bulk Complete Orders

```bash
1. Manufacturing Orders
2. Filter: Status = IN_PROGRESS
3. Select orders ready to complete
4. Actions → "Complete selected orders"
5. Click "Go"

✅ All selected orders completed
✅ Inventory updated for all
```

### Calculate Local %

```bash
1. Select manufacturing orders
2. Actions → "Calculate local materials %"
3. Click "Go"

✅ Shows % of locally sourced materials
```

## 📋 Checklist for New Product

- [ ] Product created with vendor
- [ ] Product has track_inventory = True
- [ ] BOM created for product
- [ ] At least 1 material added to BOM
- [ ] Costs calculated (auto)
- [ ] Manufacturing order created
- [ ] Order started
- [ ] Order completed
- [ ] Inventory updated (auto)
- [ ] Product available on marketplace

## 🎨 What's Still Needed (Frontend)

**Templates to Build:**
1. `manufacturing/dashboard.html` - Main dashboard
2. `manufacturing/bom_list.html` - List all BOMs
3. `manufacturing/bom_create.html` - Create BOM
4. `manufacturing/bom_detail.html` - View/Edit BOM
5. `manufacturing/orders_list.html` - List orders
6. `manufacturing/order_create.html` - Create order
7. `manufacturing/order_detail.html` - Order details
8. `manufacturing/materials.html` - Materials overview
9. `manufacturing/analytics.html` - Impact report

**Estimated Time:** 2-3 days

## 🔍 Debugging

### Check if BOM costs are calculating:

```python
python manage.py shell

from manufacturing.models import BillOfMaterials

bom = BillOfMaterials.objects.first()
if bom:
    print(f"BOM: {bom.product.name}")
    print(f"Items: {bom.items.count()}")
    print(f"Material cost: ${bom.total_material_cost}")
    print(f"Total cost: ${bom.total_cost_per_unit}")
    print(f"Suggested price: ${bom.suggested_selling_price}")
    
    # Recalculate
    bom.calculate_costs()
    print("\n✅ Costs recalculated")
    print(f"New total cost: ${bom.total_cost_per_unit}")

exit()
```

### Check if inventory updates work:

```python
python manage.py shell

from manufacturing.models import ManufacturingOrder
from products.models import Product

# Get a completed order
mo = ManufacturingOrder.objects.filter(status='COMPLETED').first()
if mo:
    print(f"Order: {mo.mo_number}")
    print(f"Product: {mo.product.name}")
    print(f"Approved: {mo.quantity_approved}")
    print(f"Current stock: {mo.product.stock_quantity}")
    
    # Check if stock was updated
    print("\n✅ Stock should include manufactured units")

exit()
```

## 🎊 Success Indicators

**You know it's working when:**

1. ✅ BOM shows calculated costs
2. ✅ Manufacturing orders have MO numbers
3. ✅ Completed orders update product stock
4. ✅ Local materials % is calculated
5. ✅ Analytics show production data
6. ✅ Workers are tracked
7. ✅ Community contribution is calculated

## 📞 Support

**For Issues:**
1. Check Django admin logs
2. Verify all relationships are set
3. Ensure raw materials are approved
4. Check product has track_inventory enabled

**Common Issues:**

**BOM costs not calculating:**
- Ensure materials have unit prices
- Check batch_size is not zero
- Click "Recalculate costs" action

**Inventory not updating:**
- Check product.track_inventory = True
- Verify quantity_approved is set
- Ensure order status is COMPLETED

**Local % showing 0:**
- Click "Calculate local materials %" action
- Check BOM has materials
- Verify materials have is_locally_sourced set

---

## 🏆 You're Ready!

Your manufacturing module is **fully operational**. You can:
- ✅ Create product recipes (BOMs)
- ✅ Track production
- ✅ Calculate costs automatically
- ✅ Update inventory automatically
- ✅ Track jobs created
- ✅ Measure community impact
- ✅ Generate analytics

**The system is live and ready for vendors!**

---

**Status:** ✅ Fully Functional (Admin)  
**Next:** Build vendor-facing templates  
**Documentation:** `MANUFACTURING_MODULE_GUIDE.md`  
**Last Updated:** November 19, 2025

