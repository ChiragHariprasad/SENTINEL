import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.risk_entity import EntityCreate, EntityUpdate, EntityResponse, EntityListResponse
from app.schemas.common import StandardResponse
from app.services.graph_service import create_entity, get_entity, list_entities, update_entity, delete_entity

router = APIRouter(prefix="/entities", tags=["Entities v2"])


@router.post("")
async def api_create_entity(
    body: EntityCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entity = await create_entity(
        db,
        entity_type=body.entity_type,
        entity_name=body.entity_name,
        external_id=body.external_id,
        status=body.status,
        attributes=body.attributes,
    )
    return StandardResponse(data=EntityResponse.model_validate(entity).model_dump())


@router.get("")
async def api_list_entities(
    entity_type: str | None = Query(None),
    search: str | None = Query(None),
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entities, total = await list_entities(db, entity_type=entity_type, search=search, status=status, page=page, size=size)
    return StandardResponse(data=EntityListResponse(
        entities=[EntityResponse.model_validate(e).model_dump() for e in entities],
        total=total,
        page=page,
        size=size,
    ).model_dump())


@router.get("/{entity_id}")
async def api_get_entity(
    entity_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entity = await get_entity(db, entity_id)
    return StandardResponse(data=EntityResponse.model_validate(entity).model_dump())


@router.put("/{entity_id}")
async def api_update_entity(
    entity_id: uuid.UUID,
    body: EntityUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entity = await update_entity(
        db,
        entity_id=entity_id,
        entity_name=body.entity_name,
        external_id=body.external_id,
        risk_score=body.risk_score,
        status=body.status,
        attributes=body.attributes,
    )
    return StandardResponse(data=EntityResponse.model_validate(entity).model_dump())


@router.delete("/{entity_id}")
async def api_delete_entity(
    entity_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await delete_entity(db, entity_id)
    return StandardResponse(message="Entity archived")
