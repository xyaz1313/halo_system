#!/usr/bin/env bash
# Bare-metal dev launcher: install the backend in editable mode,
# bring the SQLite schema up to date, then start uvicorn with
# hot reload bound to localhost.
#
# This is the no-Docker path. For the Docker path see
# scripts/docker-dev.sh (which ultimately runs scripts/prestart.sh
# inside the container).
set -euo pipefail

# Always operate from the repo root so relative paths (backend/,
# alembic.ini) resolve the same regardless of where the script is
# invoked from.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# Editable install picks up local source changes without reinstalling;
# `[dev]` pulls in pytest, httpx, etc. Cheap to re-run when already
# satisfied, so we don't bother guarding it.
pip install -e "backend/.[dev]"

# Alembic reads DATABASE_URL from the environment (see
# backend/alembic/env.py). Running from backend/ keeps alembic.ini's
# relative script_location pointing at the right versions/ dir.
(cd backend && alembic upgrade head)

# 127.0.0.1 on purpose — bare-metal dev shouldn't expose the app to
# the LAN. The Docker path binds 0.0.0.0 inside the container and
# relies on the compose `ports:` mapping for exposure control.
exec uvicorn backend.main:app \
    --host 127.0.0.1 \
    --port 8000 \
    --reload
