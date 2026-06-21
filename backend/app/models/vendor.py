import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Numeric, Boolean, DateTime, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Vendor(Base):
    __tablename__ = "vendors"

    vendor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    vendor_type: Mapped[str | None] = mapped_column(String(100))
    vendor_owner: Mapped[str | None] = mapped_column(String(255))
    annual_spend: Mapped[float | None] = mapped_column(Numeric(12, 2))
    criticality: Mapped[str | None] = mapped_column(String(50))
    contract_status: Mapped[str | None] = mapped_column(String(50))
    risk_tier: Mapped[str | None] = mapped_column(String(20))
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    risk_scores = relationship("RiskScore", back_populates="vendor", lazy="selectin")
    anomaly_events = relationship("AnomalyEvent", back_populates="vendor", lazy="selectin")


vendor_category_mapping = Table(
    "vendor_category_mapping",
    Base.metadata,
    Column("vendor_id", UUID(as_uuid=True), ForeignKey("vendors.vendor_id"), primary_key=True),
    Column("category_id", UUID(as_uuid=True), ForeignKey("vendor_categories.category_id"), primary_key=True),
)


class VendorCategory(Base):
    __tablename__ = "vendor_categories"

    category_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))


class VendorCategoryMapping(Base):
    __tablename__ = "vendor_category_mapping"
    __table_args__ = {"extend_existing": True}


class VendorContact(Base):
    __tablename__ = "vendor_contacts"

    contact_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("vendors.vendor_id"))
    name: Mapped[str | None] = mapped_column(String(255))
    designation: Mapped[str | None] = mapped_column(String(100))
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))


class VendorDataAccess(Base):
    __tablename__ = "vendor_data_access"

    access_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("vendors.vendor_id"))
    data_type: Mapped[str | None] = mapped_column(String(50))
    access_level: Mapped[str | None] = mapped_column(String(50))
    system_name: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
