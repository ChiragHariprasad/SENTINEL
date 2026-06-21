from datetime import date, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.vendor import Vendor
from app.models.anomaly import AnomalyEvent
from app.models.alert import SecurityAlert
from app.models.compliance import Certification
from app.models.evaluation import EvaluationResult
from app.schemas.common import StandardResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
async def get_dashboard_summary(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Total vendors
    total = (await db.execute(select(func.count()).select_from(Vendor).where(Vendor.is_archived == False))).scalar()

    # Risk distribution
    risk_dist = {}
    for tier in ["RED", "YELLOW", "GREEN"]:
        count = (await db.execute(
            select(func.count()).select_from(Vendor).where(Vendor.risk_tier == tier, Vendor.is_archived == False)
        )).scalar()
        risk_dist[tier.lower()] = count

    # Critical vendors
    critical = (await db.execute(
        select(func.count()).select_from(Vendor).where(Vendor.risk_tier == "RED", Vendor.is_archived == False)
    )).scalar()

    # High risk (score > 70)
    from app.models.risk import RiskScore
    high_risk_sub = select(RiskScore.vendor_id).where(RiskScore.overall_score > 70).distinct().subquery()
    high_risk = (await db.execute(select(func.count()).select_from(high_risk_sub))).scalar()

    # Expiring certifications
    from datetime import timedelta
    cutoff = date.today() + timedelta(days=60)
    expiring = (await db.execute(
        select(func.count()).select_from(Certification).where(Certification.expiry_date <= cutoff, Certification.status == "active")
    )).scalar()

    # Open alerts
    open_alerts = (await db.execute(
        select(func.count()).select_from(SecurityAlert).where(SecurityAlert.status == "open")
    )).scalar()

    # Total anomalies
    total_anomalies = (await db.execute(select(func.count()).select_from(AnomalyEvent))).scalar()

    # Evaluation summary
    eval_result = await db.execute(
        select(EvaluationResult).where(EvaluationResult.anomaly_type.is_(None)).order_by(EvaluationResult.computed_at.desc()).limit(1)
    )
    eval_summary = eval_result.scalar_one_or_none()

    return StandardResponse(data={
        "total_vendors": total,
        "critical_vendors": critical,
        "high_risk_vendors": high_risk,
        "expiring_certifications": expiring,
        "open_alerts": open_alerts,
        "total_anomalies": total_anomalies,
        "risk_distribution": risk_dist,
        "evaluation_summary": {
            "precision": float(eval_summary.precision) if eval_summary else None,
            "recall": float(eval_summary.recall) if eval_summary else None,
            "f1_score": float(eval_summary.f1_score) if eval_summary else None,
        } if eval_summary else None,
    })
