from datetime import date, datetime, timezone

VENDOR_RULES = [
    {
        "name": "EXPIRED_CERTIFICATION",
        "domain": "vendor",
        "severity": "HIGH",
        "condition": lambda ctx: ctx.get("expired_cert_count", 0) > 0,
        "explanation": lambda ctx: f"{ctx.get('expired_cert_count', 0)} certification(s) expired",
    },
    {
        "name": "HIGH_RISK_SCORE",
        "domain": "vendor",
        "severity": "HIGH",
        "condition": lambda ctx: (ctx.get("risk_score") or 0) > 80,
        "explanation": lambda ctx: f"Overall risk score is {ctx.get('risk_score')}",
    },
    {
        "name": "UNDER_INVESTIGATION",
        "domain": "vendor",
        "severity": "HIGH",
        "condition": lambda ctx: ctx.get("under_investigation", False),
        "explanation": lambda ctx: "Vendor is under investigation",
    },
    {
        "name": "CONTRACT_EXPIRED",
        "domain": "vendor",
        "severity": "MEDIUM",
        "condition": lambda ctx: ctx.get("contract_status") == "expired",
        "explanation": lambda ctx: "Contract has expired",
    },
    {
        "name": "BREACHED_VENDOR",
        "domain": "vendor",
        "severity": "CRITICAL",
        "condition": lambda ctx: ctx.get("breach_count", 0) > 0,
        "explanation": lambda ctx: f"{ctx.get('breach_count')} breach(es) detected",
    },
    {
        "name": "ELEVATED_RISK",
        "domain": "vendor",
        "severity": "MEDIUM",
        "condition": lambda ctx: 61 <= (ctx.get("risk_score") or 0) <= 80,
        "explanation": lambda ctx: f"Risk score is elevated at {ctx.get('risk_score')}",
    },
]

IDENTITY_RULES = [
    {
        "name": "AFTER_HOURS_ACCESS",
        "domain": "identity",
        "severity": "MEDIUM",
        "condition": lambda ctx: ctx.get("after_hours_access", False),
        "explanation": lambda ctx: "Access detected outside business hours",
    },
    {
        "name": "EXCESSIVE_FAILURES",
        "domain": "identity",
        "severity": "HIGH",
        "condition": lambda ctx: (ctx.get("login_failures") or 0) > 5,
        "explanation": lambda ctx: f"{ctx.get('login_failures')} login failures recorded",
    },
    {
        "name": "PRIVILEGE_ESCALATION",
        "domain": "identity",
        "severity": "CRITICAL",
        "condition": lambda ctx: ctx.get("privilege_escalation", False),
        "explanation": lambda ctx: "Privilege escalation detected",
    },
    {
        "name": "STALE_ACCOUNT",
        "domain": "identity",
        "severity": "MEDIUM",
        "condition": lambda ctx: ctx.get("days_since_login") and ctx["days_since_login"] > 90,
        "explanation": lambda ctx: f"No login for {ctx.get('days_since_login')} days",
    },
]

CONFIG_RULES = [
    {
        "name": "ENCRYPTION_DISABLED",
        "domain": "config",
        "severity": "CRITICAL",
        "condition": lambda ctx: not ctx.get("encryption_enabled", True),
        "explanation": lambda ctx: "Encryption is disabled",
    },
    {
        "name": "LOGGING_DISABLED",
        "domain": "config",
        "severity": "HIGH",
        "condition": lambda ctx: not ctx.get("logging_enabled", True),
        "explanation": lambda ctx: "Audit logging is disabled",
    },
    {
        "name": "COMPLIANCE_DRIFT",
        "domain": "config",
        "severity": "HIGH",
        "condition": lambda ctx: ctx.get("compliance_drift", False),
        "explanation": lambda ctx: "Configuration has drifted from compliance baseline",
    },
    {
        "name": "PUBLIC_ACCESS",
        "domain": "config",
        "severity": "CRITICAL",
        "condition": lambda ctx: ctx.get("public_access", False),
        "explanation": lambda ctx: "Resource has public access enabled",
    },
]

ALL_RULES = {
    "vendor": VENDOR_RULES,
    "identity": IDENTITY_RULES,
    "config": CONFIG_RULES,
}


def evaluate_rules_for_entity(entity_type: str, context: dict) -> list[dict]:
    domain_map = {
        "VENDOR": "vendor", "USER": "identity",
        "SYSTEM": "config", "CONFIG": "config",
        "CONTROL": "vendor", "EVIDENCE": "vendor",
        "EXCEPTION": "vendor", "DOCUMENT": "vendor",
    }
    domain = domain_map.get(entity_type.upper(), "vendor")
    rules = ALL_RULES.get(domain, VENDOR_RULES)

    results = []
    for rule in rules:
        try:
            if rule["condition"](context):
                results.append({
                    "anomaly_type": rule["name"],
                    "domain": domain,
                    "severity": rule["severity"],
                    "confidence_score": 0.9 if rule["severity"] in ("CRITICAL", "HIGH") else 0.7,
                    "explanation": rule["explanation"](context),
                })
        except Exception:
            pass
    return results
