"""Device SQLModel tables: Anchor, Tag, and AnchorTagAssociation."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Column, DateTime, Float, ForeignKey, String, func
from sqlmodel import Field, SQLModel

from backend.core.models import BaseModel, created_at_field, id_field, updated_at_field


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Anchor(BaseModel, table=True):
    """A stationary receiver that monitors nearby tags."""

    __tablename__ = "anchors"

    # Override inherited fields with fresh Column objects (SQLModel 0.0.x fix)
    id: str = id_field()
    created_at: datetime = created_at_field()
    updated_at: datetime = updated_at_field()

    label: str = Field(nullable=False)
    visibility: str = Field(nullable=False)  # "public" or "private"
    owner_account_id: Optional[str] = Field(
        default=None,
        sa_column=Column(
            String(36),
            ForeignKey("accounts.id", ondelete="CASCADE"),
            nullable=True,
        ),
    )
    signal_threshold: float = Field(
        default=-70.0,
        sa_column=Column(Float, nullable=False, default=-70.0),
    )
    status: str = Field(default="active", nullable=False)


class Tag(BaseModel, table=True):
    """A small device worn by the patient."""

    __tablename__ = "tags"

    # Override inherited fields with fresh Column objects (SQLModel 0.0.x fix)
    id: str = id_field()
    created_at: datetime = created_at_field()
    updated_at: datetime = updated_at_field()

    account_id: str = Field(
        sa_column=Column(
            String(36),
            ForeignKey("accounts.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    label: Optional[str] = Field(default=None)
    status: str = Field(default="active", nullable=False)


class AnchorTagAssociation(SQLModel, table=True):
    """Links a tag to an anchor for monitoring. Composite PK, no UUID id."""

    __tablename__ = "anchor_tag_associations"
    __table_args__ = ()

    anchor_id: str = Field(
        sa_column=Column(
            String(36),
            ForeignKey("anchors.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )
    tag_id: str = Field(
        sa_column=Column(
            String(36),
            ForeignKey("tags.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )
    created_at: datetime = Field(
        default_factory=_utcnow,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            default=_utcnow,
            server_default=func.now(),
        ),
    )
