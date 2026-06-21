from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.risk_entity import RiskEntity
from app.models.risk_v2 import RiskScoreV2, AnomalyEventV2
from app.models.vendor import Vendor, VendorDataAccess
from app.models.compliance import Certification
from app.ai.rules_v2 import evaluate_rules_for_entity


async def run_anomaly_detection(
    db: AsyncSession,
    entity: RiskEntity | None = None,
    commit: bool = True,
) -> list[AnomalyEventV2]:
    if entity:
        entities = [entity]
    else:
        result = await db.execute(select(RiskEntity).where(RiskEntity.status == "active"))
        entities = result.scalars().all()

    all_events = []
    for ent in entities:
        context = await _build_entity_context(db, ent)
        rule_results = evaluate_rules_for_entity(ent.entity_type, context)

        existing = await db.execute(
            select(AnomalyEventV2).where(AnomalyEventV2.entity_id == ent.entity_id)
        )
        existing_types = {e.anomaly_type for e in existing.scalars().all()}

        for rr in rule_results:
            if rr["anomaly_type"] in existing_types:
                continue

            event = AnomalyEventV2(
                entity_id=ent.entity_id,
                anomaly_type=rr["anomaly_type"],
                domain=rr["domain"],
                severity=rr["severity"],
                confidence_score=rr["confidence_score"],
                explanation=rr["explanation"],
            )
            db.add(event)
            await db.flush()
            all_events.append(event)

    if commit:
        await db.commit()

    return all_events


async def _build_entity_context(db: AsyncSession, entity: RiskEntity) -> dict:
    context = {
        "risk_score": entity.risk_score,
    }

    if entity.entity_type == "VENDOR" and entity.external_id:
        result = await db.execute(select(Vendor).where(Vendor.vendor_id == entity.external_id))
        vendor = result.scalar_one_or_none()
        if vendor:
            certs = await db.execute(select(Certification).where(Certification.vendor_id == vendor.vendor_id))
            cert_list = certs.scalars().all()
            from datetime import date
            expired = sum(1 for c in cert_list if c.expiry_date < date.today())

            breaches = await db.execute(
                select(AnomalyEventV2).where(
                    AnomalyEventV2.entity_id == entity.entity_id,
                    AnomalyEventV2.anomaly_type == "BREACHED_VENDOR",
                )
            )

            context.update({
                "expired_cert_count": expired,
                "contract_status": vendor.contract_status,
                "under_investigation": False,
                "breach_count": len(breaches.scalars().all()),
            })

    elif entity.entity_type == "USER":
        attrs = entity.attributes or {}
        context.update({
            "after_hours_access": attrs.get("after_hours_access", False),
            "login_failures": attrs.get("login_failures", 0),
            "privilege_escalation": attrs.get("privilege_escalation", False),
            "days_since_login": attrs.get("days_since_login"),
        })

    elif entity.entity_type in ("SYSTEM", "CONFIG"):
        attrs = entity.attributes or {}
        context.update({
            "encryption_enabled": attrs.get("encryption_enabled", True),
            "logging_enabled": attrs.get("logging_enabled", True),
            "compliance_drift": attrs.get("compliance_drift", False),
            "public_access": attrs.get("public_access", False),
        })

    return context
