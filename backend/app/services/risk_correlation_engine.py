import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.risk_entity import RiskEntity
from app.models.risk_relationship import RiskRelationship, RELATIONSHIP_TYPES
from app.models.risk_v2 import RiskScoreV2, CorrelatedRisk


async def correlate_entity_risk(
    db: AsyncSession,
    entity: RiskEntity,
    commit: bool = True,
    max_depth: int = 2,
) -> CorrelatedRisk:
    latest_score = await db.execute(
        select(RiskScoreV2)
        .where(RiskScoreV2.entity_id == entity.entity_id)
        .order_by(RiskScoreV2.generated_at.desc())
        .limit(1)
    )
    latest = latest_score.scalar_one_or_none()
    base_risk = float(latest.overall_score) if latest else (entity.risk_score or 0)

    neighbor_risk = 0.0
    reasoning_parts = []
    visited = {entity.entity_id}
    queue = [(entity.entity_id, 1.0, 0)]

    while queue:
        current_id, decay, depth = queue.pop(0)
        if depth >= max_depth:
            continue

        relationships = await db.execute(
            select(RiskRelationship).where(
                RiskRelationship.source_entity_id == current_id,
            )
        )
        for rel in relationships.scalars().all():
            target_id = rel.target_entity_id
            if target_id in visited:
                continue
            visited.add(target_id)

            target_entity = await db.execute(select(RiskEntity).where(RiskEntity.entity_id == target_id))
            te = target_entity.scalar_one_or_none()
            if not te or te.risk_score is None:
                continue

            effective_weight = rel.weight * decay
            contributed = float(te.risk_score) * effective_weight / 100.0
            neighbor_risk = round(neighbor_risk + contributed, 2)

            reasoning_parts.append({
                "entity_id": str(te.entity_id),
                "entity_name": te.entity_name,
                "entity_type": te.entity_type,
                "risk_score": te.risk_score,
                "relationship": rel.relationship_type,
                "weight": rel.weight,
                "contributed_score": round(contributed, 2),
            })

            inbound = await db.execute(
                select(RiskRelationship).where(
                    RiskRelationship.target_entity_id == target_id,
                    RiskRelationship.source_entity_id != current_id,
                )
            )
            for in_rel in inbound.scalars().all():
                if in_rel.source_entity_id not in visited:
                    queue.append((in_rel.source_entity_id, decay * in_rel.weight * 0.5, depth + 1))

    correlated_risk = round(min(base_risk + neighbor_risk, 100), 2)

    corr = CorrelatedRisk(
        entity_id=entity.entity_id,
        base_risk=base_risk,
        neighbor_risk=neighbor_risk,
        correlated_risk=correlated_risk,
        reasoning={
            "base_risk": base_risk,
            "neighbor_risk": neighbor_risk,
            "correlated_risk": correlated_risk,
            "contributions": reasoning_parts,
        },
        created_at=datetime.now(timezone.utc),
    )
    db.add(corr)
    await db.flush()

    if commit:
        await db.commit()

    return corr


async def get_latest_correlated_risk(db: AsyncSession, entity_id: uuid.UUID) -> CorrelatedRisk | None:
    result = await db.execute(
        select(CorrelatedRisk)
        .where(CorrelatedRisk.entity_id == entity_id)
        .order_by(CorrelatedRisk.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()
