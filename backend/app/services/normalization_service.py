from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.raw_data import RawVendor, RawIdentityEvent, RawConfigDrift, RawException
from app.models.risk_entity import RiskEntity


async def normalize_raw_vendors(db: AsyncSession) -> dict:
    result = await db.execute(select(RawVendor).order_by(RawVendor.ingested_at))
    raw_records = result.scalars().all()

    created = 0
    skipped = 0
    for raw in raw_records:
        data = raw.raw_data
        name = data.get("vendor_name") or data.get("name") or f"Raw-Vendor-{raw.id}"
        name = name.strip()
        if not name:
            skipped += 1
            continue

        existing = await db.execute(
            select(RiskEntity).where(
                RiskEntity.entity_type == "VENDOR",
                RiskEntity.entity_name == name,
            )
        )
        if existing.scalar_one_or_none():
            skipped += 1
            continue

        entity = RiskEntity(
            entity_type="VENDOR",
            entity_name=name,
            external_id=data.get("vendor_id"),
            attributes={k: v for k, v in data.items() if k not in ("vendor_name", "name", "vendor_id")},
        )
        db.add(entity)
        created += 1

    await db.flush()
    return {"type": "vendor", "processed": len(raw_records), "created": created, "skipped": skipped}


async def normalize_raw_identities(db: AsyncSession) -> dict:
    result = await db.execute(select(RawIdentityEvent).order_by(RawIdentityEvent.ingested_at))
    raw_records = result.scalars().all()

    created = 0
    skipped = 0
    for raw in raw_records:
        data = raw.raw_data
        name = data.get("user_name") or data.get("email") or data.get("name") or f"Raw-Identity-{raw.id}"
        name = name.strip()
        if not name:
            skipped += 1
            continue

        existing = await db.execute(
            select(RiskEntity).where(
                RiskEntity.entity_type == "USER",
                RiskEntity.entity_name == name,
            )
        )
        if existing.scalar_one_or_none():
            skipped += 1
            continue

        entity = RiskEntity(
            entity_type="USER",
            entity_name=name,
            attributes={k: v for k, v in data.items() if k not in ("user_name", "email", "name")},
        )
        db.add(entity)
        created += 1

    await db.flush()
    return {"type": "identity", "processed": len(raw_records), "created": created, "skipped": skipped}


async def normalize_raw_configs(db: AsyncSession) -> dict:
    result = await db.execute(select(RawConfigDrift).order_by(RawConfigDrift.ingested_at))
    raw_records = result.scalars().all()

    created = 0
    skipped = 0
    for raw in raw_records:
        data = raw.raw_data
        name = data.get("resource_name") or data.get("system_name") or f"Raw-Config-{raw.id}"
        name = name.strip()
        if not name:
            skipped += 1
            continue

        existing = await db.execute(
            select(RiskEntity).where(
                RiskEntity.entity_type == "CONFIG",
                RiskEntity.entity_name == name,
            )
        )
        if existing.scalar_one_or_none():
            skipped += 1
            continue

        entity = RiskEntity(
            entity_type="CONFIG",
            entity_name=name,
            attributes={k: v for k, v in data.items() if k not in ("resource_name", "system_name")},
        )
        db.add(entity)
        created += 1

    await db.flush()
    return {"type": "config", "processed": len(raw_records), "created": created, "skipped": skipped}


async def normalize_all(db: AsyncSession) -> list[dict]:
    results = []
    results.append(await normalize_raw_vendors(db))
    results.append(await normalize_raw_identities(db))
    results.append(await normalize_raw_configs(db))
    await db.commit()
    return results
