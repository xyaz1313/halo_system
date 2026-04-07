# API Spec

REST API built with FastAPI. All responses are JSON.

Base path: `/api/v1`

---

## Accounts

| Method | Path | Description |
|---|---|---|
| `POST` | `/accounts` | Create a new account |
| `GET` | `/accounts` | List all accounts |
| `GET` | `/accounts/{id}` | Get account by ID |
| `PATCH` | `/accounts/{id}` | Update account fields |
| `DELETE` | `/accounts/{id}` | Delete account (cascades) |

---

## Anchors

| Method | Path | Description |
|---|---|---|
| `POST` | `/anchors` | Register a new anchor |
| `GET` | `/anchors` | List all anchors (filterable by `account_id` — returns public + private owned) |
| `GET` | `/anchors/{id}` | Get anchor by ID |
| `PATCH` | `/anchors/{id}` | Update anchor (label, threshold, status, visibility) |
| `DELETE` | `/anchors/{id}` | Delete anchor (cascades associations) |

---

## Tags

| Method | Path | Description |
|---|---|---|
| `POST` | `/tags` | Register a new tag (requires `account_id`) |
| `GET` | `/tags` | List tags (filterable by `account_id`) |
| `GET` | `/tags/{id}` | Get tag by ID |
| `PATCH` | `/tags/{id}` | Update tag (label, status) |
| `DELETE` | `/tags/{id}` | Delete tag (cascades associations) |

---

## Anchor-Tag Associations

| Method | Path | Description |
|---|---|---|
| `POST` | `/anchors/{anchor_id}/tags/{tag_id}` | Link a tag to an anchor (validates access) |
| `DELETE` | `/anchors/{anchor_id}/tags/{tag_id}` | Unlink a tag from an anchor |
| `GET` | `/anchors/{anchor_id}/tags` | List all tags linked to an anchor |
| `GET` | `/tags/{tag_id}/anchors` | List all anchors linked to a tag |

---

## Calendars

| Method | Path | Description |
|---|---|---|
| `POST` | `/calendars` | Add a calendar (requires `account_id`, `provider`, `external_calendar_id`) |
| `GET` | `/calendars` | List calendars (filterable by `account_id`) |
| `GET` | `/calendars/{id}` | Get calendar by ID |
| `PATCH` | `/calendars/{id}` | Update sync status |
| `DELETE` | `/calendars/{id}` | Remove calendar link |

---

## Notification Preferences

| Method | Path | Description |
|---|---|---|
| `POST` | `/notifications/preferences` | Create a notification preference |
| `GET` | `/notifications/preferences` | List preferences (filterable by `account_id`) |
| `GET` | `/notifications/preferences/{id}` | Get preference by ID |
| `PATCH` | `/notifications/preferences/{id}` | Update preference (email, alert types) |
| `DELETE` | `/notifications/preferences/{id}` | Delete preference |

---

## Admin (Frontend Data)

Simple dump routes for the frontend table browser. No filtering, no pagination — just return everything.

| Method | Path | Description |
|---|---|---|
| `GET` | `/admin/accounts` | All accounts |
| `GET` | `/admin/anchors` | All anchors |
| `GET` | `/admin/tags` | All tags |
| `GET` | `/admin/associations` | All anchor-tag associations |
| `GET` | `/admin/calendars` | All calendars |
| `GET` | `/admin/preferences` | All notification preferences |

---

## Notes

- FastAPI auto-generates OpenAPI/Swagger docs at `/docs`
- All IDs are UUIDs
- `PATCH` endpoints accept partial updates (only fields provided are changed)
- List endpoints support query parameter filtering (e.g., `GET /tags?account_id=...`)
- Standard error responses: 404 (not found), 422 (validation error), 400 (business rule violation like linking a tag to an inaccessible anchor)
