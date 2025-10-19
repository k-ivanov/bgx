#!/bin/bash

# Exit on error
set -e

echo "Waiting for PostgreSQL..."
while ! pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER; do
  sleep 1
done
echo "PostgreSQL started"

# Run migrations
echo "Running database migrations..."
python manage.py makemigrations --noinput || true
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist
echo "Creating superuser if needed..."
python manage.py shell << EOF
from accounts.models import User
if not User.objects.filter(username='admin').exists():
    user = User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    user.is_system_admin = True
    user.save()
    print('Superuser created with system admin privileges')
else:
    print('Superuser already exists')
EOF

# Start server
echo "Starting server..."
exec gunicorn bgx_api.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 120

