"""Integration tests for Dashboard endpoint."""


class TestDashboardSummary:
    async def test_dashboard_empty(self, auth_client):
        res = await auth_client.get("/api/v1/dashboard/summary")
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["total_vendors"] == 0
        assert data["critical_vendors"] == 0
        assert data["open_alerts"] == 0
        assert data["total_anomalies"] == 0
        assert data["evaluation_summary"] is None

    async def test_dashboard_with_data(self, auth_client, sample_vendors):
        res = await auth_client.get("/api/v1/dashboard/summary")
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["total_vendors"] == 3
        assert data["risk_distribution"] is not None
