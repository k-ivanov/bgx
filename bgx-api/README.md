# BGX API - Django REST Framework Application

A Dockerized Django REST Framework application with PostgreSQL database connection.

## Features

- Django 4.2 with Django REST Framework
- PostgreSQL 15 database
- Docker and Docker Compose setup
- CORS headers support
- Gunicorn production server
- Automatic migrations on startup
- Pre-configured admin interface

## Prerequisites

- Docker
- Docker Compose

## Quick Start

1. **Clone the repository and navigate to the project directory**

2. **Copy the environment file** (or modify the existing `.env` file):
   ```bash
   cp .env.example .env
   ```

3. **Build and start the containers**:
   ```bash
   docker-compose up --build
   ```

4. **Access the application**:
   - API: http://localhost:8000/api/
   - Admin: http://localhost:8000/admin/
   - Default admin credentials: `admin` / `admin`

## Project Structure

```
bgx-navigation/
├── bgx-api/
│   ├── bgx_api/
│   │   ├── __init__.py
│   │   ├── settings.py      # Django settings with PostgreSQL config
│   │   ├── urls.py          # URL routing
│   │   ├── asgi.py
│   │   └── wsgi.py
│   ├── manage.py
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile           # Django container configuration
│   ├── entrypoint.sh        # Startup script
│   └── .dockerignore
├── docker-compose.yml       # Docker orchestration
├── .env                     # Environment variables
└── .env.example             # Example environment variables
```

## Environment Variables

Key environment variables in `.env`:

- `SECRET_KEY`: Django secret key (change in production!)
- `DEBUG`: Debug mode (set to False in production)
- `POSTGRES_DB`: Database name
- `POSTGRES_USER`: Database user
- `POSTGRES_PASSWORD`: Database password
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `CORS_ALLOWED_ORIGINS`: Comma-separated list of allowed CORS origins

## Docker Services

### bgx-api (Django Application)
- Port: 8000
- Built from `./bgx-api/Dockerfile`
- Runs Django with Gunicorn
- Auto-runs migrations on startup
- Creates default superuser (admin/admin)

### bgx-db (PostgreSQL Database)
- Port: 5432
- PostgreSQL 15 Alpine image
- Persistent data volume
- Health checks enabled

## Common Commands

### Start containers
```bash
docker-compose up
```

### Start in background
```bash
docker-compose up -d
```

### Stop containers
```bash
docker-compose down
```

### View logs
```bash
docker-compose logs -f bgx-api
docker-compose logs -f bgx-db
```

### Run Django commands
```bash
docker-compose exec bgx-api python manage.py <command>
```

Examples:
```bash
# Create migrations
docker-compose exec bgx-api python manage.py makemigrations

# Run migrations
docker-compose exec bgx-api python manage.py migrate

# Create superuser
docker-compose exec bgx-api python manage.py createsuperuser

# Django shell
docker-compose exec bgx-api python manage.py shell
```

### Database access
```bash
docker-compose exec bgx-db psql -U bgx_user -d bgx_db
```

### Rebuild containers
```bash
docker-compose up --build
```

### Remove volumes (clean database)
```bash
docker-compose down -v
```

## Development

### Adding a new Django app

1. Create the app:
   ```bash
   docker-compose exec bgx-api python manage.py startapp myapp
   ```

2. Add it to `INSTALLED_APPS` in `bgx_api/settings.py`

### Making database changes

1. Modify your models
2. Create migrations:
   ```bash
   docker-compose exec bgx-api python manage.py makemigrations
   ```
3. Migrations will be applied automatically on container restart, or run manually:
   ```bash
   docker-compose exec bgx-api python manage.py migrate
   ```

## API Development

The project uses Django REST Framework. To add endpoints:

1. Create serializers in your app
2. Create viewsets or views
3. Register them in the router in `bgx_api/urls.py`

Example:
```python
# In your app's serializers.py
from rest_framework import serializers

class MyModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyModel
        fields = '__all__'

# In your app's views.py
from rest_framework import viewsets

class MyModelViewSet(viewsets.ModelViewSet):
    queryset = MyModel.objects.all()
    serializer_class = MyModelSerializer

# In bgx_api/urls.py
from myapp.views import MyModelViewSet

router.register(r'mymodel', MyModelViewSet)
```

## Production Notes

Before deploying to production:

1. Change `SECRET_KEY` to a secure random string
2. Set `DEBUG=False`
3. Update `ALLOWED_HOSTS` with your domain
4. Use strong database passwords
5. Consider using environment-specific .env files
6. Set up proper SSL/TLS certificates
7. Configure proper static file serving (e.g., with Nginx)
8. Set up database backups

## Troubleshooting

### Database connection issues
- Ensure PostgreSQL container is healthy: `docker-compose ps`
- Check logs: `docker-compose logs bgx-db`

### Migration issues
- Reset database: `docker-compose down -v && docker-compose up`

### Port already in use
- Change ports in `docker-compose.yml`
- Or stop the service using the port

## License

MIT

