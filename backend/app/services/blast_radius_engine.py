import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.risk_entity import RiskEntity
from app.models.risk_relationship import RiskRelationship


async def calculate_blast_radius(
    db: AsyncSession,
    entity_id: uuid.UUID,
    max_depth: int = 5,
) -> dict:
    entity = await db.execute(select(RiskEntity).where(RiskEntity.entity_id == entity_id))
    entity = entity.scalar_one_or_none()
    if not entity:
        return {"systems": 0, "controls": 0, "users": 0, "vendors": 0, "total": 0, "paths": []}

    visited = {entity_id}
    impacted = {"SYSTEM": set(), "CONTROL": set(), "USER": set(), "VENDOR": set(), "other": set()}
    paths = []
    queue = [(entity_id, [str(entity_id)])]

    for _ in range(max_depth):
        if not queue:
            break
        next_queue = []

        for current_id, current_path in queue:
            rels = await db.execute(
                select(RiskRelationship).where(RiskRelationship.source_entity_id == current_id)
            )
            for rel in rels.scalars().all():
                if rel.target_entity_id in visited:
                    continue
                visited.add(rel.target_entity_id)

                target = await db.execute(select(RiskEntity).where(RiskEntity.entity_id == rel.target_entity_id))
                te = target.scalar_one_or_none()
                if not te:
                    continue

                etype = te.entity_type
                if etype in impacted:
                    impacted[etype].add(str(te.entity_id))
                else:
                    impacted["other"].add(str(te.entity_id))

                new_path = current_path + [str(te.entity_id)]
                paths.append({
                    "entity_id": str(te.entity_id),
                    "entity_name": te.entity_name,
                    "entity_type": etype,
                    "relationship": rel.relationship_type,
                    "path": new_path,
                })
                next_queue.append((rel.target_entity_id, new_path))

        queue = next_queue

    return {
        "source_entity_id": str(entity_id),
        "source_entity_name": entity.entity_name,
        "source_entity_type": entity.entity_type,
        "systems": len(impacted["SYSTEM"]),
        "controls": len(impacted["CONTROL"]),
        "users": len(impacted["USER"]),
        "vendors": len(impacted["VENDOR"]),
        "total": sum(len(v) for v in impacted.values()),
        "impacted_entities": {
            "systems": list(impacted["SYSTEM"]),
            "controls": list(impacted["CONTROL"]),
            "users": list(impacted["USER"]),
            "vendors": list(impacted["VENDOR"]),
        },
        "paths": paths,
    }
