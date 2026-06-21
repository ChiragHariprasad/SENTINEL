import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Float, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.core.database import Base

ENTITY_TYPES = {
    "VENDOR", "USER", "SYSTEM", "CONTROL",
    "EVIDENCE", "EXCEPTION", "CONFIG", "DOCUMENT",
}


class RiskEntity(Base):
    __tablename__ = "risk_entities"

    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entity_name: Mapped[str] = mapped_column(String(255), nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(255))
    risk_score: Mapped[float | None] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(50), default="active")
    attributes: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
