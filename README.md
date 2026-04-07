# Halo System

A tracking and assistance system for dementia patients.

## Components

| Component | Directory | Description |
|---|---|---|
| **Backend** | `backend/` | Core infrastructure: APIs, database, event bus, deterministic rules |
| **Executive Agent** | `executive/` | Agentic orchestrator that coordinates between subsystems |
| **MoZo** | `mozo/` | Tag-anchor proximity monitoring for patient location |
| **Transcription** | `transcription/` | 24/7 audio transcription with speaker diarization |
| **Scheduling** | `scheduling/` | Calendar and care scheduling (see also `halo_scheduling_system`) |
| **Shared** | `shared/` | Common types, event schemas, and utilities |

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed design notes.
