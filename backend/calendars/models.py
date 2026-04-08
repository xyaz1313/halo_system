"""Calendar SQLModel table — external calendar connections and sync state."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlmodel import Field

from backend.core.models import BaseModel, created_at_field, id_field, updated_at_field


class Calendar(BaseModel, table=True):
    """An external calendar linked to an account for scheduling sync."""

    __tablename__ = "calendars"

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
    provider: str = Field(nullable=False)
    external_calendar_id: str = Field(nullable=False)
    sync_status: str = Field(default="syncing", nullable=False)
    last_synced_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
