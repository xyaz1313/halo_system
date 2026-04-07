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

### 5. Backend
- **Directory**: `backend/`
- **Purpose**: Central hub — all subsystems communicate through the backend. Owns APIs, database, event routing, calendar sync, and deterministic rules.
- **Submodules**:
  - `api/` — REST/WebSocket endpoints
  - `db/` — models and migrations
  - `events/` — event bus / message routing between subsystems
  - `rules/` — deterministic routing logic (e.g., MoZo threshold → alert)
  - `calendars/` — external calendar sync (Google Calendar, etc.), internal calendar store
- **Role**: Single source of truth. MoZo, transcription, and the executive agent all read/write through backend APIs. Calendars are added and synced here.

## Repository Structure

```
halo_system/
├── ARCHITECTURE.md
├── docker-compose.yml
├── backend/
│   ├── api/
│   ├── calendars/
│   ├── db/
│   ├── events/
│   └── rules/
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
├── scheduling/
└── shared/
```
