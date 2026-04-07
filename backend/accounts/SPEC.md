# Accounts Spec

## Model: Account

The top-level entity. All other data (devices, calendars, notifications) belongs to an account.

SQLModel table with Pydantic validation.

### Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | UUID | auto | PK, default `uuid4()` |
| `email` | str | yes | Unique. Account login / primary contact |
| `patient_name` | str | yes | |
| `patient_age` | int | yes | |
| `patient_diagnosis_stage` | str | yes | Free text for now (e.g., "early", "moderate", "advanced") |
| `patient_notes` | str | no | Default empty string |
| `caretaker_name` | str | no | |
| `caretaker_email` | str | no | |
| `created_at` | datetime | auto | Default `utcnow` |
| `updated_at` | datetime | auto | Default `utcnow`, updated on save |

### Relationships

- One-to-many → Tag
- One-to-many → Calendar
- One-to-many → NotificationPreference
- One-to-many → Anchor (private anchors only)

### Service Functions

- `create_account(session, **kwargs) → Account`
- `get_account(session, id) → Account | None`
- `get_account_by_email(session, email) → Account | None`
- `list_accounts(session) → list[Account]`
- `update_account(session, id, **kwargs) → Account`
- `delete_account(session, id) → None` — cascade deletes associated records

### Constraints

- `email` must be unique.
- Single caretaker per account.
