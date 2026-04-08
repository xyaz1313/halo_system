"""Account service functions — flat functions taking a Session."""

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from backend.accounts.models import Account
from backend.core.exceptions import AlreadyExistsError, NotFoundError, ValidationError

# Fields that may be changed via partial update (PATCH).
_PATCHABLE_FIELDS = frozenset({
    "email", "patient_name", "patient_age", "patient_diagnosis_stage",
    "patient_notes", "caretaker_name", "caretaker_email",
})

# Fields that must not be set to None via partial update.
# Derived from Account column definitions: every non-Optional field.
_NON_NULLABLE_FIELDS = frozenset({
    "email", "patient_name", "patient_age", "patient_diagnosis_stage",
    "patient_notes",
})


def _raise_if_email_taken(
    session: Session, email: str, *, exclude_id: str | None = None
) -> None:
    """Pre-check email uniqueness, excluding a given account ID for updates."""
    stmt = select(Account).where(Account.email == email)
    if exclude_id is not None:
        stmt = stmt.where(Account.id != exclude_id)
    if session.exec(stmt).first():
        raise AlreadyExistsError(f"Account with email '{email}' already exists")


def _is_unique_violation(exc: IntegrityError) -> bool:
    """Return True if the IntegrityError is a unique-constraint violation."""
    msg = str(exc.orig).lower()
    # SQLite: "UNIQUE constraint failed: accounts.email"
    # PostgreSQL: 'duplicate key value violates unique constraint'
    return "unique" in msg or "duplicate key" in msg


def _flush_or_raise(session: Session, email: str) -> None:
    """Flush; re-raise unique violations as AlreadyExistsError, others as-is."""
    try:
        session.flush()
    except IntegrityError as exc:
        session.rollback()
        if _is_unique_violation(exc):
            raise AlreadyExistsError(
                f"Account with email '{email}' already exists"
            ) from exc
        raise  # Non-unique IntegrityError (e.g. NOT NULL) propagates normally


def create_account(session: Session, **kwargs) -> Account:
    """Create a new account. Raises AlreadyExistsError on duplicate email."""
    email = kwargs.get("email")
    if email:
        _raise_if_email_taken(session, email)

    account = Account(**kwargs)
    session.add(account)
    _flush_or_raise(session, email or "")
    session.refresh(account)
    return account


def get_account(session: Session, account_id: str) -> Account:
    """Get an account by ID. Raises NotFoundError if not found."""
    account = session.get(Account, account_id)
    if not account:
        raise NotFoundError(f"Account '{account_id}' not found")
    return account


def get_account_by_email(session: Session, email: str) -> Account | None:
    """Get an account by email, or None if not found."""
    return session.exec(select(Account).where(Account.email == email)).first()


def list_accounts(session: Session) -> list[Account]:
    """Return all accounts."""
    return list(session.exec(select(Account)).all())


def update_account(session: Session, account_id: str, **kwargs) -> Account:
    """Partial-update an account. Raises NotFoundError if not found."""
    account = session.get(Account, account_id)
    if not account:
        raise NotFoundError(f"Account '{account_id}' not found")

    # Reject fields that are not patchable
    disallowed = set(kwargs.keys()) - _PATCHABLE_FIELDS
    if disallowed:
        raise ValidationError(
            f"Cannot patch fields: {sorted(disallowed)}. "
            f"Patchable fields: {sorted(_PATCHABLE_FIELDS)}"
        )

    # Reject null values for non-nullable fields
    for field in _NON_NULLABLE_FIELDS:
        if field in kwargs and kwargs[field] is None:
            raise ValidationError(f"Field '{field}' cannot be null")

    email = kwargs.get("email")
    if email:
        _raise_if_email_taken(session, email, exclude_id=account_id)

    for key, value in kwargs.items():
        setattr(account, key, value)

    session.add(account)
    _flush_or_raise(session, email or account.email)
    session.refresh(account)
    return account


def delete_account(session: Session, account_id: str) -> None:
    """Delete an account. Raises NotFoundError if not found."""
    account = session.get(Account, account_id)
    if not account:
        raise NotFoundError(f"Account '{account_id}' not found")

    session.delete(account)
    session.flush()
