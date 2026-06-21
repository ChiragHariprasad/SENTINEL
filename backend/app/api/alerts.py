import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.alert import SecurityAlert
from app.schemas.alert import AlertCreate, AlertResponse
from app.schemas.common import StandardResponse
from app.core.exceptions import NotFoundError

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("")
async def list_alerts(status: str | None = None, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = select(SecurityAlert).order_by(desc(SecurityAlert.created_at))
    if status:
        query = query.where(SecurityAlert.status == status)

    result = await db.execute(query)
    alerts = result.scalars().all()
    return StandardResponse(data={"items": [AlertResponse.model_validate(a).model_dump() for a in alerts]})


@router.post("")
async def create_alert(request: AlertCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    alert = SecurityAlert(**request.model_dump())
    db.add(alert)
    await db.flush()
    return StandardResponse(data=AlertResponse.model_validate(alert).model_dump())


@router.patch("/{alert_id}/resolve")
async def resolve_alert(alert_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(SecurityAlert).where(SecurityAlert.alert_id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise NotFoundError("Alert", str(alert_id))

    alert.status = "resolved"
    from datetime import datetime, timezone
    alert.resolved_at = datetime.now(timezone.utc)
    await db.flush()
    return StandardResponse(data={"status": "resolved"})
