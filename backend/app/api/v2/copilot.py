from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.common import StandardResponse
from app.services.copilot_engine import copilot_query
from pydantic import BaseModel


router = APIRouter(prefix="/copilot", tags=["Copilot v2"])


class CopilotQuery(BaseModel):
    question: str


@router.post("/query")
async def api_copilot_query(
    body: CopilotQuery,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await copilot_query(db, body.question)
    return StandardResponse(data=result)
