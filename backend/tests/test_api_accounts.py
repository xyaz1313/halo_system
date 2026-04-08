"""Account API endpoint tests — full HTTP round-trips via TestClient."""


class TestAccountApi:
    def test_create_account(self, client):
        resp = client.post(
            "/api/v1/accounts",
            json={
                "email": "api@example.com",
                "patient_name": "ApiUser",
                "patient_age": 55,
                "patient_diagnosis_stage": "mild",
                "patient_notes": "",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "api@example.com"
        assert "id" in data

    def test_list_accounts(self, client, session, sample_account):
        resp = client.get("/api/v1/accounts")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
        assert len(resp.json()) >= 1

    def test_get_account(self, client, session, sample_account):
        resp = client.get(f"/api/v1/accounts/{sample_account.id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == sample_account.id

    def test_get_account_not_found(self, client):
        resp = client.get("/api/v1/accounts/nonexistent")
        assert resp.status_code == 404

    def test_update_account(self, client, session, sample_account):
        resp = client.patch(
            f"/api/v1/accounts/{sample_account.id}",
            json={"patient_name": "Updated"},
        )
        assert resp.status_code == 200
        assert resp.json()["patient_name"] == "Updated"

    def test_update_account_not_found(self, client):
        resp = client.patch(
            "/api/v1/accounts/nonexistent",
            json={"patient_name": "X"},
        )
        assert resp.status_code == 404

    def test_delete_account(self, client, session, sample_account):
        resp = client.delete(f"/api/v1/accounts/{sample_account.id}")
        assert resp.status_code == 204

    def test_delete_account_not_found(self, client):
        resp = client.delete("/api/v1/accounts/nonexistent")
        assert resp.status_code == 404

    def test_duplicate_email_409(self, client, session, sample_account):
        resp = client.post(
            "/api/v1/accounts",
            json={
                "email": sample_account.email,
                "patient_name": "Dup",
                "patient_age": 50,
                "patient_diagnosis_stage": "mild",
                "patient_notes": "",
            },
        )
        assert resp.status_code == 409

    def test_validation_error_422(self, client):
        # Missing required fields
        resp = client.post(
            "/api/v1/accounts",
            json={"email": "bad@example.com"},
        )
        assert resp.status_code == 422
