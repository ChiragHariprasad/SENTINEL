import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.common import StandardResponse
from app.services.timeline_engine import get_entity_timeline, get_portfolio_timeline

router = APIRouter(prefix="/timeline", tags=["Timeline v2"])


@router.get("/entity/{entity_id}")
async def api_entity_timeline(
    entity_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    timeline = await get_entity_timeline(db, entity_id, limit=limit)
    return StandardResponse(data={"events": timeline, "total": len(timeline)})


@router.get("/portfolio")
async def api_portfolio_timeline(
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    timeline = await get_portfolio_timeline(db, limit=limit)
    return StandardResponse(data={"events": timeline, "total": len(timeline)})
