# fn-1-mj4.1 Frontend scaffolding, routing, navbar, and table views

## Description
Set up the complete frontend as a vanilla JS application served as static files from FastAPI. Includes project scaffolding, hash-based routing, persistent navbar, explicit column definitions, generic table renderer, all 6 table pages with display formatting, error/loading states, and the FastAPI static mount wiring.

**Size:** M
**Files:**
- `frontend/static/index.html`
- `frontend/static/css/pico.min.css` (vendored or CDN link in HTML)
- `frontend/static/js/app.js` (router + init)
- `frontend/static/js/api.js` (fetch wrapper with error handling)
- `frontend/static/js/table.js` (generic table renderer)
- `frontend/static/js/columns.js` (per-resource column definitions)
- Backend: add `StaticFiles` mount at `/static` and root redirect (in `main.py` or equivalent)

## Approach

- Single `index.html` with `<nav>` (6 links), `<main>` content area, and `<script type="module">` entry point
- Hash routing via `hashchange` event listener in `app.js`. Default hash is `#/accounts`
- Active navbar link uses `aria-current="page"` attribute (Pico CSS recognizes this for styling)
- `columns.js` exports a map of resource name to ordered column key arrays, matching backend model fields from `ARCHITECTURE.md:72-136`
- `api.js` exports a `fetchAdmin(endpoint)` function that:
  - Calls `GET /api/v1/admin/{endpoint}` with `Accept: application/json` header
  - On HTTP non-OK response: throws error with HTTP status code + best-effort body text
  - On network failure (fetch throws): throws error with transport error message (no status code)
  - On OK response: parses JSON and validates `Array.isArray(data)`, throws if not
- `table.js` exports a `renderTable(container, columns, rows)` function that:
  - Uses column definitions (not `Object.keys`) for headers — works even with empty arrays
  - Builds `<table>` via DOM APIs using `DocumentFragment`
  - Uses `textContent` for all cell values (XSS-safe)
  - Value formatting: `null/undefined` as `—`, arrays as comma-separated, objects as `JSON.stringify`, primitives as `String(value)`
  - Empty arrays: shows column headers + "No records found" row
- FastAPI wiring: register all API routers first, then mount `StaticFiles` at `/static` prefix, add root `GET /` redirect to `/static/index.html`
- Pico CSS for all styling — no custom CSS classes needed
- Loading state: "Loading..." text in content area while fetch is in-flight
- Error state: HTTP errors show "Failed to load: {status} {message}", network failures show "Network error: {message}"

## Key context

- Mount static files at `/static` (not `/`) to avoid shadowing `/api/*`, `/docs`, `/openapi.json` routes
- Use `aria-current="page"` for active nav link — Pico CSS styles this automatically
- `DocumentFragment` for building table rows avoids layout thrashing on large tables
- Pico CSS (https://picocss.com/) styles `<table>`, `<nav>`, `<a>` elements directly with zero classes
- Column definitions from `ARCHITECTURE.md`: Account (10 fields), Anchor (8), Tag (6), AnchorTagAssociation (3), Calendar (8), NotificationPreference (6)

## Acceptance
- [ ] `frontend/static/index.html` loads in browser via `http://127.0.0.1:8000/static/index.html` with styled navbar and content area
- [ ] Hash routing works for all 6 routes
- [ ] Root URL (no hash) defaults to `#/accounts`
- [ ] Navbar shows 6 links, active link uses `aria-current="page"`
- [ ] Each route fetches from correct `/api/v1/admin/{resource}` endpoint
- [ ] Table columns come from explicit column definitions in `columns.js`
- [ ] Empty table shows column headers plus No records found message
- [ ] Null values display as dash, arrays as comma-separated, objects as JSON.stringify
- [ ] `fetchAdmin` sets Accept header, validates Array.isArray, handles non-JSON errors with status
- [ ] HTTP non-OK errors show status code + message
- [ ] Network failures show transport error message (no status code)
- [ ] Loading indicator shown while fetch is in-flight
- [ ] All cell values use textContent, not innerHTML
- [ ] FastAPI mounts static files at `/static`, API routers registered first
- [ ] Root GET `/` redirects to `/static/index.html`
- [ ] No build step required, files are plain HTML/CSS/JS

## Done summary
Added complete frontend admin UI scaffolding: index.html with hash-based routing for 6 table views (accounts, anchors, tags, associations, calendars, preferences), ES module JS files (app.js router, api.js fetch wrapper, table.js generic renderer, columns.js definitions), vendored Pico CSS, and FastAPI StaticFiles mount at /static with root redirect.
## Evidence
- Commits: ed47a8ea0c55c15b4d827c373fd51712231709ba
- Tests: python3 -m pytest backend/tests/ -x -q (137 passed), python3 -c 'from backend.main import app' (import check), FastAPI TestClient verification of static serving and root redirect
- PRs: