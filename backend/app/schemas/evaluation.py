from pydantic import BaseModel


class SeverityMetrics(BaseModel):
    precision: float
    recall: float
    f1_score: float


class LabelMetrics(BaseModel):
    precision: float
    recall: float
    f1_score: float


class EvaluationMetricsResponse(BaseModel):
    overall: dict
    by_severity: dict[str, SeverityMetrics]
    by_label: dict[str, LabelMetrics]
    confusion_matrix: dict
    computed_at: str
