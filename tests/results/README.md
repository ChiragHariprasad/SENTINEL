# Test Results Summary

**Run:** 2026-06-21  
**System:** SENTINEL v2 (37 v2 API endpoints)

## Overview

All 5 test levels plus the full pipeline demo passed successfully. **276 test assertions + 13 demo steps — 0 failures.**

## Results by Level

| Level | File | Passed | Failed | Status |
|-------|------|--------|--------|--------|
| Level 1 — API Contract | [test_contract.json](test_contract.json) | 127 | 0 | ✅ |
| Level 2 — Business Logic | [test_business_logic.json](test_business_logic.json) | 12 | 0 | ✅ |
| Level 3 — Graph Integrity | [test_graph.json](test_graph.json) | 15 | 0 | ✅ |
| Level 9 — Chaos/Resilience | [test_chaos.json](test_chaos.json) | 12 | 0 | ✅ |
| Level 10 — Demo Validation | [test_demo.json](test_demo.json) | 110 | 0 | ✅ |
| **Total** | | **276** | **0** | **✅** |

## Full Pipeline Demo

| Step | Description | Status |
|------|-------------|--------|
| 1 | Create 11 business entities | ✅ |
| 2 | Create 10 risk relationships | ✅ |
| 3 | Calculate risk scores | ✅ |
| 4 | Run anomaly detection | ✅ |
| 5 | Run risk correlation | ✅ |
| 6 | Blast radius analysis | ✅ |
| 7 | Scenario simulation (SOC2_EXPIRED) | ✅ |
| 8 | Intelligence brief generation | ✅ |
| 9 | Executive brief generation | ✅ |
| 10 | Remediation plans | ✅ |
| 11 | Timeline recording | ✅ |
| 12 | Copilot Q&A (4 queries) | ✅ |
| 13 | Full pipeline orchestration (6 stages) | ✅ |

See [full_demo.json](full_demo.json) for output.

## Key Metrics

- **Portfolio risk score:** 29.39
- **High-risk entities:** 1
- **Recent anomalies:** 7
- **Open remediation actions:** 32
- **Pipeline correlations per run:** 1,546
- **Pipeline timeline events:** 1,546

## Documents Processed

| Document | Type | Findings | Risks |
|----------|------|----------|-------|
| ISO27001-2022_Certificate.pdf | ISO27001 | 8 | 2 |
| soc2.pdf | SOC2 Type 2 | 13 | 7 |
| Internal Audit Report H1 FY 17-18.pdf | AUDIT_REPORT | 13 | 2 |

## Files

- [summary.json](summary.json) — aggregate test summary
- [test_contract.json](test_contract.json) — Level 1 full output
- [test_business_logic.json](test_business_logic.json) — Level 2 full output
- [test_graph.json](test_graph.json) — Level 3 full output
- [test_chaos.json](test_chaos.json) — Level 9 full output
- [test_demo.json](test_demo.json) — Level 10 full output
- [full_demo.json](full_demo.json) — 13-step pipeline demo output
