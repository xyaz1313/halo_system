/**
 * Deterministic mock data for Playwright tests.
 * Field shapes match ARCHITECTURE.md:72-136.
 */

export const MOCK_DATA = {
  accounts: [
    {
      id: "a1000000-0000-0000-0000-000000000001",
      email: "alice@example.com",
      patient_name: "Alice Smith",
      patient_age: 72,
      patient_diagnosis_stage: "early",
      patient_notes: "Responds well to routine.",
      caretaker_name: "Bob Smith",
      caretaker_email: "bob@example.com",
      created_at: "2025-01-15T08:00:00Z",
      updated_at: "2025-06-01T12:00:00Z",
    },
    {
      id: "a1000000-0000-0000-0000-000000000002",
      email: "carol@example.com",
      patient_name: "Carol Jones",
      patient_age: 68,
      patient_diagnosis_stage: "moderate",
      patient_notes: null,
      caretaker_name: null,
      caretaker_email: null,
      created_at: "2025-03-10T09:30:00Z",
      updated_at: "2025-07-20T14:00:00Z",
    },
  ],

  anchors: [
    {
      id: "b2000000-0000-0000-0000-000000000001",
      label: "Kitchen",
      visibility: "public",
      owner_account_id: null,
      signal_threshold: -70.5,
      status: "active",
      created_at: "2025-02-01T10:00:00Z",
      updated_at: "2025-05-15T11:00:00Z",
    },
    {
      id: "b2000000-0000-0000-0000-000000000002",
      label: "Bedroom",
      visibility: "private",
      owner_account_id: "a1000000-0000-0000-0000-000000000001",
      signal_threshold: -65.0,
      status: "inactive",
      created_at: "2025-02-05T10:00:00Z",
      updated_at: "2025-06-20T11:00:00Z",
    },
  ],

  tags: [
    {
      id: "c3000000-0000-0000-0000-000000000001",
      account_id: "a1000000-0000-0000-0000-000000000001",
      label: "Wristband A",
      status: "active",
      created_at: "2025-01-20T08:00:00Z",
      updated_at: "2025-04-10T09:00:00Z",
    },
    {
      id: "c3000000-0000-0000-0000-000000000002",
      account_id: "a1000000-0000-0000-0000-000000000002",
      label: null,
      status: "inactive",
      created_at: "2025-03-15T08:00:00Z",
      updated_at: "2025-08-01T09:00:00Z",
    },
  ],

  associations: [
    {
      anchor_id: "b2000000-0000-0000-0000-000000000001",
      tag_id: "c3000000-0000-0000-0000-000000000001",
      created_at: "2025-02-10T12:00:00Z",
    },
  ],

  calendars: [
    {
      id: "d4000000-0000-0000-0000-000000000001",
      account_id: "a1000000-0000-0000-0000-000000000001",
      provider: "google",
      external_calendar_id: "cal_abc123",
      sync_status: "synced",
      last_synced_at: "2025-06-01T06:00:00Z",
      created_at: "2025-01-25T08:00:00Z",
      updated_at: "2025-06-01T06:00:00Z",
    },
    {
      id: "d4000000-0000-0000-0000-000000000002",
      account_id: "a1000000-0000-0000-0000-000000000002",
      provider: "google",
      external_calendar_id: "cal_xyz789",
      sync_status: "error",
      last_synced_at: null,
      created_at: "2025-04-01T10:00:00Z",
      updated_at: "2025-07-15T10:00:00Z",
    },
  ],

  preferences: [
    {
      id: "e5000000-0000-0000-0000-000000000001",
      account_id: "a1000000-0000-0000-0000-000000000001",
      alert_email: "bob@example.com",
      alert_types: ["departure", "arrival", "low_battery"],
      created_at: "2025-01-30T08:00:00Z",
      updated_at: "2025-05-20T09:00:00Z",
    },
    {
      id: "e5000000-0000-0000-0000-000000000002",
      account_id: "a1000000-0000-0000-0000-000000000002",
      alert_email: "carol@example.com",
      alert_types: [],
      created_at: "2025-03-20T08:00:00Z",
      updated_at: "2025-08-05T09:00:00Z",
    },
  ],
};

/** Column definitions mirroring frontend/static/js/columns.js */
export const COLUMNS = {
  accounts: [
    "id", "email", "patient_name", "patient_age", "patient_diagnosis_stage",
    "patient_notes", "caretaker_name", "caretaker_email", "created_at", "updated_at",
  ],
  anchors: [
    "id", "label", "visibility", "owner_account_id", "signal_threshold",
    "status", "created_at", "updated_at",
  ],
  tags: [
    "id", "account_id", "label", "status", "created_at", "updated_at",
  ],
  associations: [
    "anchor_id", "tag_id", "created_at",
  ],
  calendars: [
    "id", "account_id", "provider", "external_calendar_id", "sync_status",
    "last_synced_at", "created_at", "updated_at",
  ],
  preferences: [
    "id", "account_id", "alert_email", "alert_types", "created_at", "updated_at",
  ],
};

/** All route names matching app.js ROUTES */
export const ROUTES = ["accounts", "anchors", "tags", "associations", "calendars", "preferences"];

/** Route label map for navbar links */
export const ROUTE_LABELS = {
  accounts: "Accounts",
  anchors: "Anchors",
  tags: "Tags",
  associations: "Associations",
  calendars: "Calendars",
  preferences: "Preferences",
};
