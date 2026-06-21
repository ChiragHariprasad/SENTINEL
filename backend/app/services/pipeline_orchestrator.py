import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.models.risk_entity import RiskEntity
from app.services.risk_engine_v2 import calculate_entity_risk
from app.services.anomaly_engine_v2 import run_anomaly_detection
from app.services.risk_correlation_engine import correlate_entity_risk
from app.services.intelligence_engine import generate_daily_intelligence, generate_priorities
from app.services.executive_brief_engine import generate_executive_brief
from app.services.remediation_engine import generate_remediation_for_anomalies
from app.services.timeline_engine import record_risk_event
from sqlalchemy import select

logger = logging.getLogger(__name__)


async def run_full_pipeline(entity_id: str | None = None) -> dict:
    results = {"stages": {}, "status": "completed", "error": None}

    async with async_session_factory() as db:
        try:
            stage = "risk_calculation"
            if entity_id:
                entity_result = await db.execute(
                    select(RiskEntity).where(RiskEntity.entity_id == entity_id)
                )
                entity = entity_result.scalar_one_or_none()
                if entity:
                    await calculate_entity_risk(db, entity, commit=False)
                    results["stages"][stage] = {"entity_id": entity_id, "status": "ok"}
                else:
                    results["stages"][stage] = {"error": "entity not found", "status": "skipped"}
            else:
                entities = await db.execute(select(RiskEntity).where(RiskEntity.status == "active"))
                for e in entities.scalars().all():
                    await calculate_entity_risk(db, e, commit=False)
                results["stages"][stage] = {"status": "ok"}
            await db.flush()

            stage = "anomaly_detection"
            anomalies = await run_anomaly_detection(db, commit=False)
            results["stages"][stage] = {"anomalies_detected": len(anomalies), "status": "ok"}

            stage = "correlation"
            entities = await db.execute(select(RiskEntity).where(RiskEntity.status == "active"))
            corr_count = 0
            for e in entities.scalars().all():
                if e.risk_score is not None:
                    await correlate_entity_risk(db, e, commit=False)
                    corr_count += 1
            results["stages"][stage] = {"correlated": corr_count, "status": "ok"}

            stage = "remediation"
            actions = await generate_remediation_for_anomalies(db, commit=False)
            results["stages"][stage] = {"actions_generated": len(actions), "status": "ok"}

            stage = "intelligence"
            daily = await generate_daily_intelligence(db)
            priorities = await generate_priorities(db)
            brief = await generate_executive_brief(db)
            results["stages"][stage] = {
                "daily_intelligence": str(daily.id),
                "priorities": str(priorities.id),
                "executive_brief": str(brief.id),
                "status": "ok",
            }

            stage = "timeline"
            active = await db.execute(select(RiskEntity).where(RiskEntity.status == "active"))
            timeline_count = 0
            for e in active.scalars().all():
                if e.risk_score is not None:
                    await record_risk_event(
                        db,
                        entity_id=e.entity_id,
                        event_type="pipeline_run",
                        description=f"Risk score: {e.risk_score}",
                        new_value=e.risk_score,
                    )
                    timeline_count += 1
            results["stages"][stage] = {"events_recorded": timeline_count, "status": "ok"}

            await db.commit()
            results["pipeline_id"] = str(daily.id)

        except Exception as exc:
            await db.rollback()
            results["status"] = "failed"
            results["error"] = str(exc)
            logger.exception("Pipeline orchestration failed")

    return results
