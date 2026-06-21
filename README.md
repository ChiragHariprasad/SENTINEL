# SENTINEL v2

Intelligence-driven third-party risk management platform. Ingests documents, builds risk graphs, runs correlation/scenario/remediation engines, and answers natural-language queries via Copilot.

**37 v2 API endpoints** | **10-level validation suite (468/468 passing)** | **7 copilot intents** | **6-stage pipeline**

## Quick Links

- [Linux Run Instructions](RUN-LINUX.md)
- [Windows Run Instructions](RUN-WINDOWS.md)
- [Validation Results](validation.md)
- [Tests README](tests/README.md)

## What It Does

1. **Document Intelligence** — Upload PDFs (ISO27001 certs, SOC2 reports, audit reports); auto-extract structured findings
2. **Entity Registry** — 8 entity types (VENDOR, ORGANIZATION, CONTROL, etc.) with attributes and risk scores
3. **Risk Graph** — 12 relationship types with weighted edges and bidirectional traversal
4. **Risk Scoring** — 5-tier system (CRITICAL/HIGH/ELEVATED/MINIMAL/UNKNOWN) across 6 dimensions
5. **Anomaly Detection** — 14 rule-based anomaly detectors
6. **Risk Correlation** — Graph-based weighted propagation with BFS from neighbors
7. **Blast Radius** — Impact analysis with path enumeration
8. **Scenario Simulation** — 7 scenario types (BREACH, FAILURE, CERT_EXPIRED, SOC2_EXPIRED, etc.)
9. **Remediation Engine** — 14 anomaly-type templates with action generation
10. **Intelligence & Executive Briefs** — Daily snapshots, priorities, portfolio-level summaries
11. **Timeline** — Risk score change events per entity
12. **Copilot** — 7 intents: risk_explanation, remediation, simulation, prioritization, executive_summary, entity_lookup, blast_radius

## Project Structure

```
SENTINEL/
├── backend/                  # Python FastAPI (v1 + v2)
│   └── app/
│       ├── api/v2/           # 14 route modules → 37 endpoints
│       ├── models/           # 15+ ORM models
│       ├── services/         # 12 engine modules
│       └── main.py           # App entrypoint
├── frontend/                 # Next.js UI
├── Test_Files/               # 3 sample PDFs
│   ├── ISO27001-2022_Certificate.pdf
│   ├── soc2.pdf
│   └── Internal Audit Report H1 FY 17-18.pdf
├── tests/                    # Validation suite
│   └── full_demo.py          # 13-step pipeline demo
├── compose.standalone.yml    # Docker compose
├── RUN-LINUX.md
├── RUN-WINDOWS.md
└── DEMO_RESULTS.md
```

## Architecture

```
PDF Upload → Document Intelligence → Entity Registry → Risk Graph
  → Risk Scoring → Anomaly Detection → Risk Correlation
  → Blast Radius → Scenario Simulation → Intelligence/Executive Brief
  → Remediation → Timeline → Copilot Q&A
```

All stages exposed as v2 API endpoints plus a `POST /api/v2/pipeline/run` orchestrator that runs all 6 stages sequentially.

## V2 API Endpoints

| Domain | Endpoints |
|--------|----------|
| Entities | `POST/GET /entities`, `GET/PUT/DELETE /entities/{id}` |
| Graph | `POST /relationships`, `GET /entity/{id}`, `GET /entity/{id}/impact` |
| Risk | `POST /calculate`, `POST /recalculate`, `GET /{id}`, `GET /{id}/history` |
| Correlation | `POST /run`, `GET /{entity_id}` |
| Anomalies | `POST /run`, `GET /` |
| Blast Radius | `GET /{entity_id}` |
| Intelligence | `POST /daily`, `POST /priorities`, `POST /executive`, `GET /snapshots` |
| Remediation | `POST /generate`, `POST /generate-from-anomalies`, `GET /actions`, `PATCH /actions/{id}/complete` |
| Timeline | `GET /entity/{entity_id}`, `GET /portfolio` |
| Pipeline | `POST /run` |
| Scenario | `GET /templates`, `POST /run`, `GET /results` |
| Ingestion | `POST /csv`, `POST /json`, `POST /manual`, `POST /normalize` |
| Documents | `POST /upload`, `POST /analyze`, `GET /findings`, `POST /build-graph` |
| Copilot | `POST /query` |

## Test Suite (10 Levels)

| Level | Name | Tests | Status |
|-------|------|-------|--------|
| 1 | API Contract | 127 | ✅ PASS |
| 2 | Business Logic | 12 | ✅ PASS |
| 3 | Graph Integrity | 15 | ✅ PASS |
| 4 | Integration | 92 | ✅ PASS |
| 5 | Engine Validation | 10 | ✅ PASS |
| 6 | Security Scenarios | 100 | ✅ PASS |
| 7 | Frontend UI | — | ⚠️ legacy |
| 9 | Chaos/Resilience | 12 | ✅ PASS |
| 10 | Demo Validation | 110 | ✅ PASS |

## Key Results

- **3 real PDFs** processed (ISO27001, SOC2 Type 2, Internal Audit) — 34 findings, 11 risks
- **11 entities** + **10 relationships** created in the risk graph
- **Portfolio risk score:** 29.39 | **1 high-risk entity** | **32 open remediation actions**
- **Blast radius:** Walkover outage → 5 vendors impacted
- **Pipeline:** 6/6 stages completed, 1,546 entities correlated per run
- **Copilot:** routes 7 intent types with stop-word-filtered entity matching

See [validation.md](validation.md) for the full 13-step pipeline breakdown.  
Raw test outputs (JSON) are in [tests/results/](tests/results/).
