import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.risk_entity import RiskEntity
from app.models.risk_v2 import RiskScoreV2, RiskHistoryV2
from app.schemas.common import StandardResponse
from app.core.exceptions import NotFoundError
from app.services.risk_engine_v2 import calculate_entity_risk
from app.services.graph_service import get_entity
from pydantic import BaseModel

router = APIRouter(prefix="/risk", tags=["Risk v2"])


class RiskCalculateRequest(BaseModel):
    entity_id: uuid.UUID


@router.post("/calculate")
async def api_calculate_risk(
    body: RiskCalculateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entity = await get_entity(db, body.entity_id)
    risk_score = await calculate_entity_risk(db, entity, commit=True)
    return StandardResponse(data={
        "entity_id": str(risk_score.entity_id),
        "overall_score": float(risk_score.overall_score),
        "risk_tier": risk_score.risk_tier,
        "security_score": float(risk_score.security_score) if risk_score.security_score else None,
        "compliance_score": float(risk_score.compliance_score) if risk_score.compliance_score else None,
        "operational_score": float(risk_score.operational_score) if risk_score.operational_score else None,
        "financial_score": float(risk_score.financial_score) if risk_score.financial_score else None,
        "access_score": float(risk_score.access_score) if risk_score.access_score else None,
        "generated_at": risk_score.generated_at.isoformat(),
    })


@router.get("/{entity_id}")
async def api_get_risk(
    entity_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(RiskScoreV2)
        .where(RiskScoreV2.entity_id == entity_id)
        .order_by(desc(RiskScoreV2.generated_at))
        .limit(1)
    )
    risk = result.scalar_one_or_none()
    if not risk:
        return StandardResponse(data=None)
    return StandardResponse(data={
        "entity_id": str(risk.entity_id),
        "overall_score": float(risk.overall_score),
        "risk_tier": risk.risk_tier,
        "security_score": float(risk.security_score) if risk.security_score else None,
        "compliance_score": float(risk.compliance_score) if risk.compliance_score else None,
        "operational_score": float(risk.operational_score) if risk.operational_score else None,
        "financial_score": float(risk.financial_score) if risk.financial_score else None,
        "access_score": float(risk.access_score) if risk.access_score else None,
        "generated_at": risk.generated_at.isoformat(),
    })


@router.get("/{entity_id}/history")
async def api_get_risk_history(
    entity_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(RiskHistoryV2)
        .where(RiskHistoryV2.entity_id == entity_id)
        .order_by(desc(RiskHistoryV2.created_at))
        .limit(50)
    )
    history = result.scalars().all()
    return StandardResponse(data={
        "history": [
            {
                "overall_score": float(h.overall_score) if h.overall_score else None,
                "risk_tier": h.risk_tier,
                "change_reason": h.change_reason,
                "created_at": h.created_at.isoformat(),
            }
            for h in history
        ]
    })


@router.post("/recalculate")
async def api_recalculate_all(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(RiskEntity).where(RiskEntity.status == "active"))
    entities = result.scalars().all()

    for entity in entities:
        await calculate_entity_risk(db, entity, commit=False)
    await db.commit()

    return StandardResponse(message=f"Risk recalculated for {len(entities)} entities")
