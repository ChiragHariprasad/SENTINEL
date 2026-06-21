import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.risk_entity import RiskEntity
from app.models.risk_relationship import RiskRelationship
from app.models.risk_v2 import RiskScoreV2
from app.models.scenario import ScenarioRun

SCENARIO_TEMPLATES = {
    "BREACH": {
        "name": "Vendor Breach",
        "description": "Simulate the impact of a vendor security breach",
        "risk_increase_pct": 0.35,
        "severity": "CRITICAL",
    },
    "FAILURE": {
        "name": "Vendor Failure",
        "description": "Simulate the impact of a vendor going out of business",
        "risk_increase_pct": 0.50,
        "severity": "CRITICAL",
    },
    "CONTRACT_EXPIRY": {
        "name": "Contract Termination",
        "description": "Simulate the impact of contract termination",
        "risk_increase_pct": 0.20,
        "severity": "HIGH",
    },
    "CERT_EXPIRED": {
        "name": "Certification Expiry",
        "description": "Simulate the impact of all certifications expiring (e.g. SOC2, ISO27001)",
        "risk_increase_pct": 0.25,
        "severity": "HIGH",
    },
    "SOC2_EXPIRED": {
        "name": "SOC2 Certification Expired",
        "description": "Simulate the impact of SOC2 certification expiring for a vendor",
        "risk_increase_pct": 0.30,
        "severity": "HIGH",
    },
    "IDENTITY_COMPROMISE": {
        "name": "Identity Compromise",
        "description": "Simulate the impact of a user account compromise",
        "risk_increase_pct": 0.30,
        "severity": "CRITICAL",
    },
    "CONFIG_DRIFT": {
        "name": "Configuration Drift",
        "description": "Simulate the impact of configuration drift across systems",
        "risk_increase_pct": 0.15,
        "severity": "MEDIUM",
    },
}


async def run_scenario(
    db: AsyncSession,
    entity_id: uuid.UUID,
    scenario_type: str,
    commit: bool = True,
) -> ScenarioRun:
    scenario_def = SCENARIO_TEMPLATES.get(scenario_type)
    if not scenario_def:
        raise ValueError(f"Unknown scenario type: {scenario_type}")

    entity = await db.execute(select(RiskEntity).where(RiskEntity.entity_id == entity_id))
    entity = entity.scalar_one_or_none()
    if not entity:
        raise ValueError(f"Entity {entity_id} not found")

    latest = await db.execute(
        select(RiskScoreV2)
        .where(RiskScoreV2.entity_id == entity_id)
        .order_by(RiskScoreV2.generated_at.desc())
        .limit(1)
    )
    current_risk = latest.scalar_one_or_none()
    current_score = float(current_risk.overall_score) if current_risk else (entity.risk_score or 0)

    impacted = await _traverse_graph(db, entity_id, max_depth=5)
    risk_delta = round(current_score * scenario_def["risk_increase_pct"], 2)
    projected_score = round(min(current_score + risk_delta, 100), 2)

    base_delta = risk_delta
    for imp in impacted["all_entities"]:
        imp_entity = await db.execute(select(RiskEntity).where(RiskEntity.entity_id == imp["entity_id"]))
        ie = imp_entity.scalar_one_or_none()
        if ie and ie.risk_score is not None:
            imp["projected_risk"] = round(min(float(ie.risk_score) + float(ie.risk_score) * scenario_def["risk_increase_pct"] * 0.5, 100), 2)
            imp["risk_delta"] = round(float(ie.risk_score) * scenario_def["risk_increase_pct"] * 0.5, 2)

    results = {
        "scenario": scenario_def["name"],
        "description": scenario_def["description"],
        "source_entity": {
            "entity_id": str(entity.entity_id),
            "entity_name": entity.entity_name,
            "entity_type": entity.entity_type,
            "current_risk": current_score,
        },
        "impact": {
            "current_risk": current_score,
            "risk_delta": risk_delta,
            "projected_risk": projected_score,
            "risk_increase_pct": scenario_def["risk_increase_pct"],
        },
        "blast_radius": {
            "affected_systems": impacted["systems"],
            "affected_controls": impacted["controls"],
            "affected_users": impacted["users"],
            "affected_vendors": impacted["vendors"],
            "total_affected": impacted["total"],
        },
        "impacted_entities": impacted["all_entities"][:50],
        "impact_paths": impacted["paths"][:20],
    }

    run = ScenarioRun(
        entity_id=entity_id,
        scenario_type=scenario_type,
        input_data={
            "entity_id": str(entity_id),
            "scenario_type": scenario_type,
            "entity_name": entity.entity_name,
            "entity_type": entity.entity_type,
        },
        results=results,
        risk_delta=risk_delta,
        created_at=datetime.now(timezone.utc),
    )
    db.add(run)
    await db.flush()

    if commit:
        await db.commit()

    return run


async def _traverse_graph(
    db: AsyncSession,
    entity_id: uuid.UUID,
    max_depth: int = 5,
) -> dict:
    visited = {entity_id}
    impacted = {"SYSTEM": set(), "CONTROL": set(), "USER": set(), "VENDOR": set(), "other": set()}
    all_entities = []
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

                entry = {
                    "entity_id": str(te.entity_id),
                    "entity_name": te.entity_name,
                    "entity_type": etype,
                    "current_risk": te.risk_score,
                    "projected_risk": None,
                    "risk_delta": None,
                    "relationship": rel.relationship_type,
                }
                all_entities.append(entry)

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
        "systems": len(impacted["SYSTEM"]),
        "controls": len(impacted["CONTROL"]),
        "users": len(impacted["USER"]),
        "vendors": len(impacted["VENDOR"]),
        "total": sum(len(v) for v in impacted.values()),
        "all_entities": all_entities,
        "paths": paths,
    }


def get_scenario_templates() -> list[dict]:
    return [
        {
            "id": key,
            "name": val["name"],
            "description": val["description"],
            "severity": val["severity"],
            "risk_increase_pct": val["risk_increase_pct"],
        }
        for key, val in SCENARIO_TEMPLATES.items()
    ]
