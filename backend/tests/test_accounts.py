"""Account model and service tests — direct DB, no HTTP."""

import pytest

from backend.accounts.service import (
    create_account,
    delete_account,
    get_account,
    get_account_by_email,
    list_accounts,
    update_account,
)
from backend.core.exceptions import AlreadyExistsError, NotFoundError


class TestCreateAccount:
    def test_create_with_required_fields(self, session):
        acct = create_account(
            session,
            email="bob@example.com",
            patient_name="Bob",
            patient_age=65,
            patient_diagnosis_stage="moderate",
            patient_notes="",
        )
        assert acct.id
        assert acct.email == "bob@example.com"
        assert acct.patient_name == "Bob"
        assert acct.patient_age == 65
        assert acct.created_at is not None

    def test_create_with_optional_caretaker_fields(self, session):
        acct = create_account(
            session,
            email="carol@example.com",
            patient_name="Carol",
            patient_age=80,
            patient_diagnosis_stage="severe",
            patient_notes="needs help",
            caretaker_name="Dan",
            caretaker_email="dan@example.com",
        )
        assert acct.caretaker_name == "Dan"
        assert acct.caretaker_email == "dan@example.com"

    def test_duplicate_email_raises(self, session):
        create_account(
            session,
            email="dup@example.com",
            patient_name="First",
            patient_age=60,
            patient_diagnosis_stage="mild",
            patient_notes="",
        )
        with pytest.raises(AlreadyExistsError, match="already exists"):
            create_account(
                session,
                email="dup@example.com",
                patient_name="Second",
                patient_age=70,
                patient_diagnosis_stage="mild",
                patient_notes="",
            )


class TestGetAccount:
    def test_get_by_id(self, session, sample_account):
        acct = get_account(session, sample_account.id)
        assert acct.email == sample_account.email

    def test_get_not_found(self, session):
        with pytest.raises(NotFoundError):
            get_account(session, "nonexistent-id")

    def test_get_by_email(self, session, sample_account):
        acct = get_account_by_email(session, sample_account.email)
        assert acct is not None
        assert acct.id == sample_account.id

    def test_get_by_email_not_found(self, session):
        result = get_account_by_email(session, "no-such@example.com")
        assert result is None


class TestListAccounts:
    def test_list_empty(self, session):
        assert list_accounts(session) == []

    def test_list_returns_all(self, session, sample_account):
        accounts = list_accounts(session)
        assert len(accounts) == 1
        assert accounts[0].id == sample_account.id


class TestUpdateAccount:
    def test_update_fields(self, session, sample_account):
        updated = update_account(session, sample_account.id, patient_name="Alice Updated")
        assert updated.patient_name == "Alice Updated"

    def test_update_not_found(self, session):
        with pytest.raises(NotFoundError):
            update_account(session, "nonexistent-id", patient_name="X")


class TestUpdateAccountAllowlist:
    def test_rejects_non_patchable_field(self, session, sample_account):
        from backend.core.exceptions import ValidationError

        with pytest.raises(ValidationError, match="Cannot patch"):
            update_account(session, sample_account.id, id="new-id")


class TestDeleteAccount:
    def test_delete(self, session, sample_account):
        delete_account(session, sample_account.id)
        with pytest.raises(NotFoundError):
            get_account(session, sample_account.id)

    def test_delete_not_found(self, session):
        with pytest.raises(NotFoundError):
            delete_account(session, "nonexistent-id")


class TestAccountCascadeDelete:
    """Verify cascade delete: account removal cascades to tags, calendars,
    preferences, and private anchors."""

    def test_cascade_deletes_children(self, session):
        from sqlmodel import select

        from backend.calendars.models import Calendar
        from backend.calendars.service import create_calendar
        from backend.devices.models import Anchor, Tag
        from backend.devices.service import create_anchor, create_tag
        from backend.notifications.models import NotificationPreference
        from backend.notifications.service import create_preference

        # Create account with child objects
        acct = create_account(
            session,
            email="cascade@example.com",
            patient_name="Cascade",
            patient_age=70,
            patient_diagnosis_stage="mild",
            patient_notes="",
        )
        tag = create_tag(session, acct.id, label="CascadeTag")
        private_anchor = create_anchor(
            session,
            label="CascadeAnchor",
            visibility="private",
            owner_account_id=acct.id,
        )
        cal = create_calendar(session, acct.id, "google", "cascade-ext")
        pref = create_preference(
            session, acct.id, "cascade@a.com", ["schedule_confirmation"]
        )

        # Verify children exist
        assert session.get(Tag, tag.id) is not None
        assert session.get(Anchor, private_anchor.id) is not None
        assert session.get(Calendar, cal.id) is not None
        assert session.get(NotificationPreference, pref.id) is not None

        # Delete the account
        delete_account(session, acct.id)

        # Verify all children are gone
        assert session.exec(
            select(Tag).where(Tag.account_id == acct.id)
        ).first() is None
        assert session.exec(
            select(Anchor).where(Anchor.owner_account_id == acct.id)
        ).first() is None
        assert session.exec(
            select(Calendar).where(Calendar.account_id == acct.id)
        ).first() is None
        assert session.exec(
            select(NotificationPreference).where(
                NotificationPreference.account_id == acct.id
            )
        ).first() is None
