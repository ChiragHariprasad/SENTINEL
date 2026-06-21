from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.intelligence import IntelligenceSnapshot
from app.schemas.common import StandardResponse
from app.services.intelligence_engine import generate_daily_intelligence, generate_priorities
from app.services.executive_brief_engine import generate_executive_brief

router = APIRouter(prefix="/intelligence", tags=["Intelligence v2"])


@router.post("/daily")
async def api_generate_daily_intelligence(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    snapshot = await generate_daily_intelligence(db)
    await db.commit()
    return StandardResponse(data={
        "id": str(snapshot.id),
        "title": snapshot.title,
        "summary": snapshot.summary,
        "content": snapshot.content,
        "generated_at": snapshot.generated_at.isoformat(),
    })


@router.post("/priorities")
async def api_generate_priorities(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    snapshot = await generate_priorities(db)
    await db.commit()
    return StandardResponse(data={
        "id": str(snapshot.id),
        "title": snapshot.title,
        "summary": snapshot.summary,
        "content": snapshot.content,
        "generated_at": snapshot.generated_at.isoformat(),
    })


@router.post("/executive")
async def api_generate_executive_brief(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    snapshot = await generate_executive_brief(db)
    await db.commit()
    return StandardResponse(data={
        "id": str(snapshot.id),
        "title": snapshot.title,
        "summary": snapshot.summary,
        "content": snapshot.content,
        "generated_at": snapshot.generated_at.isoformat(),
    })


@router.get("/snapshots")
async def api_list_snapshots(
    snapshot_type: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(IntelligenceSnapshot).order_by(desc(IntelligenceSnapshot.generated_at)).limit(50)
    if snapshot_type:
        q = q.where(IntelligenceSnapshot.snapshot_type == snapshot_type)
    result = await db.execute(q)
    snapshots = result.scalars().all()
    return StandardResponse(data={
        "snapshots": [
            {
                "id": str(s.id),
                "snapshot_type": s.snapshot_type,
                "title": s.title,
                "summary": s.summary,
                "priority": s.priority,
                "generated_at": s.generated_at.isoformat(),
            }
            for s in snapshots
        ]
    })
