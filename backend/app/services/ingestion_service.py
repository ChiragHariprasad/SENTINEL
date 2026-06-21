import csv
import io
import json
import uuid
from datetime import datetime, timezone
from typing import BinaryIO

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.raw_data import RawVendor, RawIdentityEvent, RawConfigDrift, RawException, RawDocument
from app.models.risk_entity import RiskEntity
from app.core.storage import store_file


SUPPORTED_CSV_TYPES = {
    "vendor": RawVendor,
    "identity": RawIdentityEvent,
    "config": RawConfigDrift,
    "exception": RawException,
}


async def ingest_csv(
    db: AsyncSession,
    file: BinaryIO,
    file_name: str,
    csv_type: str,
) -> dict:
    raw_model = SUPPORTED_CSV_TYPES.get(csv_type)
    if not raw_model:
        raise ValueError(f"Unsupported CSV type: {csv_type}. Supported: {list(SUPPORTED_CSV_TYPES.keys())}")

    content = file.read()
    if isinstance(content, bytes):
        content = content.decode("utf-8")

    file_path = await store_file(content.encode(), file_name, subdir="csv")

    reader = csv.DictReader(io.StringIO(content))
    rows = list(reader)

    created_count = 0
    entity_ids = []

    for idx, row in enumerate(rows):
        record = raw_model(
            source_file=file_name,
            row_index=idx,
            raw_data=row,
        )
        db.add(record)
        await db.flush()
        created_count += 1

        entity = await _normalize_csv_row(csv_type, row, idx)
        if entity:
            existing = await db.execute(
                select(RiskEntity).where(
                    RiskEntity.entity_type == entity.entity_type,
                    RiskEntity.entity_name == entity.entity_name,
                )
            )
            if not existing.scalar_one_or_none():
                db.add(entity)
                await db.flush()
                entity_ids.append(str(entity.entity_id))

    await db.commit()

    return {
        "file_name": file_name,
        "csv_type": csv_type,
        "total_rows": len(rows),
        "records_created": created_count,
        "entities_created": len(entity_ids),
        "entity_ids": entity_ids,
        "storage_path": file_path,
    }


async def _normalize_csv_row(csv_type: str, row: dict, idx: int) -> RiskEntity | None:
    if csv_type == "vendor":
        name = row.get("vendor_name") or row.get("name") or f"Imported-Vendor-{idx}"
        return RiskEntity(
            entity_type="VENDOR",
            entity_name=name.strip(),
            external_id=row.get("vendor_id"),
            attributes={k: v for k, v in row.items() if v and k not in ("vendor_name", "name", "vendor_id")},
        )

    elif csv_type == "identity":
        name = row.get("user_name") or row.get("email") or row.get("name") or f"Imported-User-{idx}"
        return RiskEntity(
            entity_type="USER",
            entity_name=name.strip(),
            attributes={k: v for k, v in row.items() if v and k not in ("user_name", "email", "name")},
        )

    elif csv_type == "config":
        name = row.get("resource_name") or row.get("system_name") or f"Imported-Config-{idx}"
        return RiskEntity(
            entity_type="CONFIG",
            entity_name=name.strip(),
            attributes={k: v for k, v in row.items() if v and k not in ("resource_name", "system_name")},
        )

    elif csv_type == "exception":
        name = row.get("exception_name") or row.get("policy") or f"Imported-Exception-{idx}"
        return RiskEntity(
            entity_type="EXCEPTION",
            entity_name=name.strip(),
            attributes={k: v for k, v in row.items() if v and k not in ("exception_name", "policy")},
        )

    return None


async def ingest_json(
    db: AsyncSession,
    data: dict | list,
    source: str = "api",
) -> dict:
    items = data if isinstance(data, list) else [data]
    created_count = 0
    entity_ids = []

    for item in items:
        entity_type = (item.get("entity_type") or item.get("type") or "VENDOR").upper()
        entity_name = item.get("entity_name") or item.get("name") or f"API-Import-{uuid.uuid4().hex[:8]}"

        existing = await db.execute(
            select(RiskEntity).where(
                RiskEntity.entity_type == entity_type,
                RiskEntity.entity_name == entity_name,
            )
        )
        if existing.scalar_one_or_none():
            continue

        entity = RiskEntity(
            entity_type=entity_type,
            entity_name=entity_name,
            external_id=item.get("external_id"),
            status=item.get("status", "active"),
            attributes={k: v for k, v in item.items() if k not in ("entity_type", "type", "entity_name", "name", "external_id", "status")},
        )
        db.add(entity)
        await db.flush()
        created_count += 1
        entity_ids.append(str(entity.entity_id))

    await db.commit()

    return {
        "source": source,
        "items_processed": len(items),
        "entities_created": created_count,
        "entity_ids": entity_ids,
    }


async def ingest_manual_entity(
    db: AsyncSession,
    entity_type: str,
    entity_name: str,
    attributes: dict | None = None,
) -> RiskEntity:
    existing = await db.execute(
        select(RiskEntity).where(
            RiskEntity.entity_type == entity_type.upper(),
            RiskEntity.entity_name == entity_name,
        )
    )
    if existing.scalar_one_or_none():
        raise ValueError(f"Entity '{entity_name}' of type '{entity_type}' already exists")

    entity = RiskEntity(
        entity_type=entity_type.upper(),
        entity_name=entity_name,
        attributes=attributes or {},
    )
    db.add(entity)
    await db.flush()
    await db.commit()
    return entity
