# fn-2-szr.1 Project scaffolding, core base model, and database setup

## Description

Create the Python project structure, declare all dependencies, define the base SQLModel class with DB-agnostic UUID, set up the database engine/session factory (including SQLite FK pragma), initialize Alembic with a central model registry, and create the FastAPI application entry point. Also define the typed exception classes used by all service layers.

**Size:** M
**Files:**
- `backend/pyproject.toml` (setuptools backend, deps + dev deps)
- `backend/__init__.py` and `__init__.py` in each submodule
- `backend/core/models.py` (BaseModel with String(36) UUID, created_at, updated_at)
- `backend/core/exceptions.py` (NotFoundError, AlreadyExistsError, ValidationError, AccessDeniedError)
- `backend/db/engine.py` (engine, session factory, get_db, foreign_keys pragma)
- `backend/models.py` (central model registry — scaffolded empty, populated incrementally by tasks 2-4)
- `backend/alembic.ini` + `backend/alembic/` (env.py imports model registry, versions/)
- `backend/main.py` (FastAPI app, lifespan, global exception handlers returning JSONResponse)

## Approach

- `pyproject.toml`: setuptools with `packages = find:`, deps (fastapi, sqlmodel, sqlalchemy, alembic, uvicorn), optional dev deps (pytest, httpx)
- BaseModel in `core/models.py`: UUID `id` as `sa_column(Column(String(36)))` with `default_factory=lambda: str(uuid4())`. `created_at` with `server_default`. `updated_at` with SQLAlchemy `onupdate` (client-side default setting datetime in Python before flush)
- `core/exceptions.py`: typed exception hierarchy (NotFoundError, AlreadyExistsError, ValidationError, AccessDeniedError) — services raise these, routers map them
- `db/engine.py`: DATABASE_URL from env (default `sqlite:///halo.db`). SQLite connect event sets `PRAGMA foreign_keys=ON`. Session factory via `sessionmaker`. `get_db()` generator for Depends.
- `backend/models.py`: scaffolded as empty registry file with a docstring explaining its purpose. Tasks 2-4 add their model imports here. Alembic env.py imports this file.
- Alembic env.py: `import backend.models` before accessing `SQLModel.metadata` as `target_metadata`
- `main.py`: FastAPI app with global exception handlers (`@app.exception_handler(NotFoundError)`, etc.) that return `JSONResponse({"detail": ...}, status_code=...)` for each typed exception. Routes do NOT use try/except — they let exceptions propagate to the global handlers. Empty router includes (filled by later tasks).
- All commands run from repo root; imports use `backend.*` namespace

## Key context

- UUID as String(36) is DB-agnostic — works on SQLite and Postgres without driver-specific types
- SQLite needs `PRAGMA foreign_keys=ON` via `@event.listens_for(engine, "connect")` or cascade deletes silently fail
- SQLAlchemy `onupdate` parameter on a Column sets a client-side default in Python — works on all engines including SQLite
- Central model registry prevents Alembic autogenerate from silently missing tables
- Typed exceptions keep service layer clean; HTTP mapping happens once in main.py

## Acceptance
- [ ] `pip install -e "backend/.[dev]"` succeeds from repo root
- [ ] BaseModel importable with String(36) UUID id, created_at, updated_at
- [ ] Typed exceptions importable from `backend.core.exceptions`
- [ ] Engine enables `PRAGMA foreign_keys=ON` for SQLite connections
- [ ] Central model registry scaffolded at `backend/models.py` (empty, ready for task 2-4 imports)
- [ ] Alembic env.py imports `backend.models` before accessing metadata
- [ ] Alembic autogenerate works (even if no models yet — produces empty migration)
- [ ] `alembic upgrade head` runs without error
- [ ] `uvicorn backend.main:app` starts and shows `/docs`
- [ ] Exception handlers map typed exceptions to correct HTTP status codes
- [ ] All submodule `__init__.py` files exist

## Done summary
TBD

## Evidence
- Commits:
- Tests:
- PRs:
