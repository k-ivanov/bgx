# BGX Racing API - Complete Guide

## Overview

The BGX Racing API is a comprehensive REST API for managing championship races, clubs, riders, and results. Built with Django REST Framework, it provides full CRUD operations with role-based access control.

## Table of Contents

1. [Authentication](#authentication)
2. [User Roles](#user-roles)
3. [API Endpoints](#api-endpoints)
4. [Data Models](#data-models)
5. [Permissions](#permissions)
6. [Usage Examples](#usage-examples)

## Authentication

The API uses JWT (JSON Web Token) authentication.

### Register a New User

```bash
POST /api/auth/register/
Content-Type: application/json

{
  "username": "john_doe",
  "password": "securePassword123",
  "password2": "securePassword123",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe"
}
```

Response includes access and refresh tokens:
```json
{
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    ...
  },
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Login

```bash
POST /api/auth/login/
Content-Type: application/json

{
  "username": "john_doe",
  "password": "securePassword123"
}
```

Response:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Refresh Token

```bash
POST /api/auth/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Using Tokens

Include the access token in the Authorization header:

```bash
GET /api/riders/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

## User Roles

Users can have multiple roles:

- **System Admin** (`is_system_admin`): Full access to everything
- **Club Admin** (`is_club_admin`): Can manage their club and its races
- **Rider** (`is_rider`): Has a rider profile, can sign up for races

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Obtain JWT tokens
- `POST /api/auth/refresh/` - Refresh access token

### Users
- `GET /api/users/` - List users (admin only)
- `GET /api/users/me/` - Get current user info
- `GET /api/users/{id}/` - Get user details
- `PATCH /api/users/{id}/` - Update user

### Clubs
- `GET /api/clubs/` - List all clubs
- `POST /api/clubs/` - Create club (admin only)
- `GET /api/clubs/{id}/` - Get club details
- `PATCH /api/clubs/{id}/` - Update club (admin or club admin)
- `DELETE /api/clubs/{id}/` - Delete club (admin only)
- `GET /api/clubs/{id}/riders/` - Get club members
- `GET /api/clubs/{id}/organized-races/` - Get races organized by club

### Riders
- `GET /api/riders/` - List all riders
- `POST /api/riders/` - Create rider profile
- `GET /api/riders/{id}/` - Get rider details
- `PATCH /api/riders/{id}/` - Update rider (owner or admin)
- `DELETE /api/riders/{id}/` - Delete rider (owner or admin)
- `GET /api/riders/{id}/results/` - Get rider's race results
- `GET /api/riders/{id}/upcoming-races/` - Get rider's upcoming races

### Championships
- `GET /api/championships/` - List championships
- `POST /api/championships/` - Create championship (admin only)
- `GET /api/championships/{id}/` - Get championship details
- `PATCH /api/championships/{id}/` - Update championship (admin only)
- `DELETE /api/championships/{id}/` - Delete championship (admin only)
- `GET /api/championships/{id}/races/` - Get races in championship
- `GET /api/championships/{id}/standings/` - Get championship standings

### Races
- `GET /api/races/` - List races
- `POST /api/races/` - Create race (admin or club admin)
- `GET /api/races/{id}/` - Get race details
- `PATCH /api/races/{id}/` - Update race (admin or organizer)
- `DELETE /api/races/{id}/` - Delete race (admin only)
- `POST /api/races/{id}/signup/` - Sign up for race
- `GET /api/races/{id}/participants/` - Get race participants
- `GET /api/races/{id}/results/` - Get race results
- `GET /api/races/{id}/days/` - Get race days
- `POST /api/races/{id}/days/` - Create race day (organizer)

### Race Days
- `GET /api/race-days/` - List race days
- `GET /api/race-days/{id}/` - Get race day details
- `PATCH /api/race-days/{id}/` - Update race day (organizer)
- `DELETE /api/race-days/{id}/` - Delete race day (organizer)
- `GET /api/race-days/{id}/results/` - Get results for this day

### Results
- `GET /api/results/race-day-results/` - List race day results
- `POST /api/results/race-day-results/` - Submit race day result (organizer)
- `GET /api/results/race-results/?race={id}` - Get overall race results
- `GET /api/results/championship-results/?championship={id}` - Get championship standings
- `GET /api/results/club-standings/?championship={id}` - Get club standings

## Data Models

### Championship
```json
{
  "id": 1,
  "name": "Bulgarian Enduro Championship",
  "year": 2024,
  "description": "...",
  "logo": "url",
  "start_date": "2024-03-01",
  "end_date": "2024-11-30",
  "sponsor_info": "...",
  "status": "active"
}
```

### Race
```json
{
  "id": 1,
  "name": "Alba Damascena Enduro",
  "description": "...",
  "location": "Kazanlak",
  "start_date": "2024-04-15",
  "end_date": "2024-04-16",
  "registration_open": true,
  "registration_deadline": "2024-04-10",
  "max_participants": 200,
  "entry_fee": "50.00",
  "status": "upcoming"
}
```

### RaceDay
```json
{
  "id": 1,
  "race": 1,
  "day_number": 1,
  "date": "2024-04-15",
  "type": "prologue",
  "description": "Qualification day"
}
```

### Rider
```json
{
  "id": 1,
  "user": 5,
  "username": "john_doe",
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1990-05-15",
  "email": "john@example.com",
  "phone": "+359888123456",
  "club": 2,
  "is_licensed": true,
  "license_number": "BG12345",
  "license_expiry": "2024-12-31",
  "bike_info": {
    "brand": "KTM",
    "model": "300 EXC",
    "year": 2023
  }
}
```

### RaceParticipation
```json
{
  "id": 1,
  "race": 1,
  "rider": 5,
  "category": "expert",
  "status": "confirmed",
  "bib_number": "123",
  "registration_date": "2024-03-20T10:30:00Z"
}
```

## Permissions

### Public (No Authentication)
- View clubs
- View championships
- View races

### Authenticated Users
- View riders
- View results
- Create own rider profile
- Sign up for races

### Club Admins
- Create races (for their club)
- Manage their club's races
- Submit results for their races
- Manage race participants

### System Admins
- Full access to everything
- Create/edit/delete clubs
- Create/edit/delete championships
- Manage all races
- Manage users

## Usage Examples

### Create a Rider Profile

```bash
curl -X POST http://localhost:8000/api/riders/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1990-05-15",
    "email": "john@example.com",
    "phone": "+359888123456",
    "club": 1,
    "is_licensed": true,
    "license_number": "BG12345",
    "bike_info": {
      "brand": "KTM",
      "model": "300 EXC",
      "year": 2023
    }
  }'
```

### Sign Up for a Race

```bash
curl -X POST http://localhost:8000/api/races/1/signup/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "expert"
  }'
```

### Submit Race Day Results

```bash
curl -X POST http://localhost:8000/api/results/race-day-results/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "race_day": 1,
    "rider": 5,
    "position": 3,
    "time_taken": "01:45:30",
    "points_earned": 20
  }'
```

### Get Championship Standings

```bash
curl http://localhost:8000/api/results/championship-results/?championship=1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Categories

Available race categories:
- `expert` - Expert
- `profi` - Profi
- `junior` - Junior
- `standard` - Standard
- `standard_junior` - Standard Junior
- `seniors_40` - Seniors 40+
- `seniors_50` - Seniors 50+
- `women` - Women

## Race Day Types

- `prologue` - Prologue (Qualification)
- `navigation` - Navigation
- `endurocross` - Endurocross

## Automatic Calculations

The system automatically calculates:

1. **Race Results**: Aggregated from all race day results
2. **Championship Standings**: Sum of points from all races in the championship
3. **Club Standings**: Sum of points from all club riders

Calculations are triggered automatically when race day results are saved.

## Import CSV Results

Use the management command to import results from CSV files:

```bash
docker-compose exec bgx-api python manage.py import_race_results \
  --race-day-id 1 \
  --file /path/to/results.csv \
  --match-by-name
```

CSV format:
```csv
RaceNumber,FirstName,LastName,Position,Points
123,John,Doe,1,25
124,Jane,Smith,2,20
```

## API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- OpenAPI Schema: http://localhost:8000/api/schema/

