import csv
import io
import uuid
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.evaluation import EvaluationResult
from app.models.ground_truth import GroundTruthLabel
from app.models.vendor import Vendor
from app.schemas.common import StandardResponse
from app.core.exceptions import ValidationError
from app.services.evaluation_service import compute_evaluation

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])


@router.get("/metrics")
async def get_evaluation_metrics(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    results = await db.execute(
        select(EvaluationResult).order_by(EvaluationResult.computed_at.desc())
    )
    all_results = results.scalars().all()

    overall = None
    by_severity = {}
    by_label = {}

    for r in all_results:
        item = {
            "precision": float(r.precision) if r.precision else 0,
            "recall": float(r.recall) if r.recall else 0,
            "f1_score": float(r.f1_score) if r.f1_score else 0,
        }
        if r.anomaly_type is None and r.severity is None:
            overall = item
        elif r.anomaly_type is None and r.severity:
            by_severity[r.severity] = item
        elif r.anomaly_type:
            by_label[r.anomaly_type] = item

    if not overall:
        overall = {"precision": 0, "recall": 0, "f1_score": 0}

    return StandardResponse(data={
        "overall": overall,
        "by_severity": by_severity,
        "by_label": by_label,
        "confusion_matrix": {"labels": list(by_label.keys()), "matrix": []},
        "computed_at": all_results[0].computed_at.isoformat() if all_results else "",
    })


@router.post("/run")
async def run_evaluation(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await compute_evaluation(db)
    return StandardResponse(data=result)


@router.post("/upload-labels")
async def upload_labels(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.filename or not file.filename.endswith(".csv"):
        raise ValidationError("Only CSV files are supported")

    content = await file.read()
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))

    prev = await db.execute(select(GroundTruthLabel))
    for r in prev.scalars().all():
        await db.delete(r)
    await db.flush()

    loaded = 0
    errors = []

    for row in reader:
        try:
            vendor_key = row.get("vendor_id") or row.get("vendor_name") or row.get("vendor")
            if not vendor_key:
                errors.append("Row missing vendor identifier")
                continue

            result = await db.execute(
                select(Vendor).where(Vendor.vendor_id == vendor_key)
            )
            vendor = result.scalar_one_or_none()
            if not vendor:
                result = await db.execute(
                    select(Vendor).where(Vendor.vendor_name == vendor_key)
                )
                vendor = result.scalar_one_or_none()

            if not vendor:
                errors.append(f"Vendor not found: {vendor_key}")
                continue

            anomaly_type = row.get("anomaly_type") or row.get("label") or row.get("rule")
            if not anomaly_type:
                errors.append(f"Row missing anomaly_type for {vendor_key}")
                continue

            label = GroundTruthLabel(
                vendor_id=vendor.vendor_id,
                anomaly_type=anomaly_type,
                severity=row.get("severity") or "MEDIUM",
                source=file.filename or "vendor_labels.csv",
            )
            db.add(label)
            loaded += 1

        except Exception as e:
            errors.append(str(e))

    await db.flush()

    return StandardResponse(data={
        "loaded": loaded,
        "errors": errors[:50],
        "ground_truth_count": loaded,
    })
