import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.common import StandardResponse
from app.services.pipeline_orchestrator import run_full_pipeline
from pydantic import BaseModel

router = APIRouter(prefix="/pipeline", tags=["Pipeline v2"])


class PipelineRequest(BaseModel):
    entity_id: str | None = None


@router.post("/run")
async def api_run_pipeline(
    body: PipelineRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await run_full_pipeline(entity_id=body.entity_id)
    return StandardResponse(data=result)
