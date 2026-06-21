from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.models.risk_entity import RiskEntity
from app.models.risk_v2 import RiskScoreV2, CorrelatedRisk, AnomalyEventV2
from app.models.intelligence import IntelligenceSnapshot, RemediationAction, RiskEvent
from app.models.risk_relationship import RiskRelationship


async def generate_daily_intelligence(db: AsyncSession) -> IntelligenceSnapshot:
    entities = await db.execute(
        select(RiskEntity).where(RiskEntity.status == "active").order_by(desc(RiskEntity.risk_score)).limit(100)
    )
    all_entities = entities.scalars().all()

    scored = [e for e in all_entities if e.risk_score is not None]
    scored.sort(key=lambda e: e.risk_score or 0, reverse=True)

    critical = [e for e in scored if e.risk_score and e.risk_score > 80]
    high = [e for e in scored if e.risk_score and 61 <= e.risk_score <= 80]

    anomalies = await db.execute(
        select(AnomalyEventV2).order_by(desc(AnomalyEventV2.detected_at)).limit(50)
    )
    anomaly_list = anomalies.scalars().all()

    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    anomaly_list.sort(key=lambda a: severity_order.get(a.severity, 99))

    recent_window = datetime.now(timezone.utc) - timedelta(days=30)
    recent = [a for a in anomaly_list if a.detected_at and a.detected_at >= recent_window]

    entity_type_dist = {}
    for e in scored:
        entity_type_dist[e.entity_type] = entity_type_dist.get(e.entity_type, 0) + 1

    anomaly_type_dist = {}
    for a in recent:
        anomaly_type_dist[a.anomaly_type] = anomaly_type_dist.get(a.anomaly_type, 0) + 1

    avg_risk = round(sum(e.risk_score or 0 for e in scored) / max(len(scored), 1), 2)

    content = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_entities": len(all_entities),
            "scored_entities": len(scored),
            "average_risk": avg_risk,
            "critical_count": len(critical),
            "high_count": len(high),
            "recent_anomalies": len(recent),
        },
        "critical_entities": [
            {"entity_id": str(e.entity_id), "entity_name": e.entity_name, "entity_type": e.entity_type, "risk_score": e.risk_score}
            for e in critical[:10]
        ],
        "high_risk_entities": [
            {"entity_id": str(e.entity_id), "entity_name": e.entity_name, "entity_type": e.entity_type, "risk_score": e.risk_score}
            for e in high[:10]
        ],
        "entity_type_distribution": entity_type_dist,
        "anomaly_type_distribution": anomaly_type_dist,
        "critical_anomalies": [
            {"id": str(a.id), "anomaly_type": a.anomaly_type, "entity_id": str(a.entity_id), "severity": a.severity, "explanation": a.explanation}
            for a in anomaly_list if a.severity == "CRITICAL"
        ],
    }

    snapshot = IntelligenceSnapshot(
        snapshot_type="daily_intelligence",
        title=f"Daily Intelligence - {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        summary=f"{len(critical)} critical, {len(high)} high-risk entities. {len(recent)} recent anomalies.",
        content=content,
        priority="high" if len(critical) > 0 else "normal",
    )
    db.add(snapshot)
    await db.flush()
    return snapshot


async def generate_priorities(db: AsyncSession) -> IntelligenceSnapshot:
    anomalies = await db.execute(
        select(AnomalyEventV2).order_by(desc(AnomalyEventV2.detected_at)).limit(100)
    )
    anomaly_list = anomalies.scalars().all()

    open_actions = await db.execute(
        select(RemediationAction).where(RemediationAction.status == "open").order_by(desc(RemediationAction.created_at))
    )
    actions = open_actions.scalars().all()

    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}

    unresolved_critical = [a for a in anomaly_list if a.severity == "CRITICAL"]
    unresolved_high = [a for a in anomaly_list if a.severity == "HIGH"]

    priorities = []
    for a in (unresolved_critical + unresolved_high)[:10]:
        priority_entry = {
            "type": "anomaly",
            "anomaly_type": a.anomaly_type,
            "entity_id": str(a.entity_id),
            "severity": a.severity,
            "explanation": a.explanation,
            "detected_at": a.detected_at.isoformat() if a.detected_at else None,
        }
        entity = await db.execute(select(RiskEntity).where(RiskEntity.entity_id == a.entity_id))
        e = entity.scalar_one_or_none()
        if e:
            priority_entry["entity_name"] = e.entity_name
            priority_entry["entity_type"] = e.entity_type
        priorities.append(priority_entry)

    for act in actions[:10]:
        priorities.append({
            "type": "action",
            "action": act.action,
            "entity_id": str(act.entity_id) if act.entity_id else None,
            "priority": act.priority,
            "owner": act.owner,
            "due_date": act.due_date,
            "created_at": act.created_at.isoformat() if act.created_at else None,
        })

    priorities.sort(key=lambda p: severity_order.get(p.get("severity"), 99))

    content = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_priorities": len(priorities),
        "critical_anomalies_unresolved": len(unresolved_critical),
        "high_anomalies_unresolved": len(unresolved_high),
        "open_actions": len(actions),
        "priorities": priorities[:20],
    }

    snapshot = IntelligenceSnapshot(
        snapshot_type="priorities",
        title=f"Priority Actions - {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        summary=f"{len(unresolved_critical)} critical, {len(unresolved_high)} high anomalies. {len(actions)} open actions.",
        content=content,
        priority="high" if len(unresolved_critical) > 0 else "normal",
    )
    db.add(snapshot)
    await db.flush()
    return snapshot
