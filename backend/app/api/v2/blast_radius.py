import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.common import StandardResponse
from app.services.blast_radius_engine import calculate_blast_radius

router = APIRouter(prefix="/blast-radius", tags=["Blast Radius v2"])


@router.get("/{entity_id}")
async def api_get_blast_radius(
    entity_id: uuid.UUID,
    max_depth: int = Query(5, ge=1, le=10),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await calculate_blast_radius(db, entity_id, max_depth=max_depth)
    return StandardResponse(data=result)
