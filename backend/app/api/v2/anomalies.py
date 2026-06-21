import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.risk_v2 import AnomalyEventV2
from app.models.risk_entity import RiskEntity
from app.schemas.common import StandardResponse
from app.services.anomaly_engine_v2 import run_anomaly_detection
from app.services.graph_service import get_entity
from pydantic import BaseModel

router = APIRouter(prefix="/anomalies", tags=["Anomalies v2"])


class AnomalyRunRequest(BaseModel):
    entity_id: uuid.UUID | None = None


@router.post("/run")
async def api_run_anomaly_detection(
    body: AnomalyRunRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entity = None
    if body.entity_id:
        entity = await get_entity(db, body.entity_id)

    events = await run_anomaly_detection(db, entity=entity, commit=True)
    return StandardResponse(data={
        "events_detected": len(events),
        "events": [
            {
                "id": str(e.id),
                "entity_id": str(e.entity_id),
                "anomaly_type": e.anomaly_type,
                "domain": e.domain,
                "severity": e.severity,
                "confidence_score": float(e.confidence_score) if e.confidence_score else None,
                "explanation": e.explanation,
                "detected_at": e.detected_at.isoformat(),
            }
            for e in events
        ],
    })


@router.get("")
async def api_list_anomalies(
    entity_id: uuid.UUID | None = Query(None),
    domain: str | None = Query(None),
    severity: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(AnomalyEventV2)
    if entity_id:
        query = query.where(AnomalyEventV2.entity_id == entity_id)
    if domain:
        query = query.where(AnomalyEventV2.domain == domain)
    if severity:
        query = query.where(AnomalyEventV2.severity == severity)

    query = query.order_by(desc(AnomalyEventV2.detected_at)).limit(limit)
    result = await db.execute(query)
    events = result.scalars().all()

    return StandardResponse(data={
        "total": len(events),
        "events": [
            {
                "id": str(e.id),
                "entity_id": str(e.entity_id),
                "anomaly_type": e.anomaly_type,
                "domain": e.domain,
                "severity": e.severity,
                "confidence_score": float(e.confidence_score) if e.confidence_score else None,
                "explanation": e.explanation,
                "detected_at": e.detected_at.isoformat(),
            }
            for e in events
        ],
    })
