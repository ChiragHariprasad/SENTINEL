"""Integration tests for Alert endpoints."""


class TestListAlerts:
    async def test_empty_list(self, auth_client):
        res = await auth_client.get("/api/v1/alerts")
        assert res.status_code == 200
        assert res.json()["data"]["items"] == []


class TestCreateAlert:
    async def test_create_alert(self, auth_client, sample_vendor):
        res = await auth_client.post("/api/v1/alerts", json={
            "vendor_id": str(sample_vendor.vendor_id),
            "alert_type": "BREACH",
            "severity": "HIGH",
            "message": "Security breach detected",
        })
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["alert_type"] == "BREACH"
        assert data["severity"] == "HIGH"
        assert data["status"] == "open"


class TestResolveAlert:
    async def test_resolve_alert(self, auth_client, sample_vendor):
        create_res = await auth_client.post("/api/v1/alerts", json={
            "vendor_id": str(sample_vendor.vendor_id),
            "alert_type": "BREACH",
            "severity": "HIGH",
            "message": "Test alert",
        })
        alert_id = create_res.json()["data"]["alert_id"]

        res = await auth_client.patch(f"/api/v1/alerts/{alert_id}/resolve")
        assert res.status_code == 200
        assert res.json()["data"]["status"] == "resolved"

    async def test_resolve_nonexistent(self, auth_client):
        import uuid
        res = await auth_client.patch(f"/api/v1/alerts/{uuid.uuid4()}/resolve")
        assert res.status_code == 404
