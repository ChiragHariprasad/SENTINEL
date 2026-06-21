import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.intelligence import RemediationAction
from app.models.risk_entity import RiskEntity
from app.schemas.common import StandardResponse
from app.services.graph_service import get_entity
from app.services.remediation_engine import generate_remediation, generate_remediation_for_anomalies
from pydantic import BaseModel

router = APIRouter(prefix="/remediation", tags=["Remediation v2"])


class GenerateRemediationRequest(BaseModel):
    entity_id: uuid.UUID
    anomaly_type: str


@router.post("/generate")
async def api_generate_remediation(
    body: GenerateRemediationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entity = await get_entity(db, body.entity_id)
    actions = await generate_remediation(db, entity, body.anomaly_type, commit=True)
    return StandardResponse(data={
        "actions_generated": len(actions),
        "actions": [
            {
                "id": str(a.id),
                "action": a.action,
                "priority": a.priority,
                "owner": a.owner,
                "status": a.status,
                "due_date": a.due_date,
            }
            for a in actions
        ],
    })


@router.post("/generate-from-anomalies")
async def api_generate_from_anomalies(
    entity_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    actions = await generate_remediation_for_anomalies(db, entity_id=entity_id, commit=True)
    return StandardResponse(data={
        "actions_generated": len(actions),
        "actions": [
            {
                "id": str(a.id),
                "entity_id": str(a.entity_id) if a.entity_id else None,
                "anomaly_type": a.anomaly_type,
                "action": a.action,
                "priority": a.priority,
                "owner": a.owner,
                "status": a.status,
            }
            for a in actions
        ],
    })


@router.get("/actions")
async def api_list_actions(
    status: str | None = Query(None),
    entity_id: uuid.UUID | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(RemediationAction).order_by(desc(RemediationAction.created_at)).limit(limit)
    if status:
        q = q.where(RemediationAction.status == status)
    if entity_id:
        q = q.where(RemediationAction.entity_id == entity_id)
    result = await db.execute(q)
    actions = result.scalars().all()
    return StandardResponse(data={
        "total": len(actions),
        "actions": [
            {
                "id": str(a.id),
                "entity_id": str(a.entity_id) if a.entity_id else None,
                "anomaly_type": a.anomaly_type,
                "priority": a.priority,
                "owner": a.owner,
                "action": a.action,
                "status": a.status,
                "due_date": a.due_date,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in actions
        ],
    })


@router.patch("/actions/{action_id}/complete")
async def api_complete_action(
    action_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(RemediationAction).where(RemediationAction.id == action_id))
    action = result.scalar_one_or_none()
    if not action:
        return StandardResponse(success=False, data=None, message="Action not found")

    from datetime import datetime, timezone
    action.status = "completed"
    action.resolved_at = datetime.now(timezone.utc)
    await db.commit()
    return StandardResponse(data={"id": str(action.id), "status": "completed"})
