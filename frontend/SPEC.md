# Frontend Spec

Bare-bones admin/debug UI for browsing backend data. No auth, no security — internal use only.

## Purpose

A simple way to view and browse all backend tables without needing to query the API manually or look at the DB directly.

## Tech

- **React** or **plain HTML + JS** — TBD, whatever gets us there fastest
- Talks to backend admin routes (`/api/v1/admin/...`)

## Layout

- **Navbar** at the top, persistent across all pages
  - Links: Accounts | Anchors | Tags | Associations | Calendars | Preferences
- **Content area** below the navbar

## Routes & Pages

| Frontend Route | Backend Route | Description |
|---|---|---|
| `/` | — | Home / redirect to `/accounts` |
| `/accounts` | `GET /api/v1/admin/accounts` | Table of all accounts |
| `/anchors` | `GET /api/v1/admin/anchors` | Table of all anchors |
| `/tags` | `GET /api/v1/admin/tags` | Table of all tags |
| `/associations` | `GET /api/v1/admin/associations` | Table of all anchor-tag associations |
| `/calendars` | `GET /api/v1/admin/calendars` | Table of all calendars |
| `/preferences` | `GET /api/v1/admin/preferences` | Table of all notification preferences |

## Page Behavior

- Each page fetches its table data on load from the corresponding admin route
- Renders as a simple table — one column per field, one row per record
- No create/edit/delete — read-only
- No pagination or filtering for now

## Notes

- No auth, no login, no roles
- Designed for local dev / internal debugging
- Can evolve into a real admin panel later
