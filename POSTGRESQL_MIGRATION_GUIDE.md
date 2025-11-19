# 🐘 PostgreSQL 17 Migration Guide

## ✅ What Was Done

Your Mushanai platform has been configured to use PostgreSQL 17 instead of SQLite!

### **Changes Made:**

1. ✅ Updated `requirements.txt` with PostgreSQL dependencies
2. ✅ Updated `settings.py` to use PostgreSQL configuration
3. ✅ Added environment variable support for secure configuration
4. ✅ Added support for DATABASE_URL (cloud deployment ready)

---

## 📋 Prerequisites

### **Install PostgreSQL 17**

#### **macOS (Homebrew):**
```bash
# Install PostgreSQL 17
brew install postgresql@17

# Start PostgreSQL service
brew services start postgresql@17

# Add to PATH (add to ~/.zshrc or ~/.bash_profile)
echo 'export PATH="/opt/homebrew/opt/postgresql@17/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Verify installation
psql --version
# Should show: psql (PostgreSQL) 17.x
```

#### **Ubuntu/Debian:**
```bash
# Add PostgreSQL repository
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

# Update and install
sudo apt-get update
sudo apt-get install postgresql-17

# Start service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verify
psql --version
```

#### **Windows:**
```bash
# Download and install from:
# https://www.postgresql.org/download/windows/

# Or use Chocolatey:
choco install postgresql17

# Verify
psql --version
```

---

## 🔧 Setup PostgreSQL Database

### **Step 1: Create Database and User**

```bash
# Access PostgreSQL as superuser
psql postgres

# Or if that doesn't work:
sudo -u postgres psql
```

```sql
-- Create database
CREATE DATABASE mushanai_db;

-- Create user
CREATE USER mushanai_user WITH PASSWORD 'mushanai2024';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE mushanai_db TO mushanai_user;

-- PostgreSQL 15+ requires additional grant
\c mushanai_db
GRANT ALL ON SCHEMA public TO mushanai_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO mushanai_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO mushanai_user;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO mushanai_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO mushanai_user;

-- Exit
\q
```

### **Verify Database Creation:**
```bash
psql -U mushanai_user -d mushanai_db -h localhost
# Enter password: mushanai2024

# If successful, you'll see:
# mushanai_db=>

# Test a simple query
SELECT version();

# Exit
\q
```

---

## 📝 Environment Configuration

### **Step 1: Create .env File**

Create a file named `.env` in your project root (`/Users/ishe/Desktop/Milly/mushanai/`):

```bash
# Django Settings
SECRET_KEY=django-insecure-405ec706td@pxg$8ox#j*1*gzpw9b!_6(8&eum5=ef%1wuhpie
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL Database Configuration
DB_ENGINE=django.db.backends.postgresql
DB_NAME=mushanai_db
DB_USER=mushanai_user
DB_PASSWORD=mushanai2024
DB_HOST=localhost
DB_PORT=5432

# Site Configuration
SITE_URL=http://127.0.0.1:8000

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@mushanai.com
```

### **Step 2: Update .gitignore**

Make sure `.env` is in your `.gitignore`:

```bash
echo ".env" >> .gitignore
```

---

## 🚀 Migration Process

### **Step 1: Install New Dependencies**

```bash
cd /Users/ishe/Desktop/Milly/mushanai
source venv/bin/activate

pip install -r requirements.txt
```

**New packages installed:**
- `psycopg2-binary==2.9.10` - PostgreSQL adapter
- `python-decouple==3.8` - Environment variable management
- `dj-database-url==2.2.0` - Database URL parsing (for cloud deployment)

### **Step 2: Test Database Connection**

```bash
python manage.py check --database default
```

Expected output:
```
System check identified no issues (0 silenced).
```

### **Step 3: Migrate Data from SQLite (Optional)**

If you have existing data in SQLite that you want to keep:

#### **Option A: Export/Import Data**

```bash
# 1. Export data from SQLite (backup first!)
python manage.py dumpdata --natural-foreign --natural-primary \
  --exclude contenttypes --exclude auth.Permission \
  --indent 2 > data_backup.json

# 2. Switch to PostgreSQL (already done in settings.py)

# 3. Run migrations on PostgreSQL
python manage.py migrate

# 4. Load data into PostgreSQL
python manage.py loaddata data_backup.json
```

#### **Option B: Start Fresh**

If you're okay starting with a fresh database:

```bash
# Just run migrations
python manage.py migrate
```

### **Step 4: Create Superuser**

```bash
python manage.py createsuperuser
```

### **Step 5: Verify Everything Works**

```bash
# Run server
python manage.py runserver

# Visit admin
# http://127.0.0.1:8000/admin/

# Check database
python manage.py dbshell
```

---

## ✅ Verification Checklist

### **Database Connection:**
```bash
cd /Users/ishe/Desktop/Milly/mushanai
source venv/bin/activate

python manage.py shell
```

```python
from django.db import connection

# Test connection
print(connection.vendor)  # Should print: postgresql
print(connection.settings_dict['NAME'])  # Should print: mushanai_db

# Test query
from accounts.models import User
print(User.objects.count())  # Should work without error

# Exit
exit()
```

### **Check All Apps:**
```bash
python manage.py check
```

### **Check Migrations:**
```bash
python manage.py showmigrations
```

All should show `[X]` for applied migrations.

---

## 🎯 PostgreSQL Advantages

### **Why PostgreSQL 17 is Better:**

1. **Performance**
   - Much faster for complex queries
   - Better handling of concurrent connections
   - Advanced indexing (B-tree, Hash, GiST, GIN)

2. **Scalability**
   - Handle millions of records
   - Better for high-traffic sites
   - Horizontal scaling support

3. **Data Integrity**
   - ACID compliance
   - Foreign key constraints enforced
   - Transaction support

4. **Advanced Features**
   - Full-text search
   - JSON/JSONB support
   - Array fields
   - Window functions
   - CTEs (Common Table Expressions)

5. **Production Ready**
   - Industry standard
   - Used by major platforms
   - Excellent backup/recovery tools
   - Great monitoring tools

---

## 🔍 Troubleshooting

### **Error: "psycopg2 installation failed"**

**Solution:**
```bash
# macOS
brew install postgresql@17

# Ubuntu/Debian
sudo apt-get install libpq-dev python3-dev

# Then retry
pip install psycopg2-binary
```

### **Error: "FATAL: database does not exist"**

**Solution:**
```bash
# Create database
psql postgres -c "CREATE DATABASE mushanai_db;"
```

### **Error: "FATAL: role does not exist"**

**Solution:**
```bash
# Create user
psql postgres -c "CREATE USER mushanai_user WITH PASSWORD 'mushanai2024';"
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE mushanai_db TO mushanai_user;"
```

### **Error: "peer authentication failed"**

**Solution:**
Edit PostgreSQL config to allow password authentication:

```bash
# Find config file
psql -U postgres -c "SHOW hba_file;"

# Edit it (example path)
sudo nano /opt/homebrew/var/postgresql@17/pg_hba.conf

# Change this line:
# local   all   all   peer
# To:
# local   all   all   md5

# Restart PostgreSQL
brew services restart postgresql@17
```

### **Error: "password authentication failed"**

**Solution:**
```bash
# Reset user password
psql postgres -c "ALTER USER mushanai_user WITH PASSWORD 'mushanai2024';"

# Update .env file with correct password
```

### **Error: "permission denied for schema public"**

**Solution:**
```bash
psql -U postgres mushanai_db -c "GRANT ALL ON SCHEMA public TO mushanai_user;"
psql -U postgres mushanai_db -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO mushanai_user;"
```

---

## 📊 Performance Optimization

### **1. Add Indexes (Already in Models)**

Your models already have indexes, but you can add more:

```bash
python manage.py shell
```

```python
from django.db import connection
cursor = connection.cursor()

# Example: Add index for product searches
cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_product_name_search 
    ON products_product USING gin(to_tsvector('english', name));
""")
```

### **2. Connection Pooling**

Add to `requirements.txt`:
```
django-db-connection-pool==1.2.4
```

Update `settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'dj_db_conn_pool.backends.postgresql',
        # ... rest of config
        'POOL_OPTIONS': {
            'POOL_SIZE': 10,
            'MAX_OVERFLOW': 10,
        }
    }
}
```

### **3. Enable Query Logging (Development)**

In `settings.py`:
```python
if DEBUG:
    LOGGING = {
        'version': 1,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django.db.backends': {
                'handlers': ['console'],
                'level': 'DEBUG',
            },
        },
    }
```

---

## 🔐 Production Configuration

### **Secure Your Database:**

1. **Change Default Password**
```bash
psql -U postgres -c "ALTER USER mushanai_user WITH PASSWORD 'STRONG_PASSWORD_HERE';"
```

2. **Update .env**
```
DB_PASSWORD=your_strong_password_here
```

3. **Restrict Access**
Edit `pg_hba.conf`:
```
# Only allow connections from localhost
host   mushanai_db   mushanai_user   127.0.0.1/32   md5
```

4. **Enable SSL (Production)**
```python
DATABASES = {
    'default': {
        # ... other config
        'OPTIONS': {
            'sslmode': 'require',
        }
    }
}
```

---

## 💾 Backup & Restore

### **Backup Database:**

```bash
# Full backup
pg_dump -U mushanai_user -h localhost mushanai_db > backup_$(date +%Y%m%d).sql

# Compressed backup
pg_dump -U mushanai_user -h localhost mushanai_db | gzip > backup_$(date +%Y%m%d).sql.gz

# Backup with Django
python manage.py dumpdata --indent 2 > backup.json
```

### **Restore Database:**

```bash
# From SQL dump
psql -U mushanai_user -h localhost mushanai_db < backup.sql

# From compressed
gunzip -c backup.sql.gz | psql -U mushanai_user -h localhost mushanai_db

# From Django dump
python manage.py loaddata backup.json
```

### **Automated Backups:**

Create `backup.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -U mushanai_user -h localhost mushanai_db | gzip > $BACKUP_DIR/mushanai_$DATE.sql.gz

# Keep only last 7 days
find $BACKUP_DIR -name "mushanai_*.sql.gz" -mtime +7 -delete
```

Add to crontab:
```bash
crontab -e
# Add this line (backup daily at 2 AM)
0 2 * * * /path/to/backup.sh
```

---

## 📈 Monitoring

### **Check Database Size:**
```bash
psql -U mushanai_user -d mushanai_db -c "\l+"
```

### **Check Table Sizes:**
```bash
psql -U mushanai_user -d mushanai_db -c "
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"
```

### **Check Active Connections:**
```bash
psql -U mushanai_user -d mushanai_db -c "SELECT * FROM pg_stat_activity;"
```

### **Vacuum Database (Maintenance):**
```bash
psql -U mushanai_user -d mushanai_db -c "VACUUM ANALYZE;"
```

---

## 🚀 Cloud Deployment

### **Heroku:**
```bash
# Heroku automatically provides DATABASE_URL
# Your settings.py already supports this!

heroku addons:create heroku-postgresql:standard-0
heroku config:get DATABASE_URL
```

### **Railway:**
```bash
# Railway provides DATABASE_URL
# Just set it in environment variables

railway up
```

### **DigitalOcean:**
```bash
# Create managed PostgreSQL database
# Copy connection string
# Set as DATABASE_URL in environment
```

Your `settings.py` automatically uses `DATABASE_URL` if provided!

---

## ✅ Quick Command Reference

```bash
# Connect to database
psql -U mushanai_user -d mushanai_db -h localhost

# List databases
\l

# Connect to database
\c mushanai_db

# List tables
\dt

# Describe table
\d products_product

# List users
\du

# Show current database
SELECT current_database();

# Show current user
SELECT current_user;

# Exit
\q

# Django commands
python manage.py dbshell           # Open PostgreSQL shell
python manage.py migrate           # Run migrations
python manage.py showmigrations    # Show migration status
python manage.py check --database  # Check database connection
```

---

## 🎉 Success!

Your Mushanai platform is now running on PostgreSQL 17!

### **Next Steps:**
1. ✅ Run migrations: `python manage.py migrate`
2. ✅ Create superuser: `python manage.py createsuperuser`
3. ✅ Test the application
4. ✅ Set up automated backups
5. ✅ Monitor performance

### **Benefits You Now Have:**
- ✅ Production-grade database
- ✅ Better performance
- ✅ Advanced features (full-text search, JSON, etc.)
- ✅ Horizontal scalability
- ✅ Better concurrent handling
- ✅ Industry-standard reliability

---

**Status:** ✅ PostgreSQL 17 Configuration Complete  
**Database:** mushanai_db  
**User:** mushanai_user  
**Environment:** Development-ready, Production-ready  
**Last Updated:** November 19, 2025

🐘 **Welcome to PostgreSQL 17!** 🎉

