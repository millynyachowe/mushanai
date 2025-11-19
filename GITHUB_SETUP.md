# 🚀 GitHub Setup Guide

## ✅ Git Repository Initialized

Your Mushanai platform has been committed to git:

```
✅ 250 files committed
✅ Initial commit: "Mushanai Platform with PostgreSQL 17, Suppliers, Manufacturing, and Social Media modules"
✅ .env file protected (in .gitignore)
✅ Sensitive data excluded
```

---

## 🔐 GitHub Authentication (Required)

GitHub no longer accepts passwords for git operations. You need a **Personal Access Token (PAT)**.

### **Step 1: Create Personal Access Token**

1. Go to: https://github.com/settings/tokens
2. Click: **"Generate new token"** → **"Generate new token (classic)"**
3. Name it: `Mushanai Platform`
4. Select scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
5. Set expiration: **No expiration** or **90 days**
6. Click: **"Generate token"**
7. **⚠️ COPY THE TOKEN** - You won't see it again!

**Example token:** `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

## 📤 Push to GitHub

### **Option 1: Create New Repository on GitHub**

1. Go to: https://github.com/new
2. Repository name: `mushanai`
3. Description: "Mushanai - Zimbabwean E-commerce Platform"
4. **Private** (recommended for now)
5. **DO NOT** initialize with README (you already have one)
6. Click: **"Create repository"**

### **Option 2: Use Existing Repository**

If you already have a repository, skip to Step 2.

---

## 🔗 Connect and Push

### **Step 2: Add Remote**

```bash
cd /Users/ishe/Desktop/Milly/mushanai

# Replace USERNAME with your GitHub username (millynyachowe)
git remote add origin https://github.com/millynyachowe/mushanai.git

# Verify
git remote -v
```

### **Step 3: Push to GitHub**

```bash
# Push to main branch
git branch -M main
git push -u origin main
```

**When prompted for credentials:**
```
Username: millynyachowe
Password: [PASTE YOUR PERSONAL ACCESS TOKEN HERE]
```

**⚠️ DO NOT use your GitHub password - use the PAT token!**

---

## 🎯 Quick Commands

### **Complete Setup (All-in-One):**

```bash
cd /Users/ishe/Desktop/Milly/mushanai

# Add remote (replace with your actual repo URL)
git remote add origin https://github.com/millynyachowe/mushanai.git

# Set main branch
git branch -M main

# Push to GitHub
git push -u origin main
```

**When prompted:**
- Username: `millynyachowe`
- Password: `[Your PAT token]`

---

## 💡 Save Credentials (Optional)

To avoid entering token every time:

```bash
# Store credentials for 1 hour
git config --global credential.helper cache

# Store credentials permanently (macOS)
git config --global credential.helper osxkeychain

# Or for Linux
git config --global credential.helper store
```

---

## 🔒 What's Protected

Your `.gitignore` file ensures these are **NOT** committed:

```
✅ .env (database passwords, secrets)
✅ db.sqlite3 (old database)
✅ __pycache__/ (Python cache)
✅ *.pyc (compiled files)
✅ /media/ (uploaded files)
✅ /staticfiles/ (collected static files)
✅ venv/ (virtual environment)
```

**Safe to commit:**
- All source code
- Templates
- Documentation
- requirements.txt
- ENV_EXAMPLE.txt (template without secrets)
- setup scripts

---

## 📝 Repository Structure

Your repository includes:

```
mushanai/
├── accounts/           # User authentication
├── customers/          # Customer portal
├── vendors/            # Vendor management
├── suppliers/          # Raw materials suppliers
├── manufacturing/      # Production management
├── social_media/       # Facebook/Instagram integration
├── products/           # Product catalog
├── orders/            # Order management
├── payments/          # Payment processing
├── logistics/         # Delivery management
├── loyalty/           # Loyalty programs
├── projects/          # Community projects
├── ministries/        # Ministry oversight
├── store/             # Store frontend
├── templates/         # HTML templates
├── mushanaicore/      # Django settings
├── requirements.txt   # Dependencies
├── manage.py          # Django management
└── Documentation:
    ├── POSTGRESQL_MIGRATION_GUIDE.md
    ├── MANUFACTURING_MODULE_GUIDE.md
    ├── SUPPLIERS_MODULE_COMPLETE_GUIDE.md
    ├── SOCIAL_MEDIA_INTEGRATION_GUIDE.md
    └── 20+ other guides
```

---

## 🚀 After First Push

### **Future Updates:**

```bash
# Stage changes
git add .

# Commit
git commit -m "Your commit message"

# Push
git push
```

### **Check Status:**

```bash
git status          # See changed files
git log --oneline   # See commit history
git remote -v       # See remote URLs
```

### **Create Branches:**

```bash
# Create feature branch
git checkout -b feature/new-feature

# Work on feature...

# Push feature branch
git push -u origin feature/new-feature
```

---

## 🔄 Collaboration

### **Clone Repository (Others):**

```bash
git clone https://github.com/millynyachowe/mushanai.git
cd mushanai

# Install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copy environment file
cp ENV_EXAMPLE.txt .env
# Edit .env with your database credentials

# Setup database
./setup_postgresql.sh
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### **Pull Latest Changes:**

```bash
git pull origin main
```

---

## 📊 Repository Stats

**Initial Commit:**
```
Files: 250
Lines of Code: 35,216
Modules: 13
Documentation Pages: 25+
```

**Includes:**
- Complete Django application
- All modules (Vendors, Manufacturing, Suppliers, Social Media)
- PostgreSQL 17 configuration
- Comprehensive documentation
- Setup scripts
- Production-ready code

---

## 🔍 Verify Your Push

After pushing, verify at:
```
https://github.com/millynyachowe/mushanai
```

You should see:
- ✅ All files except .env
- ✅ README.md displayed
- ✅ 250+ files
- ✅ All documentation

---

## ⚠️ Important Reminders

1. **Never commit .env file** (it's in .gitignore)
2. **Use Personal Access Token**, not password
3. **Change default passwords** before production
4. **Review .gitignore** before committing sensitive files
5. **Create branches** for new features
6. **Write descriptive commit messages**
7. **Pull before push** when collaborating

---

## 🎯 Quick Reference

```bash
# Add files
git add .

# Commit
git commit -m "Description of changes"

# Push
git push

# Pull updates
git pull

# Check status
git status

# View history
git log --oneline

# Create branch
git checkout -b branch-name

# Switch branch
git checkout branch-name

# Merge branch
git merge branch-name
```

---

## 🆘 Troubleshooting

### **Error: "remote origin already exists"**

```bash
# Remove old remote
git remote remove origin

# Add new remote
git remote add origin https://github.com/millynyachowe/mushanai.git
```

### **Error: "Authentication failed"**

- Make sure you're using **Personal Access Token**, not password
- Generate new token at: https://github.com/settings/tokens
- Use token as password when prompted

### **Error: "refusing to merge unrelated histories"**

```bash
git pull origin main --allow-unrelated-histories
```

### **Error: "Permission denied"**

- Check you have access to the repository
- Verify your GitHub username
- Ensure token has `repo` scope

---

## 🎉 Success!

Once pushed, your Mushanai platform will be:
- ✅ Safely backed up on GitHub
- ✅ Version controlled
- ✅ Ready for collaboration
- ✅ Accessible from anywhere
- ✅ Protected from data loss

---

**Repository:** https://github.com/millynyachowe/mushanai  
**Your Username:** millynyachowe  
**Authentication:** Personal Access Token (PAT)  
**Status:** Ready to push!  

🚀 **Let's get your code on GitHub!** 🎊

