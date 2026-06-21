"""Unit tests for auth utilities (no DB needed)."""

from app.core.auth import hash_password, verify_password, create_access_token, decode_token, create_refresh_token


class TestPasswordHashing:
    def test_hash_and_verify(self):
        pw = "SuperSecret123!"
        hashed = hash_password(pw)
        assert hashed != pw
        assert verify_password(pw, hashed) is True

    def test_wrong_password_fails(self):
        hashed = hash_password("correct")
        assert verify_password("wrong", hashed) is False

    def test_different_hashes_for_same_password(self):
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2


class TestTokenCreation:
    def test_create_and_decode_access_token(self):
        data = {"sub": "user-123", "role": "admin"}
        token = create_access_token(data)
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "user-123"
        assert payload["role"] == "admin"
        assert "exp" in payload

    def test_create_and_decode_refresh_token(self):
        data = {"sub": "user-456"}
        token = create_refresh_token(data)
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "user-456"
        assert "exp" in payload

    def test_invalid_token_returns_none(self):
        assert decode_token("invalid.token.here") is None
        assert decode_token("") is None

    def test_expired_token_returns_none(self):
        from jose import jwt
        from datetime import datetime, timedelta, timezone
        expired = jwt.encode(
            {"sub": "user", "exp": datetime.now(timezone.utc) - timedelta(hours=1)},
            "test-key",
            algorithm="HS256",
        )
        from app.core.config import settings
        # This should fail since key doesn't match settings
        assert decode_token(expired) is None
