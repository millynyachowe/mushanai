# Vendor Expenses Module - Complete Guide

## 🎯 Overview

The Expenses Module is a comprehensive expense tracking and management system for vendors. It allows vendors to record, categorize, filter, edit, and export all their business expenses.

## ✨ Features

### 1. **Expense Tracking**
- Record business expenses with detailed information
- 9 expense categories:
  - Supplies & Materials
  - Shipping & Delivery
  - Marketing & Advertising
  - Utilities
  - Rent
  - Salaries & Wages
  - Equipment
  - Professional Services
  - Other

### 2. **Expense Management**
- ✅ **Create** new expenses
- ✅ **View** expense details
- ✅ **Edit** existing expenses
- ✅ **Delete** expenses (with confirmation)
- ✅ **Upload** receipt images
- ✅ **Download** receipt images

### 3. **Advanced Filtering**
- **Search** by description, notes, or reference number
- **Filter by category**
- **Filter by date range** (start date - end date)
- **Real-time filtering** with instant results

### 4. **Financial Insights**
- **Total expenses** calculation (filtered)
- **Category breakdown** (top 3 categories)
- **Expense count** per category
- **Visual summary cards**

### 5. **Export Functionality**
- **CSV Export** with all expense details
- **Filtered exports** (exports only filtered data)
- Includes: Date, Description, Category, Amount, Payment Method, Reference, Notes, Company

### 6. **Multi-Company Support**
- Track expenses per company
- Filter and report by company
- Optional company assignment

### 7. **Receipt Management**
- Upload receipt images (JPG, PNG, etc.)
- View receipt images inline
- Download receipt images
- Full-size image viewer

## 🔗 URLs and Access

### Main URLs
```
/vendor/accounting/expenses/              # List all expenses
/vendor/accounting/expenses/create/       # Create new expense
/vendor/accounting/expenses/<id>/         # View expense details
/vendor/accounting/expenses/<id>/edit/    # Edit expense
/vendor/accounting/expenses/<id>/delete/  # Delete expense
/vendor/accounting/expenses/export/       # Export to CSV
```

### Quick Access
- From Dashboard: **Accounting** → **Expenses**
- From Accounting Dashboard: **View Expenses** button
- Direct URL: `http://127.0.0.1:8000/vendor/accounting/expenses/`

## 📊 How to Use

### Recording an Expense

1. Navigate to **Expenses** section
2. Click **Record Expense** button
3. Fill in the form:
   - **Description** (required) - e.g., "Office Supplies"
   - **Category** (required) - Select from dropdown
   - **Amount** (required) - Dollar amount
   - **Expense Date** (required) - When expense occurred
   - **Payment Method** (optional) - How you paid
   - **Reference Number** (optional) - Invoice #, transaction ID, etc.
   - **Receipt Image** (optional) - Upload photo/scan
   - **Notes** (optional) - Additional details
   - **Company** (optional) - If you have multiple companies
4. Click **Record Expense**

### Viewing Expenses

1. Go to **Expenses** list
2. See summary cards at top:
   - Total expenses
   - Top 3 category breakdowns
3. View table with all expenses
4. Click on any row action button:
   - 👁️ **View** - See full details
   - ✏️ **Edit** - Modify expense
   - 🗑️ **Delete** - Remove expense

### Filtering Expenses

1. Use the **Filters** card
2. Enter search term, select category, or choose date range
3. Click **Filter** button
4. See filtered results with updated totals
5. Click **Clear** to reset filters

### Exporting Data

1. Apply filters (if desired)
2. Click **Export CSV** button
3. CSV file downloads with:
   - Only filtered expenses (if filters applied)
   - All fields included
   - Ready for Excel/Google Sheets

### Editing an Expense

1. Find expense in list
2. Click **Edit** button (pencil icon)
3. Modify any fields
4. Click **Update Expense**
5. See success message

### Deleting an Expense

1. Find expense in list
2. Click **Delete** button (trash icon)
3. Review expense details
4. Click **Yes, Delete This Expense**
5. Expense removed permanently

## 💡 Use Cases

### Monthly Expense Review
```
1. Set date range to current month
2. Review all expenses
3. Export to CSV
4. Share with accountant
```

### Category Analysis
```
1. Filter by specific category (e.g., "Marketing")
2. View total spent
3. Identify cost-saving opportunities
```

### Tax Preparation
```
1. Set date range to tax year
2. Export all expenses
3. Organize by category
4. Submit to tax preparer
```

### Multi-Company Accounting
```
1. Filter by company
2. View company-specific expenses
3. Generate per-company reports
```

## 🎨 UI Features

### Summary Cards
- **Red card** - Total expenses with count
- **3 category cards** - Top spending categories

### Expense Table
- **Sortable columns**
- **Badge indicators** for categories
- **Company icons** for multi-company expenses
- **Action buttons** in each row
- **Responsive design** - works on mobile

### Filters Card
- **Search box** - Find expenses by text
- **Category dropdown** - Filter by type
- **Date pickers** - Select date range
- **Filter button** - Apply filters
- **Clear button** - Reset all filters

### Detail View
- **Large expense card** with all information
- **Receipt image preview** on right side
- **Quick actions** for common tasks
- **Edit and delete** buttons prominent

## 📈 Integration

### Accounting Dashboard
- Expenses feed into **"Expenses This Month"** metric
- Used in **profit calculation** (Revenue - Expenses)
- Shown in **recent expenses** table

### Financial Reports
- All expenses included in totals
- Category breakdowns available
- Export for external analysis

### Multi-Company
- Expenses tracked per company
- Can filter by company
- Separate company totals

## 🔐 Security

- ✅ Vendor-only access (user type check)
- ✅ Users can only see their own expenses
- ✅ CSRF protection on all forms
- ✅ File upload validation (images only)
- ✅ SQL injection protection (Django ORM)

## 💾 Database Fields

### VendorExpense Model
```python
- vendor (ForeignKey) - Who created the expense
- company (ForeignKey) - Which company (optional)
- description (CharField) - What was purchased
- category (CharField) - Expense type
- amount (DecimalField) - Cost
- expense_date (DateField) - When it occurred
- payment_method (CharField) - How paid
- reference_number (CharField) - Invoice/transaction ID
- receipt_image (ImageField) - Receipt photo
- notes (TextField) - Additional info
- created_at (DateTimeField) - When recorded
- updated_at (DateTimeField) - Last modified
```

## 🚀 Quick Start

### For Vendors:

1. **Login** to your vendor account
2. Go to **Dashboard** → **Accounting** → **Expenses**
3. Click **Record Expense**
4. Fill in expense details
5. Upload receipt (optional)
6. Save

### Your First Expense:
```
Description: Office Supplies
Category: Supplies & Materials
Amount: $45.99
Date: Today
Payment Method: Cash
Notes: Pens, paper, and folders
```

## 📱 Mobile Usage

The expenses module is **fully responsive**:
- Cards stack on mobile
- Table scrolls horizontally
- Filters adapt to small screens
- Touch-friendly buttons
- Mobile camera for receipt upload

## 🔄 Workflow Examples

### Daily Recording
```
1. Make purchase → 2. Take photo of receipt → 
3. Open expenses → 4. Record expense → 
5. Upload receipt → 6. Done!
```

### Weekly Review
```
1. Open expenses → 2. Filter to last 7 days → 
3. Review all expenses → 4. Verify amounts → 
5. Add missing notes
```

### Monthly Export
```
1. Set date range to month → 2. Apply filter → 
3. Review totals → 4. Export CSV → 
5. Email to accountant
```

## 🎯 Best Practices

### ✅ DO:
- Record expenses promptly
- Upload receipt images
- Use detailed descriptions
- Select accurate categories
- Add reference numbers
- Include relevant notes

### ❌ DON'T:
- Wait to record expenses
- Forget receipt images
- Use vague descriptions
- Mix expense categories
- Leave reference numbers blank

## 📞 Tips & Tricks

### Tip 1: Recurring Expenses
For regular expenses (rent, utilities):
- Create one expense
- Add detailed notes
- Use consistent naming
- Easy to find in search

### Tip 2: Receipt Photos
- Take photos immediately after purchase
- Ensure receipt is clear and readable
- Include entire receipt in frame
- Upload while creating expense

### Tip 3: Tax Time
- Use categories that match tax forms
- Add tax-relevant notes
- Export at year-end
- Keep original receipts

### Tip 4: Search
- Search works across:
  - Description
  - Notes
  - Reference numbers
- Use partial matches
- Try different keywords

## 🎊 Success Metrics

Your vendors can now:
- ✅ Track **100%** of business expenses
- ✅ Filter and search **instantly**
- ✅ Export to **CSV/Excel**
- ✅ Upload and store **receipt images**
- ✅ Edit/delete as needed
- ✅ View **category breakdowns**
- ✅ Manage **multiple companies**

## 📚 Related Documentation

- **VENDOR_SYSTEM_GUIDE.md** - Full vendor system overview
- **VENDOR_QUICK_REFERENCE.md** - Quick URL reference
- **MIGRATION_INSTRUCTIONS.md** - Setup instructions

---

**Module Status**: ✅ Production Ready  
**Last Updated**: November 19, 2025  
**Version**: 2.0 (Enhanced)

The expenses module is a complete, professional-grade expense tracking system ready for immediate use!

