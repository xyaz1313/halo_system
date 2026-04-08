"""Device API endpoint tests — Anchors, Tags, Associations via TestClient."""


class TestAnchorApi:
    def test_create_public_anchor(self, client):
        resp = client.post(
            "/api/v1/anchors",
            json={"label": "API Anchor", "visibility": "public"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["label"] == "API Anchor"
        assert data["visibility"] == "public"

    def test_get_anchor(self, client, session, sample_anchor_public):
        resp = client.get(f"/api/v1/anchors/{sample_anchor_public.id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == sample_anchor_public.id

    def test_get_anchor_not_found(self, client):
        resp = client.get("/api/v1/anchors/nonexistent")
        assert resp.status_code == 404

    def test_list_anchors_for_account(
        self, client, session, sample_account, sample_anchor_public
    ):
        resp = client.get(
            "/api/v1/anchors", params={"account_id": sample_account.id}
        )
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_update_anchor(self, client, session, sample_anchor_public):
        resp = client.patch(
            f"/api/v1/anchors/{sample_anchor_public.id}",
            json={"label": "Renamed"},
        )
        assert resp.status_code == 200
        assert resp.json()["label"] == "Renamed"

    def test_update_anchor_not_found(self, client):
        resp = client.patch(
            "/api/v1/anchors/nonexistent", json={"label": "X"}
        )
        assert resp.status_code == 404

    def test_delete_anchor(self, client, session, sample_anchor_public):
        resp = client.delete(f"/api/v1/anchors/{sample_anchor_public.id}")
        assert resp.status_code == 204

    def test_delete_anchor_not_found(self, client):
        resp = client.delete("/api/v1/anchors/nonexistent")
        assert resp.status_code == 404

    def test_visibility_validation_422(self, client, session, sample_account):
        resp = client.post(
            "/api/v1/anchors",
            json={
                "label": "Bad",
                "visibility": "private",
                # missing owner_account_id
            },
        )
        assert resp.status_code == 422


class TestTagApi:
    def test_create_tag(self, client, session, sample_account):
        resp = client.post(
            "/api/v1/tags",
            json={"account_id": sample_account.id, "label": "API Tag"},
        )
        assert resp.status_code == 201
        assert resp.json()["label"] == "API Tag"

    def test_get_tag(self, client, session, sample_tag):
        resp = client.get(f"/api/v1/tags/{sample_tag.id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == sample_tag.id

    def test_get_tag_not_found(self, client):
        resp = client.get("/api/v1/tags/nonexistent")
        assert resp.status_code == 404

    def test_list_tags(self, client, session, sample_account, sample_tag):
        resp = client.get(
            "/api/v1/tags", params={"account_id": sample_account.id}
        )
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_update_tag(self, client, session, sample_tag):
        resp = client.patch(
            f"/api/v1/tags/{sample_tag.id}", json={"label": "Renamed Tag"}
        )
        assert resp.status_code == 200
        assert resp.json()["label"] == "Renamed Tag"

    def test_delete_tag(self, client, session, sample_tag):
        resp = client.delete(f"/api/v1/tags/{sample_tag.id}")
        assert resp.status_code == 204

    def test_delete_tag_not_found(self, client):
        resp = client.delete("/api/v1/tags/nonexistent")
        assert resp.status_code == 404


class TestAssociationApi:
    def test_link_tag_to_anchor(
        self, client, session, sample_tag, sample_anchor_public
    ):
        resp = client.post(
            f"/api/v1/anchors/{sample_anchor_public.id}/tags/{sample_tag.id}"
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["anchor_id"] == sample_anchor_public.id
        assert data["tag_id"] == sample_tag.id

    def test_unlink_tag_from_anchor(
        self, client, session, sample_tag, sample_anchor_public
    ):
        # Link first
        client.post(
            f"/api/v1/anchors/{sample_anchor_public.id}/tags/{sample_tag.id}"
        )
        resp = client.delete(
            f"/api/v1/anchors/{sample_anchor_public.id}/tags/{sample_tag.id}"
        )
        assert resp.status_code == 204

    def test_list_tags_for_anchor(
        self, client, session, sample_tag, sample_anchor_public
    ):
        client.post(
            f"/api/v1/anchors/{sample_anchor_public.id}/tags/{sample_tag.id}"
        )
        resp = client.get(
            f"/api/v1/anchors/{sample_anchor_public.id}/tags"
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_duplicate_association_409(
        self, client, session, sample_tag, sample_anchor_public
    ):
        client.post(
            f"/api/v1/anchors/{sample_anchor_public.id}/tags/{sample_tag.id}"
        )
        resp = client.post(
            f"/api/v1/anchors/{sample_anchor_public.id}/tags/{sample_tag.id}"
        )
        assert resp.status_code == 409

    def test_list_anchors_for_tag(
        self, client, session, sample_tag, sample_anchor_public
    ):
        client.post(
            f"/api/v1/anchors/{sample_anchor_public.id}/tags/{sample_tag.id}"
        )
        resp = client.get(f"/api/v1/tags/{sample_tag.id}/anchors")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["anchor_id"] == sample_anchor_public.id

    def test_access_denied_403(self, client, session, sample_tag):
        # Create another account's private anchor
        from backend.accounts.service import create_account
        from backend.devices.service import create_anchor

        other = create_account(
            session,
            email="other2@example.com",
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
        resp = client.post(
            f"/api/v1/anchors/{other_anchor.id}/tags/{sample_tag.id}"
        )
        assert resp.status_code == 403
