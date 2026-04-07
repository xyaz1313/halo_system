# fn-2-szr.3 Device models (Anchor, Tag, Association), services, and API routes

## Description

Implement Anchor, Tag, and AnchorTagAssociation models with visibility rules and access validation. Includes all service functions and API routes. Services raise typed exceptions.

**Size:** M
**Files:**
- `backend/devices/models.py` (Anchor, Tag, AnchorTagAssociation)
- `backend/devices/service.py` (all service functions per spec)
- `backend/api/devices.py` (anchor, tag, and association routes)
- Update `backend/models.py` to import devices.models
- Update `backend/main.py` to include devices router

## Approach

- Anchor model inherits BaseModel. Fields: label, visibility (public/private string), owner_account_id (FK to Account, nullable), signal_threshold (float, default -70.0), status (active/inactive)
- Visibility coupling enforced in service: public requires owner_account_id=NULL; private requires owner_account_id set. Raises ValidationError if invalid.
- On PATCH: changing to public nulls owner_account_id; changing to private requires owner_account_id in request (raises ValidationError if missing)
- Tag model inherits BaseModel. Fields: account_id (FK to Account), label, status
- AnchorTagAssociation: does NOT inherit BaseModel. Composite PK via `__table_args__`, only anchor_id + tag_id + created_at
- `link_tag_to_anchor` validates access (tag account can see anchor), raises AccessDeniedError or AlreadyExistsError
- `list_anchors_for_account` returns public + private owned by that account
- All service functions raise typed exceptions from `backend.core.exceptions`

## Key context

- Per `backend/devices/SPEC.md`: anchor visibility is the core access control mechanism
- AnchorTagAssociation composite PK: define with `__table_args__` and explicit Column declarations
- Association routes: `POST /anchors/{id}/tags/{id}`, `DELETE /anchors/{id}/tags/{id}`, `GET /anchors/{id}/tags`, `GET /tags/{id}/anchors`
- Cascade: deleting an anchor/tag cascades to their associations via DB FK constraints (foreign_keys=ON enabled in engine)

## Acceptance
- [ ] Anchor model enforces visibility/owner coupling on create and update
- [ ] Public anchors have NULL owner; private anchors have required owner
- [ ] PATCH visibility change enforces coupling (raises ValidationError)
- [ ] Tag model with account_id FK works
- [ ] AnchorTagAssociation uses composite PK, no UUID id
- [ ] `link_tag_to_anchor` validates access (raises AccessDeniedError)
- [ ] Duplicate association raises AlreadyExistsError (409)
- [ ] `list_anchors_for_account` returns public + owned private
- [ ] All CRUD routes for anchors and tags with correct status codes
- [ ] Association sub-routes work (link, unlink, list by anchor, list by tag)
- [ ] Models registered in `backend/models.py`

## Done summary
TBD

## Evidence
- Commits:
- Tests:
- PRs:
