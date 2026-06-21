import uuid
from datetime import date, datetime, timezone

from sqlalchemy import String, Numeric, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class ComplianceFramework(Base):
    __tablename__ = "compliance_frameworks"

    framework_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    framework_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)


class Certification(Base):
    __tablename__ = "certifications"

    certification_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("vendors.vendor_id"), nullable=False)
    certification_type: Mapped[str] = mapped_column(String(100), nullable=False)
    issuer: Mapped[str | None] = mapped_column(String(255))
    issue_date: Mapped[date | None] = mapped_column(Date)
    expiry_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active")


class VendorCompliance(Base):
    __tablename__ = "vendor_compliance"

    vendor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("vendors.vendor_id"), primary_key=True)
    framework_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("compliance_frameworks.framework_id"), primary_key=True)
    compliance_status: Mapped[str | None] = mapped_column(String(50))
    score: Mapped[float | None] = mapped_column(Numeric(5, 2))
