# Halo System Architecture

A system designed to track and assist dementia patients.

## Components

### 1. Scheduling Tool
- **Directory**: `scheduling/`
- **Prior work**: `halo_scheduling_system` repo
- **Purpose**: Scheduling logic and decision-making tool used by the executive agent
- **How it works**: The executive agent calls into the scheduling tool to make decisions about patient care timing — e.g., when to schedule activities, resolve conflicts, suggest rescheduling. Reads calendar data from the backend, returns scheduling decisions.
- **Relationship**: Consumes calendar data from `backend/calendars/`, used by `executive/`

### 2. MoZo (Tag-Anchor Proximity System)
- **Directory**: `mozo/`
- **Purpose**: Patient proximity monitoring using a tag-anchor system
- **How it works**: Patient wears a small tag; a stationary anchor monitors signal strength. If RSSI drops below a configured threshold, the patient is considered to have left the area.
- **Key concepts**: Tag (patient-worn), Anchor (stationary receiver), signal threshold, departure detection

### 3. Audio Transcription & Diarization Pipeline
- **Directory**: `transcription/`
- **Purpose**: Continuous transcription of 24/7 ambient audio with speaker identification
- **How it works**: Ingests a continuous audio stream from the patient's environment, performs real-time (or near-real-time) speech-to-text transcription, and applies speaker diarization to label/identify distinct speakers across conversations.
- **Key concepts**: Streaming audio ingestion, ASR (automatic speech recognition), speaker diarization, speaker ID assignment, continuous operation
- **Status**: Early/exploratory — architecture and tooling TBD
- **Open questions**:
  - ASR engine selection (local vs cloud, latency vs accuracy tradeoffs)
  - Diarization approach (online vs batch, how to persist speaker IDs across sessions)
  - Streaming output format and downstream consumers

### 4. Executive Agent (OpenClaw-style Orchestrator)
- **Directory**: `executive/`
- **Purpose**: Central orchestration layer that coordinates between all other subsystems
- **How it works**: An agentic system (inspired by OpenClaw patterns) that acts as the decision-making executive — receiving signals from MoZo, transcription, scheduling, etc. and deciding what actions to take. Mix of LLM-driven reasoning and deterministic logic where appropriate.
- **Key concepts**: Inter-system coordination, event-driven decision making, deterministic routing where possible, agentic fallback for ambiguous situations
- **Design considerations**:
  - Which decisions should be hard-coded/deterministic vs. LLM-mediated
  - How subsystems report events to the executive (event bus, polling, direct calls)
  - Action space — what can the executive actually *do* in response to events

### 5. Memory (Storage & Retrieval)
- **Directory**: `memory/`
- **Purpose**: Long-term knowledge store for patient context, conversation history, and extracted information
- **How it works**: Receives structured data from the transcription pipeline and executive agent. Supports storage and semantic retrieval so the executive agent can query relevant context when making decisions.
- **Key concepts**: Memory ingestion, semantic search/retrieval, patient context over time
- **Relationship**: Written to by `transcription/` and `executive/`, queried by `executive/`

### 6. Backend
- **Directory**: `backend/`
- **Purpose**: Central hub — all subsystems communicate through the backend. Owns APIs, database, event routing, calendar sync, and deterministic rules.
- **Submodules**:
  - `accounts/` — account management (email, patient info, optional caretaker info). Top-level entity that all other data hangs off of.
  - `api/` — REST/WebSocket endpoints
  - `core/` — base abstractions, shared backend patterns, service/repository interfaces
  - `db/` — models and migrations
  - `calendars/` — external calendar sync (Google Calendar, etc.), internal calendar store
  - `devices/` — MoZo anchor/tag registry, associations, signal history. Anchors have a visibility model: public (visible to all) or private (scoped to specific accounts).
  - `events/` — event bus / message routing between subsystems
  - `rules/` — deterministic routing logic (e.g., MoZo threshold → alert)
  - `notifications/` — email-based communication with caregivers/patients. Two modes: one-way alerts (e.g., MoZo departure) and interactive confirmations (e.g., "approve this scheduling change?")
- **Role**: Single source of truth. MoZo, transcription, and the executive agent all read/write through backend APIs. Calendars are added and synced here.

## Data Models

### Account
| Field | Type | Notes |
|---|---|---|
| `id` | UUID (PK) | |
| `email` | string | Account login / primary contact |
| `patient_name` | string | |
| `patient_age` | int | |
| `patient_diagnosis_stage` | string | |
| `patient_notes` | text | |
| `caretaker_name` | string (optional) | |
| `caretaker_email` | string (optional) | |
| `created_at` | timestamp | |
| `updated_at` | timestamp | |

### Anchor
| Field | Type | Notes |
|---|---|---|
| `id` | UUID (PK) | |
| `label` | string | Friendly name (e.g., "Kitchen", "Front Door") |
| `visibility` | enum | `public` or `private` |
| `owner_account_id` | FK → Account (nullable) | Required if private, null if public |
| `signal_threshold` | float | RSSI cutoff for departure detection |
| `status` | enum | `active` / `inactive` |
| `created_at` | timestamp | |
| `updated_at` | timestamp | |

### Tag
| Field | Type | Notes |
|---|---|---|
| `id` | UUID (PK) | |
| `account_id` | FK → Account | |
| `label` | string (optional) | Friendly name |
| `status` | enum | `active` / `inactive` |
| `created_at` | timestamp | |
| `updated_at` | timestamp | |

### AnchorTagAssociation
| Field | Type | Notes |
|---|---|---|
| `anchor_id` | FK → Anchor | Composite PK |
| `tag_id` | FK → Tag | Composite PK |
| `created_at` | timestamp | |

### Calendar
| Field | Type | Notes |
|---|---|---|
| `id` | UUID (PK) | |
| `account_id` | FK → Account | |
| `provider` | string | e.g., "google" |
| `external_calendar_id` | string | ID from the provider |
| `sync_status` | enum | `syncing` / `synced` / `error` |
| `last_synced_at` | timestamp (nullable) | |
| `created_at` | timestamp | |
| `updated_at` | timestamp | |

### NotificationPreference
| Field | Type | Notes |
|---|---|---|
| `id` | UUID (PK) | |
| `account_id` | FK → Account | |
| `alert_email` | string | Where to send alerts |
| `alert_types` | list/enum | Which events trigger emails |
| `created_at` | timestamp | |
| `updated_at` | timestamp | |

> **Design decisions**: Single caretaker per account. Private anchors owned by exactly one account. Scheduling confirmations always enabled (no toggle). Patient info stored as flat fields.

## Repository Structure

```
halo_system/
├── ARCHITECTURE.md
├── docker-compose.yml
├── backend/
│   ├── accounts/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── calendars/
│   ├── devices/
│   ├── events/
│   ├── rules/
│   └── notifications/
├── executive/
│   ├── agent/
│   └── actions/
├── mozo/
│   ├── anchor/
│   └── tag/
├── transcription/
│   ├── ingestion/
│   ├── asr/
│   └── diarization/
├── memory/
├── scheduling/
└── shared/
```
