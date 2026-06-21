"""
Seed script: Load vendor_registry.csv into the database.

Usage:
    python scripts/seed_vendors.py --csv data/vendor_registry.csv

Idempotent: safe to re-run. Uses vendor_name as dedup key.
"""

import argparse
import csv
import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.core.database import async_session_factory, engine, Base
from app.models.vendor import Vendor, VendorDataAccess
from app.services.anomaly_service import run_anomaly_detection
from app.services.evaluation_service import compute_evaluation
from sqlalchemy import select


async def seed(csv_path: str):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as db:
        with open(csv_path, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            processed = 0
            for row in reader:
                vendor_name = row.get("vendor_name") or row.get("Vendor Name") or row.get("vendor")
                if not vendor_name:
                    continue

                result = await db.execute(select(Vendor).where(Vendor.vendor_name == vendor_name))
                if result.scalar_one_or_none():
                    print(f"Skipping duplicate: {vendor_name}")
                    continue

                vendor = Vendor(
                    vendor_name=vendor_name,
                    vendor_type=row.get("vendor_type") or row.get("Vendor Type") or row.get("type"),
                    vendor_owner=row.get("vendor_owner") or row.get("Vendor Owner") or row.get("owner"),
                    annual_spend=float(row.get("annual_spend") or row.get("Annual Spend") or 0),
                    criticality=row.get("criticality") or row.get("Criticality"),
                    contract_status=row.get("contract_status") or row.get("Contract Status"),
                )
                db.add(vendor)
                await db.flush()

                data_access = row.get("data_access") or row.get("Data Access") or row.get("data_type")
                if data_access:
                    db.add(VendorDataAccess(
                        vendor_id=vendor.vendor_id,
                        data_type=data_access,
                        access_level=row.get("access_level") or "Read",
                        is_active=True,
                    ))

                processed += 1

            await db.commit()
            print(f"Imported {processed} vendors")

        vendors_result = await db.execute(select(Vendor))
        vendors = vendors_result.scalars().all()
        for v in vendors:
            await run_anomaly_detection(db, v)
        await db.commit()
        print("Anomaly detection complete")

        await compute_evaluation(db)
        await db.commit()
        print("Evaluation metrics computed")

    await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed vendors from CSV")
    parser.add_argument("--csv", required=True, help="Path to vendor_registry.csv")
    args = parser.parse_args()
    asyncio.run(seed(args.csv))
