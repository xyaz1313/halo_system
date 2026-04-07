# Events Spec

Internal event bus for subsystem communication. Events drive behavior — when something happens, other parts of the system react.

**Status: Initial spec — likely to evolve as subsystems are built out.**

## Event Structure

Each event has:
- `event_type` — string identifier (e.g., `mozo.departure`)
- `source` — which subsystem emitted it
- `account_id` — which account this relates to
- `payload` — event-specific data (dict)
- `timestamp` — when it occurred

## Event Types (initial set)

| Event | Source | Consumers | Description |
|---|---|---|---|
| `mozo.departure` | MoZo | Rules, Executive | Tag signal dropped below threshold |
| `mozo.return` | MoZo | Rules, Executive | Tag signal recovered |
| `transcript.segment_ready` | Transcription | Memory, Executive | New transcript chunk available |
| `calendar.sync_complete` | Calendars | Executive | Calendar finished syncing |
| `calendar.conflict` | Calendars | Notifications, Executive | Conflicting events detected |
| `schedule.confirmation_needed` | Executive | Notifications | Agent wants to make a scheduling change, needs approval |
| `schedule.confirmed` | Notifications | Executive | User approved a scheduling change |
| `schedule.denied` | Notifications | Executive | User denied a scheduling change |

## Implementation

- Start simple: in-process pub/sub (publish/subscribe pattern)
- Handlers register for event types they care about
- Synchronous to start, async later if needed
- Can be swapped for Redis pub/sub, NATS, etc. if we need cross-process communication

## Interface

- `publish(event)` — emit an event to all registered handlers
- `subscribe(event_type, handler)` — register a handler for an event type
- `unsubscribe(event_type, handler)` — remove a handler
