# Devices Spec

Manages MoZo anchors, tags, and their associations. All SQLModel tables.

---

## Model: Anchor

A stationary receiver that monitors nearby tags.

### Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | UUID | auto | PK |
| `label` | str | yes | Friendly name (e.g., "Kitchen", "Front Door") |
| `visibility` | str | yes | `"public"` or `"private"` |
| `owner_account_id` | UUID (FK → Account) | conditional | Required if private, null if public |
| `signal_threshold` | float | yes | RSSI cutoff. Default: -70.0 |
| `status` | str | yes | `"active"` / `"inactive"`. Default: `"active"` |
| `created_at` | datetime | auto | |
| `updated_at` | datetime | auto | |

### Service Functions

- `create_anchor(session, **kwargs) → Anchor` — validates visibility/owner rules
- `get_anchor(session, id) → Anchor | None`
- `list_anchors_for_account(session, account_id) → list[Anchor]` — returns all public + private owned by account
- `update_anchor(session, id, **kwargs) → Anchor`
- `delete_anchor(session, id) → None` — cascades to associations

### Constraints

- Public: `owner_account_id` must be null.
- Private: `owner_account_id` must reference a valid Account.

---

## Model: Tag

A small device worn by the patient.

### Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | UUID | auto | PK |
| `account_id` | UUID (FK → Account) | yes | |
| `label` | str | no | Optional friendly name |
| `status` | str | yes | `"active"` / `"inactive"`. Default: `"active"` |
| `created_at` | datetime | auto | |
| `updated_at` | datetime | auto | |

### Service Functions

- `create_tag(session, account_id, **kwargs) → Tag`
- `get_tag(session, id) → Tag | None`
- `list_tags_for_account(session, account_id) → list[Tag]`
- `update_tag(session, id, **kwargs) → Tag`
- `delete_tag(session, id) → None` — cascades to associations

---

## Model: AnchorTagAssociation

Links a tag to an anchor for monitoring.

### Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `anchor_id` | UUID (FK → Anchor) | yes | Composite PK |
| `tag_id` | UUID (FK → Tag) | yes | Composite PK |
| `created_at` | datetime | auto | |

### Service Functions

- `link_tag_to_anchor(session, anchor_id, tag_id) → AnchorTagAssociation` — validates access
- `unlink_tag_from_anchor(session, anchor_id, tag_id) → None`
- `list_associations_for_anchor(session, anchor_id) → list[AnchorTagAssociation]`
- `list_associations_for_tag(session, tag_id) → list[AnchorTagAssociation]`

### Constraints

- A tag can be linked to multiple anchors.
- An anchor can monitor multiple tags.
- Access check on link: tag's account must have visibility to the anchor (public, or private owned by same account).
