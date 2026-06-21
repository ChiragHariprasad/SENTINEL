from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.vendor import Vendor, VendorDataAccess
from app.models.risk import RiskScore, RiskHistory
from app.models.compliance import Certification
from app.ai.scoring import calculate_weighted_score


async def calculate_vendor_risk(db: AsyncSession, vendor: Vendor, commit: bool = True) -> RiskScore:
    scores = await calculate_risk_dimensions(db, vendor)
    overall_score, risk_tier = calculate_weighted_score(scores)

    prev = await db.execute(
        select(RiskScore).where(RiskScore.vendor_id == vendor.vendor_id).order_by(RiskScore.generated_at.desc()).limit(1)
    )
    previous_score = prev.scalar_one_or_none()

    risk_score = RiskScore(
        vendor_id=vendor.vendor_id,
        security_score=scores["security"],
        data_access_score=scores["data_access"],
        compliance_score=scores["compliance"],
        financial_score=scores["financial"],
        contract_score=scores["contract"],
        overall_score=overall_score,
        risk_tier=risk_tier,
        generated_at=datetime.now(timezone.utc),
    )
    db.add(risk_score)
    await db.flush()

    vendor.risk_tier = risk_tier

    change_reason = None
    if previous_score:
        delta = float(overall_score) - float(previous_score.overall_score)
        if delta > 5:
            change_reason = f"Score increased by {delta:.1f} points"
        elif delta < -5:
            change_reason = f"Score decreased by {abs(delta):.1f} points"

    history = RiskHistory(
        vendor_id=vendor.vendor_id,
        overall_score=overall_score,
        risk_tier=risk_tier,
        change_reason=change_reason,
        created_at=datetime.now(timezone.utc),
    )
    db.add(history)
    await db.flush()

    return risk_score


async def calculate_risk_dimensions(db: AsyncSession, vendor: Vendor) -> dict:
    scores = {
        "security": 0,
        "data_access": 0,
        "compliance": 0,
        "financial": 0,
        "contract": 0,
    }

    # Security: breach history indicator
    from app.models.anomaly import AnomalyEvent
    breaches = await db.execute(
        select(AnomalyEvent).where(
            AnomalyEvent.vendor_id == vendor.vendor_id,
            AnomalyEvent.anomaly_type.in_(["BREACHED_VENDOR_HIGH_ACCESS", "RECENTLY_BREACHED_VENDOR"]),
        )
    )
    breach_count = len(breaches.scalars().all())
    scores["security"] = min(100, breach_count * 25 + (20 if vendor.criticality == "HIGH" else 0))

    # Data access
    access = await db.execute(
        select(VendorDataAccess).where(VendorDataAccess.vendor_id == vendor.vendor_id, VendorDataAccess.is_active == True)
    )
    access_list = access.scalars().all()
    data_score = 0
    for a in access_list:
        if a.data_type and a.data_type.upper() in ("PII", "PCI", "PHI", "FINANCIAL"):
            data_score += 30
        if a.access_level and a.access_level.lower() == "admin":
            data_score += 20
    scores["data_access"] = min(100, data_score)

    # Compliance
    certs = await db.execute(
        select(Certification).where(Certification.vendor_id == vendor.vendor_id)
    )
    cert_list = certs.scalars().all()
    from datetime import date
    expired = sum(1 for c in cert_list if c.expiry_date < date.today())
    total = len(cert_list)
    scores["compliance"] = min(100, (expired / max(total, 1)) * 100)

    # Financial: based on spend and criticality
    if vendor.annual_spend and float(vendor.annual_spend) > 1000000:
        scores["financial"] = 60
    elif vendor.annual_spend and float(vendor.annual_spend) > 500000:
        scores["financial"] = 40
    else:
        scores["financial"] = 20

    # Contract risk
    if vendor.contract_status and vendor.contract_status.lower() == "expired":
        scores["contract"] = 80
    elif vendor.contract_status and vendor.contract_status.lower() == "active":
        scores["contract"] = 20
    else:
        scores["contract"] = 40

    return scores
