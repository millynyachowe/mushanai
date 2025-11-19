# 🐘 PostgreSQL 17 - Quick Start Guide

## ✅ What's Been Done

Your Mushanai platform has been configured to use PostgreSQL 17!

### **Changes Made:**
- ✅ Updated `requirements.txt` with PostgreSQL packages
- ✅ Updated `settings.py` to use PostgreSQL
- ✅ Created `.env` file for configuration
- ✅ Installed packages: `psycopg2-binary`, `python-decouple`, `dj-database-url`
- ✅ Created setup script `setup_postgresql.sh`

---

## 🚀 Quick Setup (5 Minutes)

### **Step 1: Install PostgreSQL 17**

#### **macOS:**
```bash
# Install
brew install postgresql@17

# Start service
brew services start postgresql@17

# Verify
psql --version
```

#### **Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install postgresql-17

sudo systemctl start postgresql
sudo systemctl enable postgresql

psql --version
```

### **Step 2: Create Database**

Run the automated setup script:

```bash
cd /Users/ishe/Desktop/Milly/mushanai
./setup_postgresql.sh
```

**Or manually:**

```bash
# Access PostgreSQL
psql postgres

# Run these commands:
CREATE DATABASE mushanai_db;
CREATE USER mushanai_user WITH PASSWORD 'mushanai2024';
GRANT ALL PRIVILEGES ON DATABASE mushanai_db TO mushanai_user;

\c mushanai_db
GRANT ALL ON SCHEMA public TO mushanai_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO mushanai_user;

\q
```

### **Step 3: Run Migrations**

```bash
cd /Users/ishe/Desktop/Milly/mushanai
source venv/bin/activate

# Test connection
python manage.py check

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start server
python manage.py runserver
```

---

## 🔍 Verify Installation

```bash
cd /Users/ishe/Desktop/Milly/mushanai
source venv/bin/activate

python manage.py shell
```

```python
from django.db import connection

# Test connection
print(connection.vendor)  # Should print: postgresql

# Test query
from accounts.models import User
print(f"Users: {User.objects.count()}")

exit()
```

---

## 📝 Configuration Files

### **.env File** (Already created)
```
DB_NAME=mushanai_db
DB_USER=mushanai_user
DB_PASSWORD=mushanai2024
DB_HOST=localhost
DB_PORT=5432
```

### **Database Credentials:**
- **Database:** mushanai_db
- **User:** mushanai_user
- **Password:** mushanai2024
- **Host:** localhost
- **Port:** 5432

---

## 🐛 Troubleshooting

### **Error: "PostgreSQL is not installed"**

**macOS:**
```bash
brew install postgresql@17
brew services start postgresql@17
```

**Ubuntu:**
```bash
sudo apt-get install postgresql-17
sudo systemctl start postgresql
```

### **Error: "Connection refused"**

PostgreSQL service is not running:

```bash
# macOS
brew services start postgresql@17

# Ubuntu
sudo systemctl start postgresql

# Check status
pg_isready
```

### **Error: "peer authentication failed"**

Edit PostgreSQL config:

```bash
# Find config
psql -U postgres -c "SHOW hba_file;"

# Edit (example path)
sudo nano /opt/homebrew/var/postgresql@17/pg_hba.conf

# Change:
# local   all   all   peer
# To:
# local   all   all   md5

# Restart
brew services restart postgresql@17
```

### **Error: "database does not exist"**

```bash
psql postgres -c "CREATE DATABASE mushanai_db;"
```

### **Error: "role does not exist"**

```bash
psql postgres -c "CREATE USER mushanai_user WITH PASSWORD 'mushanai2024';"
```

---

## 💾 Data Migration

### **From SQLite (If you have existing data):**

```bash
# 1. Backup SQLite data
python manage.py dumpdata --natural-foreign --natural-primary \
  --exclude contenttypes --exclude auth.Permission \
  --indent 2 > data_backup.json

# 2. Switch to PostgreSQL (already done)

# 3. Run migrations
python manage.py migrate

# 4. Load data
python manage.py loaddata data_backup.json
```

---

## 📊 Useful Commands

```bash
# Connect to database
psql -U mushanai_user -d mushanai_db -h localhost

# Inside psql:
\l              # List databases
\dt             # List tables
\d table_name   # Describe table
\q              # Quit

# Django commands
python manage.py dbshell           # Open PostgreSQL shell
python manage.py migrate           # Run migrations
python manage.py showmigrations    # Show status
```

---

## 🎯 Next Steps

1. ✅ Install PostgreSQL 17
2. ✅ Run `./setup_postgresql.sh`
3. ✅ Run `python manage.py migrate`
4. ✅ Create superuser
5. ✅ Test application

---

## 📚 Full Documentation

See `POSTGRESQL_MIGRATION_GUIDE.md` for:
- Detailed setup instructions
- Performance optimization
- Backup & restore
- Security best practices
- Production deployment
- Monitoring & maintenance

---

**Status:** ✅ Configuration Complete  
**Database:** PostgreSQL 17  
**Next:** Install PostgreSQL and run migrations  
**Support:** See POSTGRESQL_MIGRATION_GUIDE.md  

🐘 **Welcome to PostgreSQL!** 🎉

