import uuid
import csv
import io
from enum import Enum
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.vendor import Vendor
from app.models.risk import RiskScore
from app.models.anomaly import AnomalyEvent
from app.schemas.common import StandardResponse

router = APIRouter(prefix="/reports", tags=["Reports"])


class ReportTypeEnum(str, Enum):
    VENDOR_RISK_REGISTER = "vendor_risk_register"


@router.post("")
async def generate_report(report_type: ReportTypeEnum = Query(ReportTypeEnum.VENDOR_RISK_REGISTER), db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    vendors = (await db.execute(select(Vendor).where(Vendor.is_archived == False))).scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Vendor Name", "Vendor Type", "Risk Tier", "Overall Score", "Criticality", "Contract Status"])

    for v in vendors:
        risk = (await db.execute(
            select(RiskScore).where(RiskScore.vendor_id == v.vendor_id).order_by(RiskScore.generated_at.desc()).limit(1)
        )).scalar_one_or_none()

        writer.writerow([
            v.vendor_name, v.vendor_type, v.risk_tier or "",
            float(risk.overall_score) if risk else "", v.criticality or "", v.contract_status or "",
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=vendor_risk_register.csv"},
    )


@router.get("/{report_id}/download")
async def download_report(report_id: str):
    return StandardResponse(message="Report download endpoint")
