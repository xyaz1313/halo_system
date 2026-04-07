# Frontend Spec

Bare-bones admin/debug UI for browsing backend data. No auth, no security — internal use only.

## Purpose

A simple way to view and browse all backend tables without needing to query the API manually or look at the DB directly.

## Tech

- **React** or **plain HTML + JS** — TBD, whatever gets us there fastest
- Talks to the backend REST API (`/api/v1/...`)

## Pages

| Page | Route | Description |
|---|---|---|
| Home | `/` | Links to each table browser |
| Accounts | `/accounts` | List all accounts, click to view detail |
| Account Detail | `/accounts/{id}` | Show account fields + linked tags, anchors, calendars, preferences |
| Anchors | `/anchors` | List all anchors, show visibility, status |
| Tags | `/tags` | List all tags, show account, status |
| Calendars | `/calendars` | List all calendars, show sync status |
| Notifications | `/notifications` | List all notification preferences |

## Features

- Table view for each model (sortable columns)
- Click a row to see full detail
- Detail pages show related records (e.g., account detail shows its tags, anchors, calendars)
- No create/edit/delete from the UI for now — read-only browser

## Notes

- No auth, no login, no roles
- Designed for local dev / internal debugging
- Can evolve into a real admin panel later
