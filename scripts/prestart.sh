#!/usr/bin/env bash
# Container entrypoint: bring the schema up to date, then start uvicorn.
#
# This runs inside the container (CMD in Dockerfile). It is NOT intended
# for bare-metal use — see scripts/dev.sh for that.
set -euo pipefail

# Alembic is configured from backend/alembic.ini and reads DATABASE_URL
# from the environment (see backend/alembic/env.py). Running from the
# backend directory keeps relative paths in alembic.ini working.
cd /app/backend
alembic upgrade head
cd /app

# --reload is fine here because the compose file bind-mounts the repo
# into /app; production would drop this flag and switch to gunicorn.
#
# Scope the reloader explicitly. With a full-repo bind-mount uvicorn
# would otherwise watch frontend/node_modules/, test-results/, .flow/
# and similar — which on many hosts blows past inotify limits or just
# pegs CPU. Only the Python source and served static files actually
# matter for reload.
exec uvicorn backend.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --reload-dir /app/backend \
    --reload-dir /app/frontend \
    --reload-exclude '**/node_modules/**' \
    --reload-exclude '**/__pycache__/**' \
    --reload-exclude '**/.pytest_cache/**' \
    --reload-exclude '**/test-results/**'
