from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.models.risk_entity import RiskEntity
from app.models.risk_v2 import RiskScoreV2, AnomalyEventV2, CorrelatedRisk
from app.models.intelligence import IntelligenceSnapshot, RemediationAction
from app.models.risk_relationship import RiskRelationship


async def generate_executive_brief(db: AsyncSession) -> IntelligenceSnapshot:
    entities = await db.execute(
        select(RiskEntity).where(RiskEntity.status == "active").order_by(desc(RiskEntity.risk_score)).limit(200)
    )
    all_entities = entities.scalars().all()
    scored = [e for e in all_entities if e.risk_score is not None]

    total_risk = round(sum(e.risk_score or 0 for e in scored) / max(len(scored), 1), 2)
    critical = [e for e in scored if e.risk_score and e.risk_score > 80]
    high = [e for e in scored if e.risk_score and 61 <= e.risk_score <= 80]

    anomalies = await db.execute(
        select(AnomalyEventV2).order_by(desc(AnomalyEventV2.detected_at)).limit(100)
    )
    anomaly_list = anomalies.scalars().all()
    critical_anomalies = [a for a in anomaly_list if a.severity == "CRITICAL"]
    high_anomalies = [a for a in anomaly_list if a.severity == "HIGH"]

    open_actions = await db.execute(
        select(RemediationAction).where(RemediationAction.status == "open")
    )
    actions = open_actions.scalars().all()

    entity_type_count = {}
    for e in scored:
        entity_type_count[e.entity_type] = entity_type_count.get(e.entity_type, 0) + 1

    top_risks = sorted(scored, key=lambda e: e.risk_score or 0, reverse=True)[:5]
    top_entities = [
        {"entity_name": e.entity_name, "entity_type": e.entity_type, "risk_score": e.risk_score}
        for e in top_risks
    ]

    risk_tier_count = {"CRITICAL": len(critical), "HIGH": len(high)}
    risk_tier_count["ELEVATED"] = sum(1 for e in scored if e.risk_score and 41 <= e.risk_score <= 60)

    content = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "executive_summary": (
            f"Portfolio risk score is {total_risk}. "
            f"{len(critical)} entities are critical, {len(high)} are high-risk. "
            f"{len(critical_anomalies)} critical and {len(high_anomalies)} high-severity anomalies active. "
            f"{len(actions)} remediation actions are open."
        ),
        "portfolio_risk_score": total_risk,
        "risk_tier_distribution": risk_tier_count,
        "entity_type_breakdown": entity_type_count,
        "top_risks": top_entities,
        "anomaly_overview": {
            "critical": len(critical_anomalies),
            "high": len(high_anomalies),
            "total_recent": len(anomaly_list),
        },
        "remediation_status": {
            "open": len(actions),
            "overdue": sum(1 for a in actions if a.due_date and a.due_date < datetime.now(timezone.utc).strftime("%Y-%m-%d")),
        },
        "recommendations": _generate_recommendations(critical, high, critical_anomalies, actions),
    }

    snapshot = IntelligenceSnapshot(
        snapshot_type="executive_brief",
        title=f"Executive Brief - {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        summary=content["executive_summary"],
        content=content,
        priority="high" if len(critical) > 0 else "normal",
    )
    db.add(snapshot)
    await db.flush()
    return snapshot


def _generate_recommendations(critical: list, high: list, critical_anomalies: list, actions: list) -> list:
    recs = []
    if len(critical) > 5:
        recs.append(f"Immediate attention required: {len(critical)} entities have critical risk scores.")
    if len(critical_anomalies) > 3:
        recs.append(f"Critical anomaly volume is high ({len(critical_anomalies)}). Prioritize investigation.")
    if len(actions) > 10:
        recs.append(f"Remediation backlog: {len(actions)} actions are open. Consider assigning additional resources.")
    if len(critical) == 0 and len(high) == 0:
        recs.append("Portfolio risk is well-controlled. Continue monitoring for emerging risks.")
    if not recs:
        recs.append("No critical issues detected. Maintain standard risk monitoring procedures.")
    return recs
