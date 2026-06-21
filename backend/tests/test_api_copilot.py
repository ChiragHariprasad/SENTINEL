"""Integration tests for Copilot endpoint."""


class TestCopilotQuery:
    async def test_copilot_empty_db(self, auth_client):
        res = await auth_client.post("/api/v1/copilot/query", json={
            "question": "Show me all vendors",
        })
        assert res.status_code == 200
        data = res.json()["data"]
        assert "answer" in data

    async def test_copilot_requires_auth(self, client):
        res = await client.post("/api/v1/copilot/query", json={
            "question": "Show me all vendors",
        })
        assert res.status_code == 403
