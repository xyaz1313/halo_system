# Halo System

A tracking and assistance system for dementia patients.

## Components

| Component | Directory | Description |
|---|---|---|
| **Backend** | `backend/` | Central hub: APIs, database, event bus, calendar sync, deterministic rules. All subsystems go through here. |
| **Executive Agent** | `executive/` | Agentic orchestrator that coordinates between subsystems |
| **Frontend** | `frontend/` | Read-only admin UI for browsing backend data |
| **Memory** | `memory/` | Long-term knowledge store and semantic retrieval for patient context |
| **MoZo** | `mozo/` | Tag-anchor proximity monitoring for patient location |
| **Scheduling** | `scheduling/` | Scheduling decision tool used by the executive agent |
| **Transcription** | `transcription/` | 24/7 audio transcription with speaker diarization |
| **Shared** | `shared/` | Common types, event schemas, and utilities |

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed design notes.

## Getting Started

### Prerequisites

- **Docker path:** Docker Engine 20.10+ with the Compose V2 plugin (`docker compose`).
- **Bare-metal path:** Python 3.11+ and `pip`.

### Quickstart — Docker (recommended)

Runs the backend + frontend static files in a single container with SQLite and hot reload. Migrations are applied automatically on container start.

```bash
./scripts/docker-dev.sh            # equivalent to: docker compose up --build
```

Then open http://localhost:8000 (UI) and http://localhost:8000/docs (API docs).

The SQLite database lives on a named Docker volume (`halo_data`) so it survives `docker compose down` + `docker compose up`. To wipe it:

```bash
docker compose down -v
```

### Quickstart — bare metal

No Docker required. Uses a local `halo.db` file in the repo root by default.

```bash
./scripts/dev.sh
```

This installs the backend in editable mode, runs `alembic upgrade head`, and starts `uvicorn --reload` on http://127.0.0.1:8000.

### Environment variables

Copy `.env.example` to `.env` to override defaults for bare-metal runs. `scripts/dev.sh` sources `.env` automatically before invoking Alembic and Uvicorn, so variables defined there take effect (unless already exported in your shell, which wins).

The main knob is `DATABASE_URL`. Note that the Docker Compose service sets `DATABASE_URL` explicitly on the `app` container (pointing at the named volume), so `.env` values are **not** used inside the container by design — overriding the DB URL there would bypass the persistent volume. If you need per-developer Compose overrides, use a `docker-compose.override.yml`.
