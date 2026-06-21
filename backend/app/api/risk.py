import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.vendor import Vendor
from app.models.risk import RiskScore, RiskHistory
from app.schemas.risk import RiskScoreResponse, RiskHistoryResponse
from app.schemas.common import StandardResponse
from app.core.exceptions import NotFoundError
from app.services.risk_service import calculate_vendor_risk

router = APIRouter(prefix="/risk", tags=["Risk"])


@router.post("/calculate")
async def calculate_risk(vendor_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Vendor).where(Vendor.vendor_id == vendor_id))
    vendor = result.scalar_one_or_none()
    if not vendor:
        raise NotFoundError("Vendor", str(vendor_id))

    risk_score = await calculate_vendor_risk(db, vendor)
    return StandardResponse(data=RiskScoreResponse.model_validate(risk_score).model_dump())


@router.get("/vendors/{vendor_id}")
async def get_vendor_risk(vendor_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(RiskScore).where(RiskScore.vendor_id == vendor_id).order_by(desc(RiskScore.generated_at)).limit(1)
    )
    risk = result.scalar_one_or_none()
    if not risk:
        raise NotFoundError("Risk score for vendor", str(vendor_id))
    return StandardResponse(data=RiskScoreResponse.model_validate(risk).model_dump())


@router.get("/vendors/{vendor_id}/history")
async def get_risk_history(vendor_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(RiskHistory).where(RiskHistory.vendor_id == vendor_id).order_by(desc(RiskHistory.created_at)).limit(50)
    )
    history = result.scalars().all()
    return StandardResponse(data={"history": [RiskHistoryResponse.model_validate(h).model_dump() for h in history]})


@router.post("/recalculate")
async def recalculate_all(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Vendor).where(Vendor.is_archived == False))
    vendors = result.scalars().all()

    for vendor in vendors:
        score = await calculate_vendor_risk(db, vendor, commit=False)

    await db.commit()
    return StandardResponse(message=f"Risk recalculated for {len(vendors)} vendors")
