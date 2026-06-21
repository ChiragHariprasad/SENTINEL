"""Integration tests for Contract endpoints."""

import uuid


class TestUploadContract:
    async def test_upload_txt_contract(self, auth_client, sample_vendor):
        res = await auth_client.post(
            "/api/v1/contracts/upload",
            data={"vendor_id": str(sample_vendor.vendor_id), "contract_name": "Test Contract"},
            files={"file": ("contract.txt", b"This is a test contract with some terms and conditions.", "text/plain")},
        )
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["status"] == "uploaded"
        assert "contract_id" in data

    async def test_upload_without_auth(self, client, sample_vendor):
        res = await client.post(
            "/api/v1/contracts/upload",
            data={"vendor_id": str(sample_vendor.vendor_id)},
            files={"file": ("contract.txt", b"test", "text/plain")},
        )
        assert res.status_code == 403


class TestGetContract:
    async def test_get_contract(self, auth_client, sample_vendor):
        upload = await auth_client.post(
            "/api/v1/contracts/upload",
            data={"vendor_id": str(sample_vendor.vendor_id)},
            files={"file": ("test.txt", b"test", "text/plain")},
        )
        cid = upload.json()["data"]["contract_id"]

        res = await auth_client.get(f"/api/v1/contracts/{cid}")
        assert res.status_code == 200
        assert res.json()["data"]["contract_id"] == cid

    async def test_get_nonexistent(self, auth_client):
        res = await auth_client.get(f"/api/v1/contracts/{uuid.uuid4()}")
        assert res.status_code == 404
