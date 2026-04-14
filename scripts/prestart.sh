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
exec uvicorn backend.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload
