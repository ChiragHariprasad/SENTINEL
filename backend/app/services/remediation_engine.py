from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.risk_entity import RiskEntity
from app.models.intelligence import RemediationAction


REMEDIATION_TEMPLATES = {
    "BREACHED_VENDOR": {
        "actions": [
            "Request Incident Report from vendor",
            "Restrict vendor access to critical systems",
            "Conduct vendor security review",
            "Escalate to Security Team",
        ],
        "owner": "Security Team",
        "priority": "CRITICAL",
        "due_days": 7,
    },
    "EXPIRED_CERTIFICATION": {
        "actions": [
            "Request updated certification certificate from vendor",
            "Create compliance review task",
            "Notify vendor owner of expiry",
            "Schedule recertification assessment",
        ],
        "owner": "Compliance Team",
        "priority": "HIGH",
        "due_days": 30,
    },
    "HIGH_RISK_SCORE": {
        "actions": [
            "Conduct detailed risk assessment",
            "Review vendor security posture",
            "Identify risk reduction opportunities",
            "Update risk mitigation plan",
        ],
        "owner": "Risk Team",
        "priority": "HIGH",
        "due_days": 14,
    },
    "UNDER_INVESTIGATION": {
        "actions": [
            "Monitor investigation progress",
            "Prepare containment plan",
            "Notify stakeholders",
            "Document findings",
        ],
        "owner": "Security Team",
        "priority": "CRITICAL",
        "due_days": 5,
    },
    "CONTRACT_EXPIRED": {
        "actions": [
            "Initiate contract renewal process",
            "Review contract terms and conditions",
            "Negotiate updated agreement",
            "Update vendor registry status",
        ],
        "owner": "Procurement Team",
        "priority": "HIGH",
        "due_days": 45,
    },
    "ELEVATED_RISK": {
        "actions": [
            "Review risk score drivers",
            "Schedule vendor risk review",
            "Implement risk monitoring",
            "Update risk register",
        ],
        "owner": "Risk Team",
        "priority": "MEDIUM",
        "due_days": 30,
    },
    "AFTER_HOURS_ACCESS": {
        "actions": [
            "Verify access was authorized",
            "Review access patterns",
            "Enable access alerts",
            "Update access policy if needed",
        ],
        "owner": "IT Security",
        "priority": "MEDIUM",
        "due_days": 3,
    },
    "EXCESSIVE_FAILURES": {
        "actions": [
            "Review authentication logs",
            "Reset user credentials",
            "Enable multi-factor authentication",
            "Investigate potential brute force",
        ],
        "owner": "IT Security",
        "priority": "HIGH",
        "due_days": 1,
    },
    "PRIVILEGE_ESCALATION": {
        "actions": [
            "Immediately revoke escalated privileges",
            "Investigate root cause",
            "Review access control policies",
            "Conduct security incident review",
        ],
        "owner": "Security Team",
        "priority": "CRITICAL",
        "due_days": 1,
    },
    "STALE_ACCOUNT": {
        "actions": [
            "Verify if account is still needed",
            "Disable stale account",
            "Notify account owner",
            "Review account lifecycle policy",
        ],
        "owner": "IT Operations",
        "priority": "MEDIUM",
        "due_days": 7,
    },
    "ENCRYPTION_DISABLED": {
        "actions": [
            "Enable encryption immediately",
            "Verify data at rest encryption",
            "Verify data in transit encryption",
            "Audit configuration change history",
        ],
        "owner": "Infrastructure Team",
        "priority": "CRITICAL",
        "due_days": 1,
    },
    "LOGGING_DISABLED": {
        "actions": [
            "Re-enable audit logging",
            "Verify log integrity",
            "Review log retention policy",
            "Check for log gaps",
        ],
        "owner": "Infrastructure Team",
        "priority": "HIGH",
        "due_days": 2,
    },
    "COMPLIANCE_DRIFT": {
        "actions": [
            "Revert configuration to baseline",
            "Verify compliance status",
            "Update change management records",
            "Schedule compliance review",
        ],
        "owner": "Compliance Team",
        "priority": "HIGH",
        "due_days": 7,
    },
    "PUBLIC_ACCESS": {
        "actions": [
            "Restrict public access immediately",
            "Review access logs for unauthorized access",
            "Verify no data exposure occurred",
            "Update security group rules",
        ],
        "owner": "Security Team",
        "priority": "CRITICAL",
        "due_days": 1,
    },
}


async def generate_remediation(
    db: AsyncSession,
    entity: RiskEntity,
    anomaly_type: str,
    commit: bool = True,
) -> list[RemediationAction]:
    template = REMEDIATION_TEMPLATES.get(anomaly_type)
    if not template:
        return []

    created_actions = []
    for action_text in template["actions"]:
        action = RemediationAction(
            entity_id=entity.entity_id,
            anomaly_type=anomaly_type,
            priority=template["priority"],
            owner=template["owner"],
            action=action_text,
            status="open",
            due_date=(
                datetime.now(timezone.utc).isoformat()[:10]
            ),
        )
        db.add(action)
        await db.flush()
        created_actions.append(action)

    if commit:
        await db.commit()

    return created_actions


async def generate_remediation_for_anomalies(
    db: AsyncSession,
    entity_id=None,
    commit: bool = True,
) -> list[RemediationAction]:
    from app.models.risk_v2 import AnomalyEventV2

    q = select(AnomalyEventV2)
    if entity_id:
        q = q.where(AnomalyEventV2.entity_id == entity_id)
    result = await db.execute(q)
    anomalies = result.scalars().all()

    all_actions = []
    for anomaly in anomalies:
        entity = await db.execute(select(RiskEntity).where(RiskEntity.entity_id == anomaly.entity_id))
        entity_obj = entity.scalar_one_or_none()
        if not entity_obj:
            continue

        existing = await db.execute(
            select(RemediationAction).where(
                RemediationAction.entity_id == anomaly.entity_id,
                RemediationAction.anomaly_type == anomaly.anomaly_type,
                RemediationAction.status == "open",
            ).limit(1)
        )
        if existing.scalar() is not None:
            continue

        actions = await generate_remediation(db, entity_obj, anomaly.anomaly_type, commit=False)
        all_actions.extend(actions)

    if commit:
        await db.commit()

    return all_actions
