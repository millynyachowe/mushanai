#!/bin/bash

# PostgreSQL 17 Setup Script for Mushanai
# This script helps you set up PostgreSQL database

echo "🐘 PostgreSQL 17 Setup for Mushanai"
echo "===================================="
echo ""

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed!"
    echo ""
    echo "Install PostgreSQL 17:"
    echo "  macOS:    brew install postgresql@17"
    echo "  Ubuntu:   sudo apt-get install postgresql-17"
    echo "  Windows:  Download from https://www.postgresql.org/download/"
    echo ""
    exit 1
fi

echo "✅ PostgreSQL is installed"
psql --version
echo ""

# Check if PostgreSQL service is running
if pg_isready &> /dev/null; then
    echo "✅ PostgreSQL service is running"
else
    echo "⚠️  PostgreSQL service is not running"
    echo "Start it with: brew services start postgresql@17"
    echo ""
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "📝 Creating database and user..."
echo ""

# Create database and user
psql postgres << EOF
-- Create database
CREATE DATABASE mushanai_db;

-- Create user
CREATE USER mushanai_user WITH PASSWORD 'mushanai2024';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE mushanai_db TO mushanai_user;

-- Connect to the database
\c mushanai_db

-- Grant schema privileges (PostgreSQL 15+)
GRANT ALL ON SCHEMA public TO mushanai_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO mushanai_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO mushanai_user;

-- Set default privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO mushanai_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO mushanai_user;
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Database setup complete!"
    echo ""
    echo "Database Details:"
    echo "  Database: mushanai_db"
    echo "  User:     mushanai_user"
    echo "  Password: mushanai2024"
    echo "  Host:     localhost"
    echo "  Port:     5432"
    echo ""
    echo "Next steps:"
    echo "  1. cd /Users/ishe/Desktop/Milly/mushanai"
    echo "  2. source venv/bin/activate"
    echo "  3. python manage.py migrate"
    echo "  4. python manage.py createsuperuser"
    echo "  5. python manage.py runserver"
    echo ""
else
    echo ""
    echo "❌ Error creating database"
    echo ""
    echo "Try manually:"
    echo "  psql postgres"
    echo "  CREATE DATABASE mushanai_db;"
    echo "  CREATE USER mushanai_user WITH PASSWORD 'mushanai2024';"
    echo "  GRANT ALL PRIVILEGES ON DATABASE mushanai_db TO mushanai_user;"
    echo ""
fi

