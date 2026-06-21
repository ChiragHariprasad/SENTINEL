"""Integration tests for CSV Import endpoints."""

import io
import csv


class TestImportVendors:
    async def test_import_csv(self, auth_client):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["vendor_name", "vendor_type", "criticality", "contract_status"])
        writer.writerow(["ImportedCorp", "SaaS", "HIGH", "active"])
        writer.writerow(["SecondCorp", "Consulting", "MEDIUM", "active"])
        output.seek(0)

        res = await auth_client.post(
            "/api/v1/vendors/import",
            files={"file": ("vendors.csv", output.getvalue().encode("utf-8"), "text/csv")},
        )
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["processed"] == 2
        assert data["failed"] == 0

    async def test_import_duplicate_vendor(self, auth_client, sample_vendor):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["vendor_name", "vendor_type"])
        writer.writerow(["TestCorp", "SaaS"])  # same name as sample_vendor
        output.seek(0)

        res = await auth_client.post(
            "/api/v1/vendors/import",
            files={"file": ("vendors.csv", output.getvalue().encode("utf-8"), "text/csv")},
        )
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["processed"] == 0
        assert data["failed"] == 1

    async def test_import_invalid_format(self, auth_client):
        res = await auth_client.post(
            "/api/v1/vendors/import",
            files={"file": ("data.txt", b"not a csv", "text/plain")},
        )
        assert res.status_code == 422


class TestGetImportStatus:
    async def test_import_then_check_status(self, auth_client):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["vendor_name", "vendor_type"])
        writer.writerow(["StatusCorp", "SaaS"])
        output.seek(0)

        import_res = await auth_client.post(
            "/api/v1/vendors/import",
            files={"file": ("vendors.csv", output.getvalue().encode("utf-8"), "text/csv")},
        )
        job_id = import_res.json()["data"]["job_id"]

        res = await auth_client.get(f"/api/v1/vendors/imports/{job_id}")
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["status"] is not None
