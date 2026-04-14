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

# Copy just the package metadata first so the heavy `pip install` layer
# is cached across source edits. An editable install doesn't actually
# need the source tree present at install time — pip writes a .pth entry
# pointing at wherever the package lives, so we can stage pyproject.toml
# alone, install, and then bring in the source.
COPY backend/pyproject.toml ./backend/pyproject.toml
RUN pip install -e "backend/.[dev]"

# Now the source. The compose file bind-mounts the repo over /app for
# hot reload, but we still want a runnable image from `docker build`
# alone (e.g. for one-shot runs, CI, or smoke tests).
COPY backend/ ./backend/
COPY . .

# Ensure the prestart entrypoint is executable even if the host lost the
# bit (e.g. Windows checkout).
RUN chmod +x scripts/prestart.sh

EXPOSE 8000

CMD ["scripts/prestart.sh"]
