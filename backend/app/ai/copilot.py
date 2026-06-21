import json
import re as re_module

from app.core.config import settings


INTENT_PATTERNS = [
    {
        "intent": "vendor_by_data_access",
        "patterns": ["access", "pii", "data", "financial", "phi", "pci"],
        "sql_template": (
            "SELECT v.vendor_name, v.vendor_type, vda.data_type, vda.access_level "
            "FROM vendors v JOIN vendor_data_access vda ON v.vendor_id = vda.vendor_id "
            "WHERE vda.is_active = true AND v.is_archived = false AND "
            "vda.data_type ILIKE '%{keyword}%' ORDER BY v.vendor_name"
        ),
    },
    {
        "intent": "vendor_by_risk_tier",
        "patterns": ["critical", "red", "high risk", "risk tier"],
        "sql_template": (
            "SELECT v.vendor_name, v.vendor_type, v.risk_tier, rs.overall_score "
            "FROM vendors v JOIN risk_scores rs ON v.vendor_id = rs.vendor_id "
            "WHERE v.risk_tier = '{tier}' AND v.is_archived = false "
            "ORDER BY rs.overall_score DESC"
        ),
    },
    {
        "intent": "vendor_by_expired_cert",
        "patterns": ["expired", "expiring", "certification", "cert"],
        "sql_template": (
            "SELECT v.vendor_name, c.certification_type, c.expiry_date "
            "FROM certifications c JOIN vendors v ON c.vendor_id = v.vendor_id "
            "WHERE c.expiry_date < CURRENT_DATE AND c.status = 'active' AND v.is_archived = false "
            "ORDER BY c.expiry_date"
        ),
    },
    {
        "intent": "vendor_by_breach",
        "patterns": ["breach", "breached", "incident"],
        "sql_template": (
            "SELECT v.vendor_name, a.anomaly_type, a.severity, a.explanation "
            "FROM anomaly_events a JOIN vendors v ON a.vendor_id = v.vendor_id "
            "WHERE a.anomaly_type LIKE '%BREACH%' AND v.is_archived = false "
            "ORDER BY a.detected_at DESC"
        ),
    },
    {
        "intent": "vendor_count_by_type",
        "patterns": ["how many", "count", "number of"],
        "sql_template": (
            "SELECT v.vendor_type, COUNT(*) as count "
            "FROM vendors v WHERE v.is_archived = false "
            "GROUP BY v.vendor_type ORDER BY count DESC"
        ),
    },
    {
        "intent": "all_vendors",
        "patterns": ["all vendors", "show vendors", "list vendors"],
        "sql_template": (
            "SELECT v.vendor_name, v.vendor_type, v.risk_tier, v.contract_status "
            "FROM vendors v WHERE v.is_archived = false ORDER BY v.vendor_name"
        ),
    },
]


async def generate_sql(question: str) -> str:
    q = question.lower()

    for intent in INTENT_PATTERNS:
        if any(p in q for p in intent["patterns"]):
            sql = intent["sql_template"]

            # Extract keyword for data access
            if "{keyword}" in sql:
                for kw in ["pii", "pci", "phi", "financial", "confidential"]:
                    if kw in q:
                        sql = sql.replace("{keyword}", kw.upper())
                        break
                else:
                    sql = sql.replace("{keyword}", "PII")

            # Extract tier
            if "{tier}" in sql:
                if "critical" in q or "red" in q:
                    sql = sql.replace("{tier}", "RED")
                elif "yellow" in q:
                    sql = sql.replace("{tier}", "YELLOW")
                elif "green" in q:
                    sql = sql.replace("{tier}", "GREEN")
                else:
                    sql = sql.replace("{tier}", "RED")

            return sql

    # Fallback: general vendor query
    return "SELECT vendor_name, vendor_type, risk_tier FROM vendors WHERE is_archived = false ORDER BY vendor_name LIMIT 20"


async def format_response(question: str, data: list[dict], columns: list[str]) -> str:
    if not data:
        return "I couldn't find any results matching your question."

    if not settings.LLM_API_KEY:
        return format_fallback_response(question, data)

    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.LLM_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.LLM_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.LLM_MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a vendor risk analyst assistant. Format the data as a clear, concise answer.",
                        },
                        {
                            "role": "user",
                            "content": f"Question: {question}\n\nData: {json.dumps(data[:10])}\n\nProvide a natural answer.",
                        },
                    ],
                    "temperature": 0.3,
                    "max_tokens": 500,
                },
                timeout=10.0,
            )
            result = response.json()
            return result["choices"][0]["message"]["content"]
    except Exception:
        return format_fallback_response(question, data)


def format_fallback_response(question: str, data: list[dict]) -> str:
    lines = [f"Here are the results for your query about '{question}':"]
    for i, item in enumerate(data[:10], 1):
        parts = [f"{k}: {v}" for k, v in item.items() if v is not None]
        lines.append(f"  {i}. {' | '.join(parts)}")

    if len(data) > 10:
        lines.append(f"  ... and {len(data) - 10} more results.")

    return "\n".join(lines)
