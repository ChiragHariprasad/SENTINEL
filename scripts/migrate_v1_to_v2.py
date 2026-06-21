"""
Migrate existing v1 data to v2 Entity Registry.

Creates RiskEntity records for all existing Vendors, Systems (from data access),
and Controls (from certifications). Creates relationships between them.

Idempotent: safe to re-run.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from sqlalchemy import select
from app.core.database import async_session_factory
from app.models.vendor import Vendor, VendorDataAccess
from app.models.compliance import Certification
from app.models.risk_entity import RiskEntity
from app.models.risk_relationship import RiskRelationship


async def migrate():
    async with async_session_factory() as db:
        vendors = await db.execute(select(Vendor).where(Vendor.is_archived == False))
        vendors = vendors.scalars().all()
        migrated_count = 0

        for vendor in vendors:
            existing = await db.execute(
                select(RiskEntity).where(
                    RiskEntity.entity_type == "VENDOR",
                    RiskEntity.entity_name == vendor.vendor_name,
                )
            )
            if existing.scalar_one_or_none():
                continue

            entity = RiskEntity(
                entity_type="VENDOR",
                entity_name=vendor.vendor_name,
                external_id=str(vendor.vendor_id),
                risk_score=None,
                status="archived" if vendor.is_archived else "active",
                attributes={
                    "vendor_type": vendor.vendor_type,
                    "vendor_owner": vendor.vendor_owner,
                    "annual_spend": float(vendor.annual_spend) if vendor.annual_spend else None,
                    "criticality": vendor.criticality,
                    "contract_status": vendor.contract_status,
                    "risk_tier": vendor.risk_tier,
                },
            )
            db.add(entity)
            await db.flush()
            vendor_entity_id = entity.entity_id

            access_records = await db.execute(
                select(VendorDataAccess).where(
                    VendorDataAccess.vendor_id == vendor.vendor_id,
                    VendorDataAccess.is_active == True,
                )
            )
            for access in access_records.scalars().all():
                system_name = access.system_name or f"System-{access.data_type}"
                sys_result = await db.execute(
                    select(RiskEntity).where(
                        RiskEntity.entity_type == "SYSTEM",
                        RiskEntity.entity_name == system_name,
                    )
                )
                system_entity = sys_result.scalar_one_or_none()
                if not system_entity:
                    system_entity = RiskEntity(
                        entity_type="SYSTEM",
                        entity_name=system_name,
                        attributes={
                            "data_type": access.data_type,
                            "access_level": access.access_level,
                        },
                    )
                    db.add(system_entity)
                    await db.flush()

                existing_rel = await db.execute(
                    select(RiskRelationship).where(
                        RiskRelationship.source_entity_id == vendor_entity_id,
                        RiskRelationship.target_entity_id == system_entity.entity_id,
                        RiskRelationship.relationship_type == "HAS_ACCESS_TO",
                    )
                )
                if not existing_rel.scalar_one_or_none():
                    db.add(RiskRelationship(
                        source_entity_id=vendor_entity_id,
                        target_entity_id=system_entity.entity_id,
                        relationship_type="HAS_ACCESS_TO",
                        weight=1.0,
                    ))

            certs = await db.execute(
                select(Certification).where(Certification.vendor_id == vendor.vendor_id)
            )
            for cert in certs.scalars().all():
                control_name = f"{cert.certification_type}-{cert.certification_id}"
                ctrl_result = await db.execute(
                    select(RiskEntity).where(
                        RiskEntity.entity_type == "CONTROL",
                        RiskEntity.entity_name == control_name,
                    )
                )
                control_entity = ctrl_result.scalar_one_or_none()
                if not control_entity:
                    control_entity = RiskEntity(
                        entity_type="CONTROL",
                        entity_name=control_name,
                        attributes={
                            "certification_type": cert.certification_type,
                            "issuer": cert.issuer,
                            "issue_date": str(cert.issue_date) if cert.issue_date else None,
                            "expiry_date": str(cert.expiry_date),
                            "status": cert.status,
                        },
                    )
                    db.add(control_entity)
                    await db.flush()

                existing_rel = await db.execute(
                    select(RiskRelationship).where(
                        RiskRelationship.source_entity_id == vendor_entity_id,
                        RiskRelationship.target_entity_id == control_entity.entity_id,
                        RiskRelationship.relationship_type == "AFFECTS",
                    )
                )
                if not existing_rel.scalar_one_or_none():
                    db.add(RiskRelationship(
                        source_entity_id=vendor_entity_id,
                        target_entity_id=control_entity.entity_id,
                        relationship_type="AFFECTS",
                        weight=0.8,
                    ))

            migrated_count += 1
            print(f"  Migrated vendor: {vendor.vendor_name} (entity_id={vendor_entity_id})")

        await db.commit()
        print(f"\nMigration complete. Migrated {migrated_count}/{len(vendors)} vendors.")
        print("Created entities in risk_entities and relationships in risk_relationships.")


if __name__ == "__main__":
    asyncio.run(migrate())
