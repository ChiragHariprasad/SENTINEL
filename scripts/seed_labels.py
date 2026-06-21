"""
Seed script: Load vendor_labels.csv for ground truth comparison.

Usage:
    python scripts/seed_labels.py --csv data/vendor_labels.csv

Idempotent: safe to re-run. Replaces existing ground truth.
"""

import argparse
import csv
import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.core.database import async_session_factory, engine, Base
from app.models.ground_truth import GroundTruthLabel
from app.models.vendor import Vendor
from app.services.evaluation_service import compute_evaluation
from sqlalchemy import select


async def seed(csv_path: str):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as db:
        prev = await db.execute(select(GroundTruthLabel))
        for r in prev.scalars().all():
            await db.delete(r)
        await db.flush()

        with open(csv_path, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            loaded = 0
            errors = []

            for row in reader:
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
                    errors.append(f"Missing anomaly_type for {vendor_key}")
                    continue

                label = GroundTruthLabel(
                    vendor_id=vendor.vendor_id,
                    anomaly_type=anomaly_type,
                    severity=row.get("severity") or "MEDIUM",
                    source=csv_path,
                )
                db.add(label)
                loaded += 1

            await db.commit()
            print(f"Loaded {loaded} ground truth labels")
            if errors:
                for e in errors[:10]:
                    print(f"  Warning: {e}")

        await compute_evaluation(db)
        await db.commit()
        print("Evaluation metrics recomputed against ground truth")

    await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed ground truth labels from CSV")
    parser.add_argument("--csv", required=True, help="Path to vendor_labels.csv")
    args = parser.parse_args()
    asyncio.run(seed(args.csv))
