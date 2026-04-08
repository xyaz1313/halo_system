"""Notification Preference API endpoint tests — full HTTP round-trips via TestClient."""


class TestPreferenceApi:
    def test_create_preference(self, client, session, sample_account):
        resp = client.post(
            "/api/v1/notifications/preferences",
            json={
                "account_id": sample_account.id,
                "alert_email": "api@alerts.com",
                "alert_types": ["mozo_departure"],
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["alert_email"] == "api@alerts.com"
        assert "schedule_confirmation" in data["alert_types"]

    def test_list_preferences(self, client, session, sample_account):
        client.post(
            "/api/v1/notifications/preferences",
            json={
                "account_id": sample_account.id,
                "alert_email": "list@a.com",
                "alert_types": ["schedule_confirmation"],
            },
        )
        resp = client.get("/api/v1/notifications/preferences")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_list_preferences_filtered(self, client, session, sample_account):
        client.post(
            "/api/v1/notifications/preferences",
            json={
                "account_id": sample_account.id,
                "alert_email": "filt@a.com",
                "alert_types": ["schedule_confirmation"],
            },
        )
        resp = client.get(
            "/api/v1/notifications/preferences",
            params={"account_id": sample_account.id},
        )
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_get_preference(self, client, session, sample_account):
        create_resp = client.post(
            "/api/v1/notifications/preferences",
            json={
                "account_id": sample_account.id,
                "alert_email": "get@a.com",
                "alert_types": ["schedule_confirmation"],
            },
        )
        pref_id = create_resp.json()["id"]
        resp = client.get(f"/api/v1/notifications/preferences/{pref_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == pref_id

    def test_get_preference_not_found(self, client):
        resp = client.get("/api/v1/notifications/preferences/nonexistent")
        assert resp.status_code == 404

    def test_update_preference(self, client, session, sample_account):
        create_resp = client.post(
            "/api/v1/notifications/preferences",
            json={
                "account_id": sample_account.id,
                "alert_email": "upd@a.com",
                "alert_types": ["schedule_confirmation"],
            },
        )
        pref_id = create_resp.json()["id"]
        resp = client.patch(
            f"/api/v1/notifications/preferences/{pref_id}",
            json={"alert_email": "new@a.com"},
        )
        assert resp.status_code == 200
        assert resp.json()["alert_email"] == "new@a.com"

    def test_update_alert_types_unknown_422(self, client, session, sample_account):
        create_resp = client.post(
            "/api/v1/notifications/preferences",
            json={
                "account_id": sample_account.id,
                "alert_email": "val@a.com",
                "alert_types": ["schedule_confirmation"],
            },
        )
        pref_id = create_resp.json()["id"]
        resp = client.patch(
            f"/api/v1/notifications/preferences/{pref_id}",
            json={"alert_types": ["bogus_type"]},
        )
        assert resp.status_code == 422

    def test_delete_preference(self, client, session, sample_account):
        create_resp = client.post(
            "/api/v1/notifications/preferences",
            json={
                "account_id": sample_account.id,
                "alert_email": "del@a.com",
                "alert_types": ["schedule_confirmation"],
            },
        )
        pref_id = create_resp.json()["id"]
        resp = client.delete(f"/api/v1/notifications/preferences/{pref_id}")
        assert resp.status_code == 204

    def test_delete_preference_not_found(self, client):
        resp = client.delete("/api/v1/notifications/preferences/nonexistent")
        assert resp.status_code == 404

    def test_patch_with_explicit_null_alert_types_422(
        self, client, session, sample_account
    ):
        """Sending alert_types: null in PATCH body should return 422, not silently drop it."""
        create_resp = client.post(
            "/api/v1/notifications/preferences",
            json={
                "account_id": sample_account.id,
                "alert_email": "null@a.com",
                "alert_types": ["schedule_confirmation"],
            },
        )
        pref_id = create_resp.json()["id"]
        resp = client.patch(
            f"/api/v1/notifications/preferences/{pref_id}",
            json={"alert_types": None},
        )
        assert resp.status_code == 422

    def test_create_unknown_alert_type_422(self, client, session, sample_account):
        resp = client.post(
            "/api/v1/notifications/preferences",
            json={
                "account_id": sample_account.id,
                "alert_email": "bad@a.com",
                "alert_types": ["invalid_type"],
            },
        )
        assert resp.status_code == 422
