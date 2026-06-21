"""Integration tests for Certification endpoints."""

from datetime import date, timedelta


class TestListCertifications:
    async def test_empty_list(self, auth_client):
        res = await auth_client.get("/api/v1/certifications")
        assert res.status_code == 200
        assert res.json()["data"]["items"] == []


class TestCreateCertification:
    async def test_create_cert(self, auth_client, sample_vendor):
        res = await auth_client.post("/api/v1/certifications", json={
            "vendor_id": str(sample_vendor.vendor_id),
            "certification_type": "SOC 2 Type II",
            "issuer": "AICPA",
            "expiry_date": (date.today() + timedelta(days=180)).isoformat(),
        })
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["certification_type"] == "SOC 2 Type II"
        assert data["status"] == "active"


class TestExpiringCertifications:
    async def test_expiring_empty(self, auth_client):
        res = await auth_client.get("/api/v1/certifications/expiring")
        assert res.status_code == 200

    async def test_expiring_with_data(self, auth_client, sample_vendor):
        await auth_client.post("/api/v1/certifications", json={
            "vendor_id": str(sample_vendor.vendor_id),
            "certification_type": "ISO 27001",
            "expiry_date": (date.today() + timedelta(days=10)).isoformat(),
        })
        res = await auth_client.get("/api/v1/certifications/expiring?days=30")
        assert res.status_code == 200
        assert len(res.json()["data"]["items"]) == 1


class TestFrameworks:
    async def test_list_frameworks(self, auth_client):
        res = await auth_client.get("/api/v1/certifications/frameworks")
        assert res.status_code == 200
