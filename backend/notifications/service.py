"""NotificationPreference service functions — CRUD with alert_types validation."""

from sqlmodel import Session, select

from backend.accounts.models import Account
from backend.core.exceptions import NotFoundError, ValidationError
from backend.notifications.models import NotificationPreference

# Known alert types.
KNOWN_ALERT_TYPES = frozenset({
    "mozo_departure",
    "schedule_confirmation",
    "schedule_conflict",
})

# This type is always included — users cannot opt out.
_REQUIRED_TYPE = "schedule_confirmation"

# Fields that may be changed via partial update (PATCH).
_PATCHABLE_FIELDS = frozenset({"alert_email", "alert_types"})


def _validate_account_exists(session: Session, account_id: str) -> None:
    """Raise NotFoundError if account does not exist."""
    if not session.get(Account, account_id):
        raise NotFoundError(f"Account '{account_id}' not found")


def _normalize_alert_types(alert_types: list[str]) -> list[str]:
    """Validate, deduplicate, and ensure schedule_confirmation is present.

    - Raises ValidationError on unknown types.
    - Deduplicates preserving input order.
    - Appends schedule_confirmation at end if missing.
    """
    unknown = set(alert_types) - KNOWN_ALERT_TYPES
    if unknown:
        raise ValidationError(
            f"Unknown alert types: {sorted(unknown)}. "
            f"Valid types: {sorted(KNOWN_ALERT_TYPES)}"
        )

    # Deduplicate preserving input order
    seen: set[str] = set()
    deduped: list[str] = []
    for t in alert_types:
        if t not in seen:
            seen.add(t)
            deduped.append(t)

    # Ensure required type is present
    if _REQUIRED_TYPE not in seen:
        deduped.append(_REQUIRED_TYPE)

    return deduped


def create_preference(
    session: Session,
    account_id: str,
    alert_email: str,
    alert_types: list[str],
) -> NotificationPreference:
    """Create a notification preference for an account."""
    _validate_account_exists(session, account_id)
    normalized = _normalize_alert_types(alert_types)

    pref = NotificationPreference(
        account_id=account_id,
        alert_email=alert_email,
        alert_types=normalized,
    )
    session.add(pref)
    session.flush()
    session.refresh(pref)
    return pref


def get_preference(session: Session, preference_id: str) -> NotificationPreference:
    """Get a preference by ID. Raises NotFoundError if not found."""
    pref = session.get(NotificationPreference, preference_id)
    if not pref:
        raise NotFoundError(f"NotificationPreference '{preference_id}' not found")
    return pref


def list_preferences_for_account(
    session: Session, account_id: str
) -> list[NotificationPreference]:
    """Return all notification preferences for an account."""
    stmt = select(NotificationPreference).where(
        NotificationPreference.account_id == account_id
    )
    return list(session.exec(stmt).all())


def list_preferences(
    session: Session, *, account_id: str | None = None
) -> list[NotificationPreference]:
    """Return preferences, optionally filtered by account_id."""
    stmt = select(NotificationPreference)
    if account_id is not None:
        stmt = stmt.where(NotificationPreference.account_id == account_id)
    return list(session.exec(stmt).all())


def update_preference(
    session: Session, preference_id: str, **kwargs
) -> NotificationPreference:
    """Partial-update a notification preference."""
    pref = session.get(NotificationPreference, preference_id)
    if not pref:
        raise NotFoundError(f"NotificationPreference '{preference_id}' not found")

    # Reject fields that are not patchable
    disallowed = set(kwargs.keys()) - _PATCHABLE_FIELDS
    if disallowed:
        raise ValidationError(
            f"Cannot patch fields: {sorted(disallowed)}. "
            f"Patchable fields: {sorted(_PATCHABLE_FIELDS)}"
        )

    # Validate and normalize alert_types if provided
    if "alert_types" in kwargs:
        if kwargs["alert_types"] is None:
            raise ValidationError("alert_types cannot be null")
        kwargs["alert_types"] = _normalize_alert_types(kwargs["alert_types"])

    for key, value in kwargs.items():
        setattr(pref, key, value)

    session.add(pref)
    session.flush()
    session.refresh(pref)
    return pref


def delete_preference(session: Session, preference_id: str) -> None:
    """Delete a notification preference. Raises NotFoundError if not found."""
    pref = session.get(NotificationPreference, preference_id)
    if not pref:
        raise NotFoundError(f"NotificationPreference '{preference_id}' not found")
    session.delete(pref)
    session.flush()
