import uuid
from datetime import datetime

from pydantic import BaseModel


class ImportResponse(BaseModel):
    job_id: uuid.UUID
    status: str


class ImportStatusResponse(BaseModel):
    job_id: uuid.UUID
    processed: int
    failed: int
    status: str

    class Config:
        from_attributes = True
