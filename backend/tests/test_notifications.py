"""NotificationPreference model and service tests — direct DB, no HTTP."""

import pytest

from backend.core.exceptions import NotFoundError, ValidationError
from backend.notifications.service import (
    create_preference,
    delete_preference,
    get_preference,
    list_preferences_for_account,
    update_preference,
)


class TestPreferenceCrud:
    def test_create(self, session, sample_account):
        pref = create_preference(
            session,
            sample_account.id,
            alert_email="alerts@example.com",
            alert_types=["mozo_departure"],
        )
        assert pref.alert_email == "alerts@example.com"
        # schedule_confirmation auto-included
        assert "schedule_confirmation" in pref.alert_types
        assert "mozo_departure" in pref.alert_types

    def test_get(self, session, sample_account):
        pref = create_preference(
            session,
            sample_account.id,
            alert_email="a@b.com",
            alert_types=["schedule_confirmation"],
        )
        found = get_preference(session, pref.id)
        assert found.id == pref.id

    def test_get_not_found(self, session):
        with pytest.raises(NotFoundError):
            get_preference(session, "no-such-pref")

    def test_list_for_account(self, session, sample_account):
        create_preference(
            session, sample_account.id, "a@b.com", ["schedule_confirmation"]
        )
        create_preference(
            session, sample_account.id, "c@d.com", ["mozo_departure"]
        )
        prefs = list_preferences_for_account(session, sample_account.id)
        assert len(prefs) == 2

    def test_delete(self, session, sample_account):
        pref = create_preference(
            session, sample_account.id, "x@y.com", ["schedule_confirmation"]
        )
        delete_preference(session, pref.id)
        with pytest.raises(NotFoundError):
            get_preference(session, pref.id)

    def test_delete_not_found(self, session):
        with pytest.raises(NotFoundError):
            delete_preference(session, "no-such-pref")


class TestPreferenceUpdate:
    def test_update_alert_email(self, session, sample_account):
        pref = create_preference(
            session, sample_account.id, "old@b.com", ["schedule_confirmation"]
        )
        updated = update_preference(session, pref.id, alert_email="new@b.com")
        assert updated.alert_email == "new@b.com"

    def test_update_alert_types(self, session, sample_account):
        pref = create_preference(
            session, sample_account.id, "a@b.com", ["schedule_confirmation"]
        )
        updated = update_preference(
            session, pref.id, alert_types=["mozo_departure", "schedule_conflict"]
        )
        assert "mozo_departure" in updated.alert_types
        assert "schedule_conflict" in updated.alert_types
        assert "schedule_confirmation" in updated.alert_types


class TestAlertTypesValidation:
    def test_unknown_alert_type_raises(self, session, sample_account):
        with pytest.raises(ValidationError, match="Unknown alert types"):
            create_preference(
                session,
                sample_account.id,
                "a@b.com",
                ["bogus_type"],
            )

    def test_schedule_confirmation_auto_included(self, session, sample_account):
        pref = create_preference(
            session,
            sample_account.id,
            "a@b.com",
            ["mozo_departure"],
        )
        assert "schedule_confirmation" in pref.alert_types

    def test_deduplication(self, session, sample_account):
        pref = create_preference(
            session,
            sample_account.id,
            "a@b.com",
            ["mozo_departure", "mozo_departure", "schedule_confirmation"],
        )
        assert pref.alert_types.count("mozo_departure") == 1


class TestPreferenceUpdateNullHandling:
    """Verify that explicit null values are passed through to service validation."""

    def test_update_alert_types_null_raises(self, session, sample_account):
        """Setting alert_types to None should raise ValidationError, not be silently dropped."""
        pref = create_preference(
            session, sample_account.id, "a@b.com", ["schedule_confirmation"]
        )
        with pytest.raises(ValidationError, match="cannot be null"):
            update_preference(session, pref.id, alert_types=None)

    def test_update_rejects_non_patchable_field(self, session, sample_account):
        """Attempting to PATCH a non-patchable field should raise ValidationError."""
        pref = create_preference(
            session, sample_account.id, "a@b.com", ["schedule_confirmation"]
        )
        with pytest.raises(ValidationError, match="Cannot patch"):
            update_preference(session, pref.id, account_id="other-id")


class TestJsonRoundTrip:
    def test_alert_types_persisted(self, session, sample_account):
        pref = create_preference(
            session,
            sample_account.id,
            "a@b.com",
            ["mozo_departure", "schedule_conflict"],
        )
        # Re-fetch from DB
        fetched = get_preference(session, pref.id)
        assert isinstance(fetched.alert_types, list)
        assert "mozo_departure" in fetched.alert_types
        assert "schedule_confirmation" in fetched.alert_types
