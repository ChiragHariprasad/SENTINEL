import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.models.risk_entity import RiskEntity
from app.models.risk_v2 import RiskScoreV2, RiskHistoryV2, AnomalyEventV2
from app.models.intelligence import RiskEvent, RemediationAction


async def record_risk_event(
    db: AsyncSession,
    entity_id: uuid.UUID,
    event_type: str,
    description: str | None = None,
    old_value: float | None = None,
    new_value: float | None = None,
    metadata: dict | None = None,
) -> RiskEvent:
    event = RiskEvent(
        entity_id=entity_id,
        event_type=event_type,
        description=description,
        old_value=old_value,
        new_value=new_value,
        metadata=metadata or {},
        created_at=datetime.now(timezone.utc),
    )
    db.add(event)
    await db.flush()
    return event


async def get_entity_timeline(
    db: AsyncSession,
    entity_id: uuid.UUID,
    limit: int = 50,
) -> list[dict]:
    events = await db.execute(
        select(RiskEvent)
        .where(RiskEvent.entity_id == entity_id)
        .order_by(desc(RiskEvent.created_at))
        .limit(limit)
    )
    risk_events_list = events.scalars().all()

    anomalies = await db.execute(
        select(AnomalyEventV2)
        .where(AnomalyEventV2.entity_id == entity_id)
        .order_by(desc(AnomalyEventV2.detected_at))
        .limit(limit)
    )
    anomaly_list = anomalies.scalars().all()

    history = await db.execute(
        select(RiskHistoryV2)
        .where(RiskHistoryV2.entity_id == entity_id)
        .order_by(desc(RiskHistoryV2.created_at))
        .limit(limit)
    )
    history_list = history.scalars().all()

    actions = await db.execute(
        select(RemediationAction)
        .where(RemediationAction.entity_id == entity_id)
        .order_by(desc(RemediationAction.created_at))
        .limit(limit)
    )
    action_list = actions.scalars().all()

    timeline_entries = []

    for h in history_list:
        timeline_entries.append({
            "date": h.created_at.isoformat() if h.created_at else None,
            "event_type": "risk_change",
            "description": h.change_reason or "Risk score updated",
            "old_value": float(h.overall_score) if h.overall_score else None,
            "new_value": None,
            "metadata": {"risk_tier": h.risk_tier},
        })

    for a in anomaly_list:
        timeline_entries.append({
            "date": a.detected_at.isoformat() if a.detected_at else None,
            "event_type": "anomaly",
            "description": f"{a.anomaly_type}: {a.explanation}" if a.explanation else a.anomaly_type,
            "old_value": None,
            "new_value": None,
            "metadata": {"severity": a.severity, "anomaly_type": a.anomaly_type},
        })

    for ac in action_list:
        timeline_entries.append({
            "date": ac.created_at.isoformat() if ac.created_at else None,
            "event_type": "remediation",
            "description": ac.action,
            "old_value": None,
            "new_value": None,
            "metadata": {"priority": ac.priority, "status": ac.status, "owner": ac.owner},
        })

    for e in risk_events_list:
        timeline_entries.append({
            "date": e.created_at.isoformat() if e.created_at else None,
            "event_type": e.event_type,
            "description": e.description,
            "old_value": e.old_value,
            "new_value": e.new_value,
            "metadata": e.attributes,
        })

    timeline_entries.sort(key=lambda x: x.get("date") or "", reverse=True)
    return timeline_entries[:limit]


async def get_portfolio_timeline(
    db: AsyncSession,
    limit: int = 100,
) -> list[dict]:
    events = await db.execute(
        select(RiskEvent).order_by(desc(RiskEvent.created_at)).limit(limit)
    )
    all_events = events.scalars().all()

    timeline = []
    for e in all_events:
        entity = await db.execute(select(RiskEntity).where(RiskEntity.entity_id == e.entity_id))
        ent = entity.scalar_one_or_none()
        timeline.append({
            "date": e.created_at.isoformat() if e.created_at else None,
            "event_type": e.event_type,
            "entity_name": ent.entity_name if ent else None,
            "entity_type": ent.entity_type if ent else None,
            "description": e.description,
            "old_value": e.old_value,
            "new_value": e.new_value,
        })

    anomalies = await db.execute(
        select(AnomalyEventV2).order_by(desc(AnomalyEventV2.detected_at)).limit(limit)
    )
    for a in anomalies.scalars().all():
        entity = await db.execute(select(RiskEntity).where(RiskEntity.entity_id == a.entity_id))
        ent = entity.scalar_one_or_none()
        timeline.append({
            "date": a.detected_at.isoformat() if a.detected_at else None,
            "event_type": "anomaly",
            "entity_name": ent.entity_name if ent else None,
            "entity_type": ent.entity_type if ent else None,
            "description": f"{a.anomaly_type}: {a.explanation}" if a.explanation else a.anomaly_type,
            "old_value": None,
            "new_value": None,
        })

    timeline.sort(key=lambda x: x.get("date") or "", reverse=True)
    return timeline[:limit]
