import csv
import io
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.vendor import Vendor, VendorDataAccess
from app.models.import_job import CsvImport
from app.models.anomaly import AnomalyEvent
from app.schemas.import_job import ImportResponse, ImportStatusResponse
from app.schemas.common import StandardResponse
from app.core.exceptions import ValidationError
from app.services.anomaly_service import run_anomaly_detection
from app.services.evaluation_service import compute_evaluation

router = APIRouter(prefix="/vendors", tags=["Import"])


@router.post("/import")
async def import_vendors(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.filename or not file.filename.endswith(".csv"):
        raise ValidationError("Only CSV files are supported")

    content = await file.read()
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))

    import_job = CsvImport(file_name=file.filename, file_type="registry", status="processing")
    db.add(import_job)
    await db.flush()

    processed = 0
    failed = 0
    errors = []

    for row in reader:
        try:
            vendor_name = row.get("vendor_name") or row.get("Vendor Name") or row.get("vendor")
            if not vendor_name:
                failed += 1
                continue

            existing = await db.execute(select(Vendor).where(Vendor.vendor_name == vendor_name))
            if existing.scalar_one_or_none():
                failed += 1
                errors.append(f"Duplicate vendor: {vendor_name}")
                continue

            vendor = Vendor(
                vendor_name=vendor_name,
                vendor_type=row.get("vendor_type") or row.get("Vendor Type") or row.get("type"),
                vendor_owner=row.get("vendor_owner") or row.get("Vendor Owner") or row.get("owner"),
                annual_spend=float(row.get("annual_spend") or row.get("Annual Spend") or 0 or 0),
                criticality=row.get("criticality") or row.get("Criticality"),
                contract_status=row.get("contract_status") or row.get("Contract Status"),
            )
            db.add(vendor)
            await db.flush()

            # Import vendor_labels data if present
            data_access = row.get("data_access") or row.get("Data Access") or row.get("data_type")
            if data_access:
                access = VendorDataAccess(
                    vendor_id=vendor.vendor_id,
                    data_type=data_access,
                    access_level=row.get("access_level") or "Read",
                    is_active=True,
                )
                db.add(access)

            processed += 1

        except Exception as e:
            failed += 1
            errors.append(str(e))

    import_job.records_processed = processed
    import_job.records_failed = failed
    import_job.error_log = {"errors": errors[:100]}
    import_job.status = "completed" if failed == 0 else "completed_with_errors"

    await db.flush()

    return StandardResponse(data={
        "job_id": str(import_job.import_id),
        "status": import_job.status,
        "processed": processed,
        "failed": failed,
    })


@router.get("/imports/{job_id}")
async def get_import_status(job_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(CsvImport).where(CsvImport.import_id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Import", str(job_id))

    return StandardResponse(data={
        "job_id": str(job.import_id),
        "status": job.status,
        "processed": job.records_processed,
        "failed": job.records_failed,
    })
