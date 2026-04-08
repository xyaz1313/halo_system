# Halo System — Backend

Python/FastAPI backend for the Halo caretaker-assistance system. Provides the data layer, REST API, event bus, and structured logging that all other subsystems depend on.

## Quick Start

```bash
# Install (from repo root)
pip install -e "backend/.[dev]"

# Run dev server
uvicorn backend.main:app --host 127.0.0.1 --reload

# Run tests
pytest backend/tests/ -v

# Open API docs
open http://127.0.0.1:8000/docs
```

## Project Structure

```
backend/
├── main.py                 # FastAPI app, lifespan, global exception handlers
├── models.py               # Central model registry (imported by Alembic)
├── pyproject.toml           # Dependencies and build config
│
├── core/                    # Shared foundations
│   ├── models.py            #   BaseModel: UUID PK (String(36)), timestamps
│   └── exceptions.py        #   NotFoundError, AlreadyExistsError, ValidationError, AccessDeniedError
│
├── db/                      # Database engine and session
│   └── engine.py            #   SQLite (dev) / PostgreSQL (prod), PRAGMA foreign_keys=ON
│
├── accounts/                # Top-level entity — patients + caretakers
│   ├── models.py            #   Account table
│   └── service.py           #   create, get, get_by_email, list, update, delete
│
├── devices/                 # Proximity monitoring hardware
│   ├── models.py            #   Anchor (public/private visibility), Tag, AnchorTagAssociation
│   └── service.py           #   CRUD + visibility rules + association access control
│
├── calendars/               # External calendar sync tracking
│   ├── models.py            #   Calendar table (provider/external_id immutable after create)
│   └── service.py           #   CRUD + immutability enforcement
│
├── notifications/           # Alert preferences
│   ├── models.py            #   NotificationPreference table (JSON alert_types column)
│   └── service.py           #   CRUD + alert_types validation + schedule_confirmation auto-include
│
├── events/                  # In-process pub/sub event bus
│   ├── bus.py               #   publish, subscribe, unsubscribe, reset
│   └── types.py             #   8 event type constants (mozo.departure, calendar.sync_complete, etc.)
│
├── logging/                 # Structured JSON logging
│   └── config.py            #   JSON formatter on app + uvicorn loggers
│
├── api/                     # FastAPI route handlers
│   ├── accounts.py          #   /api/v1/accounts
│   ├── devices.py           #   /api/v1/anchors, /api/v1/tags, association sub-routes
│   ├── calendars.py         #   /api/v1/calendars
│   ├── notifications.py     #   /api/v1/notifications/preferences
│   └── admin.py             #   /api/v1/admin/* (debug-only table dumps, NO auth)
│
├── rules/                   # Deterministic routing logic (not yet implemented)
│
├── alembic/                 # Database migrations
│   ├── env.py
│   └── versions/
├── alembic.ini
│
└── tests/                   # pytest test suite (137 tests)
    ├── conftest.py           #   In-memory SQLite, StaticPool, fixtures
    ├── test_accounts.py      #   Account CRUD + cascade delete
    ├── test_devices.py       #   Visibility, access control, associations
    ├── test_calendars.py     #   Immutability enforcement
    ├── test_notifications.py #   alert_types validation, JSON round-trip
    ├── test_events.py        #   Event bus publish/subscribe/isolation
    ├── test_admin.py         #   Admin dump routes
    └── test_api_*.py         #   HTTP round-trip tests for each module
```

## Architecture

### Data Models

Six SQLModel tables, all with UUID primary keys (stored as `String(36)` for SQLite/Postgres portability):

- **Account** — patient + caretaker info, cascade deletes to all children
- **Anchor** — stationary receivers with public/private visibility
- **Tag** — patient-worn devices, linked to one account
- **AnchorTagAssociation** — composite PK linking tags to anchors (with access validation)
- **Calendar** — external calendar sync state (provider/external_id immutable)
- **NotificationPreference** — per-account alert routing (JSON `alert_types` column)

### API

All routes under `/api/v1/`. Standard REST (POST/GET/PATCH/DELETE) for each resource plus:

- **Association sub-routes**: `POST /anchors/{id}/tags/{id}`, `DELETE /anchors/{id}/tags/{id}`, etc.
- **Admin routes**: `GET /admin/accounts`, `/admin/anchors`, `/admin/tags`, `/admin/associations`, `/admin/calendars`, `/admin/preferences` — full table dumps for debug use only

### Error Handling

Services raise typed exceptions. Global handlers in `main.py` map them to HTTP responses:

| Exception | Status | Meaning |
|-----------|--------|---------|
| `NotFoundError` | 404 | Resource not found |
| `AlreadyExistsError` | 409 | Duplicate (email, association) |
| `ValidationError` | 422 | Business rule violation |
| `AccessDeniedError` | 403 | Insufficient access (e.g., tag can't see anchor) |

### Event Bus

In-process synchronous pub/sub. 8 event types spanning MoZo proximity, transcription, calendar, and scheduling domains. Handler exceptions are caught and logged — they never block other handlers.

### Database

- **Dev**: SQLite with `PRAGMA foreign_keys=ON`
- **Prod**: PostgreSQL
- **Config**: `DATABASE_URL` env var (defaults to `sqlite:///halo.db`)
- **Migrations**: Alembic with autogenerate

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///halo.db` | Database connection string |

## Running Alembic

```bash
# Generate migration after model changes
cd backend && alembic revision --autogenerate -m "description"

# Apply migrations
cd backend && alembic upgrade head
```
