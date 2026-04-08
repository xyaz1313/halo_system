"""NotificationPreference SQLModel table — alert preferences per account."""

from datetime import datetime
from typing import List

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.types import JSON
from sqlmodel import Field

from backend.core.models import BaseModel, created_at_field, id_field, updated_at_field


class NotificationPreference(BaseModel, table=True):
    """Notification preferences for an account — which alerts to send where."""

    __tablename__ = "notification_preferences"

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
    alert_email: str = Field(nullable=False)
    alert_types: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON, nullable=False),
    )
