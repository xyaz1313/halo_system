"""Device model and service tests — Anchor, Tag, Association direct DB tests."""

import pytest

from backend.core.exceptions import (
    AccessDeniedError,
    AlreadyExistsError,
    NotFoundError,
    ValidationError,
)
from backend.devices.service import (
    create_anchor,
    create_tag,
    delete_anchor,
    delete_tag,
    get_anchor,
    get_tag,
    link_tag_to_anchor,
    list_anchors_for_account,
    list_associations_for_anchor,
    list_tags_for_account,
    unlink_tag_from_anchor,
    update_anchor,
)


class TestAnchorCreate:
    def test_create_public(self, session):
        anchor = create_anchor(session, label="Public A", visibility="public")
        assert anchor.visibility == "public"
        assert anchor.owner_account_id is None

    def test_create_private_with_owner(self, session, sample_account):
        anchor = create_anchor(
            session,
            label="Private A",
            visibility="private",
            owner_account_id=sample_account.id,
        )
        assert anchor.visibility == "private"
        assert anchor.owner_account_id == sample_account.id

    def test_reject_private_without_owner(self, session):
        with pytest.raises(ValidationError, match="require"):
            create_anchor(session, label="Bad", visibility="private")

    def test_reject_public_with_owner(self, session, sample_account):
        with pytest.raises(ValidationError, match="must not"):
            create_anchor(
                session,
                label="Bad",
                visibility="public",
                owner_account_id=sample_account.id,
            )


class TestAnchorVisibilityUpdate:
    def test_change_to_public_nulls_owner(self, session, sample_anchor_private):
        updated = update_anchor(
            session, sample_anchor_private.id, visibility="public"
        )
        assert updated.visibility == "public"
        assert updated.owner_account_id is None

    def test_change_to_private_requires_owner(self, session, sample_anchor_public):
        with pytest.raises(ValidationError, match="requires owner"):
            update_anchor(
                session, sample_anchor_public.id, visibility="private"
            )


class TestTagCrud:
    def test_create_tag(self, session, sample_account):
        tag = create_tag(session, sample_account.id, label="T1")
        assert tag.account_id == sample_account.id
        assert tag.label == "T1"

    def test_get_tag(self, session, sample_tag):
        tag = get_tag(session, sample_tag.id)
        assert tag.id == sample_tag.id

    def test_get_tag_not_found(self, session):
        with pytest.raises(NotFoundError):
            get_tag(session, "no-such-tag")

    def test_list_tags_for_account(self, session, sample_account, sample_tag):
        tags = list_tags_for_account(session, sample_account.id)
        assert len(tags) == 1
        assert tags[0].id == sample_tag.id

    def test_delete_tag(self, session, sample_tag):
        delete_tag(session, sample_tag.id)
        with pytest.raises(NotFoundError):
            get_tag(session, sample_tag.id)


class TestAssociation:
    def test_link_tag_to_public_anchor(
        self, session, sample_tag, sample_anchor_public
    ):
        assoc = link_tag_to_anchor(
            session, sample_anchor_public.id, sample_tag.id
        )
        assert assoc.anchor_id == sample_anchor_public.id
        assert assoc.tag_id == sample_tag.id

    def test_link_tag_to_owned_private_anchor(
        self, session, sample_tag, sample_anchor_private
    ):
        assoc = link_tag_to_anchor(
            session, sample_anchor_private.id, sample_tag.id
        )
        assert assoc.anchor_id == sample_anchor_private.id

    def test_reject_link_to_other_private_anchor(self, session, sample_tag):
        # Create a second account and a private anchor owned by it
        from backend.accounts.service import create_account

        other = create_account(
            session,
            email="other@example.com",
            patient_name="Other",
            patient_age=50,
            patient_diagnosis_stage="mild",
            patient_notes="",
        )
        other_anchor = create_anchor(
            session,
            label="Other Private",
            visibility="private",
            owner_account_id=other.id,
        )
        with pytest.raises(AccessDeniedError):
            link_tag_to_anchor(session, other_anchor.id, sample_tag.id)

    def test_duplicate_association_raises(
        self, session, sample_tag, sample_anchor_public
    ):
        link_tag_to_anchor(session, sample_anchor_public.id, sample_tag.id)
        with pytest.raises(AlreadyExistsError):
            link_tag_to_anchor(session, sample_anchor_public.id, sample_tag.id)

    def test_unlink(self, session, sample_tag, sample_anchor_public):
        link_tag_to_anchor(session, sample_anchor_public.id, sample_tag.id)
        unlink_tag_from_anchor(session, sample_anchor_public.id, sample_tag.id)
        assocs = list_associations_for_anchor(session, sample_anchor_public.id)
        assert len(assocs) == 0

    def test_unlink_not_found(self, session):
        with pytest.raises(NotFoundError):
            unlink_tag_from_anchor(session, "bad-anchor", "bad-tag")


class TestOwnerAccountIdValidation:
    """Verify that empty-string owner_account_id is not silently accepted."""

    def test_empty_string_owner_rejected_on_create(self, session):
        """An empty string is not None, so it should fail account lookup."""
        with pytest.raises(NotFoundError):
            create_anchor(
                session,
                label="Bad",
                visibility="private",
                owner_account_id="",
            )

    def test_empty_string_owner_rejected_on_update(
        self, session, sample_anchor_public
    ):
        """Changing to private with empty-string owner should fail (account not found)."""
        with pytest.raises(NotFoundError, match="not found"):
            update_anchor(
                session,
                sample_anchor_public.id,
                visibility="private",
                owner_account_id="",
            )


class TestPatchableFieldAllowlist:
    """Verify that non-patchable fields are rejected."""

    def test_anchor_rejects_non_patchable_field(self, session, sample_anchor_public):
        with pytest.raises(ValidationError, match="Cannot patch"):
            update_anchor(session, sample_anchor_public.id, id="new-id")

    def test_tag_rejects_non_patchable_field(self, session, sample_tag):
        from backend.devices.service import update_tag

        with pytest.raises(ValidationError, match="Cannot patch"):
            update_tag(session, sample_tag.id, account_id="other-account")


class TestListAnchorsForAccount:
    def test_returns_public_and_owned_private(
        self, session, sample_account, sample_anchor_public, sample_anchor_private
    ):
        anchors = list_anchors_for_account(session, sample_account.id)
        ids = {a.id for a in anchors}
        assert sample_anchor_public.id in ids
        assert sample_anchor_private.id in ids


class TestDeleteCascade:
    def test_delete_anchor_cascades_associations(
        self, session, sample_tag, sample_anchor_public
    ):
        link_tag_to_anchor(session, sample_anchor_public.id, sample_tag.id)
        delete_anchor(session, sample_anchor_public.id)
        assocs = list_associations_for_anchor(session, sample_anchor_public.id)
        assert len(assocs) == 0

    def test_delete_tag_cascades_associations(
        self, session, sample_tag, sample_anchor_public
    ):
        link_tag_to_anchor(session, sample_anchor_public.id, sample_tag.id)
        delete_tag(session, sample_tag.id)
        assocs = list_associations_for_anchor(session, sample_anchor_public.id)
        assert len(assocs) == 0
