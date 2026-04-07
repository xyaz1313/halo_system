# Core Abstractions Spec

## ORM: SQLModel

All models are built with SQLModel (SQLAlchemy + Pydantic). This gives us:
- Table-mapped models that double as Pydantic validation schemas
- Built-in serialization (`.model_dump()`)
- SQLAlchemy engine/session under the hood
- Migration support via Alembic

## Database

- **SQLite** for development
- **Postgres** for production
- Connection and session management lives in `backend/db/`

## Base Fields

All models inherit common fields:
- `id` — UUID, primary key, auto-generated
- `created_at` — timestamp, set on creation
- `updated_at` — timestamp, updated on every save

## Session / CRUD Pattern

CRUD operations go through SQLModel sessions, not model methods:
- **Create**: instantiate model, `session.add()`, `session.commit()`
- **Read**: `session.get(Model, id)` or `session.exec(select(Model).where(...))`
- **Update**: modify fields, `session.add()`, `session.commit()`
- **Delete**: `session.delete()`, `session.commit()`

Service functions per module can wrap these patterns (e.g., `accounts.create_account(session, **kwargs)`).
