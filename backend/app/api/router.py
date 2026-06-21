from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.vendors import router as vendors_router
from app.api.imports import router as imports_router
from app.api.risk import router as risk_router
from app.api.anomalies import router as anomalies_router
from app.api.evaluation import router as evaluation_router
from app.api.certifications import router as certifications_router
from app.api.alerts import router as alerts_router
from app.api.contracts import router as contracts_router
from app.api.copilot import router as copilot_router
from app.api.reports import router as reports_router
from app.api.dashboard import router as dashboard_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(vendors_router)
api_router.include_router(imports_router)
api_router.include_router(risk_router)
api_router.include_router(anomalies_router)
api_router.include_router(evaluation_router)
api_router.include_router(certifications_router)
api_router.include_router(alerts_router)
api_router.include_router(contracts_router)
api_router.include_router(copilot_router)
api_router.include_router(reports_router)
api_router.include_router(dashboard_router)
