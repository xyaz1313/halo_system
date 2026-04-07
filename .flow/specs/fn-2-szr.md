# Implement Backend Data Layer, API, and Services

## Overview

Build the complete Halo System backend: SQLModel data models, service layers, FastAPI REST API, in-process event bus, structured logging, and comprehensive tests. This is the foundational layer that all other subsystems (frontend, executive, MoZo, transcription, scheduling) depend on.

All module specs live in `backend/*/SPEC.md`. This epic implements everything specified there, plus the necessary scaffolding (project config, packaging, Alembic setup) that is not yet specced.

## Scope

**In scope:**
- Python project scaffolding: `pyproject.toml` (setuptools backend), `__init__.py` files, dependency declarations
- Core base model with DB-agnostic UUID PK (stored as `String(36)` for SQLite/Postgres portability) and timestamps
- Database engine/session setup with SQLite (dev) and PostgreSQL (prod) support, including `PRAGMA foreign_keys=ON` for SQLite
- Alembic migration infrastructure with central model registry
- All 6 data models: Account, Anchor, Tag, AnchorTagAssociation, Calendar, NotificationPreference
- Service functions for each model (CRUD + business logic), raising typed exceptions mapped by global exception handlers in main.py
- FastAPI REST API: all CRUD routes + admin dump routes
- In-process event bus (publish/subscribe/unsubscribe), resettable for tests
- Structured JSON logging (app logger + uvicorn integration)
- Comprehensive pytest test suite using Starlette TestClient

**Out of scope:**
- Rules module (no spec exists — deferred until spec is written)
- Calendar sync mechanism (OAuth, Google API integration — model only)
- Notification email delivery (preference model only, delivery TBD)
- MoZo signal history DB model (referenced in logging spec but undefined — deferred)
- Frontend static file serving (covered by frontend epic fn-1-mj4)
- Executive agent, transcription, memory subsystems

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| UUID storage | `String(36)` column type | DB-agnostic; works identically on SQLite and Postgres. Python-side uuid4 default. |
| Session type | Synchronous | Specs don't require async; SQLite doesn't benefit from it; simpler service functions |
| Base model for AnchorTagAssociation | Skip base class | Composite PK (anchor_id, tag_id) + created_at only — no UUID id, no updated_at |
| `updated_at` mechanism | SQLAlchemy `onupdate` (client-side default) | Sets datetime in Python before flush; works on all DB engines including SQLite |
| Build backend | setuptools with `packages = find:` | Standard, well-supported; editable install via `pip install -e .` |
| Test client | Starlette `TestClient` (sync, from `fastapi.testclient`) | Built-in, sync, no async complexity; NOT httpx direct |
| Model registry | `backend/models.py` — scaffolded empty in task 1, populated incrementally by tasks 2-4 | Single import point for Alembic env.py; prevents silent table omissions |
| SQLite FK enforcement | `PRAGMA foreign_keys=ON` via connect event | Required for cascade delete to work in SQLite; Postgres enforces by default |
| Exception mapping | Services raise typed exceptions; global FastAPI exception handlers in `main.py` map to HTTPException | Clean separation: `NotFoundError` -> 404, `AlreadyExistsError` -> 409, `ValidationError` -> 422, `AccessDeniedError` -> 400. Global handlers, not per-route try/except. |
| Event bus | Simple dict-based (custom), resettable singleton | Lighter than blinker; matches spec interface exactly; reset method for test isolation |
| Logging | JSON formatter on app logger + uvicorn loggers (`uvicorn`, `uvicorn.access`) with `propagate=False` | Single-handler, no double-logging; propagation disabled on uvicorn loggers |
| Error response format | FastAPI default `{"detail": "..."}` | Standard, well-documented |
| Anchor visibility on PATCH | Enforce coupling | Changing to public nulls owner_account_id; changing to private requires owner_account_id |
| Calendar immutability | Return 422 if client tries to change provider/external_calendar_id | Explicit error better than silent ignore |
| alert_types validation | Validate against known set, auto-include schedule_confirmation, dedupe + stable order | Catch typos; normalize deterministically |
| Duplicate association | Return 409 Conflict | Explicit error; idempotent 200 hides bugs |
| Working directory | Run all commands from repo root; imports use `backend.*`. Exception: Alembic commands require `cd backend` (alembic.ini is relative). | Consistent for uvicorn, pytest; Alembic is the explicit exception. |

## Approach

Follow the dependency order: scaffolding -> core/db -> models+services (accounts first, then devices, then calendars+notifications) -> event bus + logging -> API routes -> admin routes -> tests.

Each task produces working, testable code. Service functions take a `Session` parameter directly (no repository pattern). FastAPI routes use `Annotated[Session, Depends(get_db)]` for DI.

Central model registry (`backend/models.py`) is scaffolded empty in task 1, then each model task (2-4) adds its import. Alembic env.py imports this registry. Account relationships to child models use string-based forward references; cascade delete is verified in the test suite (fn-2-szr.6) after all models exist.

## Risks / Dependencies

- **SQLite JSON column behavior**: `alert_types` stored as TEXT in SQLite, native JSON in Postgres. No JSON-path queries planned. Tests verify JSON round-trip.
- **Alembic autogenerate**: Central model registry (`backend/models.py`) ensures all tables are visible. Import this before accessing `SQLModel.metadata`.
- **Event bus single-process limitation**: In-process pub/sub means events don't cross worker boundaries. Acceptable for initial implementation; can swap for Redis/NATS later.
- **Forward references in Account relationships**: Account defines relationships to Tag, Calendar, etc. using string references. Works with SQLAlchemy lazy resolution but requires all models imported at runtime.

## Acceptance

- [ ] `pyproject.toml` declares all dependencies with setuptools backend; `pip install -e ".[dev]"` works
- [ ] UUID PKs stored as String(36), portable across SQLite and Postgres
- [ ] All 6 models create tables via SQLModel.metadata.create_all
- [ ] Central model registry (`backend/models.py`) imports all model modules
- [ ] Alembic init works and can generate migrations from model changes
- [ ] SQLite engine enables foreign_keys=ON via connect event
- [ ] All service functions implemented per SPEC.md files
- [ ] Services raise typed exceptions (NotFoundError, AlreadyExistsError, etc.)
- [ ] Global exception handlers in main.py map service exceptions to correct HTTP status codes via JSONResponse
- [ ] Anchor visibility rules enforced (public/private coupling)
- [ ] AnchorTagAssociation access validation works
- [ ] Calendar immutability enforced (422 on provider/external_calendar_id change)
- [ ] alert_types validated, schedule_confirmation auto-included, deduped
- [ ] Event bus publish/subscribe/unsubscribe works, resettable for tests
- [ ] Structured JSON logging on app + uvicorn loggers, no double-logging
- [ ] All CRUD API routes return correct status codes
- [ ] All 6 admin dump routes return complete table data
- [ ] Test suite passes using Starlette TestClient + in-memory SQLite with StaticPool

## Test notes

- **Framework:** pytest + Starlette `TestClient` (from `fastapi.testclient`)
- **DB isolation:** In-memory SQLite with `StaticPool`, `check_same_thread=False`, `PRAGMA foreign_keys=ON`; fresh tables per test module
- **Event bus:** Reset between tests via `bus.reset()` fixture
- **Fixtures in conftest.py:** `engine`, `db_session`, `client`, `sample_account`, `sample_anchor_public`, `sample_anchor_private`, `sample_tag`
- **Three test layers:** Model/service (direct DB), API endpoint (HTTP round-trip), admin routes (integration)
- **Cascade tests:** Verified in test suite after all models exist

## Quick commands

```bash
# Install dependencies (from repo root)
pip install -e "backend/.[dev]"

# Run all tests
pytest backend/tests/ -v

# Start dev server
uvicorn backend.main:app --host 127.0.0.1 --reload

# Generate Alembic migration
cd backend && alembic revision --autogenerate -m "description"

# Apply migrations
cd backend && alembic upgrade head
```

## References

- `backend/core/SPEC.md` — base model, session, CRUD patterns
- `backend/db/SPEC.md` — engine, session factory, Alembic setup
- `backend/accounts/SPEC.md` — Account model + 6 service functions
- `backend/devices/SPEC.md` — Anchor, Tag, AnchorTagAssociation + visibility rules
- `backend/calendars/SPEC.md` — Calendar model + 5 service functions
- `backend/notifications/SPEC.md` — NotificationPreference + alert types
- `backend/events/SPEC.md` — event bus interface + 8 event types
- `backend/logging/SPEC.md` — structured JSON logging
- `backend/api/SPEC.md` — all REST endpoints + admin routes
- `backend/TESTING.md` — test strategy, fixtures, test cases
- `ARCHITECTURE.md:72-136` — canonical data model definitions
