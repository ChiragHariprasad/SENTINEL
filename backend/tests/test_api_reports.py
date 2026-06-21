"""Integration tests for Report endpoints."""


class TestGenerateReport:
    async def test_generate_csv_report(self, auth_client, sample_vendors):
        res = await auth_client.post("/api/v1/reports", params={"report_type": "vendor_risk_register"})
        assert res.status_code == 200
        assert "text/csv" in res.headers["content-type"]
        assert b"Vendor Name" in res.content
        assert b"Acme Corp" in res.content

    async def test_generate_report_no_vendors(self, auth_client):
        res = await auth_client.post("/api/v1/reports", params={"report_type": "vendor_risk_register"})
        assert res.status_code == 200


class TestDownloadReport:
    async def test_download_endpoint(self, auth_client):
        res = await auth_client.get("/api/v1/reports/some-id/download")
        assert res.status_code == 200
