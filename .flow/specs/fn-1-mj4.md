# Implement Frontend Admin UI

## Overview

Build a read-only admin/debug UI for browsing all backend data tables. The frontend is an internal tool — no auth, no CRUD forms, no pagination. Six table views displaying data fetched from the backend's `/api/v1/admin/*` endpoints, with a persistent navbar for navigation.

**Tech decision:** Plain HTML + vanilla JS + Pico CSS (classless). React is overkill for 6 identical read-only tables with no forms, state management, or interactivity beyond navigation. Zero build step — serve static files directly from FastAPI via `StaticFiles` mount.

## Scope

**In scope:**
- Single `index.html` with hash-based routing (`#/accounts`, `#/anchors`, etc.)
- Persistent navbar with 6 links (Accounts, Anchors, Tags, Associations, Calendars, Preferences)
- Generic table renderer with explicit per-resource column definitions (not derived from JSON keys)
- Loading and error states for each table
- Display formatting: null as dash, arrays as comma-separated, objects as JSON.stringify, raw ISO timestamps and UUIDs
- Pico CSS for styling (classless — styles semantic HTML directly)
- Static file serving from FastAPI (`StaticFiles` mount at `/static` prefix, with root redirect)
- FastAPI backend wiring: mount static files, ensure API route precedence

**Out of scope:**
- Authentication / authorization
- Create / edit / delete operations
- Pagination, sorting, filtering
- React or any JS framework
- Build tooling (Vite, Webpack, etc.)

## Approach

- **Routing:** Hash-based (`window.location.hash` + `hashchange` event). No server-side route handling needed. Root `/` redirects to `/static/index.html`, and client-side hash routing defaults to `#/accounts`.
- **Structure:** ES modules with no build step:
  ```
  frontend/static/
    index.html
    css/pico.min.css
    js/
      app.js       (router + init)
      api.js       (fetch wrapper with error handling)
      table.js     (generic table renderer)
      columns.js   (per-resource column definitions)
  ```
- **Column definitions:** Explicit column lists per resource in `columns.js`. This ensures table headers render correctly even when the API returns an empty array (`[]`). Column keys match the backend model field names from `ARCHITECTURE.md:72-136`.
- **Table rendering:** Generic function takes column definitions + rows, builds `<table>` via DOM APIs. Uses `textContent` (not `innerHTML`) for XSS safety.
- **Value formatting:** `null/undefined` renders as `—`, arrays render as comma-separated strings of formatted elements, plain objects render as `JSON.stringify(value)`, primitives render as `String(value)`.
- **Active link:** Uses `aria-current="page"` attribute on the active navbar `<a>` element (Pico CSS recognizes this for styling).
- **Serving:** FastAPI mounts static files at `/static` prefix (not root `/`) to avoid shadowing `/api/*`, `/docs`, and `/openapi.json`. A root route (`GET /`) redirects to `/static/index.html`. All API routers are registered before the static mount.
- **CSS:** Pico CSS classless framework — `<table>`, `<nav>`, `<a>` styled automatically.

## Display conventions

| Case | Rendering |
|------|-----------|
| `null` / `undefined` | Dash (`—`) |
| Arrays (e.g. `alert_types`) | Comma-separated string of formatted elements |
| Plain objects | `JSON.stringify(value)` |
| Primitives | `String(value)` |
| UUIDs | Full display (debug tool) |
| Timestamps | Raw ISO 8601 (debug tool) |
| Enums (visibility, status, sync_status) | Raw string value |
| Empty table (`[]` response) | Table headers from column definitions + "No records found" message |

## Risks / Dependencies

- **Backend dependency:** Admin API routes must exist for the frontend to fetch real data. Frontend can be developed against mock/stub data first.
- **FastAPI static mount:** Backend must register API routers first, then mount `StaticFiles` at `/static` to avoid route shadowing. Root redirect from `/` to `/static/index.html` handled by a simple route.
- **Column definitions maintenance:** If backend models add/remove fields, `columns.js` must be updated to match. Acceptable trade-off for correct empty-table rendering.
- **Large datasets:** No pagination means browser may struggle with very large tables (>5000 rows). Acceptable risk — admin tables are expected to be small.

## Acceptance

- [ ] All 6 routes load and display correct table data from admin endpoints
- [ ] Navbar is persistent across all routes with active link via `aria-current="page"`
- [ ] Root URL redirects to `/static/index.html`, which defaults to `#/accounts`
- [ ] Empty tables show column headers (from definitions) + "No records found" (not an error)
- [ ] HTTP non-OK errors show status code + message
- [ ] Network failures show transport error message (no status code)
- [ ] Loading state visible while fetching
- [ ] Null values display as dash, arrays as comma-separated, objects as JSON.stringify
- [ ] Uses `textContent` for cell values (XSS-safe)
- [ ] No build step — static files served directly
- [ ] FastAPI mounts static files at `/static`, API routers registered first
- [ ] `fetchAdmin` validates `Array.isArray(data)` and handles non-JSON error responses
- [ ] Smoke tests and data display tests pass

## Test notes

- **Strategy:** Playwright tests run against FastAPI serving both API and static files. API responses mocked via Playwright `page.route("**/api/v1/admin/**", ...)` to fulfill deterministic JSON, allowing tests without a seeded database.
- **Smoke tests:** Each route loads, navbar renders all 6 links, navbar links navigate correctly
- **Data display tests:** Each page fetches correct admin endpoint, table renders correct columns per column definitions, rows match mock data, empty state renders column headers + "No records found"
- **Error tests:** Mocked 500 response shows error message with status code, mocked network failure shows error

## Quick commands

```bash
# Start FastAPI backend (serves API + static frontend)
cd backend && uvicorn main:app --host 127.0.0.1 --reload

# Open frontend in browser
open http://127.0.0.1:8000/static/index.html

# Run Playwright frontend tests
npx playwright test frontend/tests/
```

## References

- `frontend/SPEC.md` — original frontend spec
- `frontend/TESTING.md` — testing strategy
- `backend/api/SPEC.md:80-92` — admin endpoint definitions
- `ARCHITECTURE.md:72-136` — data model field definitions
- Pico CSS: https://picocss.com/
