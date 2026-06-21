from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.vendor import Vendor, VendorDataAccess
from app.models.anomaly import AnomalyEvent
from app.models.compliance import Certification
from app.models.risk import RiskScore
from app.ai.rules import ANOMALY_RULES, evaluate_rule


async def run_anomaly_detection(db: AsyncSession, vendor: Vendor | None = None, commit: bool = True) -> list[AnomalyEvent]:
    if vendor:
        vendors = [vendor]
    else:
        result = await db.execute(select(Vendor).where(Vendor.is_archived == False))
        vendors = result.scalars().all()

    detected = []

    for v in vendors:
        context = await build_vendor_context(db, v)

        # Remove existing anomalies for this vendor
        existing = await db.execute(
            select(AnomalyEvent).where(AnomalyEvent.vendor_id == v.vendor_id)
        )
        for e in existing.scalars().all():
            await db.delete(e)

        for rule in ANOMALY_RULES:
            result = evaluate_rule(rule, v, context)
            if result:
                event = AnomalyEvent(
                    vendor_id=v.vendor_id,
                    anomaly_type=result["label"],
                    severity=result["severity"],
                    confidence_score=result.get("confidence", 1.0),
                    explanation=result.get("explanation", ""),
                    detected_at=datetime.now(timezone.utc),
                )
                db.add(event)
                detected.append(event)

        await db.flush()

    return detected


async def build_vendor_context(db: AsyncSession, vendor: Vendor) -> dict:
    context = {
        "has_data_access": {},
        "breach_count": 0,
        "recent_breach": False,
        "has_expired_cert": False,
        "expired_certs": [],
        "contract_expired": False,
        "has_active_access": False,
        "under_investigation": False,
        "risk_score": 0,
        "risk_tier": vendor.risk_tier or "",
        "annual_spend": float(vendor.annual_spend) if vendor.annual_spend else 0,
    }

    # Data access info
    access = await db.execute(
        select(VendorDataAccess).where(VendorDataAccess.vendor_id == vendor.vendor_id, VendorDataAccess.is_active == True)
    )
    for a in access.scalars().all():
        if a.data_type:
            context["has_data_access"][a.data_type.upper()] = True
        if a.is_active:
            context["has_active_access"] = True

    # Breaches
    from app.models.anomaly import AnomalyEvent
    breaches = await db.execute(
        select(AnomalyEvent).where(
            AnomalyEvent.vendor_id == vendor.vendor_id,
            AnomalyEvent.anomaly_type.in_(["RECENTLY_BREACHED_VENDOR", "BREACHED_VENDOR_HIGH_ACCESS"]),
        )
    )
    context["breach_count"] = len(breaches.scalars().all())
    context["recent_breach"] = context["breach_count"] > 0

    # Certifications
    from datetime import date
    certs = await db.execute(select(Certification).where(Certification.vendor_id == vendor.vendor_id))
    for c in certs.scalars().all():
        if c.expiry_date < date.today():
            context["has_expired_cert"] = True
            context["expired_certs"].append(c.certification_type)

    # Contract status
    if vendor.contract_status and vendor.contract_status.lower() == "expired":
        context["contract_expired"] = True

    # Risk score
    risk = await db.execute(
        select(RiskScore).where(RiskScore.vendor_id == vendor.vendor_id).order_by(RiskScore.generated_at.desc()).limit(1)
    )
    risk_score = risk.scalar_one_or_none()
    if risk_score:
        context["risk_score"] = float(risk_score.overall_score)
        context["risk_tier"] = risk_score.risk_tier

    return context
