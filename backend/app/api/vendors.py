import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.vendor import Vendor, VendorDataAccess
from app.schemas.vendor import VendorCreate, VendorUpdate, VendorResponse, VendorListResponse, VendorDataAccessCreate, VendorDataAccessResponse
from app.schemas.common import StandardResponse
from app.core.exceptions import NotFoundError

router = APIRouter(prefix="/vendors", tags=["Vendors"])


@router.get("")
async def list_vendors(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    risk_tier: str | None = None,
    vendor_type: str | None = None,
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Vendor).where(Vendor.is_archived == False)

    if risk_tier:
        query = query.where(Vendor.risk_tier == risk_tier.upper())
    if vendor_type:
        query = query.where(Vendor.vendor_type.ilike(f"%{vendor_type}%"))
    if search:
        query = query.where(Vendor.vendor_name.ilike(f"%{search}%"))

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    query = query.offset((page - 1) * size).limit(size).order_by(Vendor.vendor_name)
    result = await db.execute(query)
    vendors = result.scalars().all()

    return StandardResponse(data={
        "total": total,
        "items": [VendorResponse.model_validate(v).model_dump() for v in vendors],
    })


@router.post("")
async def create_vendor(request: VendorCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    vendor = Vendor(**request.model_dump())
    db.add(vendor)
    await db.flush()
    return StandardResponse(data=VendorResponse.model_validate(vendor).model_dump())


@router.get("/{vendor_id}")
async def get_vendor(vendor_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Vendor).where(Vendor.vendor_id == vendor_id))
    vendor = result.scalar_one_or_none()
    if not vendor:
        raise NotFoundError("Vendor", str(vendor_id))
    return StandardResponse(data=VendorResponse.model_validate(vendor).model_dump())


@router.put("/{vendor_id}")
async def update_vendor(vendor_id: uuid.UUID, request: VendorUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Vendor).where(Vendor.vendor_id == vendor_id))
    vendor = result.scalar_one_or_none()
    if not vendor:
        raise NotFoundError("Vendor", str(vendor_id))

    for key, val in request.model_dump(exclude_unset=True).items():
        setattr(vendor, key, val)

    await db.flush()
    return StandardResponse(data=VendorResponse.model_validate(vendor).model_dump())


@router.delete("/{vendor_id}")
async def delete_vendor(vendor_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Vendor).where(Vendor.vendor_id == vendor_id))
    vendor = result.scalar_one_or_none()
    if not vendor:
        raise NotFoundError("Vendor", str(vendor_id))
    vendor.is_archived = True
    await db.flush()
    return StandardResponse(message="Vendor archived")


@router.get("/categories/list")
async def list_categories(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.models.vendor import VendorCategory
    result = await db.execute(select(VendorCategory))
    categories = result.scalars().all()
    return StandardResponse(data={"items": [{"category_id": str(c.category_id), "category_name": c.category_name} for c in categories]})


@router.post("/data-access")
async def create_data_access(request: VendorDataAccessCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    access = VendorDataAccess(**request.model_dump())
    db.add(access)
    await db.flush()
    return StandardResponse(data=VendorDataAccessResponse.model_validate(access).model_dump())


@router.get("/{vendor_id}/data-access")
async def list_data_access(vendor_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(VendorDataAccess).where(VendorDataAccess.vendor_id == vendor_id, VendorDataAccess.is_active == True))
    items = result.scalars().all()
    return StandardResponse(data={"items": [VendorDataAccessResponse.model_validate(a).model_dump() for a in items]})
