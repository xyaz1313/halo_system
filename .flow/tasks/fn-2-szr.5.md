# fn-2-szr.5 Event bus, structured logging, and admin routes

## Description

Implement the in-process event bus (publish/subscribe/unsubscribe) with reset capability for tests, structured JSON logging integrated with uvicorn loggers, and all 6 admin dump routes.

**Size:** M
**Files:**
- `backend/events/bus.py` (EventBus class with reset method)
- `backend/events/types.py` (event type constants)
- `backend/logging/config.py` (JSON formatter, logger setup for app + uvicorn)
- `backend/api/admin.py` (6 admin GET routes)
- Update `backend/main.py` to include admin router and call logging setup in lifespan

## Approach

- Event bus: dict-based singleton mapping event type strings to handler lists. `publish(event_type, **data)`, `subscribe(event_type, handler)`, `unsubscribe(event_type, handler)` (idempotent — no error if handler not found). `reset()` clears all subscriptions (for test isolation).
- Handler exceptions: catch, log the error, continue to next handler (never propagate to publisher)
- Event types as string constants in `types.py`: mozo.departure, mozo.return, transcript.segment_ready, calendar.sync_complete, calendar.conflict, schedule.confirmation_needed, schedule.confirmed, schedule.denied
- Structured logging: custom JSON formatter applied to root logger and uvicorn loggers (`uvicorn`, `uvicorn.access`). Single handler per logger with `propagate=False` on uvicorn loggers to prevent double-logging. Log entries: timestamp, level, category, message, data.
- Logging setup called once during FastAPI lifespan startup
- Admin routes: 6 GET endpoints at `/api/v1/admin/` returning `session.exec(select(Model)).all()` as JSON arrays. No filtering, no pagination. Empty tables return 200 + `[]`.

## Key context

- Per `backend/events/SPEC.md`: 8 event types, sync handlers, in-process only
- Per `backend/logging/SPEC.md`: structured JSON, categories per subsystem
- Uvicorn has its own loggers — must configure them explicitly or they emit non-JSON output alongside your JSON logs
- Event bus singleton: each FastAPI worker gets its own instance — acceptable for single-worker dev
- `unsubscribe` should be idempotent (no error if handler not found) for clean test teardown
- Admin routes are the simplest layer — just select-all queries on each model

## Acceptance
- [ ] Event bus publish/subscribe/unsubscribe works
- [ ] `reset()` clears all subscriptions
- [ ] Publishing calls all registered handlers for that event type
- [ ] Handler exceptions are caught and logged, don't block other handlers
- [ ] `unsubscribe` is idempotent
- [ ] All 8 event type constants defined
- [ ] Structured JSON logging outputs to stdout
- [ ] Uvicorn loggers configured with JSON formatter, `propagate=False` (no double-logging)
- [ ] Log entries include timestamp, level, category, message fields
- [ ] All 6 admin routes return 200 with JSON arrays
- [ ] Admin routes return empty arrays when tables are empty
- [ ] Admin routes registered at `/api/v1/admin/*`

## Done summary
TBD

## Evidence
- Commits:
- Tests:
- PRs:
