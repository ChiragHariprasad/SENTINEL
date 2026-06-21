import uuid
from datetime import datetime

from pydantic import BaseModel


class AnomalyEventResponse(BaseModel):
    event_id: uuid.UUID
    vendor_id: uuid.UUID
    anomaly_type: str
    severity: str
    confidence_score: float | None
    explanation: str | None
    detected_at: datetime

    class Config:
        from_attributes = True


class AnomalyListResponse(BaseModel):
    count: int
    items: list[AnomalyEventResponse]


class AnomalyLabelResponse(BaseModel):
    label_name: str
    description: str | None
    default_severity: str | None

    class Config:
        from_attributes = True
