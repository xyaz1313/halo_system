# fn-3-qan.1 Dockerfile, .dockerignore, and prestart script

## Description

Create a single-stage Dockerfile, a .dockerignore to keep images lean, and a prestart.sh script that runs Alembic migrations before starting uvicorn with hot reload.

**Size:** S
**Files:**
- `Dockerfile` (at repo root)
- `.dockerignore`
- `scripts/prestart.sh`

## Approach

- Single-stage Dockerfile with `python:3.11-slim` base:
  - `WORKDIR /app`
  - Install minimal system deps if needed
  - Copy `backend/pyproject.toml` first for layer cache
  - `pip install -e "backend/.[dev]"`
  - Copy source (will be overlaid by bind-mount in compose)
  - `CMD ["scripts/prestart.sh"]`
- `.dockerignore`: exclude `.venv`, `__pycache__`, `.git`, `*.db`, `node_modules`, `.flow`, `*.egg-info`, `test-results/`, `.pytest_cache`, `frontend/node_modules`
- `scripts/prestart.sh`:
  - `set -e`
  - `cd /app/backend && alembic upgrade head && cd /app`
  - `exec uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload`

## Key context

- App must run from repo root — `backend.main:app` import path and static file resolution (`parent.parent / "frontend" / "static"`) depend on `WORKDIR /app` being the repo root
- `DATABASE_URL` env var controls DB; SQLite only for now
- Alembic `env.py` reads `DATABASE_URL` and overrides `alembic.ini` if set
- pyproject.toml uses setuptools with `where = [".."]` — install as `pip install -e "backend/.[dev]"` from repo root
- Prod-grade concerns (non-root user, gunicorn workers, healthcheck) are intentionally deferred — out of scope

## Acceptance
- [ ] `docker build -t halo-backend .` builds successfully
- [ ] `prestart.sh` runs Alembic migrations then starts uvicorn with `--reload`
- [ ] `.dockerignore` excludes .venv, __pycache__, .git, *.db, node_modules, .flow, *.egg-info
- [ ] Image size is reasonable (< 400MB)

## Done summary
Added a single-stage python:3.11-slim Dockerfile, a .dockerignore that trims virtualenvs, caches, databases, node_modules, and flow plumbing, and a scripts/prestart.sh entrypoint that runs `alembic upgrade head` then execs uvicorn on 0.0.0.0:8000 with `--reload` scoped to backend/frontend. Verified the image builds to 298MB, migrations apply, and `/docs` returns HTTP 200.
## Evidence
- Commits: 968d699fb87ed1ac71a2f9ae3a66491ccc74f0c2, 4c3901595dfbad7a95406e0da720ab233f49d7ea
- Tests: docker build -t halo-backend ., docker run --rm -e DATABASE_URL=sqlite:////tmp/test.db -d --name halo-test -p 18766:8000 halo-backend && curl /docs -> HTTP 200, bash -n scripts/prestart.sh
- PRs: