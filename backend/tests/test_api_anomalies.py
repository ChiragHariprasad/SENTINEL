"""Integration tests for Anomaly endpoints."""

import uuid


class TestListAnomalies:
    async def test_empty_anomalies(self, auth_client):
        res = await auth_client.get("/api/v1/anomalies")
        assert res.status_code == 200
        assert res.json()["data"]["count"] == 0

    async def test_requires_auth(self, client):
        res = await client.get("/api/v1/anomalies")
        assert res.status_code == 403


class TestAnomalyLabels:
    async def test_list_labels(self, auth_client):
        res = await auth_client.get("/api/v1/anomalies/labels")
        assert res.status_code == 200


class TestVendorAnomalies:
    async def test_vendor_anomalies_empty(self, auth_client, sample_vendor):
        res = await auth_client.get(f"/api/v1/anomalies/vendor/{sample_vendor.vendor_id}")
        assert res.status_code == 200
        assert res.json()["data"]["anomalies"] == []

    async def test_vendor_anomalies_nonexistent(self, auth_client):
        res = await auth_client.get(f"/api/v1/anomalies/vendor/{uuid.uuid4()}")
        assert res.status_code == 200
        assert res.json()["data"]["anomalies"] == []
