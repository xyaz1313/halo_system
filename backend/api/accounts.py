"""Account CRUD API routes."""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel as PydanticBaseModel
from sqlmodel import Session

from backend.accounts import service
from backend.db.engine import get_db

router = APIRouter(prefix="/accounts", tags=["accounts"])


# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------


class AccountCreate(PydanticBaseModel):
    email: str
    patient_name: str
    patient_age: int
    patient_diagnosis_stage: str
    patient_notes: str = ""
    caretaker_name: Optional[str] = None
    caretaker_email: Optional[str] = None


class AccountUpdate(PydanticBaseModel):
    email: Optional[str] = None
    patient_name: Optional[str] = None
    patient_age: Optional[int] = None
    patient_diagnosis_stage: Optional[str] = None
    patient_notes: Optional[str] = None
    caretaker_name: Optional[str] = None
    caretaker_email: Optional[str] = None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

DBSession = Annotated[Session, Depends(get_db)]


@router.post("", status_code=201)
def create_account(body: AccountCreate, session: DBSession):
    return service.create_account(session, **body.model_dump())


@router.get("")
def list_accounts(session: DBSession):
    return service.list_accounts(session)


@router.get("/{account_id}")
def get_account(account_id: str, session: DBSession):
    return service.get_account(session, account_id)


@router.patch("/{account_id}")
def update_account(account_id: str, body: AccountUpdate, session: DBSession):
    data = body.model_dump(exclude_unset=True)
    return service.update_account(session, account_id, **data)


@router.delete("/{account_id}", status_code=204)
def delete_account(account_id: str, session: DBSession):
    service.delete_account(session, account_id)
