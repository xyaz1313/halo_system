"""Account SQLModel table — top-level entity for the Halo System."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String
from sqlmodel import Field

from backend.core.models import BaseModel, created_at_field, id_field, updated_at_field


class Account(BaseModel, table=True):
    """A patient/caretaker account — the root entity that owns all other data."""

    __tablename__ = "accounts"

    # Override inherited fields with fresh Column objects (SQLModel 0.0.x fix)
    id: str = id_field()
    created_at: datetime = created_at_field()
    updated_at: datetime = updated_at_field()

    email: str = Field(sa_column=Column(String, unique=True, nullable=False, index=True))
    patient_name: str = Field(nullable=False)
    patient_age: int = Field(nullable=False)
    patient_diagnosis_stage: str = Field(nullable=False)
    patient_notes: str = Field(default="")
    caretaker_name: Optional[str] = Field(default=None)
    caretaker_email: Optional[str] = Field(default=None)

    # Relationships to child models (Tag, Calendar, NotificationPreference,
    # Anchor) are added by tasks fn-2-szr.3 and fn-2-szr.4 once those models
    # exist.  They use back_populates and cascade="all, delete-orphan".
    # Cascade delete is verified in the test suite (fn-2-szr.6).
