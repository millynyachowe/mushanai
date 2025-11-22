#!/bin/bash
set -e

echo "🐘 Waiting for PostgreSQL..."
# Database readiness is handled by docker-compose healthcheck
sleep 2
echo "✅ PostgreSQL is ready!"

echo "🔄 Running database migrations..."
python manage.py migrate --noinput

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

echo "👤 Creating superuser (if not exists)..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@mushanai.com', 'admin123')
    print('✅ Superuser created: admin / admin123')
else:
    print('ℹ️  Superuser already exists')
EOF

echo "🚀 Starting Gunicorn..."
exec gunicorn mushanaicore.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info

