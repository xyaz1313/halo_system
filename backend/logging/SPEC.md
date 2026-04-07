# Logging Spec

Audit and historical record of system activity. Logs are for debugging, auditing, and analysis — not for driving behavior (that's events).

## What Gets Logged

| Category | Examples |
|---|---|
| **Account activity** | Account created, updated, deleted |
| **Device activity** | Anchor/tag registered, linked, status changed |
| **MoZo signals** | Raw signal strength readings (historical record, not just threshold crossings) |
| **Calendar activity** | Calendar added, sync started/completed/failed |
| **Notifications** | Email sent, confirmation link clicked |
| **Executive decisions** | What the agent decided and why |
| **Errors** | Failed syncs, unreachable devices, delivery failures |

## Log Entry Structure

- `timestamp` — when it happened
- `level` — info, warning, error
- `category` — which subsystem (account, device, mozo, calendar, notification, executive)
- `account_id` — which account this relates to (nullable for system-level logs)
- `message` — human-readable description
- `data` — structured payload (dict, optional)

## Implementation

- Python `logging` module as the base
- Structured JSON log output for machine readability
- File-based for dev, can route to external service later (e.g., CloudWatch, Datadog)
- MoZo signal history stored in DB (queryable) in addition to logs

## Notes

- Logs are write-only from the application's perspective — no business logic reads logs
- Retention policy TBD
- MoZo signal data is the exception: raw readings are logged AND stored in the DB for historical queries (e.g., "show me signal strength over the last 24 hours")
