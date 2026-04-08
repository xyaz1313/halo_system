"""Calendar API endpoint tests — full HTTP round-trips via TestClient."""


class TestCalendarApi:
    def test_create_calendar(self, client, session, sample_account):
        resp = client.post(
            "/api/v1/calendars",
            json={
                "account_id": sample_account.id,
                "provider": "google",
                "external_calendar_id": "ext-api-1",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["provider"] == "google"
        assert data["sync_status"] == "syncing"

    def test_list_calendars(self, client, session, sample_account):
        client.post(
            "/api/v1/calendars",
            json={
                "account_id": sample_account.id,
                "provider": "google",
                "external_calendar_id": "ext-list-1",
            },
        )
        resp = client.get("/api/v1/calendars")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_list_calendars_filtered(self, client, session, sample_account):
        client.post(
            "/api/v1/calendars",
            json={
                "account_id": sample_account.id,
                "provider": "google",
                "external_calendar_id": "ext-filter-1",
            },
        )
        resp = client.get(
            "/api/v1/calendars",
            params={"account_id": sample_account.id},
        )
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_get_calendar(self, client, session, sample_account):
        create_resp = client.post(
            "/api/v1/calendars",
            json={
                "account_id": sample_account.id,
                "provider": "google",
                "external_calendar_id": "ext-get-1",
            },
        )
        cal_id = create_resp.json()["id"]
        resp = client.get(f"/api/v1/calendars/{cal_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == cal_id

    def test_get_calendar_not_found(self, client):
        resp = client.get("/api/v1/calendars/nonexistent")
        assert resp.status_code == 404

    def test_update_calendar(self, client, session, sample_account):
        create_resp = client.post(
            "/api/v1/calendars",
            json={
                "account_id": sample_account.id,
                "provider": "google",
                "external_calendar_id": "ext-upd-1",
            },
        )
        cal_id = create_resp.json()["id"]
        resp = client.patch(
            f"/api/v1/calendars/{cal_id}",
            json={"sync_status": "synced"},
        )
        assert resp.status_code == 200
        assert resp.json()["sync_status"] == "synced"

    def test_update_immutable_field_422(self, client, session, sample_account):
        """Attempting to PATCH immutable fields (provider, external_calendar_id)
        is rejected at the API layer with 422 via Pydantic extra='forbid'."""
        create_resp = client.post(
            "/api/v1/calendars",
            json={
                "account_id": sample_account.id,
                "provider": "google",
                "external_calendar_id": "ext-imm-1",
            },
        )
        cal_id = create_resp.json()["id"]
        resp = client.patch(
            f"/api/v1/calendars/{cal_id}",
            json={"provider": "outlook"},
        )
        assert resp.status_code == 422

    def test_update_external_calendar_id_422(self, client, session, sample_account):
        create_resp = client.post(
            "/api/v1/calendars",
            json={
                "account_id": sample_account.id,
                "provider": "google",
                "external_calendar_id": "ext-imm-2",
            },
        )
        cal_id = create_resp.json()["id"]
        resp = client.patch(
            f"/api/v1/calendars/{cal_id}",
            json={"external_calendar_id": "new-id"},
        )
        assert resp.status_code == 422

    def test_invalid_sync_status_422(self, client, session, sample_account):
        create_resp = client.post(
            "/api/v1/calendars",
            json={
                "account_id": sample_account.id,
                "provider": "google",
                "external_calendar_id": "ext-invalid-sync",
            },
        )
        cal_id = create_resp.json()["id"]
        resp = client.patch(
            f"/api/v1/calendars/{cal_id}",
            json={"sync_status": "bad_status"},
        )
        assert resp.status_code == 422

    def test_delete_calendar(self, client, session, sample_account):
        create_resp = client.post(
            "/api/v1/calendars",
            json={
                "account_id": sample_account.id,
                "provider": "google",
                "external_calendar_id": "ext-del-1",
            },
        )
        cal_id = create_resp.json()["id"]
        resp = client.delete(f"/api/v1/calendars/{cal_id}")
        assert resp.status_code == 204

    def test_delete_calendar_not_found(self, client):
        resp = client.delete("/api/v1/calendars/nonexistent")
        assert resp.status_code == 404
