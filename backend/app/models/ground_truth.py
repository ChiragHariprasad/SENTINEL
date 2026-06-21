import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class GroundTruthLabel(Base):
    __tablename__ = "ground_truth_labels"

    gt_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("vendors.vendor_id"), nullable=False)
    anomaly_type: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str | None] = mapped_column(String(20))
    source: Mapped[str | None] = mapped_column(String(100), default="vendor_labels.csv")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
