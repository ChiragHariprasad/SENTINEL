from pydantic import BaseModel
from datetime import datetime, timezone


class StandardResponse(BaseModel):
    success: bool = True
    data: dict | list | None = None
    message: str = "Operation completed"
    timestamp: str = datetime.now(timezone.utc).isoformat()


class ErrorResponse(BaseModel):
    success: bool = False
    error: dict | None = None
