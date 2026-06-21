import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, func
from sqlalchemy.orm import selectinload

from app.models.risk_entity import RiskEntity
from app.models.risk_relationship import RiskRelationship
from app.core.exceptions import NotFoundError, DuplicateError


async def create_entity(
    db: AsyncSession,
    entity_type: str,
    entity_name: str,
    external_id: str | None = None,
    status: str = "active",
    attributes: dict | None = None,
) -> RiskEntity:
    entity = RiskEntity(
        entity_type=entity_type.upper(),
        entity_name=entity_name,
        external_id=external_id,
        status=status,
        attributes=attributes or {},
    )
    db.add(entity)
    await db.flush()
    return entity


async def get_entity(db: AsyncSession, entity_id: uuid.UUID) -> RiskEntity:
    result = await db.execute(select(RiskEntity).where(RiskEntity.entity_id == entity_id))
    entity = result.scalar_one_or_none()
    if not entity:
        raise NotFoundError("RiskEntity", str(entity_id))
    return entity


async def list_entities(
    db: AsyncSession,
    entity_type: str | None = None,
    search: str | None = None,
    status: str | None = None,
    page: int = 1,
    size: int = 50,
) -> tuple[list[RiskEntity], int]:
    query = select(RiskEntity)

    if entity_type:
        query = query.where(RiskEntity.entity_type == entity_type.upper())
    if status:
        query = query.where(RiskEntity.status == status)
    if search:
        query = query.where(RiskEntity.entity_name.ilike(f"%{search}%"))

    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    query = query.order_by(RiskEntity.entity_name).offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    entities = result.scalars().all()

    return list(entities), total


async def update_entity(
    db: AsyncSession,
    entity_id: uuid.UUID,
    entity_name: str | None = None,
    external_id: str | None = None,
    risk_score: float | None = None,
    status: str | None = None,
    attributes: dict | None = None,
) -> RiskEntity:
    entity = await get_entity(db, entity_id)

    if entity_name is not None:
        entity.entity_name = entity_name
    if external_id is not None:
        entity.external_id = external_id
    if risk_score is not None:
        entity.risk_score = risk_score
    if status is not None:
        entity.status = status
    if attributes is not None:
        entity.attributes = attributes

    await db.flush()
    return entity


async def delete_entity(db: AsyncSession, entity_id: uuid.UUID) -> None:
    entity = await get_entity(db, entity_id)
    entity.status = "archived"
    await db.flush()


async def create_relationship(
    db: AsyncSession,
    source_entity_id: uuid.UUID,
    target_entity_id: uuid.UUID,
    relationship_type: str,
    weight: float | None = None,
    attributes: dict | None = None,
) -> RiskRelationship:
    await get_entity(db, source_entity_id)
    await get_entity(db, target_entity_id)

    existing = await db.execute(
        select(RiskRelationship).where(
            RiskRelationship.source_entity_id == source_entity_id,
            RiskRelationship.target_entity_id == target_entity_id,
            RiskRelationship.relationship_type == relationship_type.upper(),
        )
    )
    if existing.scalar_one_or_none():
        raise DuplicateError(
            f"Relationship {relationship_type} already exists between {source_entity_id} and {target_entity_id}"
        )

    rel = RiskRelationship(
        source_entity_id=source_entity_id,
        target_entity_id=target_entity_id,
        relationship_type=relationship_type.upper(),
        weight=weight or 1.0,
        attributes=attributes or {},
    )
    db.add(rel)
    await db.flush()
    return rel


async def get_entity_graph(db: AsyncSession, entity_id: uuid.UUID, depth: int = 1) -> dict:
    entity = await get_entity(db, entity_id)

    node_ids = {str(entity_id)}
    seen_edges = set()
    edges = []
    nodes = {str(entity_id): {"id": str(entity_id), "label": entity.entity_name, "type": entity.entity_type, "risk_score": entity.risk_score, "status": entity.status}}

    current_ids = {entity_id}
    for _ in range(depth):
        outbound = await db.execute(
            select(RiskRelationship).where(RiskRelationship.source_entity_id.in_(current_ids))
        )
        inbound = await db.execute(
            select(RiskRelationship).where(RiskRelationship.target_entity_id.in_(current_ids))
        )

        current_ids = set()

        for rel in list(outbound.scalars().all()) + list(inbound.scalars().all()):
            src = str(rel.source_entity_id)
            tgt = str(rel.target_entity_id)
            edge_key = f"{src}|{rel.relationship_type}|{tgt}"
            if edge_key not in seen_edges:
                seen_edges.add(edge_key)
                edges.append({"source": src, "target": tgt, "relationship": rel.relationship_type, "weight": rel.weight})

            for nid, eid_field in [(tgt, rel.target_entity_id), (src, rel.source_entity_id)]:
                if nid not in node_ids:
                    node_ids.add(nid)
                    current_ids.add(eid_field)
                    n_result = await db.execute(select(RiskEntity).where(RiskEntity.entity_id == eid_field))
                    ne = n_result.scalar_one_or_none()
                    if ne:
                        nodes[nid] = {"id": nid, "label": ne.entity_name, "type": ne.entity_type, "risk_score": ne.risk_score, "status": ne.status}

    return {"nodes": list(nodes.values()), "edges": edges}


async def get_impact_path(db: AsyncSession, entity_id: uuid.UUID) -> list[dict]:
    entity = await get_entity(db, entity_id)
    path = [
        {"entity_id": str(entity.entity_id), "entity_name": entity.entity_name, "entity_type": entity.entity_type, "risk_score": entity.risk_score, "relationship_type": None, "relationship_weight": None}
    ]

    visited = {entity_id}
    queue = [(entity_id, None, None)]

    while queue:
        current_id, rel_type, rel_weight = queue.pop(0)

        outbound = await db.execute(
            select(RiskRelationship).where(RiskRelationship.source_entity_id == current_id)
        )
        for rel in outbound.scalars().all():
            if rel.target_entity_id not in visited:
                visited.add(rel.target_entity_id)
                target = await db.execute(select(RiskEntity).where(RiskEntity.entity_id == rel.target_entity_id))
                te = target.scalar_one_or_none()
                if te:
                    path.append({
                        "entity_id": str(te.entity_id),
                        "entity_name": te.entity_name,
                        "entity_type": te.entity_type,
                        "risk_score": te.risk_score,
                        "relationship_type": rel.relationship_type,
                        "relationship_weight": rel.weight,
                    })
                    queue.append((rel.target_entity_id, rel.relationship_type, rel.weight))

    return path
