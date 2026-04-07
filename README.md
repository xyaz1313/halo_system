# Halo System

A tracking and assistance system for dementia patients.

## Components

| Component | Directory | Description |
|---|---|---|
| **Backend** | `backend/` | Central hub: APIs, database, event bus, calendar sync, deterministic rules. All subsystems go through here. |
| **Executive Agent** | `executive/` | Agentic orchestrator that coordinates between subsystems |
| **MoZo** | `mozo/` | Tag-anchor proximity monitoring for patient location |
| **Transcription** | `transcription/` | 24/7 audio transcription with speaker diarization |
| **Shared** | `shared/` | Common types, event schemas, and utilities |

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed design notes.
