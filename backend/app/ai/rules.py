from app.models.vendor import Vendor

ANOMALY_RULES = [
    {
        "name": "BREACHED_VENDOR_HIGH_ACCESS",
        "severity": "CRITICAL",
        "description": "Vendor has experienced a breach and has access to sensitive data",
        "check": lambda v, ctx: (
            ctx.get("recent_breach") and
            any(dt in ("PII", "PCI", "PHI", "FINANCIAL") for dt in ctx.get("has_data_access", {}))
        ),
        "explanation": lambda v, ctx: (
            f"{v.vendor_name} has been breached and has access to sensitive data types: "
            f"{', '.join(k for k in ctx.get('has_data_access', {}) if k in ('PII','PCI','PHI','FINANCIAL'))}"
        ),
    },
    {
        "name": "VENDOR_UNDER_INVESTIGATION",
        "severity": "HIGH",
        "description": "Vendor is currently under investigation",
        "check": lambda v, ctx: ctx.get("under_investigation", False),
        "explanation": lambda v, ctx: f"{v.vendor_name} is currently under investigation",
    },
    {
        "name": "HIGH_RISK_SCORE",
        "severity": "HIGH",
        "description": "Vendor has a high risk score",
        "check": lambda v, ctx: ctx.get("risk_score", 0) > 80,
        "explanation": lambda v, ctx: (
            f"{v.vendor_name} has a risk score of {ctx.get('risk_score', 0)}, "
            f"exceeding the HIGH threshold of 80"
        ),
    },
    {
        "name": "EXPIRED_CERTIFICATION",
        "severity": "HIGH",
        "description": "Vendor has expired certifications",
        "check": lambda v, ctx: ctx.get("has_expired_cert", False),
        "explanation": lambda v, ctx: (
            f"{v.vendor_name} has expired certifications: "
            f"{', '.join(ctx.get('expired_certs', []))}"
        ),
    },
    {
        "name": "RECENTLY_BREACHED_VENDOR",
        "severity": "HIGH",
        "description": "Vendor has experienced a recent breach",
        "check": lambda v, ctx: ctx.get("recent_breach", False),
        "explanation": lambda v, ctx: (
            f"{v.vendor_name} has {ctx.get('breach_count', 0)} breach(s) detected"
        ),
    },
    {
        "name": "CONTRACT_EXPIRED_ACTIVE_ACCESS",
        "severity": "MEDIUM",
        "description": "Vendor's contract has expired but access is still active",
        "check": lambda v, ctx: (
            ctx.get("contract_expired", False) and
            ctx.get("has_active_access", False)
        ),
        "explanation": lambda v, ctx: (
            f"{v.vendor_name}'s contract has expired but they still have active system access"
        ),
    },
    {
        "name": "ELEVATED_RISK_VENDOR",
        "severity": "MEDIUM",
        "description": "Vendor has elevated risk indicators",
        "check": lambda v, ctx: (
            60 < ctx.get("risk_score", 0) <= 80
        ),
        "explanation": lambda v, ctx: (
            f"{v.vendor_name} has a risk score of {ctx.get('risk_score', 0)}, "
            f"indicating elevated risk"
        ),
    },
]


def evaluate_rule(rule: dict, vendor: Vendor, context: dict) -> dict | None:
    try:
        if rule["check"](vendor, context):
            return {
                "label": rule["name"],
                "severity": rule["severity"],
                "confidence": 0.95,
                "explanation": rule["explanation"](vendor, context),
            }
    except Exception:
        return None

    return None
