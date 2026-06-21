import uuid
from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel


class CertStatusEnum(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    PENDING = "pending"


class CertificationCreate(BaseModel):
    vendor_id: uuid.UUID
    certification_type: str
    issuer: str | None = None
    issue_date: date | None = None
    expiry_date: date
    status: CertStatusEnum = CertStatusEnum.ACTIVE


class CertificationResponse(BaseModel):
    certification_id: uuid.UUID
    vendor_id: uuid.UUID
    certification_type: str
    issuer: str | None
    issue_date: date | None
    expiry_date: date
    status: str

    class Config:
        from_attributes = True


class ComplianceFrameworkResponse(BaseModel):
    framework_id: uuid.UUID
    framework_name: str
    description: str | None

    class Config:
        from_attributes = True
