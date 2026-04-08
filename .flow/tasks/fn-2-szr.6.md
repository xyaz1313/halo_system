# fn-2-szr.6 Comprehensive test suite

## Description

Write the full pytest test suite covering all three layers: model/service tests, API endpoint tests, and admin route tests. Uses Starlette TestClient (from `fastapi.testclient`), in-memory SQLite with StaticPool and foreign_keys=ON. This is where cascade delete and cross-model business rules are verified.

**Size:** M
**Files:**
- `backend/tests/__init__.py`
- `backend/tests/conftest.py` (engine, session, client, sample data fixtures, event bus reset)
- `backend/tests/test_accounts.py`
- `backend/tests/test_devices.py`
- `backend/tests/test_calendars.py`
- `backend/tests/test_notifications.py`
- `backend/tests/test_events.py`
- `backend/tests/test_admin.py`
- `backend/tests/test_api_accounts.py`
- `backend/tests/test_api_devices.py`
- `backend/tests/test_api_calendars.py`
- `backend/tests/test_api_notifications.py`

## Approach

- conftest.py: in-memory SQLite engine with `StaticPool`, `check_same_thread=False`. Connect event enables `PRAGMA foreign_keys=ON`. Session fixture creates tables, yields session, drops tables. Client fixture uses `TestClient(app)` with `get_db` dependency override. Event bus `reset()` called in fixture.
- Sample data fixtures: `sample_account`, `sample_anchor_public`, `sample_anchor_private`, `sample_tag` — created via service functions, committed to session
- Model/service tests: test CRUD operations and business rules directly against DB session
  - Account: create, get, get_by_email, list, update, delete, duplicate email error
  - Devices: anchor visibility rules, tag CRUD, association access validation, duplicate association error, list_anchors_for_account
  - Calendars: CRUD, immutability enforcement on update
  - Notifications: CRUD, alert_types validation, schedule_confirmation auto-include, JSON round-trip
  - Events: publish/subscribe, handler exception isolation, unsubscribe idempotent, reset
- API tests: full HTTP round-trips via TestClient
  - Status codes for all success and error cases (201, 200, 204, 404, 409, 422, 400)
  - Response body shapes
- Admin tests: all 6 endpoints return correct data, empty tables return `[]`
- **Cascade tests**: delete account, verify tags/calendars/preferences AND private anchors are cascade-deleted (this is the first place cascades are fully testable)

## Key context

- Use `from fastapi.testclient import TestClient` (Starlette-based, sync) — NOT httpx directly
- StaticPool ensures single connection shared across test thread — required for in-memory SQLite
- `PRAGMA foreign_keys=ON` must also be set in test engine (same connect event pattern as prod)
- Event bus reset fixture prevents handler leakage between tests
- Cascade delete tests: create account with tags/calendars/preferences, delete account, verify children gone
- Edge cases: duplicate email (409), duplicate association (409), visibility change coupling (422), immutable calendar fields (422), unknown alert_types (422), access denied on association (400)

## Acceptance
- [ ] `pytest backend/tests/ -v` runs all tests and passes
- [ ] conftest.py provides engine, session, client, sample data, and event bus reset fixtures
- [ ] Model/service tests cover all CRUD operations for each module
- [ ] Model/service tests cover business rules: visibility, access validation, immutability, alert_types validation
- [ ] Cascade delete test: delete account verifies tags, calendars, preferences, and private anchors are gone
- [ ] API tests verify correct status codes for success and error cases
- [ ] Admin route tests verify all 6 endpoints return correct data
- [ ] Admin route tests verify empty table returns 200 + empty array
- [ ] Event bus tests verify publish/subscribe, handler exception isolation, reset
- [ ] All tests use in-memory SQLite with StaticPool and foreign_keys=ON

## Done summary
Comprehensive pytest test suite covering all three layers (model/service, API endpoint, admin routes) with 129 tests. Includes cascade delete verification, event bus tests, and enforces calendar immutability at the API layer via Pydantic extra='forbid'.
## Evidence
- Commits: a76904f, b673c71
- Tests: python3 -m pytest backend/tests/ -v
- PRs: