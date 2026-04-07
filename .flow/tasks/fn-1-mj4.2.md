# fn-1-mj4.2 Frontend smoke and data display tests

## Description
Write Playwright browser tests for the frontend admin UI. Tests run against FastAPI serving both static files and API routes, with API responses mocked via Playwright route interception.

**Size:** M
**Files:**
- `frontend/tests/` (Playwright test files)
- `frontend/tests/mocks/` (mock JSON response data for each admin endpoint)
- `frontend/playwright.config.js` (or `.ts`)
- `frontend/package.json` (Playwright dev dependency)

## Approach

- Playwright tests run against the running FastAPI server at `http://127.0.0.1:8000` (serves both `/static/*` and `/api/*`)
- API responses mocked using `page.route("**/api/v1/admin/**", handler)` to return deterministic JSON fixtures
- Mock data includes: nullable fields (owner_account_id, last_synced_at), array fields (alert_types), and an empty response for at least one resource
- Base URL: `http://127.0.0.1:8000/static/index.html`
- Test categories:
  1. **Smoke tests:** Each of 6 hash routes loads without JS errors, navbar renders 6 links, clicking each link navigates to correct route
  2. **Data display tests:** Each page fetches correct admin endpoint (verified via route interception), table renders columns matching column definitions from `columns.js`, table rows match mock response data, empty response shows column headers + "No records found"
  3. **Error tests:** Mocked 500 response shows error message with HTTP status code, mocked network failure (abort) shows transport error message without status code

## Key context

- Playwright `page.route()` intercepts fetch requests — no need for a test backend or dependency overrides
- Mock data fixtures should match the exact field shapes from `ARCHITECTURE.md:72-136`
- Include at least one mock with null values to verify dash rendering
- Include at least one mock with alert_types array to verify comma-separated rendering
- Standardize on `http://127.0.0.1:8000` (not `localhost`) to match uvicorn bind address

## Acceptance
- [ ] Smoke test: all 6 hash routes load without JS errors
- [ ] Smoke test: navbar renders 6 links on every route
- [ ] Smoke test: clicking each navbar link navigates to the correct route
- [ ] Data test: each page fetches from correct /api/v1/admin/ endpoint (verified via route interception)
- [ ] Data test: table columns match column definitions from columns.js
- [ ] Data test: table rows match mock response data
- [ ] Data test: empty response renders column headers plus No records found
- [ ] Error test: mocked 500 response shows error message with HTTP status code
- [ ] Error test: mocked network failure shows transport error message (no status code)
- [ ] Edge case: null values render as dash
- [ ] Edge case: alert_types array renders as comma-separated string
- [ ] Tests run against FastAPI with mocked API responses via Playwright page.route
- [ ] Root `/` redirect lands on `/static/index.html` defaulting to `#/accounts`
- [ ] Active nav link sets `aria-current="page"` correctly per route

## Done summary
TBD

## Evidence
- Commits:
- Tests:
- PRs:
