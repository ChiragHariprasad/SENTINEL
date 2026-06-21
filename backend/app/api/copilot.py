from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.copilot import CopilotQueryRequest, CopilotQueryResponse
from app.schemas.common import StandardResponse
from app.services.copilot_service import answer_question

router = APIRouter(prefix="/copilot", tags=["Copilot"])


@router.post("/query")
async def copilot_query(request: CopilotQueryRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await answer_question(db, request.question)
    return StandardResponse(data={"answer": result["answer"], "sources": result.get("sources", [])})
