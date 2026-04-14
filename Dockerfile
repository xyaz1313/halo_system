# Single-stage dev-style image for the Halo System.
# The backend (FastAPI) also serves the frontend static files, so one
# container is enough for local development. Production hardening
# (non-root user, gunicorn workers, healthchecks) is intentionally deferred.
FROM python:3.11-slim

# Keep Python predictable inside a container.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# The app expects to run from the repo root — `backend.main:app` and the
# static-file resolution in backend/main.py both depend on this.
WORKDIR /app

# No apt packages needed at this stage — every runtime dependency
# (fastapi, sqlmodel, sqlalchemy, alembic, uvicorn[standard]) ships a
# prebuilt manylinux wheel for CPython 3.11 on x86_64/arm64. If a future
# dep needs a C toolchain, add `build-essential` here with a matching
# apt-get purge in the same RUN layer.

# Copy just the package metadata first so `pip install` can be cached
# across source edits. `where = [".."]` in backend/pyproject.toml means
# setuptools needs the `backend/` directory itself at install time, so we
# copy the whole backend tree here. The source is bind-mounted over this
# in docker-compose, but we keep it so `docker build` alone produces a
# runnable image.
COPY backend/ ./backend/

# Editable install from the repo root — matches the layout the project
# already uses in development.
RUN pip install -e "backend/.[dev]"

# Copy the rest of the repo (frontend static files, scripts, etc.). In
# compose this is overlaid by a bind-mount for hot reload.
COPY . .

# Ensure the prestart entrypoint is executable even if the host lost the
# bit (e.g. Windows checkout).
RUN chmod +x scripts/prestart.sh

EXPOSE 8000

CMD ["scripts/prestart.sh"]
