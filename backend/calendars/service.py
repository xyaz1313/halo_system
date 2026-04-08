"""Calendar service functions — CRUD with immutability enforcement."""

from datetime import datetime

from sqlmodel import Session, select

from backend.accounts.models import Account
from backend.calendars.models import Calendar
from backend.core.exceptions import NotFoundError, ValidationError

# Fields that are immutable after creation.
_IMMUTABLE_FIELDS = frozenset({"provider", "external_calendar_id"})

# Valid sync_status values.
_VALID_SYNC_STATUSES = frozenset({"syncing", "synced", "error"})


def _validate_account_exists(session: Session, account_id: str) -> None:
    """Raise NotFoundError if account does not exist."""
    if not session.get(Account, account_id):
        raise NotFoundError(f"Account '{account_id}' not found")


def create_calendar(
    session: Session,
    account_id: str,
    provider: str,
    external_calendar_id: str,
) -> Calendar:
    """Create a new calendar link for an account."""
    _validate_account_exists(session, account_id)

    calendar = Calendar(
        account_id=account_id,
        provider=provider,
        external_calendar_id=external_calendar_id,
    )
    session.add(calendar)
    session.flush()
    session.refresh(calendar)
    return calendar


def get_calendar(session: Session, calendar_id: str) -> Calendar:
    """Get a calendar by ID. Raises NotFoundError if not found."""
    calendar = session.get(Calendar, calendar_id)
    if not calendar:
        raise NotFoundError(f"Calendar '{calendar_id}' not found")
    return calendar


def list_calendars_for_account(
    session: Session, account_id: str
) -> list[Calendar]:
    """Return all calendars for an account."""
    stmt = select(Calendar).where(Calendar.account_id == account_id)
    return list(session.exec(stmt).all())


def list_calendars(
    session: Session, *, account_id: str | None = None
) -> list[Calendar]:
    """Return calendars, optionally filtered by account_id."""
    stmt = select(Calendar)
    if account_id is not None:
        stmt = stmt.where(Calendar.account_id == account_id)
    return list(session.exec(stmt).all())


def update_sync_status(
    session: Session,
    calendar_id: str,
    status: str,
    last_synced_at: datetime | None = None,
) -> Calendar:
    """Update a calendar's sync_status (and optionally last_synced_at).

    Raises ValidationError if status is not a valid sync status.
    """
    calendar = session.get(Calendar, calendar_id)
    if not calendar:
        raise NotFoundError(f"Calendar '{calendar_id}' not found")

    if status not in _VALID_SYNC_STATUSES:
        raise ValidationError(
            f"sync_status must be one of {sorted(_VALID_SYNC_STATUSES)}, got '{status}'"
        )

    calendar.sync_status = status
    if last_synced_at is not None:
        calendar.last_synced_at = last_synced_at

    session.add(calendar)
    session.flush()
    session.refresh(calendar)
    return calendar


_PATCHABLE_FIELDS = frozenset({"sync_status", "last_synced_at"})


def update_calendar(session: Session, calendar_id: str, **kwargs) -> Calendar:
    """Partial-update a calendar. Rejects changes to immutable fields.

    Only sync_status and last_synced_at are patchable.
    Raises ValidationError if provider, external_calendar_id, or any
    other non-patchable field is included.
    """
    calendar = session.get(Calendar, calendar_id)
    if not calendar:
        raise NotFoundError(f"Calendar '{calendar_id}' not found")

    immutable_attempted = _IMMUTABLE_FIELDS & set(kwargs.keys())
    if immutable_attempted:
        raise ValidationError(
            f"Cannot change immutable fields: {sorted(immutable_attempted)}"
        )

    disallowed = set(kwargs.keys()) - _PATCHABLE_FIELDS
    if disallowed:
        raise ValidationError(
            f"Cannot patch fields: {sorted(disallowed)}. "
            f"Patchable fields: {sorted(_PATCHABLE_FIELDS)}"
        )

    if "sync_status" in kwargs and kwargs["sync_status"] not in _VALID_SYNC_STATUSES:
        raise ValidationError(
            f"sync_status must be one of {sorted(_VALID_SYNC_STATUSES)}, "
            f"got '{kwargs['sync_status']}'"
        )

    for key, value in kwargs.items():
        setattr(calendar, key, value)

    session.add(calendar)
    session.flush()
    session.refresh(calendar)
    return calendar


def delete_calendar(session: Session, calendar_id: str) -> None:
    """Delete a calendar. Raises NotFoundError if not found."""
    calendar = session.get(Calendar, calendar_id)
    if not calendar:
        raise NotFoundError(f"Calendar '{calendar_id}' not found")
    session.delete(calendar)
    session.flush()
