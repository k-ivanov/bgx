# BGX Racing Platform

A comprehensive platform for managing championship races, clubs, riders, and results for the Bulgarian Enduro/Navigation racing community.

## Project Components

### 1. BGX API (Django REST Framework + PostgreSQL)
A fully-featured REST API with:
- JWT authentication
- User management (Riders, Club Admins, System Admins)
- Clubs and rider profiles
- Championships and races
- Multi-day race support
- Automatic results calculation
- Points and standings tracking
- CSV import functionality

### 2. Race Results Processing
- PDF parsing scripts in `result-parsing/scripts/`
- Processed results in `result-parsing/final_results/`
- Python virtual environment for parsing tools

## Quick Start

### Prerequisites
- Docker
- Docker Compose

### Setup

1. **Clone and navigate to the project**:
   ```bash
   cd /path/to/bgx-navigation
   ```

2. **Create environment file** (optional, uses defaults if not created):
   ```bash
   cat > .env << 'EOF'
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1,bgx-api
   POSTGRES_DB=bgx_db
   POSTGRES_USER=bgx_user
   POSTGRES_PASSWORD=bgx_password
   CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
   EOF
   ```

3. **Start the services**:
   ```bash
   docker-compose up --build
   ```

   This will:
   - Build the Django API container
   - Start PostgreSQL database
   - Run migrations automatically
   - Create a default admin user (username: `admin`, password: `admin`)
   - Collect static files
   - Start the API server

4. **Access the application**:
   - **API Root**: http://localhost:8000/api/
   - **API Documentation**: http://localhost:8000/api/docs/
   - **Admin Panel**: http://localhost:8000/admin/
   - **Health Check**: http://localhost:8000/health/
   
   Default credentials: `admin` / `admin`

5. **Stop the services**:
   ```bash
   docker-compose down
   ```

## Architecture

### Docker Services

- **bgx-api**: Django REST Framework API
  - Port: 8000
  - JWT authentication
  - Auto-migrations on startup
  - WhiteNoise for static files
  - Gunicorn WSGI server

- **bgx-db**: PostgreSQL 15 Database
  - Port: 5432
  - Persistent volume storage
  - Health checks enabled

### Key Features

- **Multi-role Authentication**: System admins, club admins, and riders
- **Championship Management**: Create and manage racing championships
- **Race Organization**: Multi-day races with different stage types (Prologue, Navigation, Endurocross)
- **Rider Profiles**: Complete rider information including bike details and licensing
- **Automatic Calculations**: Points and standings auto-calculated from results
- **Club Management**: Track clubs, their members, and organized races
- **Results Import**: Import race results from CSV files
- **API Documentation**: Interactive Swagger/ReDoc documentation

## Environment Configuration

The application uses environment variables for configuration. You can set them in a `.env` file in the project root:

```env
# Django settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,bgx-api

# PostgreSQL settings
POSTGRES_DB=bgx_db
POSTGRES_USER=bgx_user
POSTGRES_PASSWORD=bgx_password

# CORS settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

**Note**: The `.env` file is gitignored. Create it locally as needed.

## Project Structure

```
bgx-navigation/
├── bgx-api/                      # Django REST API
│   ├── accounts/                 # User management & auth
│   ├── clubs/                    # Club models & views
│   ├── riders/                   # Rider profiles
│   ├── championships/            # Championship management
│   ├── races/                    # Race & race day models
│   ├── results/                  # Results & calculations
│   │   ├── calculations.py       # Auto-calculation logic
│   │   ├── signals.py            # Auto-trigger calculations
│   │   └── management/commands/  # Import CSV command
│   ├── bgx_api/                  # Django settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── permissions.py        # Custom permissions
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── API_GUIDE.md             # Complete API documentation
├── result-parsing/               # Race results processing
│   ├── final_results/            # Processed CSV results
│   ├── scripts/                  # PDF to CSV parser
│   └── venv/                     # Python environment
├── docker-compose.yml            # Docker orchestration
└── README.md                     # This file
```

## Common Commands

### Docker Commands
```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# Rebuild containers
docker-compose up --build

# Stop services
docker-compose down

# Remove volumes (clean database)
docker-compose down -v

# View logs
docker-compose logs -f bgx-api
docker-compose logs -f bgx-db
```

### Django Commands
```bash
# Run migrations
docker-compose exec bgx-api python manage.py migrate

# Create migrations
docker-compose exec bgx-api python manage.py makemigrations

# Create superuser
docker-compose exec bgx-api python manage.py createsuperuser

# Django shell
docker-compose exec bgx-api python manage.py shell

# Collect static files
docker-compose exec bgx-api python manage.py collectstatic
```

### Database Access
```bash
# Connect to PostgreSQL
docker-compose exec bgx-db psql -U bgx_user -d bgx_db
```

## Development

### Adding New Django Apps

1. Create a new app:
   ```bash
   docker-compose exec bgx-api python manage.py startapp myapp
   ```

2. Add to `INSTALLED_APPS` in `bgx-api/bgx_api/settings.py`

3. Create models, views, and serializers

4. Register viewsets in `bgx-api/bgx_api/urls.py`

### Database Migrations

After modifying models:
```bash
docker-compose exec bgx-api python manage.py makemigrations
docker-compose exec bgx-api python manage.py migrate
```

Or simply restart the containers (migrations run automatically):
```bash
docker-compose restart bgx-api
```

## Quick Start Guide

### 1. Create Your First Club

```bash
curl -X POST http://localhost:8000/api/clubs/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Racing Club",
    "city": "Sofia",
    "country": "Bulgaria",
    "contact_email": "info@myclub.com",
    "admin_ids": [1]
  }'
```

### 2. Create a Rider Profile

```bash
curl -X POST http://localhost:8000/api/riders/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1990-05-15",
    "email": "john@example.com",
    "club": 1,
    "is_licensed": true
  }'
```

### 3. Create a Championship

```bash
curl -X POST http://localhost:8000/api/championships/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Bulgarian Enduro Championship",
    "year": 2024,
    "start_date": "2024-03-01",
    "end_date": "2024-11-30",
    "status": "active"
  }'
```

### 4. Create a Race

```bash
curl -X POST http://localhost:8000/api/races/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alba Damascena Enduro",
    "location": "Kazanlak",
    "start_date": "2024-04-15",
    "end_date": "2024-04-16",
    "organizer_ids": [1],
    "championship_ids": [1],
    "registration_open": true
  }'
```

### 5. Import Results from CSV

```bash
docker-compose exec bgx-api python manage.py import_race_results \
  --race-day-id 1 \
  --file /path/to/results.csv \
  --match-by-name
```

See [API_GUIDE.md](bgx-api/API_GUIDE.md) for complete API documentation.

## Troubleshooting

### Port Already in Use
If port 8000 or 5432 is already in use, modify the ports in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Changed from 8000:8000
```

### Database Connection Issues
- Check if PostgreSQL is healthy: `docker-compose ps`
- View logs: `docker-compose logs bgx-db`
- Restart containers: `docker-compose restart`

### Migration Issues
- Reset database: `docker-compose down -v && docker-compose up`

## Production Deployment

Before deploying to production:

1. ✅ Change `SECRET_KEY` to a secure random value
2. ✅ Set `DEBUG=False`
3. ✅ Update `ALLOWED_HOSTS` with your domain
4. ✅ Use strong database passwords
5. ✅ Set up SSL/TLS certificates
6. ✅ Configure proper static file serving (e.g., Nginx)
7. ✅ Set up database backups
8. ✅ Use production-grade WSGI server settings

## More Information

For detailed API documentation, see `bgx-api/README.md`.

## License

MIT

