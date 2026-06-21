from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_vendors: int
    critical_vendors: int
    high_risk_vendors: int
    expiring_certifications: int
    open_alerts: int
    total_anomalies: int
    risk_distribution: dict
    evaluation_summary: dict | None
