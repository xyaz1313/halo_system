"""Calendar model and service tests — direct DB, no HTTP."""

import pytest

from backend.calendars.service import (
    create_calendar,
    delete_calendar,
    get_calendar,
    list_calendars_for_account,
    update_calendar,
    update_sync_status,
)
from backend.core.exceptions import NotFoundError, ValidationError


class TestCalendarCrud:
    def test_create(self, session, sample_account):
        cal = create_calendar(
            session, sample_account.id, "google", "ext-cal-123"
        )
        assert cal.provider == "google"
        assert cal.external_calendar_id == "ext-cal-123"
        assert cal.sync_status == "syncing"

    def test_get(self, session, sample_account):
        cal = create_calendar(
            session, sample_account.id, "google", "ext-cal-456"
        )
        found = get_calendar(session, cal.id)
        assert found.id == cal.id

    def test_get_not_found(self, session):
        with pytest.raises(NotFoundError):
            get_calendar(session, "no-such-calendar")

    def test_list_for_account(self, session, sample_account):
        create_calendar(session, sample_account.id, "google", "c1")
        create_calendar(session, sample_account.id, "outlook", "c2")
        cals = list_calendars_for_account(session, sample_account.id)
        assert len(cals) == 2

    def test_delete(self, session, sample_account):
        cal = create_calendar(
            session, sample_account.id, "google", "to-delete"
        )
        delete_calendar(session, cal.id)
        with pytest.raises(NotFoundError):
            get_calendar(session, cal.id)

    def test_delete_not_found(self, session):
        with pytest.raises(NotFoundError):
            delete_calendar(session, "no-such-calendar")


class TestCalendarSyncStatus:
    def test_update_sync_status(self, session, sample_account):
        cal = create_calendar(
            session, sample_account.id, "google", "ext-sync"
        )
        updated = update_sync_status(session, cal.id, "synced")
        assert updated.sync_status == "synced"

    def test_invalid_sync_status(self, session, sample_account):
        cal = create_calendar(
            session, sample_account.id, "google", "ext-bad"
        )
        with pytest.raises(ValidationError, match="sync_status"):
            update_sync_status(session, cal.id, "invalid_status")


class TestCalendarImmutability:
    def test_reject_provider_change(self, session, sample_account):
        cal = create_calendar(
            session, sample_account.id, "google", "ext-imm"
        )
        with pytest.raises(ValidationError, match="immutable"):
            update_calendar(session, cal.id, provider="outlook")

    def test_reject_external_calendar_id_change(self, session, sample_account):
        cal = create_calendar(
            session, sample_account.id, "google", "ext-imm2"
        )
        with pytest.raises(ValidationError, match="immutable"):
            update_calendar(session, cal.id, external_calendar_id="new-id")

    def test_allow_sync_status_update(self, session, sample_account):
        cal = create_calendar(
            session, sample_account.id, "google", "ext-ok"
        )
        updated = update_calendar(session, cal.id, sync_status="synced")
        assert updated.sync_status == "synced"
