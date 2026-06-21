from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.common import StandardResponse
from app.services.ingestion_service import ingest_csv, ingest_json, ingest_manual_entity
from app.services.normalization_service import normalize_all
from pydantic import BaseModel

router = APIRouter(prefix="/ingestion", tags=["Ingestion v2"])


class JsonIngestRequest(BaseModel):
    data: dict | list
    source: str = "api"


class ManualEntityRequest(BaseModel):
    entity_type: str
    entity_name: str
    attributes: dict | None = None


@router.post("/csv")
async def api_ingest_csv(
    file: UploadFile = File(...),
    csv_type: str = Form("vendor"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await ingest_csv(db, file.file, file.filename or "upload.csv", csv_type)
    return StandardResponse(data=result)


@router.post("/json")
async def api_ingest_json(
    body: JsonIngestRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await ingest_json(db, body.data, source=body.source)
    return StandardResponse(data=result)


@router.post("/manual")
async def api_ingest_manual(
    body: ManualEntityRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entity = await ingest_manual_entity(db, body.entity_type, body.entity_name, body.attributes)
    return StandardResponse(data={
        "entity_id": str(entity.entity_id),
        "entity_type": entity.entity_type,
        "entity_name": entity.entity_name,
        "status": entity.status,
    })


@router.post("/normalize")
async def api_normalize_all(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    results = await normalize_all(db)
    return StandardResponse(data={"results": results})
