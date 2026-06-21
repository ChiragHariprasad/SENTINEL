from datetime import datetime, timezone, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.risk_entity import RiskEntity
from app.models.risk_v2 import RiskScoreV2, RiskHistoryV2
from app.models.vendor import Vendor, VendorDataAccess
from app.models.compliance import Certification
from app.models.anomaly import AnomalyEvent
from app.ai.scoring_v2 import calculate_weighted_score


async def calculate_entity_risk(
    db: AsyncSession,
    entity: RiskEntity,
    commit: bool = True,
) -> RiskScoreV2:
    scores = await _compute_risk_dimensions(db, entity)
    overall_score, risk_tier = calculate_weighted_score(scores, entity.entity_type)

    prev = await db.execute(
        select(RiskScoreV2)
        .where(RiskScoreV2.entity_id == entity.entity_id)
        .order_by(RiskScoreV2.generated_at.desc())
        .limit(1)
    )
    previous_score = prev.scalar_one_or_none()

    risk_score = RiskScoreV2(
        entity_id=entity.entity_id,
        security_score=scores.get("security"),
        compliance_score=scores.get("compliance"),
        operational_score=scores.get("operational"),
        financial_score=scores.get("financial"),
        access_score=scores.get("access"),
        overall_score=overall_score,
        risk_tier=risk_tier,
        generated_at=datetime.now(timezone.utc),
    )
    db.add(risk_score)
    await db.flush()

    entity.risk_score = float(overall_score)

    change_reason = None
    if previous_score:
        delta = float(overall_score) - float(previous_score.overall_score)
        if abs(delta) > 5:
            direction = "increased" if delta > 0 else "decreased"
            change_reason = f"Score {direction} by {abs(delta):.1f} points"

    history = RiskHistoryV2(
        entity_id=entity.entity_id,
        overall_score=overall_score,
        risk_tier=risk_tier,
        change_reason=change_reason,
        created_at=datetime.now(timezone.utc),
    )
    db.add(history)
    await db.flush()

    if commit:
        await db.commit()

    return risk_score


async def _compute_risk_dimensions(db: AsyncSession, entity: RiskEntity) -> dict:
    scores = {"security": 0, "compliance": 0, "operational": 0, "financial": 0, "access": 0}

    if entity.entity_type == "VENDOR":
        vendor = await _get_linked_vendor(db, entity)
        if not vendor:
            return scores

        breaches = await db.execute(
            select(AnomalyEvent).where(
                AnomalyEvent.vendor_id == vendor.vendor_id,
                AnomalyEvent.anomaly_type.in_(["BREACHED_VENDOR_HIGH_ACCESS", "RECENTLY_BREACHED_VENDOR"]),
            )
        )
        breach_count = len(breaches.scalars().all())
        scores["security"] = min(100, breach_count * 25 + (20 if (vendor.criticality or "").upper() == "HIGH" else 0))

        certs = await db.execute(select(Certification).where(Certification.vendor_id == vendor.vendor_id))
        cert_list = certs.scalars().all()
        expired = sum(1 for c in cert_list if c.expiry_date < date.today())
        scores["compliance"] = min(100, (expired / max(len(cert_list), 1)) * 100)

        if vendor.contract_status and vendor.contract_status.lower() == "expired":
            scores["operational"] = 80
        elif vendor.contract_status and vendor.contract_status.lower() == "active":
            scores["operational"] = 20
        else:
            scores["operational"] = 40

        if vendor.annual_spend is not None:
            spend = float(vendor.annual_spend)
            scores["financial"] = 60 if spend > 1_000_000 else (40 if spend > 500_000 else 20)

        access = await db.execute(
            select(VendorDataAccess).where(
                VendorDataAccess.vendor_id == vendor.vendor_id,
                VendorDataAccess.is_active == True,
            )
        )
        data_score = 0
        for a in access.scalars().all():
            if a.data_type and a.data_type.upper() in ("PII", "PCI", "PHI", "FINANCIAL"):
                data_score += 30
            if a.access_level and a.access_level.lower() == "admin":
                data_score += 20
        scores["access"] = min(100, data_score)

    elif entity.entity_type == "SYSTEM":
        scores["security"] = 30
        scores["compliance"] = 20
        scores["operational"] = 25
        scores["access"] = 40

    elif entity.entity_type == "USER":
        scores["security"] = 25
        scores["access"] = 50
        scores["operational"] = 10

    elif entity.entity_type == "CONTROL":
        scores["compliance"] = 50
        scores["security"] = 30
        scores["operational"] = 20

    elif entity.entity_type == "CONFIG":
        scores["security"] = 40
        scores["compliance"] = 30
        scores["operational"] = 20

    else:
        scores["compliance"] = 25
        scores["security"] = 25

    return scores


async def _get_linked_vendor(db: AsyncSession, entity: RiskEntity) -> Vendor | None:
    if not entity.external_id:
        return None
    result = await db.execute(select(Vendor).where(Vendor.vendor_id == entity.external_id))
    return result.scalar_one_or_none()
