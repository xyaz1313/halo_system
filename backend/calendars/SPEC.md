# Calendars Spec

Manages external calendar connections and sync state. SQLModel table.

## Model: Calendar

### Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | UUID | auto | PK |
| `account_id` | UUID (FK → Account) | yes | |
| `provider` | str | yes | e.g., "google" |
| `external_calendar_id` | str | yes | ID from the provider |
| `sync_status` | str | yes | `"syncing"` / `"synced"` / `"error"`. Default: `"syncing"` |
| `last_synced_at` | datetime | no | Null until first successful sync |
| `created_at` | datetime | auto | |
| `updated_at` | datetime | auto | |

### Service Functions

- `create_calendar(session, account_id, provider, external_calendar_id) → Calendar`
- `get_calendar(session, id) → Calendar | None`
- `list_calendars_for_account(session, account_id) → list[Calendar]`
- `update_sync_status(session, id, status, last_synced_at=None) → Calendar`
- `delete_calendar(session, id) → None`

### Constraints

- An account can have multiple calendars.
- Same external calendar can be linked to multiple accounts.
- `provider` and `external_calendar_id` are immutable after creation.
