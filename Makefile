.PHONY: help start stop restart start-db stop-db logs build clean shell migrate makemigrations createsuperuser import-clubs import-riders import-results import-results-dirs

# Default target
help:
	@echo "BGX Racing Platform - Available Commands:"
	@echo ""
	@echo "  make start          - Start all services (API + DB)"
	@echo "  make stop           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo "  make restart-api    - Restart API only"
	@echo "  make start-db       - Start only the database"
	@echo "  make stop-db        - Stop only the database"
	@echo "  make build          - Build/rebuild containers"
	@echo "  make logs           - View logs (all services)"
	@echo "  make logs-api       - View API logs only"
	@echo "  make logs-db        - View database logs only"
	@echo "  make shell          - Open Django shell"
	@echo "  make bash           - Open bash in API container"
	@echo "  make migrate        - Run database migrations"
	@echo "  make makemigrations - Create new migrations"
	@echo "  make createsuperuser - Create a Django superuser"
	@echo "  make import-clubs   - Import clubs from CSV"
	@echo "  make import-riders  - Import riders (users + profiles) from CSV"
	@echo "  make import-results - Import race day results from CSV"
	@echo "  make import-results-dirs - Import results from race_day directories"
	@echo "  make clean          - Stop and remove all containers and volumes"
	@echo "  make psql           - Open PostgreSQL shell"
	@echo ""
	@echo "Frontend:"
	@echo "  make fe-install     - Install frontend dependencies"
	@echo "  make fe-dev         - Start frontend development server"
	@echo "  make fe-build       - Build frontend for production"
	@echo ""

# Start all services
start:
	@echo "Starting BGX services..."
	docker compose up -d
	@echo "Services started. API available at http://localhost:8000"

# Stop all services
stop:
	@echo "Stopping BGX services..."
	docker compose down
	@echo "Services stopped."

# Restart all services
restart:
	@echo "Restarting BGX services..."
	docker compose restart
	@echo "Services restarted."

# Start only database
start-db:
	@echo "Starting database..."
	docker compose up -d bgx-db
	@echo "Database started."

# Stop only database
stop-db:
	@echo "Stopping database..."
	docker compose stop bgx-db
	@echo "Database stopped."

# Build/rebuild containers
build:
	@echo "Building containers..."
	docker compose up --build -d
	@echo "Build complete. Services started."

# View logs (all services)
logs:
	docker compose logs -f

# View API logs only
logs-api:
	docker compose logs -f bgx-api

# View database logs only
logs-db:
	docker compose logs -f bgx-db

# Open Django shell
shell:
	docker compose exec bgx-api python manage.py shell

# Open bash in API container
bash:
	docker compose exec bgx-api bash

# Run migrations
migrate:
	docker compose exec bgx-api python manage.py migrate

# Create new migrations
makemigrations:
	docker compose exec bgx-api python manage.py makemigrations

# Create superuser
createsuperuser:
	docker compose exec bgx-api python manage.py createsuperuser

# Results calculation commands
recalculate-results:
	docker compose exec bgx-api python manage.py recalculate_results

recalculate-results-dry:
	docker compose exec bgx-api python manage.py recalculate_results --dry-run --verbose

recalculate-championship:
	@if [ -z "$(ID)" ]; then \
		echo "Error: Please specify championship ID with ID=<id>"; \
		echo "Example: make recalculate-championship ID=1"; \
		exit 1; \
	fi
	docker compose exec bgx-api python manage.py recalculate_results --championship $(ID) --verbose

recalculate-race:
	@if [ -z "$(ID)" ]; then \
		echo "Error: Please specify race ID with ID=<id>"; \
		echo "Example: make recalculate-race ID=5"; \
		exit 1; \
	fi
	docker compose exec bgx-api python manage.py recalculate_results --race $(ID) --verbose

recalculate-completed:
	docker compose exec bgx-api python manage.py recalculate_results --completed-only --verbose

# Import clubs from CSV
import-clubs:
	@echo "Importing clubs from input_data/teams.csv..."
	docker compose exec bgx-api python manage.py import_clubs
	@echo "Import complete."

# Import clubs (dry run)
import-clubs-dry:
	@echo "Dry run - importing clubs from input_data/teams.csv..."
	docker compose exec bgx-api python manage.py import_clubs --dry-run

# Import riders from CSV
import-riders:
	@echo "Importing riders from input_data/user_racers/pro_processed.csv..."
	docker compose exec bgx-api python manage.py import_riders
	@echo "Import complete."

# Import riders (dry run)
import-riders-dry:
	@echo "Dry run - importing riders from input_data/user_racers/pro_processed.csv..."
	docker compose exec bgx-api python manage.py import_riders --dry-run

# Import race day results from CSV
import-results:
	@echo "Importing race day results from input_data/user_racers/pro_processed.csv..."
	docker compose exec bgx-api python manage.py import_race_day_results
	@echo "Import complete."

# Import results (dry run)
import-results-dry:
	@echo "Dry run - importing race day results..."
	docker compose exec bgx-api python manage.py import_race_day_results --dry-run

# Import results from race_day directories
import-results-dirs:
	@echo "Importing results from race_day directories..."
	docker compose exec bgx-api python manage.py import_results_from_directories
	@echo "Import complete."

# Import results from directories (dry run)
import-results-dirs-dry:
	@echo "Dry run - importing results from race_day directories..."
	docker compose exec bgx-api python manage.py import_results_from_directories --dry-run

# Stop and remove all containers and volumes
clean:
	@echo "Stopping and removing all containers and volumes..."
	docker compose down -v
	@echo "Cleanup complete."

# Open PostgreSQL shell
psql:
	docker compose exec bgx-db psql -U bgx_user -d bgx_db

# Check service status
status:
	docker compose ps

# Restart API only
restart-api:
	docker compose restart bgx-api

# Restart DB only
restart-db:
	docker compose restart bgx-db

# ============================================
# Internationalization (i18n)
# ============================================

# Extract translatable strings from Python code
makemessages:
	docker compose exec bgx-api python manage.py makemessages -l bg -i venv -i staticfiles
	@echo "✓ Translation strings extracted to bgx-api/locale/bg/LC_MESSAGES/django.po"

# Compile translation files (.po to .mo)
compilemessages:
	docker compose exec bgx-api python manage.py compilemessages
	@echo "✓ Translations compiled successfully!"

# Update translations (extract + compile)
update-translations: makemessages compilemessages
	@echo "✓ Translations updated! Restart server: make restart-api"

# Show translation statistics
translation-stats:
	@echo "Translation statistics:"
	@msgfmt --statistics bgx-api/locale/bg/LC_MESSAGES/django.po 2>&1 || echo "No translations found"

# Frontend commands
fe-install:
	@echo "Installing frontend dependencies..."
	cd bgx-fe && npm install

fe-dev:
	@echo "Starting frontend development server..."
	cd bgx-fe && npm run dev

fe-build:
	@echo "Building frontend for production..."
	cd bgx-fe && npm run build

