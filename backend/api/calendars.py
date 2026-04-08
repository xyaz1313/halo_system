"""Calendar CRUD API routes."""

from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel as PydanticBaseModel
from sqlmodel import Session

from backend.calendars import service
from backend.db.engine import get_db

router = APIRouter(prefix="/calendars", tags=["calendars"])


# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------


class CalendarCreate(PydanticBaseModel):
    account_id: str
    provider: str
    external_calendar_id: str


class CalendarUpdate(PydanticBaseModel):
    """Only sync_status and last_synced_at are patchable.

    Pydantic ``extra="forbid"`` ensures that attempts to set immutable fields
    (provider, external_calendar_id, etc.) are rejected with 422.
    """

    model_config = {"extra": "forbid"}

    sync_status: Optional[str] = None
    last_synced_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

DBSession = Annotated[Session, Depends(get_db)]


@router.post("", status_code=201)
def create_calendar(body: CalendarCreate, session: DBSession):
    return service.create_calendar(
        session,
        account_id=body.account_id,
        provider=body.provider,
        external_calendar_id=body.external_calendar_id,
    )


@router.get("")
def list_calendars(session: DBSession, account_id: Optional[str] = None):
    """List calendars, optionally filtered by account_id."""
    return service.list_calendars(session, account_id=account_id)


@router.get("/{calendar_id}")
def get_calendar(calendar_id: str, session: DBSession):
    return service.get_calendar(session, calendar_id)


@router.patch("/{calendar_id}")
def update_calendar(calendar_id: str, body: CalendarUpdate, session: DBSession):
    data = body.model_dump(exclude_unset=True)
    return service.update_calendar(session, calendar_id, **data)


@router.delete("/{calendar_id}", status_code=204)
def delete_calendar(calendar_id: str, session: DBSession):
    service.delete_calendar(session, calendar_id)
