# fn-3-qan.2 Docker Compose, start scripts, env example, and docs

## Description

Create the docker-compose file for dev, convenience shell scripts for bare-metal and Docker startup, an .env.example file, and update documentation with Docker usage instructions.

**Size:** S
**Files:**
- `docker-compose.yml` (SQLite, hot reload, named volume for DB)
- `scripts/dev.sh` (bare-metal startup)
- `scripts/docker-dev.sh` (Docker dev)
- `.env.example`
- Update `README.md` and `backend/README.md`

## Approach

- `docker-compose.yml`:
  - `app` service: `build: .`, bind-mount `.:/app` for hot reload, port `8000:8000`, `DATABASE_URL=sqlite:////app/data/halo.db`, named volume `halo_data:/app/data` so the SQLite file survives `down`/`up`
  - Top-level `volumes: {halo_data: {}}`
- Start scripts (all in `scripts/`, executable, `#!/usr/bin/env bash` with `set -e`):
  - `dev.sh`: `pip install -e "backend/.[dev]" && (cd backend && alembic upgrade head) && uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload`
  - `docker-dev.sh`: `docker compose up --build`
- `.env.example`: documents `DATABASE_URL` (with SQLite default) and leaves a placeholder comment for future Postgres support
- README updates:
  - `README.md`: add "Getting Started" section — prerequisites, Docker quickstart, bare-metal quickstart
  - `backend/README.md`: add "Running with Docker" section

## Key context

- Hot reload in Docker uses bind-mount volume (`.:/app`) — uvicorn `--reload` watches for file changes
- SQLite DB must live on a named volume, otherwise rebuilds lose the DB
- `DATABASE_URL=sqlite:////app/data/halo.db` uses four slashes for an absolute path (SQLAlchemy SQLite convention)
- ARCHITECTURE.md already references `docker-compose.yml` in the repo structure diagram
- Postgres / prod compose override are deferred — do not add them here

## Acceptance
- [ ] `docker compose up --build` starts app with SQLite, accessible at http://localhost:8000
- [ ] Hot reload works: edit Python file, change reflected without restart
- [ ] SQLite DB persists across `docker compose down` + `docker compose up` (named volume)
- [ ] `scripts/dev.sh` works without Docker
- [ ] `scripts/docker-dev.sh` is a one-command launcher
- [ ] `.env.example` documents `DATABASE_URL`
- [ ] README.md has Docker usage section
- [ ] backend/README.md updated with Docker commands
- [ ] All existing tests still pass

## Done summary
Added docker-compose.yml (SQLite + hot-reload + named halo_data volume for DB persistence), bare-metal scripts/dev.sh (now sources .env with caller-env-wins precedence) and scripts/docker-dev.sh one-command launcher, .env.example documenting DATABASE_URL, plus Getting Started sections in README.md and backend/README.md. Codex impl-review: SHIP after one NEEDS_WORK round that fixed .env wiring in dev.sh.
## Evidence
- Commits: 1558884, 1ed528b97dc99ecfdc3ecb97f5450ef0ca5c52db
- Tests: pytest backend/tests/ -q (137 passed), bash -n scripts/dev.sh scripts/docker-dev.sh, docker compose config --quiet
- PRs: