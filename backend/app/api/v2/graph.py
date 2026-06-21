import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.risk_relationship import RelationshipCreate, RelationshipResponse
from app.schemas.graph import GraphResponse, ImpactPathResponse, ImpactPathNode
from app.schemas.common import StandardResponse
from app.services.graph_service import create_relationship, get_entity_graph, get_impact_path

router = APIRouter(prefix="/graph", tags=["Graph v2"])


@router.post("/relationships")
async def api_create_relationship(
    body: RelationshipCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rel = await create_relationship(
        db,
        source_entity_id=body.source_entity_id,
        target_entity_id=body.target_entity_id,
        relationship_type=body.relationship_type,
        weight=body.weight,
        attributes=body.attributes,
    )
    return StandardResponse(data=RelationshipResponse.model_validate(rel).model_dump())


@router.get("/entity/{entity_id}")
async def api_get_entity_graph(
    entity_id: uuid.UUID,
    depth: int = Query(1, ge=1, le=5),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    graph = await get_entity_graph(db, entity_id, depth=depth)
    return StandardResponse(data=GraphResponse(**graph).model_dump())


@router.get("/entity/{entity_id}/impact")
async def api_get_impact_path(
    entity_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    path = await get_impact_path(db, entity_id)
    return StandardResponse(data=ImpactPathResponse(
        path=[ImpactPathNode(**n) for n in path]
    ).model_dump())
