from pydantic import BaseModel


class GraphNode(BaseModel):
    id: str
    label: str
    type: str
    risk_score: float | None = None
    status: str | None = None


class GraphEdge(BaseModel):
    source: str
    target: str
    relationship: str
    weight: float


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class ImpactPathNode(BaseModel):
    entity_id: str
    entity_name: str
    entity_type: str
    risk_score: float | None
    relationship_type: str | None
    relationship_weight: float | None


class ImpactPathResponse(BaseModel):
    path: list[ImpactPathNode]
