# fn-2-szr.2 Account model, service functions, and API routes

## Description

Implement the Account SQLModel table, all 6 service functions per spec, and the CRUD API routes. Account is the top-level entity that all other models reference. Relationship declarations to child models use string-based forward references (resolved when child models are imported later). Cascade delete behavior is verified in the test suite (fn-2-szr.6) after all child models exist.

**Size:** M
**Files:**
- `backend/accounts/models.py` (Account SQLModel)
- `backend/accounts/service.py` (create, get, get_by_email, list, update, delete)
- `backend/api/accounts.py` (FastAPI router)
- Update `backend/models.py` to import accounts.models
- Update `backend/main.py` to include accounts router

## Approach

- Account model inherits BaseModel. Fields per `backend/accounts/SPEC.md`: email (unique), patient_name, patient_age, patient_diagnosis_stage, patient_notes, caretaker_name, caretaker_email
- Relationships to child models (Tag, Calendar, NotificationPreference, Anchor) declared with string references and `cascade="all, delete-orphan"` — resolved at runtime when child models are imported via model registry
- Email uniqueness enforced at DB level (unique constraint) and service level (raises AlreadyExistsError)
- Service functions: flat functions taking `session: Session`, raising typed exceptions (NotFoundError, AlreadyExistsError)
- PATCH uses `model_dump(exclude_unset=True)` for partial updates
- API routes use `Annotated[Session, Depends(get_db)]`. Routes catch typed exceptions via main.py handlers.
- Status codes: 201 (create), 200 (get/list/update), 204 (delete), 404, 422, 409

## Key context

- Cascade delete acceptance is deferred to fn-2-szr.6 (test suite) — child models don't exist yet
- String-based relationship references: `Relationship(back_populates="account", sa_relationship_kwargs={"cascade": "all, delete-orphan"})` — SQLAlchemy resolves these lazily
- Services raise typed exceptions from `backend.core.exceptions`; HTTP mapping in main.py
- Register in model registry (`backend/models.py`) and main.py router includes

## Acceptance
- [ ] Account model creates table with all fields from spec
- [ ] Email unique constraint at DB level
- [ ] `create_account` raises AlreadyExistsError on duplicate email
- [ ] `get_account` raises NotFoundError for non-existent ID
- [ ] `list_accounts` returns all accounts
- [ ] `update_account` supports partial update, raises NotFoundError if missing
- [ ] `delete_account` returns 204 (cascade verified in fn-2-szr.6)
- [ ] All API routes respond with correct status codes
- [ ] Router registered at `/api/v1/accounts`
- [ ] Model registered in `backend/models.py`

## Done summary
Implemented Account SQLModel table with all fields per spec, 6 service functions (create, get, get_by_email, list, update, delete), and CRUD API routes at /api/v1/accounts. Includes email uniqueness at DB and service levels, non-nullable field validation on PATCH, and proper IntegrityError handling.
## Evidence
- Commits: 4ad0ee7, 053204c, 713c047, 0721152
- Tests: python3 inline acceptance tests: create 201, duplicate 409, get 200, list 200, patch 200, delete 204, not-found 404, update-dup-email 409, null-field 422
- PRs: