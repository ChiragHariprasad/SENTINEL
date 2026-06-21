import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.anomaly import AnomalyEvent, AnomalyLabel
from app.schemas.anomaly import AnomalyEventResponse, AnomalyListResponse, AnomalyLabelResponse
from app.schemas.common import StandardResponse

router = APIRouter(prefix="/anomalies", tags=["Anomalies"])


@router.get("")
async def list_anomalies(
    severity: str | None = None,
    anomaly_type: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(AnomalyEvent).order_by(desc(AnomalyEvent.detected_at))
    if severity:
        query = query.where(AnomalyEvent.severity == severity.upper())
    if anomaly_type:
        query = query.where(AnomalyEvent.anomaly_type == anomaly_type)

    result = await db.execute(query)
    items = result.scalars().all()

    return StandardResponse(data={
        "count": len(items),
        "items": [AnomalyEventResponse.model_validate(a).model_dump() for a in items],
    })


@router.get("/vendor/{vendor_id}")
async def get_vendor_anomalies(vendor_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(AnomalyEvent).where(AnomalyEvent.vendor_id == vendor_id).order_by(desc(AnomalyEvent.detected_at))
    )
    items = result.scalars().all()
    return StandardResponse(data={
        "vendor_id": str(vendor_id),
        "anomalies": [AnomalyEventResponse.model_validate(a).model_dump() for a in items],
    })


@router.get("/labels")
async def list_labels(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AnomalyLabel))
    labels = result.scalars().all()
    return StandardResponse(data={"items": [AnomalyLabelResponse.model_validate(l).model_dump() for l in labels]})
