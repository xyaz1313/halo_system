"""Device service functions — Anchor, Tag, and AnchorTagAssociation CRUD."""

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from backend.accounts.models import Account
from backend.core.exceptions import (
    AccessDeniedError,
    AlreadyExistsError,
    NotFoundError,
    ValidationError,
)
from backend.devices.models import Anchor, AnchorTagAssociation, Tag


# ---------------------------------------------------------------------------
# Visibility / owner coupling helpers
# ---------------------------------------------------------------------------


def _validate_visibility_owner(visibility: str, owner_account_id: str | None) -> None:
    """Enforce visibility/owner coupling rules."""
    if visibility not in ("public", "private"):
        raise ValidationError(
            f"visibility must be 'public' or 'private', got '{visibility}'"
        )
    if visibility == "public" and owner_account_id is not None:
        raise ValidationError("Public anchors must not have an owner_account_id")
    if visibility == "private" and owner_account_id is None:
        raise ValidationError("Private anchors require an owner_account_id")


def _validate_account_exists(session: Session, account_id: str) -> None:
    """Raise NotFoundError if account does not exist."""
    if not session.get(Account, account_id):
        raise NotFoundError(f"Account '{account_id}' not found")


# ---------------------------------------------------------------------------
# Patchable field allowlists
# ---------------------------------------------------------------------------

_ANCHOR_PATCHABLE_FIELDS = frozenset({
    "label", "visibility", "owner_account_id", "signal_threshold", "status",
})

_TAG_PATCHABLE_FIELDS = frozenset({"label", "status"})


# ---------------------------------------------------------------------------
# Anchor service
# ---------------------------------------------------------------------------


def create_anchor(session: Session, **kwargs) -> Anchor:
    """Create an anchor. Validates visibility/owner coupling."""
    visibility = kwargs.get("visibility", "public")
    owner_account_id = kwargs.get("owner_account_id")
    _validate_visibility_owner(visibility, owner_account_id)

    if owner_account_id is not None:
        _validate_account_exists(session, owner_account_id)

    anchor = Anchor(**kwargs)
    session.add(anchor)
    session.flush()
    session.refresh(anchor)
    return anchor


def get_anchor(session: Session, anchor_id: str) -> Anchor:
    """Get an anchor by ID. Raises NotFoundError if not found."""
    anchor = session.get(Anchor, anchor_id)
    if not anchor:
        raise NotFoundError(f"Anchor '{anchor_id}' not found")
    return anchor


def list_anchors_for_account(session: Session, account_id: str) -> list[Anchor]:
    """Return all public anchors plus private anchors owned by account."""
    stmt = select(Anchor).where(
        (Anchor.visibility == "public")
        | (Anchor.owner_account_id == account_id)
    )
    return list(session.exec(stmt).all())


def update_anchor(session: Session, anchor_id: str, **kwargs) -> Anchor:
    """Partial-update an anchor. Enforces visibility/owner coupling on change."""
    anchor = session.get(Anchor, anchor_id)
    if not anchor:
        raise NotFoundError(f"Anchor '{anchor_id}' not found")

    # Reject fields that are not patchable
    disallowed = set(kwargs.keys()) - _ANCHOR_PATCHABLE_FIELDS
    if disallowed:
        raise ValidationError(
            f"Cannot patch fields: {sorted(disallowed)}. "
            f"Patchable fields: {sorted(_ANCHOR_PATCHABLE_FIELDS)}"
        )

    # Determine effective visibility and owner after update
    new_visibility = kwargs.get("visibility", anchor.visibility)
    new_owner = kwargs.get("owner_account_id", anchor.owner_account_id)

    # Visibility change rules
    if "visibility" in kwargs:
        if kwargs["visibility"] == "public":
            # Changing to public: null out owner
            new_owner = None
            kwargs["owner_account_id"] = None
        elif kwargs["visibility"] == "private":
            # Changing to private: owner must be provided in request
            if "owner_account_id" not in kwargs or kwargs["owner_account_id"] is None:
                raise ValidationError(
                    "Changing visibility to 'private' requires owner_account_id"
                )
            new_owner = kwargs["owner_account_id"]

    _validate_visibility_owner(new_visibility, new_owner)

    if new_owner is not None:
        _validate_account_exists(session, new_owner)

    for key, value in kwargs.items():
        setattr(anchor, key, value)

    session.add(anchor)
    session.flush()
    session.refresh(anchor)
    return anchor


def delete_anchor(session: Session, anchor_id: str) -> None:
    """Delete an anchor. Cascades to associations via FK constraints."""
    anchor = session.get(Anchor, anchor_id)
    if not anchor:
        raise NotFoundError(f"Anchor '{anchor_id}' not found")
    session.delete(anchor)
    session.flush()


# ---------------------------------------------------------------------------
# Tag service
# ---------------------------------------------------------------------------


def create_tag(session: Session, account_id: str, **kwargs) -> Tag:
    """Create a tag for an account."""
    _validate_account_exists(session, account_id)
    tag = Tag(account_id=account_id, **kwargs)
    session.add(tag)
    session.flush()
    session.refresh(tag)
    return tag


def get_tag(session: Session, tag_id: str) -> Tag:
    """Get a tag by ID. Raises NotFoundError if not found."""
    tag = session.get(Tag, tag_id)
    if not tag:
        raise NotFoundError(f"Tag '{tag_id}' not found")
    return tag


def list_tags_for_account(session: Session, account_id: str) -> list[Tag]:
    """Return all tags for an account."""
    stmt = select(Tag).where(Tag.account_id == account_id)
    return list(session.exec(stmt).all())


def update_tag(session: Session, tag_id: str, **kwargs) -> Tag:
    """Partial-update a tag."""
    tag = session.get(Tag, tag_id)
    if not tag:
        raise NotFoundError(f"Tag '{tag_id}' not found")

    # Reject fields that are not patchable
    disallowed = set(kwargs.keys()) - _TAG_PATCHABLE_FIELDS
    if disallowed:
        raise ValidationError(
            f"Cannot patch fields: {sorted(disallowed)}. "
            f"Patchable fields: {sorted(_TAG_PATCHABLE_FIELDS)}"
        )

    for key, value in kwargs.items():
        setattr(tag, key, value)

    session.add(tag)
    session.flush()
    session.refresh(tag)
    return tag


def delete_tag(session: Session, tag_id: str) -> None:
    """Delete a tag. Cascades to associations via FK constraints."""
    tag = session.get(Tag, tag_id)
    if not tag:
        raise NotFoundError(f"Tag '{tag_id}' not found")
    session.delete(tag)
    session.flush()


# ---------------------------------------------------------------------------
# Association service
# ---------------------------------------------------------------------------


def _can_see_anchor(session: Session, tag_id: str, anchor_id: str) -> bool:
    """Check if the tag's account can see the anchor (public or owned)."""
    tag = session.get(Tag, tag_id)
    if not tag:
        return False
    anchor = session.get(Anchor, anchor_id)
    if not anchor:
        return False
    if anchor.visibility == "public":
        return True
    return anchor.owner_account_id == tag.account_id


def link_tag_to_anchor(
    session: Session, anchor_id: str, tag_id: str
) -> AnchorTagAssociation:
    """Link a tag to an anchor. Validates access and uniqueness."""
    # Verify both exist
    anchor = session.get(Anchor, anchor_id)
    if not anchor:
        raise NotFoundError(f"Anchor '{anchor_id}' not found")
    tag = session.get(Tag, tag_id)
    if not tag:
        raise NotFoundError(f"Tag '{tag_id}' not found")

    # Access check: tag's account must be able to see the anchor
    if not _can_see_anchor(session, tag_id, anchor_id):
        raise AccessDeniedError(
            f"Tag's account cannot access anchor '{anchor_id}'"
        )

    # Duplicate check
    existing = session.get(AnchorTagAssociation, (anchor_id, tag_id))
    if existing:
        raise AlreadyExistsError(
            f"Association between anchor '{anchor_id}' and tag '{tag_id}' already exists"
        )

    assoc = AnchorTagAssociation(anchor_id=anchor_id, tag_id=tag_id)
    session.add(assoc)
    try:
        session.flush()
    except IntegrityError as exc:
        session.rollback()
        msg = str(exc.orig).lower()
        if "unique" in msg or "duplicate" in msg or "primary" in msg:
            raise AlreadyExistsError(
                f"Association between anchor '{anchor_id}' and tag '{tag_id}' already exists"
            ) from exc
        raise
    session.refresh(assoc)
    return assoc


def unlink_tag_from_anchor(
    session: Session, anchor_id: str, tag_id: str
) -> None:
    """Remove the association between a tag and an anchor."""
    assoc = session.get(AnchorTagAssociation, (anchor_id, tag_id))
    if not assoc:
        raise NotFoundError(
            f"No association between anchor '{anchor_id}' and tag '{tag_id}'"
        )
    session.delete(assoc)
    session.flush()


def list_associations_for_anchor(
    session: Session, anchor_id: str
) -> list[AnchorTagAssociation]:
    """List all tag associations for an anchor."""
    stmt = select(AnchorTagAssociation).where(
        AnchorTagAssociation.anchor_id == anchor_id
    )
    return list(session.exec(stmt).all())


def list_associations_for_tag(
    session: Session, tag_id: str
) -> list[AnchorTagAssociation]:
    """List all anchor associations for a tag."""
    stmt = select(AnchorTagAssociation).where(
        AnchorTagAssociation.tag_id == tag_id
    )
    return list(session.exec(stmt).all())
