# Backend Testing Spec

## Framework

- **pytest** as the test runner
- **httpx** for async API testing (FastAPI's recommended test client)
- SQLite in-memory database for test isolation

## Test Structure

```
backend/
├── tests/
│   ├── conftest.py          # shared fixtures (db session, test client, sample data)
│   ├── test_accounts.py     # account model + service tests
│   ├── test_devices.py      # anchor, tag, association tests
│   ├── test_calendars.py    # calendar model + service tests
│   ├── test_notifications.py # notification preference tests
│   ├── test_api_accounts.py  # account API endpoint tests
│   ├── test_api_devices.py   # device API endpoint tests
│   ├── test_api_calendars.py # calendar API endpoint tests
│   ├── test_api_notifications.py # notification API endpoint tests
│   └── test_api_admin.py    # admin route tests
```

## Test Layers

### 1. Model / Service Tests

Test the service functions directly against the DB (no HTTP).

**Accounts:**
- Create account with required fields
- Create account with optional caretaker fields
- Reject duplicate email
- Get account by ID
- Get account by email
- Update account fields
- Delete account cascades (tags, calendars, preferences removed)

**Devices:**
- Create public anchor (no owner)
- Create private anchor (with owner)
- Reject private anchor without owner
- Reject public anchor with owner
- Create tag for account
- Link tag to public anchor
- Link tag to private anchor owned by same account
- Reject linking tag to private anchor owned by different account
- Delete anchor cascades associations
- Delete tag cascades associations
- List anchors visible to account (public + owned private)

**Calendars:**
- Create calendar for account
- List calendars for account
- Update sync status
- Delete calendar

**Notifications:**
- Create preference with alert types
- List preferences for account
- Update alert email
- Update alert types
- Delete preference

### 2. API Endpoint Tests

Test the HTTP layer — request/response, status codes, validation errors.

For each resource:
- `POST` returns 201 + created object
- `GET` list returns 200 + array
- `GET` by ID returns 200 + object
- `GET` by bad ID returns 404
- `PATCH` returns 200 + updated object
- `PATCH` bad ID returns 404
- `DELETE` returns 204
- `DELETE` bad ID returns 404
- Validation errors return 422

### 3. Admin Route Tests

- Each admin route returns 200 + full table contents
- Empty tables return 200 + empty array
- Data created via service functions appears in admin responses

## Fixtures (conftest.py)

- `db_session` — fresh in-memory SQLite session per test
- `client` — FastAPI test client wired to the test DB
- `sample_account` — a pre-created account
- `sample_anchor_public` — a public anchor
- `sample_anchor_private` — a private anchor owned by `sample_account`
- `sample_tag` — a tag belonging to `sample_account`

## Running Tests

```bash
pytest backend/tests/ -v
```
