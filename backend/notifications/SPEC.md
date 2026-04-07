# Notifications Spec

Manages notification preferences and email delivery. SQLModel table.

## Model: NotificationPreference

### Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | UUID | auto | PK |
| `account_id` | UUID (FK → Account) | yes | |
| `alert_email` | str | yes | Where to send alerts |
| `alert_types` | list[str] | yes | Stored as JSON column. Which events trigger emails. |
| `created_at` | datetime | auto | |
| `updated_at` | datetime | auto | |

### Service Functions

- `create_preference(session, account_id, alert_email, alert_types) → NotificationPreference`
- `get_preference(session, id) → NotificationPreference | None`
- `list_preferences_for_account(session, account_id) → list[NotificationPreference]`
- `update_preference(session, id, **kwargs) → NotificationPreference`
- `delete_preference(session, id) → None`

### Alert Types (initial set)

| Type | Trigger | Mode |
|---|---|---|
| `mozo_departure` | Tag signal drops below anchor threshold | One-way alert |
| `schedule_confirmation` | Executive agent proposes a scheduling change | Interactive (confirm/deny via email link) |
| `schedule_conflict` | Calendar sync detects a conflict | One-way alert |

### Constraints

- An account can have multiple preferences (e.g., different emails for different alert types).
- Scheduling confirmations are always enabled — no opt-out.

### Notes

- `alert_types` stored as JSON array in the DB column.
- Email delivery mechanism TBD (SMTP, SendGrid, SES, etc.).
- Interactive confirmations include a link back to the backend API to approve/deny.
