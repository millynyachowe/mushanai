#!/bin/bash

echo "🐳 Mushanai Platform - Docker Quick Start"
echo "=========================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running!"
    echo "Please start Docker Desktop and try again."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Ask for environment
echo "Select environment:"
echo "1) Development (with hot reload)"
echo "2) Production (with Nginx)"
read -p "Enter choice (1 or 2): " choice

if [ "$choice" = "1" ]; then
    echo ""
    echo "🚀 Starting Development Environment..."
    echo ""
    docker-compose -f docker-compose.dev.yml up --build
elif [ "$choice" = "2" ]; then
    echo ""
    echo "🚀 Starting Production Environment..."
    echo ""
    
    # Check if .env exists
    if [ ! -f .env ]; then
        echo "⚠️  No .env file found. Copying from .env.docker..."
        cp .env.docker .env
    fi
    
    docker-compose up --build -d
    
    echo ""
    echo "✅ Services started!"
    echo ""
    echo "📊 Container Status:"
    docker-compose ps
    echo ""
    echo "🌐 Access your application:"
    echo "   - Website: http://localhost"
    echo "   - Admin: http://localhost/admin"
    echo "   - Default superuser: admin / admin123"
    echo ""
    echo "📝 View logs:"
    echo "   docker-compose logs -f"
    echo ""
    echo "🛑 Stop services:"
    echo "   docker-compose down"
else
    echo "Invalid choice!"
    exit 1
fi

