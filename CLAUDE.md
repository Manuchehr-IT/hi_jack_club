# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Hi Jack Club Poker** is a multi-service poker tournament management platform with a Telegram Mini App interface. It manages tournaments, player rankings, user profiles, and integrates with a Telegram bot and an iiko restaurant POS system.

## Tech Stack

- **Backend**: Django 5.2 + Django REST Framework with JWT authentication
- **Frontend**: React 19 + Vite with Axios for API calls
- **Async Tasks**: Celery with Redis message broker
- **Database**: PostgreSQL 16
- **Cache**: Redis (Alpine)
- **Telegram Bot**: FastAPI + aiogram 3 with webhook-based updates
- **Containerization**: Docker + Docker Compose with Traefik reverse proxy
- **File Storage**: Nginx serving static files and user uploads

## Architecture

### Monorepo Structure

The project is organized as a Docker Compose monorepo with 5 independently deployable services:

```
poker/
├── backend/              # Django REST API (port 8000)
├── frontend/             # React + Vite SPA (port 5173)
├── telegram_bot/         # FastAPI + aiogram Telegram bot (port 8000)
├── celery_app/           # Celery task worker (connected to Redis/PostgreSQL)
├── nginx/                # Static file serving (port 80)
├── docker-compose.yml    # Production compose config
├── docker-compose.override.yml  # Local development overrides
└── .env*                 # Environment configs (development/staging/production)
```

### Backend Architecture

The Django backend follows a modular app structure under `backend/apps/`:

- **users**: User authentication, profiles, referrals, rating statistics, iiko integration
- **tournaments**: Tournament CRUD, registration, waitlist, reward distributions, player rankings
- **social_network**: User-to-user social features
- **faq**: FAQ management (CKEditor 5 support)
- **about_club**: Club information pages
- **core**: Shared middleware, utilities, custom authentication
- **redis**: Redis connection pooling
- **iiko**: Integration with iiko restaurant POS API (menus, dishes, orders)
- **telegram**: Deprecated (moved to celery_app tasks)

Authentication uses **JWT tokens** (SimpleJWT) with token rotation and blacklist support. All API endpoints require authentication except signup and login.

### Frontend Architecture

React SPA with pages corresponding to major feature areas:

- **Pages**: Home, SignUp, Profile, Tournaments, Tournament (detail), QRCode, Ratings, FAQ, AboutClub, SocialNetworks
- **API Layer**: `src/api/api.js` with axios instance and centralized request handling
- **Components**: Reusable UI components (TelegramAuth, loaders, spinners, modals)
- **Hooks**: Custom React hooks for Telegram integration and scroll behavior
- **Styling**: CSS Modules + custom fonts (DaysOne)

Entry point is `src/main.jsx` → `App.jsx` which sets up React Router with TelegramAuth wrapper for authentication context.

### Telegram Bot (AsyncIO Architecture)

FastAPI server with aiogram Telegram bot framework using:

- **Webhook mode** (not polling) for incoming updates
- **FSM Storage**: Redis-backed finite state machine for user conversations
- **Dependency Injection**: Custom container for managing bot/settings/services
- **Structure**:
  - `handlers/`: Message/callback handlers organized by feature
  - `states/`: FSM state definitions
  - `keyboards/`: Inline/reply keyboards
  - `services/`: Business logic (HTTP calls to backend API)
  - `schemes/`: Pydantic models for data validation
  - `middlewares/`: FSM/logging/analytics
  - `use_cases/`: Complex multi-step workflows
  - `locales/`: i18n strings (Russian-focused)

### Celery Task Queue

Async task processing for:

- **Tournament tasks** (`celery_app/tasks/tournament.py`): Automated tournament status updates, reward calculations, rating updates
- **Telegram tasks** (`celery_app/tasks/telegram/`): Background Telegram notifications, user updates
- **Config**: Uses Redis for both broker (DB 0) and result backend (DB 3)

## Environment Configuration

Three deployment profiles with separate .env files:

- **development** (`docker-compose.override.yml`): Local debugging, hot reload, port mappings
- **staging** (`docker-compose.yml` profile)
- **production** (`docker-compose.yml` profile)

**Key env variables**:
- `ENVIRONMENT`: Sets deployment profile
- `BACKEND_DOMAIN`, `FRONTEND_DOMAIN`, `TELEGRAM_BOT_DOMAIN`: Public domain names
- `DATABASE_*`: PostgreSQL credentials
- `REDIS_HOST`, `REDIS_PORT`: Redis connection
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_BOT_ADMIN_IDS`: Telegram bot credentials
- `IIKO_*`: Restaurant POS API keys and URLs
- `JWT_*`: Token lifetime and rotation settings

## Common Development Commands

### Backend (Django)

```bash
# Run locally (requires .venv activation and PostgreSQL running)
cd backend
python manage.py runserver 0.0.0.0:8000

# Database migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Interactive shell
python manage.py shell

# Access Django admin
# Navigate to /admin (requires superuser)
```

### Frontend (React/Vite)

```bash
cd frontend

# Development server with hot reload
npm run dev          # Runs on port 5173

# Build for production
npm run build

# Lint with ESLint
npm run lint

# Preview production build
npm run preview
```

### Docker Compose

```bash
# Start all services (development mode with overrides)
docker-compose up -d

# Stop all services
docker-compose down

# Rebuild specific service
docker-compose build backend

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Run migrations in container
docker-compose exec backend python manage.py migrate

# Access Django shell in container
docker-compose exec backend python manage.py shell
```

### Celery

```bash
# Run worker locally
cd celery_app
celery -A celery worker -l info

# Run beat scheduler (for periodic tasks)
celery -A celery beat -l info
```

### Telegram Bot

```bash
cd telegram_bot

# Run locally with FastAPI/uvicorn
python main.py

# Check webhook status
curl http://localhost:8000/debug/webhook
```

## Key Files and Their Purposes

| File | Purpose |
|------|---------|
| `backend/config/settings.py` | Django settings (DB, auth, apps, middleware, logging) |
| `backend/config/urls.py` | API route registration |
| `backend/apps/*/models.py` | Database schema definitions |
| `backend/apps/*/api/` | Serializers and ViewSets for each app |
| `frontend/src/App.jsx` | Main routing and TelegramAuth wrapper |
| `frontend/src/api/api.js` | Axios instance with auth headers, centralized error handling |
| `telegram_bot/core/config.py` | Telegram bot settings (token, proxy, app config) |
| `telegram_bot/core/container.py` | Dependency injection container |
| `celery_app/celery.py` | Celery app initialization and task routing |
| `docker-compose.yml` | Service definitions (backend, frontend, bot, postgres, redis, nginx) |

## Database Schema

**Key models**:

- **User**: Telegram auth, profile data, referral system, rating points, iiko ID
- **Tournament**: Event definitions with start time, participant limits, reward templates
- **TournamentRewardDistribution**: Position-based rewards (% of bank + bonus points)
- **TournamentRegistration**: User tournament participation with status tracking
- **FAQ**, **AboutClub**, **SocialNetwork**: Content management models with CKEditor support

**Important**: Tournament registration triggers automatic recalculation of all registrations when reward distributions change (signal-based).

## API Overview

All endpoints under `/api/` require JWT authentication. Key endpoint groups:

- `/api/auth/`: Login, refresh tokens, logout
- `/api/users/`: User profile, referral codes, avatar upload
- `/api/tournaments/`: Tournament list, registration, details, leaderboards
- `/api/ratings/`: Player rankings and statistics
- `/api/faq/`: FAQ articles
- `/api/about/`: Club information
- `/api/social-network/`: Social features
- `/api/schema/`: OpenAPI schema (Swagger, ReDoc)

## Debugging Tips

1. **Backend logs**: Check `backend/logs/app.log` (RotatingFileHandler with 10MB max size)
2. **Telegram webhook**: Use `/debug/webhook` endpoint to check bot connection status
3. **Redis connectivity**: Verify Celery broker with `redis-cli ping`
4. **JWT issues**: Check token expiry in payload; refresh tokens are auto-rotated
5. **CORS errors**: Update `APP_CORS_ALLOWED_ORIGINS` in backend .env
6. **iiko API**: Verify credentials in settings; supports both cloud (iiko.services) and local (iiko.it) endpoints

## Deployment Notes

- **Static files**: Collected to `backend/staticfiles/` and served by Nginx with WhiteNoise compression
- **Media uploads**: Stored in `backend/storage/` and accessed via Nginx at `/storage/`
- **SSL/TLS**: Traefik handles automatic HTTPS with Let's Encrypt (production)
- **Secrets**: Never commit .env files; only .env.example patterns go to git
- **Reverse proxy**: Traefik routes based on domain and path prefixes (see docker-compose.yml labels)

