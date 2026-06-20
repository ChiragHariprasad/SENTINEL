# ADR-001: Rule-Based Anomaly Detection vs Machine Learning

**Status:** Accepted
**Date:** 2026-06-21
**Author:** Architecture Team
**Product:** SENTINEL

---

## Context

SENTINEL requires anomaly detection for 7 vendor risk labels:

- BREACHED_VENDOR_HIGH_ACCESS
- VENDOR_UNDER_INVESTIGATION
- HIGH_RISK_SCORE
- EXPIRED_CERTIFICATION
- RECENTLY_BREACHED_VENDOR
- CONTRACT_EXPIRED_ACTIVE_ACCESS
- ELEVATED_RISK_VENDOR

These labels form the core evaluation criteria for the challenge. The question was whether to implement detection via deterministic rules or machine learning (Isolation Forest, XGBoost, etc.).

---

## Decision

**Use deterministic rule-based detection for all 7 labels.**

---

## Rationale

| Factor | Rules | ML | Winner |
|--------|-------|----|--------|
| Explainability | Each detection has a traceable cause | Black-box, requires SHAP/LIME | Rules |
| Implementation time | 3 days | 10-14 days (feature engineering, training, tuning, evaluation) | Rules |
| Data requirements | Zero training data needed | Requires labeled historical data; only 400 vendors available | Rules |
| Recall for critical risks | Directly tunable per rule | Depends on feature quality and sample size | Rules |
| Auditability | Deterministic, reproducible | Probabilistic, harder to validate | Rules |
| Judge/demo impact | Clear "why this vendor was flagged" | "Model predicted" is less trustworthy | Rules |
| Maintenance | Add/modify rules declaratively | Requires retraining, drift monitoring, model registry | Rules |
| Scalability to 10K+ vendors | Constant-time rule evaluation | Inference scales linearly | Tie |

The challenge labels are inherently **deterministic conditions** — they evaluate known risk patterns (breach + PII, expired cert, score threshold). ML offers no advantage for well-defined classification boundaries.

ML would be appropriate for:
- Unknown anomaly patterns (unsupervised)
- Continuous risk score prediction (regression)
- Feature importance discovery across thousands of dimensions

None of these apply to the current 7-label evaluation set.

---

## Consequences

**Positive:**
- Faster implementation (3 days vs 10+ days)
- 100% explainable detections for auditor review
- Deterministic reproducibility for evaluation comparison
- No ML infrastructure (model registry, feature store, drift detection)

**Negative:**
- Rules cannot detect novel/unseen risk patterns
- Rules require manual updates when evaluation criteria change
- No learning from new data (system does not improve automatically)

---

## Future

ML-based detection (Isolation Forest + XGBoost) is planned for Phase 2 as a **supplement** to rules, not a replacement. Rules will continue to serve as the auditable baseline with ML providing:
- Early warning for unknown patterns
- Confidence scoring for borderline cases
- Automated severity calibration

---

*End of ADR-001*
