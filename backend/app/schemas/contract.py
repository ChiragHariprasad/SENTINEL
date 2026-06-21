import uuid
from datetime import date, datetime

from pydantic import BaseModel


class ContractUploadResponse(BaseModel):
    contract_id: uuid.UUID
    status: str


class ContractAnalysisResponse(BaseModel):
    contract_id: uuid.UUID
    contract_name: str | None
    vendor_id: uuid.UUID
    status: str | None
    ai_analysis: dict | None
    created_at: datetime

    class Config:
        from_attributes = True
