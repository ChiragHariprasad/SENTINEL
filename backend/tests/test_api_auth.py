"""Integration tests for Auth endpoints."""


class TestSignup:
    async def test_signup_success(self, client):
        res = await client.post("/api/v1/auth/signup", json={
            "email": "newuser@test.com",
            "password": "Password123!",
        })
        assert res.status_code == 200
        data = res.json()["data"]
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_signup_duplicate_email(self, client, admin_user):
        res = await client.post("/api/v1/auth/signup", json={
            "email": "admin@test.com",
            "password": "Password123!",
        })
        assert res.status_code == 409


class TestLogin:
    async def test_login_success(self, client, admin_user):
        res = await client.post("/api/v1/auth/login", json={
            "email": "admin@test.com",
            "password": "admin123",
        })
        assert res.status_code == 200
        data = res.json()["data"]
        assert "access_token" in data
        assert data["role"] == "admin"

    async def test_login_wrong_password(self, client):
        res = await client.post("/api/v1/auth/login", json={
            "email": "admin@test.com",
            "password": "wrongpassword",
        })
        assert res.status_code == 401

    async def test_login_nonexistent_user(self, client):
        res = await client.post("/api/v1/auth/login", json={
            "email": "nobody@test.com",
            "password": "Password123!",
        })
        assert res.status_code == 401


class TestRefresh:
    async def test_refresh_token(self, client, admin_user):
        login_res = await client.post("/api/v1/auth/login", json={
            "email": "admin@test.com",
            "password": "admin123",
        })
        refresh_token = login_res.json()["data"]["refresh_token"]

        res = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert res.status_code == 200
        assert "access_token" in res.json()["data"]

    async def test_invalid_refresh_token(self, client):
        res = await client.post("/api/v1/auth/refresh", json={"refresh_token": "invalid"})
        assert res.status_code == 401


class TestLogout:
    async def test_logout_requires_auth(self, client):
        res = await client.post("/api/v1/auth/logout")
        assert res.status_code == 403

    async def test_logout_success(self, auth_client):
        res = await auth_client.post("/api/v1/auth/logout")
        assert res.status_code == 200
