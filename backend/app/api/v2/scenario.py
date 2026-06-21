import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.scenario import ScenarioRun
from app.schemas.common import StandardResponse
from app.services.scenario_engine import run_scenario, get_scenario_templates
from pydantic import BaseModel

router = APIRouter(prefix="/scenario", tags=["Scenario v2"])


class ScenarioRunRequest(BaseModel):
    entity_id: uuid.UUID
    scenario: str


@router.get("/templates")
async def api_list_templates(
    current_user: User = Depends(get_current_user),
):
    templates = get_scenario_templates()
    return StandardResponse(data={"templates": templates, "total": len(templates)})


@router.post("/run")
async def api_run_scenario(
    body: ScenarioRunRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    run = await run_scenario(db, body.entity_id, body.scenario, commit=True)
    return StandardResponse(data={
        "id": str(run.id),
        "scenario_type": run.scenario_type,
        "risk_delta": float(run.risk_delta) if run.risk_delta else None,
        "results": run.results,
        "created_at": run.created_at.isoformat(),
    })


@router.get("/results")
async def api_list_runs(
    entity_id: uuid.UUID | None = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(ScenarioRun).order_by(desc(ScenarioRun.created_at)).limit(limit)
    if entity_id:
        q = q.where(ScenarioRun.entity_id == entity_id)
    result = await db.execute(q)
    runs = result.scalars().all()
    return StandardResponse(data={
        "total": len(runs),
        "runs": [
            {
                "id": str(r.id),
                "entity_id": str(r.entity_id),
                "scenario_type": r.scenario_type,
                "risk_delta": float(r.risk_delta) if r.risk_delta else None,
                "results": r.results,
                "created_at": r.created_at.isoformat(),
            }
            for r in runs
        ],
    })
