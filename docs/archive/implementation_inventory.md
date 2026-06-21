# Implementation Inventory

## Backend

### Implemented

| Component | Status | Location |
|-----------|--------|----------|
| FastAPI application | Complete | `backend/app/main.py` — lifespan context manager, CORS, router includes |
| Settings/Config | Complete | `backend/app/core/config.py` — Pydantic Settings with env file |
| Async Database | Complete | `backend/app/core/database.py` — SQLAlchemy async + asyncpg |
| Auth (JWT) | Complete | `backend/app/core/auth.py` — create/decode tokens, hash/verify passwords |
| Security (Bearer) | Complete | `backend/app/core/security.py` — get_current_user, require_role |
| File Storage | Complete | `backend/app/core/storage.py` — local filesystem + S3/MinIO |
| Custom Exceptions | Complete | `backend/app/core/exceptions.py` — NotFoundError, DuplicateError, etc. |

#### Services

| Service | Status | File |
|---------|--------|------|
| Graph Service | Complete | `graph_service.py` — entity CRUD, relationship CRUD, graph traversal, impact path |
| Risk Engine V2 | Complete | `risk_engine_v2.py` — 5-dimension scoring, entity-type-aware |
| Risk Correlation Engine | Complete | `risk_correlation_engine.py` — BFS graph traversal, weighted decay, reasoning chain |
| Anomaly Engine V2 | Complete | `anomaly_engine_v2.py` — entity-type rules, context building |
| Blast Radius Engine | Complete | `blast_radius_engine.py` — BFS traversal, type classification |
| Timeline Engine | Complete | `timeline_engine.py` — multi-source event aggregation |
| Scenario Engine | Complete | `scenario_engine.py` — 6 templates, BFS impact, risk projection |
| Remediation Engine | Complete | `remediation_engine.py` — 14 templates, deduplication |
| Intelligence Engine | Complete | `intelligence_engine.py` — daily snapshot, priorities |
| Executive Brief Engine | Complete | `executive_brief_engine.py` — portfolio summary, recommendations |
| Document Intelligence Engine | Complete | `document_intelligence_engine.py` — PDF OCR, classification, extraction, graph building |
| Copilot Engine V2 | Complete | `copilot_engine.py` — 6 intents, regex detection, multi-handler dispatch |
| Pipeline Orchestrator | Complete | `pipeline_orchestrator.py` — 6-stage processing, error handling, logging |
| Ingestion Service | Complete | `ingestion_service.py` — CSV, JSON, manual entity ingestion |
| Normalization Service | Complete | `normalization_service.py` — raw data to RiskEntity |
| Evaluation Service | Complete | `evaluation_service.py` — precision/recall/F1 computation |
| Contract Service | Complete | `contract_service.py` — LLM-based contract analysis |
| Copilot Service V1 | Complete | `copilot_service.py` — SQL-generation via LLM |
| Risk Service V1 | Complete | `risk_service.py` — vendor risk calculation |

#### AI/Rules

| Component | Status | File |
|-----------|--------|------|
| Scoring V1 | Complete | `ai/scoring.py` — weighted sum, GREEN/YELLOW/RED tiers |
| Scoring V2 | Complete | `ai/scoring_v2.py` — entity-type weights, 5 tiers |
| Rules V1 | Complete | `ai/rules.py` — 7 vendor rules |
| Rules V2 | Complete | `ai/rules_v2.py` — 14 rules across 3 domains (vendor, identity, config) |
| Copilot AI V1 | Complete | `ai/copilot.py` — intent matching + LLM SQL generation (Mistral) |
| Contract Analyzer AI | Complete | `ai/contract_analyzer.py` — LLM-based extraction (Mistral + mock fallback) |

#### API Routes V1 (32 routes)

| Router | Endpoints | File |
|--------|-----------|------|
| Auth | signup, login, refresh, logout | `api/auth.py` |
| Users | list, create, get, update, list_roles | `api/users.py` |
| Vendors | list, create, get, update, delete, categories, data_access | `api/vendors.py` |
| Risk | calculate, get_vendor_risk, history, recalculate_all | `api/risk.py` |
| Anomalies | list, vendor_anomalies, labels | `api/anomalies.py` |
| Alerts | list, create, resolve | `api/alerts.py` |
| Evaluations | metrics, run, upload_labels | `api/evaluation.py` |
| Certifications | list, create, expiring, frameworks | `api/certifications.py` |
| Contracts | upload, analyze, get, get_analysis | `api/contracts.py` |
| Copilot | query | `api/copilot.py` |
| Reports | list, generate, download | `api/reports.py` |
| Dashboard | summary | `api/dashboard.py` |
| Imports | import, import_status | `api/imports.py` |
| Health | health_check | `api/health.py` |

#### API Routes V2 (33 routes)

| Router | Endpoints | File |
|--------|-----------|------|
| Entities | create, list, get, update, delete | `api/v2/entities.py` |
| Graph | create_relationship, get_entity_graph, get_impact_path | `api/v2/graph.py` |
| Risk | calculate, get, history, recalculate | `api/v2/risk.py` |
| Correlation | run, get | `api/v2/correlation.py` |
| Anomalies | run, list | `api/v2/anomalies.py` |
| Blast Radius | calculate | `api/v2/blast_radius.py` |
| Timeline | entity, portfolio | `api/v2/timeline.py` |
| Scenario | templates, run, results | `api/v2/scenario.py` |
| Intelligence | daily, priorities, executive, snapshots | `api/v2/intelligence.py` |
| Remediation | generate, generate-from-anomalies, actions, complete | `api/v2/remediation.py` |
| Pipeline | run | `api/v2/pipeline.py` |
| Ingestion | csv, json, manual, normalize | `api/v2/ingestion.py` |
| Documents | upload, analyze, findings, build-graph | `api/v2/documents.py` |
| Copilot | query | `api/v2/copilot.py` |

#### Database Models (30 tables)

Complete implementation for: users, roles, vendors, vendor_categories, vendor_category_mapping, vendor_contacts, vendor_data_access, risk_scores, risk_history, anomaly_labels, anomaly_events, evaluation_results, compliance_frameworks, certifications, vendor_compliance, security_alerts, contracts, csv_imports, audit_logs, ground_truth_labels, risk_entities, risk_relationships, risk_scores_v2, risk_history_v2, correlated_risks, anomaly_events_v2, intelligence_snapshots, remediation_actions, risk_events, scenario_runs, raw_vendors, raw_identity_events, raw_config_drift, raw_exceptions, raw_documents, document_findings

### Partial

| Component | Status | Detail |
|-----------|--------|--------|
| Scenario full-impact endpoint | Partial | Route exists at `POST /scenario/full-impact` but frontend doesn't call it |
| Document analysis frontend | Partial | Upload and analyze APIs work, but no dedicated frontend page for document intelligence results |

### Missing

| Component | Status | Detail |
|-----------|--------|--------|
| Celery Workers | **NOT IMPLEMENTED** | No Celery in requirements.txt, no worker files, no task definitions |
| Redis usage in code | **NOT IMPLEMENTED** | Redis configured but not used by any Python code |
| Alembic migrations | **NOT IMPLEMENTED** | `alembic/versions/` is empty, schema uses `create_all()` |
| WebSocket/Real-time | **NOT IMPLEMENTED** | No WebSocket endpoints for push notifications |
| Rate Limiting | **NOT IMPLEMENTED** | No rate limiting on API endpoints |
| Multi-tenancy | **NOT IMPLEMENTED** | Single-tenant only |
| React Flow graph canvas | **NOT IMPLEMENTED** | Graph uses node list with expandable cards, not a visual canvas |
| Executive Timeline page | **NOT IMPLEMENTED** | No frontend page for `/timeline` |
| Advanced Graph Analytics | **NOT IMPLEMENTED** | No community detection, centrality, or path analysis |
| SOAR Integration | **NOT IMPLEMENTED** | No PagerDuty, ServiceNow, or Jira integrations |

---

## Frontend

### Implemented

| Page/Component | Status | File |
|----------------|--------|------|
| Login | Complete | `app/login/page.tsx` |
| Dashboard | Complete | `app/dashboard/page.tsx` |
| Vendor Registry (list) | Complete | `app/vendors/page.tsx` |
| Vendor Detail | Complete | `app/vendors/[id]/page.tsx` |
| New Vendor | Complete | `app/vendors/new/page.tsx` |
| Risk Register | Complete | `app/risk/page.tsx` |
| Risk Graph (node list) | Complete | `app/graph/page.tsx` |
| Scenario Simulator | Complete | `app/scenarios/page.tsx` |
| AI Copilot (chat) | Complete | `app/copilot/page.tsx` |
| Anomaly Center | Complete | `app/anomalies/page.tsx` |
| Alerts | Complete | `app/alerts/page.tsx` |
| Certifications | Complete | `app/certifications/page.tsx` |
| Contracts | Complete | `app/contracts/page.tsx` |
| Evaluation Dashboard | Complete | `app/evaluation/page.tsx` |
| Reports | Complete | `app/reports/page.tsx` |
| CSV Import | Complete | `app/import/page.tsx` |
| Admin Users | Complete | `app/admin/users/page.tsx` |
| Sidebar | Complete | `components/layout/Sidebar.tsx` |
| Dashboard Shell | Complete | `components/layout/Shell.tsx` |
| Auth Context | Complete | `lib/auth-context.tsx` |
| API Client (v1 + v2) | Complete | `lib/api-client.ts` |
| Utils | Complete | `lib/utils.ts` |

### Partial

| Component | Status | Detail |
|-----------|--------|--------|
| Executive Timeline page | **NOT IMPLEMENTED** | No `/timeline` page in frontend |

### Missing

| Component | Status |
|-----------|--------|
| React Flow graph canvas | Not implemented (uses node list instead) |
| Remediation Center page | Not implemented as a standalone page |
| Full Intelligence dashboard | Not implemented as a standalone page |

---

## Infrastructure

### Implemented

| Component | Status | Detail |
|-----------|--------|--------|
| PostgreSQL | Complete | `docker-compose.yml` — postgres:16-alpine |
| Redis | Complete | `docker-compose.yml` — redis:7-alpine |
| Docker Compose | Complete | 4 services: postgres, redis, api, frontend |
| Standalone Compose | Complete | adds MinIO, health checks, port 8082 |
| API Dockerfile | Complete | Python 3.12-slim, uvicorn |
| Frontend Dockerfile | Complete | Node 20-alpine, next build |
| JWT Authentication | Complete | Bearer token on all endpoints |
| RBAC | Complete | 3 roles (admin, analyst, executive) |
| CORS | Complete | Configurable origins |

### Partial

| Component | Status | Detail |
|-----------|--------|--------|
| MinIO/S3 Storage | Partial | Configured in standalone compose, used in storage.py with fallback to local |

### Missing

| Component | Status |
|-----------|--------|
| Celery Workers | Not implemented |
| Alembic Migrations | Not implemented (schema uses create_all) |
| Load Balancer config | Not implemented |
| Rate Limiting | Not implemented |
| Monitoring/Prometheus | Not implemented |
| Sentry integration | Listed in requirements but not configured in code |
| CI/CD pipeline | Not implemented |
| Kubernetes manifests | Not implemented |

---

## Test Coverage

| Level | Tests | Count |
|-------|-------|-------|
| Backend unit tests | 5 test files | ~50 tests |
| Backend integration tests | 14 test files | ~100 tests |
| Full API contract tests | 1 file | ~200 assertions |
| Business logic tests | 1 file | ~60 tests |
| Graph propagation tests | 1 file | ~25 tests |
| Scenario tests | 1 file | ~20 tests |
| PDF edge case tests | 1 file | ~20 tests |
| Copilot tests (100 questions) | 1 file | 100 questions |
| Load test (k6) | 1 file | 500 concurrent users |
| Chaos test | 1 file | ~25 tests |
| Demo test (10 runs) | 1 file | 10 full end-to-end runs |
| Frontend unit/component tests | 5 test files | ~15 tests |
| Frontend E2E (Puppeteer) | 2 test files | 4 scenarios |
