import uuid
from datetime import datetime

from pydantic import BaseModel


class RiskScoreResponse(BaseModel):
    risk_score_id: uuid.UUID
    vendor_id: uuid.UUID
    security_score: float | None
    data_access_score: float | None
    compliance_score: float | None
    financial_score: float | None
    contract_score: float | None
    overall_score: float
    risk_tier: str
    generated_at: datetime

    class Config:
        from_attributes = True


class RiskHistoryResponse(BaseModel):
    history_id: uuid.UUID
    vendor_id: uuid.UUID
    overall_score: float | None
    risk_tier: str | None
    change_reason: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class RiskCalculateRequest(BaseModel):
    vendor_id: uuid.UUID
