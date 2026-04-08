"""Notification Preference CRUD API routes."""

from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel as PydanticBaseModel
from sqlmodel import Session

from backend.db.engine import get_db
from backend.notifications import service

router = APIRouter(prefix="/notifications/preferences", tags=["notifications"])


# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------


class PreferenceCreate(PydanticBaseModel):
    account_id: str
    alert_email: str
    alert_types: List[str]


class PreferenceUpdate(PydanticBaseModel):
    alert_email: Optional[str] = None
    alert_types: Optional[List[str]] = None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

DBSession = Annotated[Session, Depends(get_db)]


@router.post("", status_code=201)
def create_preference(body: PreferenceCreate, session: DBSession):
    return service.create_preference(
        session,
        account_id=body.account_id,
        alert_email=body.alert_email,
        alert_types=body.alert_types,
    )


@router.get("")
def list_preferences(session: DBSession, account_id: Optional[str] = None):
    """List notification preferences, optionally filtered by account_id."""
    return service.list_preferences(session, account_id=account_id)


@router.get("/{preference_id}")
def get_preference(preference_id: str, session: DBSession):
    return service.get_preference(session, preference_id)


@router.patch("/{preference_id}")
def update_preference(
    preference_id: str, body: PreferenceUpdate, session: DBSession
):
    data = body.model_dump(exclude_unset=True)
    return service.update_preference(session, preference_id, **data)


@router.delete("/{preference_id}", status_code=204)
def delete_preference(preference_id: str, session: DBSession):
    service.delete_preference(session, preference_id)
