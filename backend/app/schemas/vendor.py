import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class CriticalityEnum(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class VendorCreate(BaseModel):
    vendor_name: str = Field(min_length=1)
    vendor_type: str | None = None
    vendor_owner: str | None = None
    annual_spend: float | None = Field(default=None, ge=0)
    criticality: CriticalityEnum | None = None
    contract_status: str | None = None


class VendorUpdate(BaseModel):
    vendor_name: str | None = None
    vendor_type: str | None = None
    vendor_owner: str | None = None
    annual_spend: float | None = None
    criticality: str | None = None
    contract_status: str | None = None
    risk_tier: str | None = None


class VendorResponse(BaseModel):
    vendor_id: uuid.UUID
    vendor_name: str
    vendor_type: str | None
    vendor_owner: str | None
    annual_spend: float | None
    criticality: str | None
    contract_status: str | None
    risk_tier: str | None
    is_archived: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VendorListResponse(BaseModel):
    total: int
    items: list[VendorResponse]


class VendorDataAccessCreate(BaseModel):
    vendor_id: uuid.UUID
    data_type: str
    access_level: str | None = None
    system_name: str | None = None
    is_active: bool = True


class VendorDataAccessResponse(BaseModel):
    access_id: uuid.UUID
    vendor_id: uuid.UUID
    data_type: str | None
    access_level: str | None
    system_name: str | None
    is_active: bool

    class Config:
        from_attributes = True
