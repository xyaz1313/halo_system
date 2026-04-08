"""Admin dump routes — return full table contents as JSON arrays.

WARNING: These endpoints are for **internal debug use only** and have NO
authentication or authorization.  They expose raw database rows including
patient data.  They MUST NOT be exposed on a public interface.  In
production, either remove this router entirely or bind the server to
localhost / place it behind a private network boundary.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from backend.accounts.models import Account
from backend.calendars.models import Calendar
from backend.db.engine import get_db
from backend.devices.models import Anchor, AnchorTagAssociation, Tag
from backend.notifications.models import NotificationPreference

router = APIRouter(prefix="/admin", tags=["admin"])

DBSession = Annotated[Session, Depends(get_db)]


@router.get("/accounts")
def dump_accounts(session: DBSession):
    return session.exec(select(Account)).all()


@router.get("/anchors")
def dump_anchors(session: DBSession):
    return session.exec(select(Anchor)).all()


@router.get("/tags")
def dump_tags(session: DBSession):
    return session.exec(select(Tag)).all()


@router.get("/associations")
def dump_associations(session: DBSession):
    return session.exec(select(AnchorTagAssociation)).all()


@router.get("/calendars")
def dump_calendars(session: DBSession):
    return session.exec(select(Calendar)).all()


@router.get("/preferences")
def dump_preferences(session: DBSession):
    return session.exec(select(NotificationPreference)).all()
