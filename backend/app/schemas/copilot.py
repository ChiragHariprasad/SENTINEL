from pydantic import BaseModel, Field


class CopilotQueryRequest(BaseModel):
    question: str = Field(min_length=1)


class CopilotQueryResponse(BaseModel):
    answer: str
    sources: list[str] = []
