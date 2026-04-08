"""Admin route tests — all 6 endpoints return correct data."""


class TestAdminRoutes:
    def test_accounts_empty(self, client):
        resp = client.get("/api/v1/admin/accounts")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_anchors_empty(self, client):
        resp = client.get("/api/v1/admin/anchors")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_tags_empty(self, client):
        resp = client.get("/api/v1/admin/tags")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_associations_empty(self, client):
        resp = client.get("/api/v1/admin/associations")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_calendars_empty(self, client):
        resp = client.get("/api/v1/admin/calendars")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_preferences_empty(self, client):
        resp = client.get("/api/v1/admin/preferences")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_accounts_with_data(self, client, session, sample_account):
        resp = client.get("/api/v1/admin/accounts")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["id"] == sample_account.id

    def test_anchors_with_data(self, client, session, sample_anchor_public):
        resp = client.get("/api/v1/admin/anchors")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["id"] == sample_anchor_public.id

    def test_tags_with_data(self, client, session, sample_tag):
        resp = client.get("/api/v1/admin/tags")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["id"] == sample_tag.id

    def test_calendars_with_data(self, client, session, sample_account):
        from backend.calendars.service import create_calendar

        cal = create_calendar(session, sample_account.id, "google", "ext-1")
        resp = client.get("/api/v1/admin/calendars")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["id"] == cal.id

    def test_preferences_with_data(self, client, session, sample_account):
        from backend.notifications.service import create_preference

        pref = create_preference(
            session, sample_account.id, "a@b.com", ["schedule_confirmation"]
        )
        resp = client.get("/api/v1/admin/preferences")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["id"] == pref.id

    def test_associations_with_data(
        self, client, session, sample_tag, sample_anchor_public
    ):
        from backend.devices.service import link_tag_to_anchor

        link_tag_to_anchor(session, sample_anchor_public.id, sample_tag.id)
        resp = client.get("/api/v1/admin/associations")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["anchor_id"] == sample_anchor_public.id
