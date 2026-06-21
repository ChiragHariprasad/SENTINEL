import json

from app.models.contract import Contract
from app.ai.contract_analyzer import analyze_contract_text


async def analyze_contract(contract: Contract) -> dict:
    text = contract.raw_text or ""

    if len(text.strip()) < 50:
        return {
            "error": "Contract text too short for analysis",
            "risk_level": "unknown",
        }

    try:
        analysis = await analyze_contract_text(text)
        return analysis
    except Exception as e:
        return {
            "error": f"Analysis failed: {str(e)}",
            "risk_level": "unknown",
        }
