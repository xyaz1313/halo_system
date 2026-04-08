# fn-2-szr.4 Calendar and Notification models, services, and API routes

## Description

Implement Calendar and NotificationPreference models with their service functions and API routes. Calendar has immutable fields; NotificationPreference has a JSON array column with validation and auto-inclusion of schedule_confirmation.

**Size:** M
**Files:**
- `backend/calendars/models.py` (Calendar SQLModel)
- `backend/calendars/service.py` (create, get, list_by_account, update_sync_status, delete)
- `backend/notifications/models.py` (NotificationPreference SQLModel)
- `backend/notifications/service.py` (create, get, list_by_account, update, delete)
- `backend/api/calendars.py` (calendar routes)
- `backend/api/notifications.py` (notification preference routes)
- Update `backend/models.py` to import calendars.models and notifications.models
- Update `backend/main.py` to include both routers

## Approach

- Calendar model inherits BaseModel. Fields: account_id (FK), provider, external_calendar_id, sync_status (syncing/synced/error), last_synced_at (nullable)
- Calendar immutability: service raises ValidationError if update includes provider or external_calendar_id
- NotificationPreference model inherits BaseModel. Fields: account_id (FK), alert_email, alert_types (JSON column)
- JSON column: `sa_column(Column(JSON))` — stores as TEXT in SQLite, native JSON in Postgres
- alert_types validation: values must be from known set. Unknown types raise ValidationError. Auto-include schedule_confirmation if missing. Deduplicate and preserve input order.
- Normalization: dedupe alert_types, ensure schedule_confirmation present, stable order (input order preserved, required type appended at end if missing)
- Standard CRUD routes, filterable by account_id on list endpoints (optional filter — no filter returns all)

## Key context

- Per `backend/calendars/SPEC.md`: provider and external_calendar_id are immutable after creation
- Per `backend/notifications/SPEC.md`: 3 alert types, schedule_confirmation always enabled (no opt-out)
- JSON column round-trip must work in SQLite — store as Python list, read back as Python list
- Services raise typed exceptions; routes rely on main.py exception handlers

## Acceptance
- [ ] Calendar model creates table with all fields
- [ ] Calendar update rejects provider/external_calendar_id changes (raises ValidationError -> 422)
- [ ] Calendar update allows sync_status and last_synced_at changes
- [ ] NotificationPreference model with JSON alert_types column works
- [ ] alert_types validated against known set (raises ValidationError on unknown)
- [ ] schedule_confirmation auto-included if missing, deduped
- [ ] JSON column round-trips correctly in SQLite (list in, list out)
- [ ] All CRUD routes for both models with correct status codes
- [ ] List endpoints filterable by account_id (optional)
- [ ] Models registered in `backend/models.py`

## Done summary
Implemented Calendar and NotificationPreference models, services, and API routes. Calendar enforces immutability on provider/external_calendar_id with a patchable fields allowlist. NotificationPreference validates alert_types against known set, auto-includes schedule_confirmation, deduplicates, and guards against null values.
## Evidence
- Commits: 3d262cb, 223eab1
- Tests: python3 -c 'import backend.models; ...' (model import verification), python3 -c '...' (alert_types normalization tests), python3 -c '...' (JSON round-trip + immutability + patchable fields tests)
- PRs: