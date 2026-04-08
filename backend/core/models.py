"""Base model with DB-agnostic UUID primary key and timestamps.

Each ``table=True`` subclass **must** re-declare the three inherited fields
using the factory helpers (``id_field``, ``created_at_field``,
``updated_at_field``) so that every table gets its own ``Column`` objects.
SQLModel 0.0.x shares ``sa_column`` instances across subclasses, which causes
``Column already assigned to Table`` errors when more than one child exists.
"""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Column, DateTime, String, func
from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Column factories — call these in every table=True subclass
# ---------------------------------------------------------------------------


def id_field() -> str:  # type: ignore[return]
    """Return a fresh ``Field`` for the UUID primary key."""
    return Field(
        default_factory=lambda: str(uuid4()),
        sa_column=Column(String(36), primary_key=True),
    )


def created_at_field() -> datetime:  # type: ignore[return]
    """Return a fresh ``Field`` for the created_at timestamp."""
    return Field(
        default_factory=_utcnow,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            default=_utcnow,
            server_default=func.now(),
        ),
    )


def updated_at_field() -> datetime:  # type: ignore[return]
    """Return a fresh ``Field`` for the updated_at timestamp."""
    return Field(
        default_factory=_utcnow,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            default=_utcnow,
            server_default=func.now(),
            onupdate=_utcnow,
        ),
    )


class BaseModel(SQLModel):
    """Abstract base for all Halo models.

    Provides:
    - ``id``: UUID stored as String(36) for SQLite/Postgres portability.
    - ``created_at``: Set once on creation.
    - ``updated_at``: Refreshed on every commit via SQLAlchemy ``onupdate``.

    Subclasses with ``table=True`` must override id/created_at/updated_at
    using the factory helpers above.
    """

    id: str = id_field()
    created_at: datetime = created_at_field()
    updated_at: datetime = updated_at_field()
