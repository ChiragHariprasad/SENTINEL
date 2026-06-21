import uuid
from datetime import datetime

from pydantic import BaseModel


class RelationshipCreate(BaseModel):
    source_entity_id: uuid.UUID
    target_entity_id: uuid.UUID
    relationship_type: str
    weight: float | None = None
    attributes: dict | None = None


class RelationshipResponse(BaseModel):
    id: uuid.UUID
    source_entity_id: uuid.UUID
    target_entity_id: uuid.UUID
    relationship_type: str
    weight: float
    attributes: dict | None
    created_at: datetime

    class Config:
        from_attributes = True
