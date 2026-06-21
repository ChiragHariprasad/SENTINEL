import json

from app.core.config import settings


async def analyze_contract_text(text: str) -> dict:
    if not settings.LLM_API_KEY:
        return mock_analysis(text)

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
                            "content": (
                                "You are a contract analyst. Extract structured data from contracts. "
                                "Return ONLY valid JSON with no additional text."
                            ),
                        },
                        {
                            "role": "user",
                            "content": f"Extract from this contract:\n\n{text[:8000]}\n\n"
                            "Return JSON: {breach_notification_days, data_owner, sla_uptime, "
                            "liability_cap, retention_period_days, has_gdpr_clause, "
                            "risk_level, key_obligations}",
                        },
                    ],
                    "temperature": 0.1,
                    "max_tokens": 1000,
                },
                timeout=15.0,
            )
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            return json.loads(content)
    except Exception:
        return mock_analysis(text)


def mock_analysis(text: str) -> dict:
    return {
        "breach_notification_days": 30,
        "data_owner": "shared",
        "sla_uptime": "99.9%",
        "liability_cap": "$1,000,000",
        "retention_period_days": 365,
        "has_gdpr_clause": "gdpr" in text.lower(),
        "risk_level": "medium",
        "key_obligations": [
            "Maintain SOC 2 certification",
            "Notify within 72 hours of breach",
            "Annual security assessment",
        ],
    }
