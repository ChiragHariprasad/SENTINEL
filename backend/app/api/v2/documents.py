import uuid

from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.raw_data import RawDocument
from app.schemas.common import StandardResponse
from app.core.storage import store_file
from app.services.document_intelligence_engine import (
    analyze_document,
    get_document_findings,
    build_graph_from_document,
    extract_text_from_pdf,
    classify_document,
)
from pydantic import BaseModel

router = APIRouter(prefix="/documents", tags=["Document Intelligence v2"])


class AnalyzeRequest(BaseModel):
    document_type: str | None = None


class GraphBuildRequest(BaseModel):
    pass


@router.post("/upload")
async def api_upload_document(
    file: UploadFile = File(...),
    document_type: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    file_data = await file.read()
    storage_path = await store_file(file_data, file.filename or "document.pdf", subdir="documents")

    text = await extract_text_from_pdf(file_data)

    if not document_type:
        document_type = await classify_document(text)

    doc = RawDocument(
        source_file=file.filename or "document.pdf",
        document_type=document_type,
        raw_text=text,
        storage_path=storage_path,
        attributes={"original_name": file.filename, "size": len(file_data)},
    )
    db.add(doc)
    await db.flush()
    await db.commit()

    return StandardResponse(data={
        "document_id": str(doc.id),
        "file_name": doc.source_file,
        "document_type": doc.document_type,
        "storage_path": storage_path,
        "text_length": len(text),
    })


@router.post("/analyze")
async def api_analyze_document(
    document_id: str = Form(...),
    document_type: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await analyze_document(db, uuid.UUID(document_id), document_type)
    return StandardResponse(data=result)


@router.get("/findings")
async def api_get_findings(
    document_id: str,
    finding_type: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    findings = await get_document_findings(db, uuid.UUID(document_id), finding_type)
    return StandardResponse(data={"document_id": document_id, "findings": findings, "total": len(findings)})


@router.post("/build-graph")
async def api_build_graph(
    document_id: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await build_graph_from_document(db, uuid.UUID(document_id))
    return StandardResponse(data=result)
