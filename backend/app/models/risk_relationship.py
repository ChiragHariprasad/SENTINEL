import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.core.database import Base

RELATIONSHIP_TYPES = {
    "HAS_ACCESS_TO": 1.0,
    "USES": 0.8,
    "OWNS": 0.8,
    "DEPENDS_ON": 0.7,
    "PROVIDES": 0.6,
    "AFFECTS": 0.8,
    "VIOLATES": 0.9,
    "SUPPORTS": 0.5,
    "MANAGES": 0.7,
    "LOCATED_IN": 0.4,
    "BELONGS_TO": 0.6,
    "PARENT_OF": 0.7,
}


class RiskRelationship(Base):
    __tablename__ = "risk_relationships"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("risk_entities.entity_id"), nullable=False, index=True
    )
    target_entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("risk_entities.entity_id"), nullable=False, index=True
    )
    relationship_type: Mapped[str] = mapped_column(String(100), nullable=False)
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    attributes: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
