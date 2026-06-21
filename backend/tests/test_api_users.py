"""Integration tests for User management endpoints."""

import uuid


class TestListUsers:
    async def test_list_users(self, auth_client, admin_user, analyst_user):
        res = await auth_client.get("/api/v1/users")
        assert res.status_code == 200
        items = res.json()["data"]["items"]
        assert len(items) >= 2


class TestCreateUser:
    async def test_create_user(self, auth_client):
        res = await auth_client.post("/api/v1/users", json={
            "email": "newuser@test.com",
            "password": "Password123!",
            "first_name": "New",
            "role": "analyst",
        })
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["email"] == "newuser@test.com"
        assert data["role"] == "analyst"

    async def test_create_user_missing_fields(self, auth_client):
        res = await auth_client.post("/api/v1/users", json={"email": "incomplete@test.com"})
        assert res.status_code == 422


class TestGetUser:
    async def test_get_user(self, auth_client, admin_user):
        res = await auth_client.get(f"/api/v1/users/{admin_user.user_id}")
        assert res.status_code == 200
        assert res.json()["data"]["email"] == "admin@test.com"

    async def test_get_nonexistent(self, auth_client):
        res = await auth_client.get(f"/api/v1/users/{uuid.uuid4()}")
        assert res.status_code == 404


class TestUpdateUser:
    async def test_update_user(self, auth_client, analyst_user):
        res = await auth_client.put(f"/api/v1/users/{analyst_user.user_id}", json={
            "first_name": "Updated",
            "role": "executive",
        })
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["first_name"] == "Updated"
        assert data["role"] == "executive"

    async def test_update_nonexistent(self, auth_client):
        res = await auth_client.put(f"/api/v1/users/{uuid.uuid4()}", json={"first_name": "Ghost"})
        assert res.status_code == 404


class TestRoles:
    async def test_list_roles(self, auth_client, admin_user):
        res = await auth_client.get("/api/v1/users/roles/list")
        assert res.status_code == 200
        role_names = [r["role_name"] for r in res.json()["data"]["items"]]
        assert "admin" in role_names
        assert "analyst" in role_names
        assert "executive" in role_names
