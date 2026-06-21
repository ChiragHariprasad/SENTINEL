from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: str
    password: str


class SignupRequest(BaseModel):
    email: str
    password: str
    first_name: str | None = None
    last_name: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    role: str


class RefreshRequest(BaseModel):
    refresh_token: str
