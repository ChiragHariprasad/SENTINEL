import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.contract import Contract
from app.schemas.contract import ContractUploadResponse, ContractAnalysisResponse
from app.schemas.common import StandardResponse
from app.core.exceptions import NotFoundError, ValidationError
from app.services.contract_service import analyze_contract

router = APIRouter(prefix="/contracts", tags=["Contracts"])


@router.post("/upload")
async def upload_contract(
    file: UploadFile = File(...),
    vendor_id: uuid.UUID = Form(...),
    contract_name: str | None = Form(None),
    contract_type: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.filename or not (file.filename.endswith(".pdf") or file.filename.endswith(".txt")):
        raise ValidationError("Only PDF and TXT files are supported")

    content = await file.read()
    text_content = content.decode("utf-8", errors="ignore") if file.filename.endswith(".txt") else ""

    contract = Contract(
        vendor_id=vendor_id,
        contract_name=contract_name or file.filename,
        contract_type=contract_type,
        status="uploaded",
        raw_text=text_content,
    )
    db.add(contract)
    await db.flush()

    return StandardResponse(data={
        "contract_id": str(contract.contract_id),
        "status": "uploaded",
    })


@router.post("/{contract_id}/analyze")
async def analyze_contract_endpoint(contract_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Contract).where(Contract.contract_id == contract_id))
    contract = result.scalar_one_or_none()
    if not contract:
        raise NotFoundError("Contract", str(contract_id))

    analysis = await analyze_contract(contract)
    contract.ai_analysis = analysis
    contract.status = "analyzed"
    await db.flush()

    return StandardResponse(data={"contract_id": str(contract_id), "status": "analyzed", "analysis": analysis})


@router.get("/{contract_id}")
async def get_contract(contract_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Contract).where(Contract.contract_id == contract_id))
    contract = result.scalar_one_or_none()
    if not contract:
        raise NotFoundError("Contract", str(contract_id))
    return StandardResponse(data=ContractAnalysisResponse.model_validate(contract).model_dump())


@router.get("/{contract_id}/analysis")
async def get_contract_analysis(contract_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Contract).where(Contract.contract_id == contract_id))
    contract = result.scalar_one_or_none()
    if not contract:
        raise NotFoundError("Contract", str(contract_id))

    return StandardResponse(data={
        "contract_id": str(contract.contract_id),
        "analysis": contract.ai_analysis,
        "status": contract.status,
    })
