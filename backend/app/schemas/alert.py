import uuid
from datetime import datetime

from pydantic import BaseModel


class AlertCreate(BaseModel):
    vendor_id: uuid.UUID
    alert_type: str
    severity: str
    message: str | None = None


class AlertResponse(BaseModel):
    alert_id: uuid.UUID
    vendor_id: uuid.UUID
    alert_type: str
    severity: str
    message: str | None
    status: str
    created_at: datetime
    resolved_at: datetime | None

    class Config:
        from_attributes = True
