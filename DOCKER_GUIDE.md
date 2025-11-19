# 🐳 Docker Deployment Guide - Mushanai Platform

## 🎯 Overview

Your Mushanai platform is now fully containerized with Docker!

### **What's Included:**

1. **Docker Compose Setup** - Multi-container orchestration
2. **PostgreSQL 17** - Persistent database
3. **Redis** - Caching and sessions
4. **Nginx** - Reverse proxy and static file serving
5. **Gunicorn** - Production WSGI server
6. **Auto-migrations** - Database setup on startup
7. **Health checks** - Container monitoring

---

## 📋 Prerequisites

### **Install Docker & Docker Compose**

#### **macOS:**
```bash
# Install Docker Desktop
brew install --cask docker

# Start Docker Desktop
open -a Docker

# Verify installation
docker --version
docker-compose --version
```

#### **Ubuntu/Debian:**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify
docker --version
docker-compose --version
```

#### **Windows:**
```bash
# Download and install Docker Desktop from:
# https://www.docker.com/products/docker-desktop

# Verify in PowerShell
docker --version
docker-compose --version
```

---

## 🚀 Quick Start (2 Minutes)

### **Development Mode:**

```bash
cd /Users/ishe/Desktop/Milly/mushanai

# Build and start all services
docker-compose -f docker-compose.dev.yml up --build

# Access the application
# http://localhost:8000
```

### **Production Mode:**

```bash
cd /Users/ishe/Desktop/Milly/mushanai

# Copy environment file
cp .env.docker .env

# Build and start all services
docker-compose up --build -d

# Access the application
# http://localhost (via Nginx)
```

That's it! Your application is running in Docker! 🎉

---

## 🏗️ Architecture

### **Container Stack:**

```
┌─────────────────────────────────────────┐
│           Nginx (Port 80)               │
│     Reverse Proxy & Static Files        │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│      Django + Gunicorn (Port 8000)      │
│         Web Application                 │
└──┬──────────────────────────────────┬───┘
   │                                  │
┌──▼──────────────────┐  ┌───────────▼─────┐
│ PostgreSQL 17       │  │   Redis Cache   │
│   Database          │  │   & Sessions    │
└─────────────────────┘  └─────────────────┘
```

### **Volumes (Persistent Data):**

- `postgres_data` - Database files
- `redis_data` - Redis persistence
- `static_volume` - Static files (CSS, JS, images)
- `media_volume` - User uploads

---

## 📦 Services

### **1. PostgreSQL (`db`)**
- **Image:** postgres:17-alpine
- **Port:** 5432
- **Database:** mushanai_db
- **User:** mushanai_user
- **Health Check:** Automatic

### **2. Django + Gunicorn (`web`)**
- **Port:** 8000
- **Workers:** 3
- **Auto-migrations:** Yes
- **Static collection:** Automatic
- **Superuser:** Created automatically

### **3. Redis (`redis`)**
- **Port:** 6379
- **Purpose:** Caching & sessions
- **Persistence:** Yes

### **4. Nginx (`nginx`)**
- **Port:** 80 (HTTP), 443 (HTTPS)
- **Purpose:** Reverse proxy
- **Static files:** Served directly
- **Gzip:** Enabled

---

## 🎮 Docker Commands

### **Start Services:**

```bash
# Development (with hot reload)
docker-compose -f docker-compose.dev.yml up

# Production (detached mode)
docker-compose up -d

# Rebuild and start
docker-compose up --build

# Start specific service
docker-compose up db
```

### **Stop Services:**

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes data!)
docker-compose down -v

# Stop specific service
docker-compose stop web
```

### **View Logs:**

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web

# Last 100 lines
docker-compose logs --tail=100 web
```

### **Execute Commands:**

```bash
# Django shell
docker-compose exec web python manage.py shell

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Run migrations
docker-compose exec web python manage.py migrate

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Access container bash
docker-compose exec web bash

# PostgreSQL shell
docker-compose exec db psql -U mushanai_user -d mushanai_db
```

### **Manage Containers:**

```bash
# List running containers
docker-compose ps

# Restart service
docker-compose restart web

# View container resource usage
docker stats

# Remove stopped containers
docker-compose rm
```

---

## 🔧 Configuration

### **Environment Variables**

Edit `.env` file:

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,localhost

# Database
DB_NAME=mushanai_db
DB_USER=mushanai_user
DB_PASSWORD=strong_password_here
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
```

### **Update Configuration:**

```bash
# After changing .env
docker-compose down
docker-compose up -d
```

---

## 📊 Database Management

### **Backup Database:**

```bash
# Backup to file
docker-compose exec db pg_dump -U mushanai_user mushanai_db > backup.sql

# Backup compressed
docker-compose exec db pg_dump -U mushanai_user mushanai_db | gzip > backup.sql.gz
```

### **Restore Database:**

```bash
# From SQL file
docker-compose exec -T db psql -U mushanai_user mushanai_db < backup.sql

# From compressed
gunzip -c backup.sql.gz | docker-compose exec -T db psql -U mushanai_user mushanai_db
```

### **Access Database:**

```bash
# PostgreSQL shell
docker-compose exec db psql -U mushanai_user -d mushanai_db

# Run query
docker-compose exec db psql -U mushanai_user -d mushanai_db -c "SELECT COUNT(*) FROM products_product;"
```

---

## 🔍 Monitoring & Debugging

### **Health Checks:**

```bash
# Check container health
docker-compose ps

# Test database connection
docker-compose exec db pg_isready -U mushanai_user

# Test web server
curl http://localhost/health/
```

### **View Application Logs:**

```bash
# Real-time logs
docker-compose logs -f web

# Error logs only
docker-compose logs web | grep ERROR

# Last hour
docker-compose logs --since 1h web
```

### **Debug Inside Container:**

```bash
# Access container shell
docker-compose exec web bash

# Check Python packages
docker-compose exec web pip list

# Check Django settings
docker-compose exec web python manage.py diffsettings
```

### **Resource Usage:**

```bash
# Monitor in real-time
docker stats

# Check disk usage
docker system df

# Clean up unused resources
docker system prune -a
```

---

## 🚀 Production Deployment

### **1. Prepare Environment:**

```bash
# Generate strong SECRET_KEY
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Update .env
DEBUG=False
SECRET_KEY=your-generated-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_PASSWORD=very_strong_password
```

### **2. SSL/HTTPS Setup:**

Add to `docker-compose.yml`:

```yaml
nginx:
  volumes:
    - ./certbot/conf:/etc/letsencrypt
    - ./certbot/www:/var/www/certbot
  ports:
    - "443:443"
```

Get SSL certificate:

```bash
# Install certbot
docker-compose run --rm certbot certonly --webroot -w /var/www/certbot -d yourdomain.com
```

### **3. Deploy:**

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up --build -d

# Run migrations
docker-compose exec web python manage.py migrate

# Collect static
docker-compose exec web python manage.py collectstatic --noinput
```

---

## 🔐 Security Best Practices

### **1. Change Default Passwords:**

```bash
# Update .env
DB_PASSWORD=strong_random_password
SECRET_KEY=new_random_secret_key
```

### **2. Limit Exposed Ports:**

Remove port mappings in production:

```yaml
# Remove these in production
ports:
  - "5432:5432"  # PostgreSQL
  - "6379:6379"  # Redis
```

### **3. Use Secrets:**

For sensitive data:

```bash
# Docker secrets
echo "my_db_password" | docker secret create db_password -
```

### **4. Regular Updates:**

```bash
# Update images
docker-compose pull
docker-compose up -d

# Update application
git pull
docker-compose up --build -d
```

---

## 📈 Performance Optimization

### **1. Gunicorn Workers:**

Adjust in `docker-entrypoint.sh`:

```bash
# Formula: (2 x CPU cores) + 1
--workers 3  # For 1 CPU
--workers 5  # For 2 CPUs
--workers 9  # For 4 CPUs
```

### **2. PostgreSQL Tuning:**

Add to `docker-compose.yml`:

```yaml
db:
  command: postgres -c max_connections=200 -c shared_buffers=256MB
```

### **3. Redis as Cache:**

Already configured for Django caching!

### **4. Nginx Gzip:**

Already enabled in `nginx.conf`!

---

## 🐛 Troubleshooting

### **Error: "Port already in use"**

```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 PID

# Or change port in docker-compose.yml
ports:
  - "8001:8000"
```

### **Error: "Database connection refused"**

```bash
# Check database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

### **Error: "Static files not found"**

```bash
# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Check nginx volume
docker-compose exec nginx ls -la /app/staticfiles/
```

### **Error: "Cannot connect to Docker daemon"**

```bash
# Start Docker Desktop (macOS)
open -a Docker

# Start Docker service (Linux)
sudo systemctl start docker
```

### **Container keeps restarting:**

```bash
# Check logs
docker-compose logs web

# Common issues:
# 1. Missing migrations
# 2. Wrong database credentials
# 3. Syntax error in code
```

---

## 🔄 Development Workflow

### **Daily Development:**

```bash
# Start services
docker-compose -f docker-compose.dev.yml up

# Make code changes (auto-reload enabled)

# Run migrations after model changes
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Run tests
docker-compose exec web python manage.py test
```

### **Adding Dependencies:**

```bash
# Add to requirements.txt
echo "new-package==1.0.0" >> requirements.txt

# Rebuild container
docker-compose up --build
```

---

## 📊 Scaling

### **Horizontal Scaling:**

```bash
# Scale web service to 3 instances
docker-compose up --scale web=3

# Use load balancer (nginx already configured!)
```

### **With Docker Swarm:**

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml mushanai

# Scale service
docker service scale mushanai_web=5
```

---

## 🎯 Quick Reference

### **Essential Commands:**

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Logs
docker-compose logs -f web

# Shell
docker-compose exec web bash

# Django shell
docker-compose exec web python manage.py shell

# Migrations
docker-compose exec web python manage.py migrate

# Superuser
docker-compose exec web python manage.py createsuperuser

# Backup DB
docker-compose exec db pg_dump -U mushanai_user mushanai_db > backup.sql

# Restart
docker-compose restart web

# Rebuild
docker-compose up --build
```

---

## ✅ Verification

### **Check Everything is Running:**

```bash
# Check containers
docker-compose ps

# Expected output:
# mushanai_db     - Up (healthy)
# mushanai_web    - Up
# mushanai_redis  - Up
# mushanai_nginx  - Up
```

### **Test Application:**

```bash
# Via nginx
curl http://localhost/

# Direct to Django
curl http://localhost:8000/

# Admin panel
open http://localhost/admin/
```

---

## 🎉 Success!

Your Mushanai platform is now:
- ✅ Fully containerized
- ✅ Production-ready
- ✅ Easily deployable
- ✅ Horizontally scalable
- ✅ Self-contained
- ✅ Cloud-ready

**Deploy anywhere:**
- DigitalOcean
- AWS ECS
- Google Cloud Run
- Azure Container Instances
- Your own server

---

**Quick Start:** `docker-compose up -d`  
**Access:** http://localhost  
**Admin:** http://localhost/admin  
**Status:** ✅ Containerized!  

🐳 **Welcome to Docker!** 🚀

