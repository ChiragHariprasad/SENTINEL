from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.anomaly import AnomalyEvent
from app.models.evaluation import EvaluationResult
from app.models.ground_truth import GroundTruthLabel


def compute_metrics(tp: int, fp: int, fn: int) -> tuple[float, float, float]:
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    return precision, recall, f1


async def compute_evaluation(db: AsyncSession) -> dict:
    prev = await db.execute(select(EvaluationResult))
    for r in prev.scalars().all():
        await db.delete(r)

    gen_result = await db.execute(select(AnomalyEvent))
    generated = gen_result.scalars().all()

    gen_map = {}
    for a in generated:
        key = (str(a.vendor_id), a.anomaly_type)
        gen_map[key] = a.severity

    gt_result = await db.execute(select(GroundTruthLabel))
    ground_truth_list = gt_result.scalars().all()

    if not ground_truth_list:
        ground_truth = gen_map.copy()
    else:
        ground_truth = {}
        for gt in ground_truth_list:
            key = (str(gt.vendor_id), gt.anomaly_type)
            ground_truth[key] = gt.severity or "MEDIUM"

    all_labels = set(list(gen_map.keys()) + list(ground_truth.keys()))

    tp = 0
    fp = 0
    fn = 0

    label_stats = {}
    severity_stats = {}

    for key in all_labels:
        vendor_id, label = key
        gen_sev = gen_map.get(key)
        gt_sev = ground_truth.get(key)

        is_match = gen_sev is not None and gt_sev is not None

        if is_match:
            tp += 1
        elif gen_sev and not gt_sev:
            fp += 1
        elif gt_sev and not gen_sev:
            fn += 1

        if label not in label_stats:
            label_stats[label] = {"tp": 0, "fp": 0, "fn": 0}
        if is_match:
            label_stats[label]["tp"] += 1
        elif gen_sev and not gt_sev:
            label_stats[label]["fp"] += 1
        elif gt_sev and not gen_sev:
            label_stats[label]["fn"] += 1

        sev = gen_sev or gt_sev or "UNKNOWN"
        if sev not in severity_stats:
            severity_stats[sev] = {"tp": 0, "fp": 0, "fn": 0}
        if is_match:
            severity_stats[sev]["tp"] += 1
        elif gen_sev and not gt_sev:
            severity_stats[sev]["fp"] += 1
        elif gt_sev and not gen_sev:
            severity_stats[sev]["fn"] += 1

    overall_p, overall_r, overall_f1 = compute_metrics(tp, fp, fn)
    overall_result = EvaluationResult(
        anomaly_type=None,
        severity=None,
        true_positives=tp,
        false_positives=fp,
        false_negatives=fn,
        precision=overall_p,
        recall=overall_r,
        f1_score=overall_f1,
        computed_at=datetime.now(timezone.utc),
    )
    db.add(overall_result)

    for sev, stats in severity_stats.items():
        p2, r2, f12 = compute_metrics(stats["tp"], stats["fp"], stats["fn"])
        severity_result = EvaluationResult(
            anomaly_type=None,
            severity=sev,
            true_positives=stats["tp"],
            false_positives=stats["fp"],
            false_negatives=stats["fn"],
            precision=p2,
            recall=r2,
            f1_score=f12,
            computed_at=datetime.now(timezone.utc),
        )
        db.add(severity_result)

    for label, stats in label_stats.items():
        p3, r3, f13 = compute_metrics(stats["tp"], stats["fp"], stats["fn"])
        label_result = EvaluationResult(
            anomaly_type=label,
            severity=None,
            true_positives=stats["tp"],
            false_positives=stats["fp"],
            false_negatives=stats["fn"],
            precision=p3,
            recall=r3,
            f1_score=f13,
            computed_at=datetime.now(timezone.utc),
        )
        db.add(label_result)

    await db.flush()

    return {
        "overall": {
            "precision": round(overall_p, 4),
            "recall": round(overall_r, 4),
            "f1_score": round(overall_f1, 4),
        },
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "ground_truth_source": "vendor_labels.csv" if ground_truth_list else "self-comparison",
    }
