from app.api.v2 import v2_router
from app.api.v2.entities import router as entities_router
from app.api.v2.graph import router as graph_router
from app.api.v2.risk import router as risk_router
from app.api.v2.correlation import router as correlation_router
from app.api.v2.anomalies import router as anomalies_router
from app.api.v2.blast_radius import router as blast_radius_router
from app.api.v2.intelligence import router as intelligence_router
from app.api.v2.remediation import router as remediation_router
from app.api.v2.timeline import router as timeline_router
from app.api.v2.pipeline import router as pipeline_router
from app.api.v2.scenario import router as scenario_router
from app.api.v2.ingestion import router as ingestion_router
from app.api.v2.documents import router as documents_router
from app.api.v2.copilot import router as copilot_router

v2_router.include_router(entities_router)
v2_router.include_router(graph_router)
v2_router.include_router(risk_router)
v2_router.include_router(correlation_router)
v2_router.include_router(anomalies_router)
v2_router.include_router(blast_radius_router)
v2_router.include_router(intelligence_router)
v2_router.include_router(remediation_router)
v2_router.include_router(timeline_router)
v2_router.include_router(pipeline_router)
v2_router.include_router(scenario_router)
v2_router.include_router(ingestion_router)
v2_router.include_router(documents_router)
v2_router.include_router(copilot_router)
