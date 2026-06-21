import uuid
from datetime import date, timedelta, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.compliance import Certification, ComplianceFramework
from app.schemas.certification import CertificationCreate, CertificationResponse
from app.schemas.common import StandardResponse

router = APIRouter(prefix="/certifications", tags=["Certifications"])


@router.get("")
async def list_certifications(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Certification))
    certs = result.scalars().all()
    return StandardResponse(data={"items": [CertificationResponse.model_validate(c).model_dump() for c in certs]})


@router.post("")
async def create_certification(request: CertificationCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    cert = Certification(**request.model_dump())
    db.add(cert)
    await db.flush()
    return StandardResponse(data=CertificationResponse.model_validate(cert).model_dump())


@router.get("/expiring")
async def get_expiring_certifications(days: int = Query(60, ge=1), db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    cutoff = date.today() + timedelta(days=days)
    result = await db.execute(
        select(Certification).where(Certification.expiry_date <= cutoff, Certification.status == "active")
    )
    certs = result.scalars().all()
    return StandardResponse(data={"items": [CertificationResponse.model_validate(c).model_dump() for c in certs]})


@router.get("/frameworks")
async def list_frameworks(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(ComplianceFramework))
    frameworks = result.scalars().all()
    return StandardResponse(data={"items": [{"framework_id": str(f.framework_id), "framework_name": f.framework_name} for f in frameworks]})
