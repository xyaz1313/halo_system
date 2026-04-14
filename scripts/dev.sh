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

# Load .env if present so developers can set DATABASE_URL (and any
# future env vars documented in .env.example) without having to
# export them in every shell. Already-exported variables in the
# caller's environment win over .env — we only set names that are
# currently unset/empty. This matches the precedence most tools use
# (docker compose, foreman, python-dotenv with override=False).
if [[ -f .env ]]; then
    while IFS= read -r line || [[ -n "$line" ]]; do
        # Skip blanks and comments.
        [[ -z "${line// }" || "$line" =~ ^[[:space:]]*# ]] && continue
        # Tolerate an optional leading `export `.
        line="${line#export }"
        # Must look like KEY=VALUE with a valid identifier key.
        if [[ "$line" =~ ^([A-Za-z_][A-Za-z0-9_]*)=(.*)$ ]]; then
            key="${BASH_REMATCH[1]}"
            val="${BASH_REMATCH[2]}"
            # Strip one matching pair of surrounding quotes if present.
            if [[ "$val" =~ ^\"(.*)\"$ || "$val" =~ ^\'(.*)\'$ ]]; then
                val="${BASH_REMATCH[1]}"
            fi
            # Only set if currently unset/empty — caller env wins.
            if [[ -z "${!key:-}" ]]; then
                export "$key=$val"
            fi
        fi
    done < .env
fi

# Alembic (invoked below) and backend/db/engine.py both read
# DATABASE_URL from the environment. We don't default it here —
# engine.py falls back to sqlite:///halo.db on its own.

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
