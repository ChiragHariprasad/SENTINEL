import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Integer, Numeric, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    result_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    anomaly_type: Mapped[str | None] = mapped_column(String(100))
    severity: Mapped[str | None] = mapped_column(String(20))
    true_positives: Mapped[int] = mapped_column(Integer, default=0)
    false_positives: Mapped[int] = mapped_column(Integer, default=0)
    false_negatives: Mapped[int] = mapped_column(Integer, default=0)
    precision: Mapped[float | None] = mapped_column(Numeric(5, 4))
    recall: Mapped[float | None] = mapped_column(Numeric(5, 4))
    f1_score: Mapped[float | None] = mapped_column(Numeric(5, 4))
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
