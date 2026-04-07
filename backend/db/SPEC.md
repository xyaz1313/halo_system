# Database Spec

## Engine & Session

- SQLModel's `create_engine()` for connection
- `Session` for transactions
- Database URL configured via environment variable (`DATABASE_URL`)
- Defaults to SQLite (`sqlite:///halo.db`) for local dev

## Migrations

- Alembic for schema migrations
- Migration scripts stored in `backend/db/migrations/`

## Initialization

- `init_db()` function to create all tables from model metadata
- Called on app startup
