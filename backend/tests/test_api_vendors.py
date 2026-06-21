"""Integration tests for Vendor endpoints."""

import uuid


class TestListVendors:
    async def test_empty_list(self, auth_client):
        res = await auth_client.get("/api/v1/vendors")
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["total"] == 0
        assert data["items"] == []

    async def test_list_with_vendors(self, auth_client, sample_vendors):
        res = await auth_client.get("/api/v1/vendors")
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["total"] == 3
        assert len(data["items"]) == 3

    async def test_filter_by_risk_tier(self, auth_client, sample_vendors):
        res = await auth_client.get("/api/v1/vendors?risk_tier=RED")
        assert res.status_code == 200
        items = res.json()["data"]["items"]
        assert all(v["risk_tier"] == "RED" for v in items)

    async def test_search(self, auth_client, sample_vendors):
        res = await auth_client.get("/api/v1/vendors?search=Acme")
        assert res.status_code == 200
        items = res.json()["data"]["items"]
        assert len(items) == 1
        assert items[0]["vendor_name"] == "Acme Corp"

    async def test_requires_auth(self, client):
        res = await client.get("/api/v1/vendors")
        assert res.status_code == 403


class TestCreateVendor:
    async def test_create_vendor(self, auth_client):
        res = await auth_client.post("/api/v1/vendors", json={
            "vendor_name": "NewVendor Inc",
            "vendor_type": "SaaS",
            "criticality": "HIGH",
        })
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["vendor_name"] == "NewVendor Inc"
        assert data["vendor_type"] == "SaaS"
        assert data["criticality"] == "HIGH"
        assert "vendor_id" in data

    async def test_create_vendor_missing_name(self, auth_client):
        res = await auth_client.post("/api/v1/vendors", json={"vendor_type": "SaaS"})
        assert res.status_code == 422


class TestGetVendor:
    async def test_get_vendor(self, auth_client, sample_vendor):
        res = await auth_client.get(f"/api/v1/vendors/{sample_vendor.vendor_id}")
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["vendor_name"] == "TestCorp"

    async def test_get_nonexistent_vendor(self, auth_client):
        res = await auth_client.get(f"/api/v1/vendors/{uuid.uuid4()}")
        assert res.status_code == 404


class TestUpdateVendor:
    async def test_update_vendor(self, auth_client, sample_vendor):
        res = await auth_client.put(f"/api/v1/vendors/{sample_vendor.vendor_id}", json={
            "vendor_name": "UpdatedCorp",
            "criticality": "LOW",
        })
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["vendor_name"] == "UpdatedCorp"
        assert data["criticality"] == "LOW"

    async def test_update_nonexistent(self, auth_client):
        res = await auth_client.put(f"/api/v1/vendors/{uuid.uuid4()}", json={"vendor_name": "Ghost"})
        assert res.status_code == 404


class TestDeleteVendor:
    async def test_archive_vendor(self, auth_client, sample_vendor):
        res = await auth_client.delete(f"/api/v1/vendors/{sample_vendor.vendor_id}")
        assert res.status_code == 200

        get_res = await auth_client.get(f"/api/v1/vendors/{sample_vendor.vendor_id}")
        assert get_res.status_code == 200
        data = get_res.json()
        assert data["data"]["is_archived"] == True


class TestCategories:
    async def test_list_categories(self, auth_client):
        res = await auth_client.get("/api/v1/vendors/categories/list")
        assert res.status_code == 200


class TestDataAccess:
    async def test_create_data_access(self, auth_client, sample_vendor):
        res = await auth_client.post("/api/v1/vendors/data-access", json={
            "vendor_id": str(sample_vendor.vendor_id),
            "data_type": "PII",
            "access_level": "Read",
        })
        assert res.status_code == 200

    async def test_list_data_access(self, auth_client, sample_vendor):
        res = await auth_client.get(f"/api/v1/vendors/{sample_vendor.vendor_id}/data-access")
        assert res.status_code == 200
        assert res.json()["data"]["items"] is not None
