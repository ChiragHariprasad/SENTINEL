import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.common import StandardResponse
from app.services.graph_service import get_entity
from app.services.risk_correlation_engine import correlate_entity_risk, get_latest_correlated_risk
from pydantic import BaseModel

router = APIRouter(prefix="/correlation", tags=["Correlation v2"])


class CorrelationRequest(BaseModel):
    entity_id: uuid.UUID


@router.post("/run")
async def api_run_correlation(
    body: CorrelationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entity = await get_entity(db, body.entity_id)
    corr = await correlate_entity_risk(db, entity, commit=True)
    return StandardResponse(data={
        "entity_id": str(corr.entity_id),
        "base_risk": float(corr.base_risk),
        "neighbor_risk": float(corr.neighbor_risk),
        "correlated_risk": float(corr.correlated_risk),
        "reasoning": corr.reasoning,
        "created_at": corr.created_at.isoformat(),
    })


@router.get("/{entity_id}")
async def api_get_correlated_risk(
    entity_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    corr = await get_latest_correlated_risk(db, entity_id)
    if not corr:
        return StandardResponse(data=None)
    return StandardResponse(data={
        "entity_id": str(corr.entity_id),
        "base_risk": float(corr.base_risk),
        "neighbor_risk": float(corr.neighbor_risk),
        "correlated_risk": float(corr.correlated_risk),
        "reasoning": corr.reasoning,
        "created_at": corr.created_at.isoformat(),
    })
