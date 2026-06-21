"""Integration tests for Risk endpoints."""

import uuid


class TestRiskCalculate:
    async def test_calculate_risk(self, auth_client, sample_vendor):
        res = await auth_client.post("/api/v1/risk/calculate", params={"vendor_id": str(sample_vendor.vendor_id)})
        assert res.status_code == 200
        data = res.json()["data"]
        assert "overall_score" in data
        assert "risk_tier" in data
        assert isinstance(data["overall_score"], (int, float))

    async def test_calculate_nonexistent_vendor(self, auth_client):
        res = await auth_client.post("/api/v1/risk/calculate", params={"vendor_id": str(uuid.uuid4())})
        assert res.status_code == 404


class TestGetVendorRisk:
    async def test_get_risk(self, auth_client, sample_vendor):
        await auth_client.post("/api/v1/risk/calculate", params={"vendor_id": str(sample_vendor.vendor_id)})
        res = await auth_client.get(f"/api/v1/risk/vendors/{sample_vendor.vendor_id}")
        assert res.status_code == 200
        data = res.json()["data"]
        assert "overall_score" in data

    async def test_get_risk_no_score(self, auth_client, sample_vendor):
        res = await auth_client.get(f"/api/v1/risk/vendors/{sample_vendor.vendor_id}")
        assert res.status_code == 404


class TestRecalculate:
    async def test_recalculate_all(self, auth_client, sample_vendors):
        res = await auth_client.post("/api/v1/risk/recalculate")
        assert res.status_code == 200


class TestRiskHistory:
    async def test_get_history_empty(self, auth_client, sample_vendor):
        res = await auth_client.get(f"/api/v1/risk/vendors/{sample_vendor.vendor_id}/history")
        assert res.status_code == 200
        assert res.json()["data"]["history"] == []

    async def test_get_history_after_calculation(self, auth_client, sample_vendor):
        await auth_client.post("/api/v1/risk/calculate", params={"vendor_id": str(sample_vendor.vendor_id)})
        res = await auth_client.get(f"/api/v1/risk/vendors/{sample_vendor.vendor_id}/history")
        assert res.status_code == 200
        assert len(res.json()["data"]["history"]) == 1
