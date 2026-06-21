import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserResponse(BaseModel):
    user_id: uuid.UUID
    email: str
    first_name: str | None
    last_name: str | None
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)
    first_name: str | None = None
    last_name: str | None = None
    role: str = Field(min_length=1)


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    role: str | None = None
    is_active: bool | None = None


class RoleResponse(BaseModel):
    role_id: uuid.UUID
    role_name: str
    description: str | None

    class Config:
        from_attributes = True
