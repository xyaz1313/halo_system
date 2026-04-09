/**
 * Per-resource column definitions.
 * Keys match backend model field names from ARCHITECTURE.md.
 */

export const COLUMNS = {
  accounts: [
    "id",
    "email",
    "patient_name",
    "patient_age",
    "patient_diagnosis_stage",
    "patient_notes",
    "caretaker_name",
    "caretaker_email",
    "created_at",
    "updated_at",
  ],
  anchors: [
    "id",
    "label",
    "visibility",
    "owner_account_id",
    "signal_threshold",
    "status",
    "created_at",
    "updated_at",
  ],
  tags: [
    "id",
    "account_id",
    "label",
    "status",
    "created_at",
    "updated_at",
  ],
  associations: [
    "anchor_id",
    "tag_id",
    "created_at",
  ],
  calendars: [
    "id",
    "account_id",
    "provider",
    "external_calendar_id",
    "sync_status",
    "last_synced_at",
    "created_at",
    "updated_at",
  ],
  preferences: [
    "id",
    "account_id",
    "alert_email",
    "alert_types",
    "created_at",
    "updated_at",
  ],
};
