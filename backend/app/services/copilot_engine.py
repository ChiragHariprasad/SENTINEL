import re
import uuid
from typing import Callable, Awaitable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.models.risk_entity import RiskEntity
from app.models.intelligence import IntelligenceSnapshot, RemediationAction
from app.services.risk_correlation_engine import correlate_entity_risk, get_latest_correlated_risk
from app.services.remediation_engine import generate_remediation
from app.services.scenario_engine import run_scenario
from app.services.intelligence_engine import generate_daily_intelligence, generate_priorities
from app.services.executive_brief_engine import generate_executive_brief


INTENT_PATTERNS: dict[str, list[str]] = {
    "blast_radius": [
        r"blast\s*radius.*?(?:of|for|about)?\s*(.+)",
        r"(?:what|which)\s+.*?impact(?:ed|s)?.*?(?:if|when)\s+(.+?)\s+(?:goes?\s*down|fails?|experiences?\s*outage|offline)",
        r"(?:depend|rely).*?(?:on|upon)\s+(.+)",
    ],
    "risk_explanation": [
        r"why is\s+(.+?)\s+risky",
        r"explain risk.*?(?:of|for|about)\s+(.+)",
        r"what.*?risk.*?(?:of|for|about)\s+(.+)",
        r"why.*?high risk.*?(?:of|for|about)\s+(.+)",
    ],
    "remediation": [
        r"how.*?(?:reduce|fix|mitigate|remediate).*?(?:risk|issue).*?(?:of|for|about|with)?\s*(.+)",
        r"what.*?(?:action|step|remediation).*?(?:for|about|on)\s+(.+)",
        r"how.*?(?:improve|lower).*?(?:score|risk).*?(?:of|for|about)\s+(.+)",
        r"(?:generate|create).*?(?:remediation|action|plan).*?(?:for|about|on)\s+(.+)",
    ],
    "simulation": [
        r"what if\s+(.+?)\s+(?:is\s+)?(?:breached|hacked|compromised|fails?|goes?\s*down)",
        r"simulate\s+(.+?)\s+(?:breach|failure|incident|compromise)",
        r"impact.*?(?:of|from)\s+(.+?)\s+(?:breach|failure|incident)",
        r"run a scenario.*?(?:for|on|about|with)\s+(.+)",
        r"(?:scenario|simulation).*?(?:for|of|about|on)\s+(.+)",
        r"(?:soc2|iso).*?expir.*?(?:for|of|on|about)?\s*(.+)",
    ],
    "prioritization": [
        r"what.*?(?:focus|priority|important|urgent).*(?:today|this week|now|currently)",
        r"what.*?(?:matter|critical|top).*(?:risk|issue)",
        r"(?:top|main|key)\s+(?:risk|priority|action)",
        r"what.*?(?:do|should)\s+(?:i\s+)?(?:focus|do|work on)",
        r"(?:top|financial|critical|high).*?(?:risk|finding|issue|concern)",
    ],
    "executive_summary": [
        r"(?:generate|create|show|get).*(?:board|executive|report|brief|summary)",
        r"(?:board|executive).*(?:report|brief|summary|update)",
        r"what.*?(?:leadership|executive|board).*(?:need|should).*?know",
        r"overview.*?(?:risk|portfolio|status)",
    ],
    "entity_lookup": [
        r"(?:tell|show|find|get|search).*?(?:me\s+)?(?:about|for|details?|info).*\s+(.+)",
        r"who\s+is\s+(.+)",
        r"what\s+is\s+(.+)",
        r"summarize\s+(.+?)\s*(?:findings|audit|info|details)",
        r"what.*?(?:are|is).*?(?:the)?\s*(?:findings|details|audit).*?(?:for|of|about)?\s+(.+)",
    ],
}


async def _detect_intent(question: str) -> tuple[str, str | None]:
    question_lower = question.lower().strip()
    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            match = re.search(pattern, question_lower)
            if match:
                entity_hint = match.group(1).strip() if match.lastindex and match.group(1) else None
                return intent, entity_hint
    return "entity_lookup", question


STOP_WORDS = {"a", "an", "the", "for", "of", "on", "in", "at", "to", "by",
              "with", "about", "if", "is", "are", "was", "were", "be", "been",
              "soc2", "iso", "cert", "contract", "expiry", "expiration", "breach",
              "failure", "compromise", "scenario", "outage", "findings", "audit",
              "info", "details", "remediation", "plan", "financial", "irregularity"}

async def _find_entity(db: AsyncSession, hint: str) -> RiskEntity | None:
    hint = hint.strip().strip("?.,!;:").lower()

    prefixes = ["vendor ", "the ", "if ", "for ", "of ", "about ", "on ",
                "run a scenario ", "run scenario ", "scenario ", "simulate ",
                "simulation ", "generate a ", "generate ", "create "]
    for p in prefixes:
        if hint.startswith(p):
            hint = hint[len(p):].strip()

    suffixes = [" experiences an outage", " goes down", " fails", " is breached",
                " is hacked", " is compromised"]
    for s in suffixes:
        if hint.endswith(s):
            hint = hint[:-len(s)].strip()

    if not hint:
        return None

    words = [w for w in hint.split() if w not in STOP_WORDS]
    if words:
        hint = " ".join(words)

    if not hint:
        return None

    result = await db.execute(
        select(RiskEntity)
        .where(RiskEntity.entity_name.ilike(f"%{hint}%"))
        .order_by(desc(RiskEntity.risk_score))
        .limit(5)
    )
    entities = result.scalars().all()
    return entities[0] if entities else None


async def _handle_risk_explanation(db: AsyncSession, hint: str | None) -> dict:
    if not hint:
        return {"answer": "Which entity would you like me to explain?", "sources": [], "engine": "risk_explanation"}

    entity = await _find_entity(db, hint)
    if not entity:
        return {"answer": f"I couldn't find any entity matching '{hint}'.", "sources": [], "engine": "risk_explanation"}

    corr = await get_latest_correlated_risk(db, entity.entity_id)
    if not corr:
        corr = await correlate_entity_risk(db, entity)

    lines = [f"**{entity.entity_name}** ({entity.entity_type}) has a correlated risk score of **{corr.correlated_risk}**."]
    lines.append(f"Base risk: {corr.base_risk}, contributed by neighbors: {corr.neighbor_risk}")

    reasoning = corr.reasoning or {}
    contributions = reasoning.get("contributions", [])
    if contributions:
        lines.append("\nRisk contributions from connected entities:")
        for c in contributions[:5]:
            lines.append(f"- *{c['entity_name']}* ({c['entity_type']}, risk={c['risk_score']}) via **{c['relationship']}** contributed +{c['contributed_score']}")

    return {
        "answer": "\n".join(lines),
        "sources": [{"entity_id": str(entity.entity_id), "entity_name": entity.entity_name, "entity_type": entity.entity_type}],
        "engine": "risk_explanation",
    }


async def _handle_remediation(db: AsyncSession, hint: str | None) -> dict:
    if not hint:
        open_actions = await db.execute(
            select(RemediationAction).where(RemediationAction.status == "open").limit(10)
        )
        actions = open_actions.scalars().all()
        if actions:
            lines = [f"**{len(actions)} open remediation actions:**"]
            for a in actions:
                lines.append(f"- {a.action} (due: {a.due_date or 'N/A'})")
            return {"answer": "\n".join(lines), "sources": [], "engine": "remediation"}
        return {"answer": "No open remediation actions.", "sources": [], "engine": "remediation"}

    entity = await _find_entity(db, hint)
    if not entity:
        return {"answer": f"I couldn't find any entity matching '{hint}'.", "sources": [], "engine": "remediation"}

    corr = await get_latest_correlated_risk(db, entity.entity_id)
    if corr:
        actions = await generate_remediation(db, entity, corr)
    else:
        actions = await generate_remediation(db, entity)

    if not actions:
        return {"answer": f"No remediation actions available for {entity.entity_name}.", "sources": [], "engine": "remediation"}

    lines = [f"**Remediation plan for {entity.entity_name}:**"]
    for a in actions[:5]:
        lines.append(f"- {a.action}")
    if len(actions) > 5:
        lines.append(f"\n*{len(actions)} total actions generated*")

    return {
        "answer": "\n".join(lines),
        "sources": [{"entity_id": str(entity.entity_id), "entity_name": entity.entity_name, "entity_type": entity.entity_type}],
        "engine": "remediation",
    }


async def _handle_simulation(db: AsyncSession, hint: str | None) -> dict:
    if not hint:
        return {"answer": "Which entity would you like to simulate a breach or failure for?", "sources": [], "engine": "simulation"}

    entity = await _find_entity(db, hint)
    if not entity:
        return {"answer": f"I couldn't find any entity matching '{hint}'.", "sources": [], "engine": "simulation"}

    scenario_type = "BREACH"
    if "fail" in hint.lower():
        scenario_type = "FAILURE"
    elif "expir" in hint.lower() or "contract" in hint.lower():
        if "soc2" in hint.lower() or "social" in hint.lower():
            scenario_type = "SOC2_EXPIRED"
        else:
            scenario_type = "CONTRACT_EXPIRY"
    elif "compromis" in hint.lower() or "identit" in hint.lower():
        scenario_type = "IDENTITY_COMPROMISE"

    try:
        scenario_run = await run_scenario(db, entity.entity_id, scenario_type, commit=True)
    except ValueError as e:
        return {"answer": str(e), "sources": [], "engine": "simulation"}

    r = scenario_run.results
    imp = r.get("impact", {})
    br = r.get("blast_radius", {})

    lines = [f"**Scenario: {r.get('scenario', scenario_type)}** — {entity.entity_name}"]
    lines.append(f"Risk impact: {imp.get('current_risk', 'N/A')} → {imp.get('projected_risk', 'N/A')} (delta: +{imp.get('risk_delta', 'N/A')})")
    lines.append(f"Blast radius: {br.get('total_affected', 0)} total entities affected")
    for key in ["affected_systems", "affected_controls", "affected_users"]:
        if br.get(key, 0) > 0:
            lines.append(f"- {key.replace('_', ' ').title()}: {br[key]}")

    return {
        "answer": "\n".join(lines),
        "sources": [{"entity_id": str(entity.entity_id), "entity_name": entity.entity_name, "entity_type": entity.entity_type}],
        "engine": f"simulation:{scenario_type}",
    }


async def _handle_prioritization(db: AsyncSession, hint: str | None = None) -> dict:
    priorities = await generate_priorities(db)
    content = priorities.content or {}

    lines = [f"**{priorities.title}**"]
    if priorities.summary:
        lines.append(priorities.summary)

    critical = content.get("critical_entities", [])
    if critical:
        lines.append(f"\n**Critical entities ({len(critical)}):**")
        for e in critical[:5]:
            lines.append(f"- {e.get('entity_name', 'Unknown')} ({e.get('entity_type', '')}) — risk: {e.get('risk_score', 'N/A')}")

    actions = content.get("recommended_actions", [])
    if actions:
        lines.append(f"\n**Recommended actions ({len(actions)}):**")
        for a in actions[:5]:
            lines.append(f"- {a.get('action', a) if isinstance(a, dict) else a}")

    return {
        "answer": "\n".join(lines),
        "sources": [{"snapshot_type": "priorities", "title": priorities.title}],
        "engine": "prioritization",
    }


async def _handle_executive_summary(db: AsyncSession, hint: str | None = None) -> dict:
    brief = await generate_executive_brief(db)
    content = brief.content or {}

    lines = [f"## {brief.title}"]
    if content.get("executive_summary"):
        lines.append(f"\n{content['executive_summary']}")

    lines.append(f"\n**Portfolio Risk Score:** {content.get('portfolio_risk_score', 'N/A')}")
    tiers = content.get("risk_tier_distribution", {})
    lines.append(f"Risk tiers — Critical: {tiers.get('CRITICAL', 0)}, High: {tiers.get('HIGH', 0)}, Elevated: {tiers.get('ELEVATED', 0)}")

    top = content.get("top_risks", [])
    if top:
        lines.append(f"\n**Top Risks:**")
        for e in top[:5]:
            lines.append(f"- {e.get('entity_name', 'Unknown')} ({e.get('entity_type', '')}) — {e.get('risk_score', 'N/A')}")

    recs = content.get("recommendations", [])
    if recs:
        lines.append(f"\n**Recommendations:**")
        for r in recs:
            lines.append(f"- {r}")

    anomaly = content.get("anomaly_overview", {})
    lines.append(f"\nAnomalies: {anomaly.get('total_recent', 0)} recent ({anomaly.get('critical', 0)} critical)")

    return {
        "answer": "\n".join(lines),
        "sources": [{"snapshot_type": "executive_brief", "title": brief.title}],
        "engine": "executive_summary",
    }


async def _handle_blast_radius(db: AsyncSession, hint: str | None) -> dict:
    if not hint:
        return {"answer": "Which entity would you like to check the blast radius for?", "sources": [], "engine": "blast_radius"}

    entity = await _find_entity(db, hint)
    if not entity:
        return {"answer": f"I couldn't find any entity matching '{hint}'.", "sources": [], "engine": "blast_radius"}

    from app.services.blast_radius_engine import calculate_blast_radius
    br = await calculate_blast_radius(db, str(entity.entity_id))

    lines = [f"**Blast Radius: {entity.entity_name}**"]
    if br.get("total", 0) > 0:
        lines.append(f"\n{br['total']} entities would be impacted:")
        for key, label in [("vendors", "Vendors"), ("systems", "Systems"), ("controls", "Controls"), ("users", "Users")]:
            count = br.get("impacted_entities", {}).get(key, [])
            if count:
                lines.append(f"- {label}: {len(count)} affected")
        paths = br.get("paths", [])
        if paths:
            lines.append(f"\nDirect dependencies:")
            for p in paths[:5]:
                lines.append(f"- {p.get('entity_name', '?')} ({p.get('relationship', '?')})")
    else:
        lines.append("No dependencies found — blast radius is empty.")

    return {
        "answer": "\n".join(lines),
        "sources": [{"entity_id": str(entity.entity_id), "entity_name": entity.entity_name, "entity_type": entity.entity_type}],
        "engine": "blast_radius",
    }


async def _handle_entity_lookup(db: AsyncSession, hint: str | None) -> dict:
    if not hint:
        return {"answer": "What would you like to know about?", "sources": [], "engine": "entity_lookup"}

    entity = await _find_entity(db, hint)
    if not entity:
        return {"answer": f"I couldn't find any entity matching '{hint}'.", "sources": [], "engine": "entity_lookup"}

    lines = [f"**{entity.entity_name}**", f"Type: {entity.entity_type}", f"Status: {entity.status}", f"Risk Score: {entity.risk_score or 'Not scored'}"]
    if entity.attributes:
        attrs = entity.attributes
        for k, v in list(attrs.items())[:8]:
            lines.append(f"{k}: {v}")

    return {
        "answer": "\n".join(lines),
        "sources": [{"entity_id": str(entity.entity_id), "entity_name": entity.entity_name, "entity_type": entity.entity_type}],
        "engine": "entity_lookup",
    }


_INTENT_HANDLERS: dict[str, Callable] = {
    "blast_radius": _handle_blast_radius,
    "risk_explanation": _handle_risk_explanation,
    "remediation": _handle_remediation,
    "simulation": _handle_simulation,
    "prioritization": _handle_prioritization,
    "executive_summary": _handle_executive_summary,
    "entity_lookup": _handle_entity_lookup,
}


async def copilot_query(db: AsyncSession, question: str) -> dict:
    intent, entity_hint = await _detect_intent(question)
    handler = _INTENT_HANDLERS.get(intent, _handle_entity_lookup)
    result = await handler(db, entity_hint)
    result["intent"] = intent
    result["question"] = question
    return result
