import uuid
from datetime import datetime

from pydantic import BaseModel


class EntityCreate(BaseModel):
    entity_type: str
    entity_name: str
    external_id: str | None = None
    status: str = "active"
    attributes: dict | None = None


class EntityUpdate(BaseModel):
    entity_name: str | None = None
    external_id: str | None = None
    risk_score: float | None = None
    status: str | None = None
    attributes: dict | None = None


class EntityResponse(BaseModel):
    entity_id: uuid.UUID
    entity_type: str
    entity_name: str
    external_id: str | None
    risk_score: float | None
    status: str
    attributes: dict | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EntityListResponse(BaseModel):
    entities: list[EntityResponse]
    total: int
    page: int
    size: int
