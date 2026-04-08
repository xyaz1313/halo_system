"""Device CRUD API routes — Anchors, Tags, and Associations."""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel as PydanticBaseModel
from sqlmodel import Session

from backend.db.engine import get_db
from backend.devices import service


# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------


class AnchorCreate(PydanticBaseModel):
    label: str
    visibility: str = "public"
    owner_account_id: Optional[str] = None
    signal_threshold: float = -70.0
    status: str = "active"


class AnchorUpdate(PydanticBaseModel):
    label: Optional[str] = None
    visibility: Optional[str] = None
    owner_account_id: Optional[str] = None
    signal_threshold: Optional[float] = None
    status: Optional[str] = None


class TagCreate(PydanticBaseModel):
    account_id: str
    label: Optional[str] = None
    status: str = "active"


class TagUpdate(PydanticBaseModel):
    label: Optional[str] = None
    status: Optional[str] = None


DBSession = Annotated[Session, Depends(get_db)]

# ---------------------------------------------------------------------------
# Anchor router — mounted at /api/v1/anchors
# ---------------------------------------------------------------------------

anchors_router = APIRouter(prefix="/anchors", tags=["anchors"])


@anchors_router.post("", status_code=201)
def create_anchor(body: AnchorCreate, session: DBSession):
    return service.create_anchor(session, **body.model_dump())


@anchors_router.get("")
def list_anchors(account_id: str, session: DBSession):
    """List anchors visible to an account (public + owned private)."""
    return service.list_anchors_for_account(session, account_id)


@anchors_router.get("/{anchor_id}")
def get_anchor(anchor_id: str, session: DBSession):
    return service.get_anchor(session, anchor_id)


@anchors_router.patch("/{anchor_id}")
def update_anchor(anchor_id: str, body: AnchorUpdate, session: DBSession):
    data = body.model_dump(exclude_unset=True)
    return service.update_anchor(session, anchor_id, **data)


@anchors_router.delete("/{anchor_id}", status_code=204)
def delete_anchor(anchor_id: str, session: DBSession):
    service.delete_anchor(session, anchor_id)


# Association sub-routes on anchors
@anchors_router.post("/{anchor_id}/tags/{tag_id}", status_code=201)
def link_tag_to_anchor(anchor_id: str, tag_id: str, session: DBSession):
    return service.link_tag_to_anchor(session, anchor_id, tag_id)


@anchors_router.delete("/{anchor_id}/tags/{tag_id}", status_code=204)
def unlink_tag_from_anchor(anchor_id: str, tag_id: str, session: DBSession):
    service.unlink_tag_from_anchor(session, anchor_id, tag_id)


@anchors_router.get("/{anchor_id}/tags")
def list_tags_for_anchor(anchor_id: str, session: DBSession):
    return service.list_associations_for_anchor(session, anchor_id)


# ---------------------------------------------------------------------------
# Tag router — mounted at /api/v1/tags
# ---------------------------------------------------------------------------

tags_router = APIRouter(prefix="/tags", tags=["tags"])


@tags_router.post("", status_code=201)
def create_tag(body: TagCreate, session: DBSession):
    return service.create_tag(session, body.account_id, label=body.label, status=body.status)


@tags_router.get("")
def list_tags(account_id: str, session: DBSession):
    """List all tags for an account."""
    return service.list_tags_for_account(session, account_id)


@tags_router.get("/{tag_id}")
def get_tag(tag_id: str, session: DBSession):
    return service.get_tag(session, tag_id)


@tags_router.patch("/{tag_id}")
def update_tag(tag_id: str, body: TagUpdate, session: DBSession):
    data = body.model_dump(exclude_unset=True)
    return service.update_tag(session, tag_id, **data)


@tags_router.delete("/{tag_id}", status_code=204)
def delete_tag(tag_id: str, session: DBSession):
    service.delete_tag(session, tag_id)


# Association sub-route on tags
@tags_router.get("/{tag_id}/anchors")
def list_anchors_for_tag(tag_id: str, session: DBSession):
    return service.list_associations_for_tag(session, tag_id)
