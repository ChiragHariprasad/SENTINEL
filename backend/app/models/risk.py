import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class RiskScore(Base):
    __tablename__ = "risk_scores"

    risk_score_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("vendors.vendor_id"), nullable=False)
    security_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    data_access_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    compliance_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    financial_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    contract_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    overall_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    risk_tier: Mapped[str] = mapped_column(String(20), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    vendor = relationship("Vendor", back_populates="risk_scores")


class RiskHistory(Base):
    __tablename__ = "risk_history"

    history_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("vendors.vendor_id"), nullable=False)
    overall_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    risk_tier: Mapped[str | None] = mapped_column(String(20))
    change_reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
