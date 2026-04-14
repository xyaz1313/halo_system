# Docker Containers and Start Scripts

## Overview

Add Docker containerization and convenience start scripts to the Halo System. The backend (FastAPI + uvicorn) and frontend (static files) are served from a single container. Docker Compose runs the app with SQLite. Convenience shell scripts provide one-command startup for both Docker and bare-metal workflows.

## Scope

**In scope:**
- Single-stage Dockerfile for backend+frontend (dev-style: uvicorn `--reload`)
- `docker-compose.yml` (SQLite, hot reload via volume mount, named volume for DB persistence)
- `.dockerignore` to keep images lean
- Convenience start scripts: `scripts/dev.sh` (bare-metal), `scripts/docker-dev.sh` (Docker)
- `scripts/prestart.sh` for container startup (run Alembic migrations, then start uvicorn)
- `.env.example` documenting all environment variables
- Documentation updates (README.md, backend/README.md)

**Out of scope:**
- Production-grade container (non-root user, gunicorn workers, healthchecks) — revisit when we have a real prod target
- PostgreSQL service / `docker-compose.prod.yml` — SQLite only for now
- CI/CD pipeline (GitHub Actions, etc.)
- Kubernetes / cloud deployment configs
- Nginx/Traefik reverse proxy
- SSL/TLS configuration
- Frontend build step (no build needed — static files)

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Container count | Single app container (backend + frontend static files) | Frontend has no build step; already served by FastAPI StaticFiles mount |
| Dockerfile strategy | Single stage, dev-style | "Just get it running" — prod target can be added later when needed |
| Base image | `python:3.11-slim` | Matches pyproject.toml `requires-python >= 3.11`; slim reduces image size |
| Package installer | pip (not uv/poetry) | Project uses setuptools + pip already; no need to add tooling |
| Hot reload | Volume mount + `--reload` flag | Bind-mount repo into container, uvicorn watches for changes |
| Database | SQLite only | Postgres deferred; `DATABASE_URL` env var still used so we can swap later |
| SQLite persistence | Named volume mounted at `/app/data` | Otherwise the DB file dies with the container |
| Migration strategy | `prestart.sh` runs `alembic upgrade head` before uvicorn | Ensures schema is current on every container start |
| Working directory | `/app` in container, repo root mapped | Matches current requirement that app runs from repo root |

## Approach

**Dockerfile** (single stage):
- `python:3.11-slim` base
- `WORKDIR /app`
- Copy `backend/pyproject.toml` first (layer cache), `pip install -e "backend/.[dev]"`
- Copy source (ignored at runtime in compose because of bind-mount)
- CMD runs `scripts/prestart.sh`

**Docker Compose**:
- `docker-compose.yml`: `app` service, bind-mount `.:/app` for hot reload, port 8000, `DATABASE_URL=sqlite:////app/data/halo.db`, named volume `halo_data:/app/data` for DB persistence

**Start scripts** (in `scripts/`):
- `dev.sh`: bare-metal startup (pip install, alembic upgrade, uvicorn --reload on 127.0.0.1)
- `docker-dev.sh`: `docker compose up --build`
- `prestart.sh`: runs inside container (alembic upgrade head, then exec uvicorn with `--reload`)

## Risks / Dependencies

- **Volume mount performance**: On macOS, Docker volume mounts can be slow. Acceptable for dev.
- **SQLite in container**: DB file must live on the named volume, otherwise it's lost on container rebuild.
- **Alembic in prestart**: If migrations fail, the container won't start. This is intentional — better to fail fast than run with wrong schema.
- **Port conflicts**: Dev script and Docker both use port 8000. Only run one at a time.

## Acceptance

- [ ] `docker compose up --build` starts the app, accessible at http://localhost:8000
- [ ] Hot reload works: edit a Python file, see changes without restart
- [ ] Alembic migrations run automatically on container start
- [ ] SQLite DB persists across `docker compose down` + `up` (named volume)
- [ ] `scripts/dev.sh` starts the app without Docker
- [ ] `scripts/docker-dev.sh` is a one-command launcher
- [ ] `.dockerignore` excludes .venv, __pycache__, .git, *.db, node_modules, .flow, *.egg-info
- [ ] README.md updated with Docker usage instructions
- [ ] All existing tests still pass (137 pytest, 51 Playwright)

## Test notes

- Verify `docker compose up` starts successfully and `/docs` is accessible
- Verify hot reload by changing a route and confirming the change without restart
- Verify SQLite persistence: create a record, `docker compose down`, `docker compose up`, record still there
- Existing pytest suite runs unchanged (tests use in-memory SQLite, not Docker)
- Playwright tests can run against the Docker container if `baseURL` matches

## Quick commands

```bash
# Dev with Docker (SQLite, hot reload)
./scripts/docker-dev.sh

# Bare-metal dev (no Docker)
./scripts/dev.sh

# Run tests in container
docker compose exec app pytest backend/tests/ -v
```

## References

- `backend/main.py` — app entry point, static file mount at `/static`
- `backend/pyproject.toml` — dependencies (fastapi, sqlmodel, alembic, uvicorn)
- `backend/db/engine.py:8` — DATABASE_URL env var handling
- `backend/alembic/env.py` — also reads DATABASE_URL
- `ARCHITECTURE.md` — already references docker-compose.yml in repo structure
- Official FastAPI Docker docs: https://fastapi.tiangolo.com/deployment/docker/
