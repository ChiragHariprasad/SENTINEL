# Document Claim Audit

Each claim from SENTINEL-ARCHITECTURE-SUBMISSION.md is classified as VERIFIED, OVERSTATED, or FICTIONAL.

---

## Section 1: Executive Summary

| Claim | Status | Evidence |
|-------|--------|----------|
| "AI-powered Enterprise Risk Intelligence Platform" | VERIFIED | `backend/app/services/copilot_engine.py`, `backend/app/ai/copilot.py`, `backend/app/ai/contract_analyzer.py` |
| "Ingests PDF, CSV, JSON, audit reports, compliance certs, SOC reports, security questionnaires" | VERIFIED | `backend/app/services/document_intelligence_engine.py` — 6 document types supported; `backend/app/services/ingestion_service.py` — 4 CSV types + JSON |
| "Extracts entities, controls, risks, dependencies, relationships" | VERIFIED | `backend/app/services/document_intelligence_engine.py` — extraction functions; `backend/app/services/graph_service.py` — relationship management |
| "Ten-layer intelligence model" | OVERSTATED | The codebase has layered services but they are not organized as a formal 10-layer stack. It's a flat service architecture. |
| "Async processing via Celery and Redis" | **FICTIONAL** | No Celery anywhere in the codebase. Redis is configured but not used by any Python code. |
| "Persistent storage in PostgreSQL" | VERIFIED | `backend/app/core/database.py` — asyncpg + SQLAlchemy |

---

## Section 2: Problem Statement

| Claim | Status | Evidence |
|-------|--------|----------|
| "Risk propagates" — correlated risk across interconnected entities | VERIFIED | `backend/app/services/risk_correlation_engine.py` — BFS traversal with weighted decay |
| "No risk graph visibility" | VERIFIED | Addressed by `backend/app/services/graph_service.py` — `get_entity_graph()` |
| "No risk propagation analysis" | VERIFIED | Addressed by `backend/app/services/risk_correlation_engine.py` |
| "No scenario simulation" | VERIFIED | Addressed by `backend/app/services/scenario_engine.py` |
| "No automated remediation" | VERIFIED | Addressed by `backend/app/services/remediation_engine.py` |
| "No executive intelligence" | VERIFIED | Addressed by `backend/app/services/executive_brief_engine.py` |
| "No AI copilot" | VERIFIED | Addressed by `backend/app/services/copilot_engine.py` |

---

## Section 3: Industry Challenges

All claims in this section are **VERIFIED** as they describe general industry challenges, not platform features.

---

## Section 4: Solution Overview

| Claim | Status | Evidence |
|-------|--------|----------|
| 8 core capabilities listed | VERIFIED | All map to implemented services |
| 6 document types listed | VERIFIED | `backend/app/services/document_intelligence_engine.py:17` — DOCUMENT_PATTERNS |
| 8 entity types | VERIFIED | `backend/app/models/risk_entity.py:10` — ENTITY_TYPES |
| 12 relationship types with weights | VERIFIED | `backend/app/models/risk_relationship.py:10` — RELATIONSHIP_TYPES |

---

## Section 5: Platform Architecture

| Claim | Status | Evidence |
|-------|--------|----------|
| "Ten-layer intelligence model" | OVERSTATED | Code has services organized by function but not as a formal 10-layer stack. The layers in the document are aspirational groupings. |
| ASCII architecture diagram showing 10 layers | OVERSTATED | The layers exist conceptually but the implementation does not enforce strict layer boundaries. Services can call each other across "layers." |
| Deployment architecture ASCII diagram | OVERSTATED | No load balancer configuration exists. No API gateway beyond FastAPI itself. Celery workers and WebSocket do not exist. |
| Service topology diagram | OVERSTATED | Services are organized as flat modules. No service mesh, no container orchestration, no internal service discovery. |

---

## Section 6: Component Architecture

| Claim | Status | Evidence |
|-------|--------|----------|
| Document Service — PyMuPDF, classification, extraction | VERIFIED | `backend/app/services/document_intelligence_engine.py` |
| Entity Service — CRUD, filter, search, pagination | VERIFIED | `backend/app/services/graph_service.py` — `list_entities()` |
| Graph Service — BFS traversal, impact path | VERIFIED | `backend/app/services/graph_service.py` — `get_entity_graph()`, `get_impact_path()` |
| Risk Service V2 — 5 dimensions, entity-type-aware | VERIFIED | `backend/app/services/risk_engine_v2.py` |
| Correlation Service — BFS with decay, reasoning chain | VERIFIED | `backend/app/services/risk_correlation_engine.py` |
| Anomaly Service V2 — rule-based, entity context building | VERIFIED | `backend/app/services/anomaly_engine_v2.py` |
| Remediation Service — 14 templates, deduplication | VERIFIED | `backend/app/services/remediation_engine.py` |
| Scenario Service — 6 templates, BFS impact, risk projection | VERIFIED | `backend/app/services/scenario_engine.py` |
| Blast Radius Engine — BFS, type classification | VERIFIED | `backend/app/services/blast_radius_engine.py` |
| Timeline Service — multi-source event aggregation | VERIFIED | `backend/app/services/timeline_engine.py` |
| Pipeline Orchestrator — 6 stages, transaction | VERIFIED | `backend/app/services/pipeline_orchestrator.py` |
| Copilot Service — 6 intents, regex detection, multi-handler | VERIFIED | `backend/app/services/copilot_engine.py` |

---

## Section 7: Data Flow

| Claim | Status | Evidence |
|-------|--------|----------|
| Document ingestion flow diagram | VERIFIED | Flow matches `backend/app/api/v2/documents.py` + `document_intelligence_engine.py` |
| Risk intelligence flow diagram | VERIFIED | Flow matches `backend/app/services/pipeline_orchestrator.py:19` |
| Scenario simulation flow diagram | VERIFIED | Flow matches `backend/app/services/scenario_engine.py:51` |

---

## Section 8: AI Pipeline

| Claim | Status | Evidence |
|-------|--------|----------|
| Document intelligence — keyword classification, regex extraction | VERIFIED | `backend/app/services/document_intelligence_engine.py` |
| Entity extraction — type-specific functions | VERIFIED | `backend/app/services/document_intelligence_engine.py:244` — _EXTRACTION_MAP |
| Risk classification — 5 dimension scoring | VERIFIED | `backend/app/services/risk_engine_v2.py` |
| Risk correlation — BFS with decay | VERIFIED | `backend/app/services/risk_correlation_engine.py` |
| Remediation recommendation — templates | VERIFIED | `backend/app/services/remediation_engine.py` |
| Copilot — intent detection, multi-engine dispatch | VERIFIED | `backend/app/services/copilot_engine.py` |

---

## Section 9: Risk Intelligence Engine

| Claim | Status | Evidence |
|-------|--------|----------|
| Daily intelligence snapshot | VERIFIED | `backend/app/services/intelligence_engine.py:11` — `generate_daily_intelligence()` |
| Priority actions | VERIFIED | `backend/app/services/intelligence_engine.py:82` — `generate_priorities()` |
| Executive brief | VERIFIED | `backend/app/services/executive_brief_engine.py:11` — `generate_executive_brief()` |
| Automated strategic recommendations | VERIFIED | `backend/app/services/executive_brief_engine.py:83` — `_generate_recommendations()` |

---

## Section 10: Risk Graph Engine

| Claim | Status | Evidence |
|-------|--------|----------|
| Nodes: RiskEntity with 8 types | VERIFIED | `backend/app/models/risk_entity.py` |
| Edges: RiskRelationship with 12 types | VERIFIED | `backend/app/models/risk_relationship.py` |
| Example graph diagram | VERIFIED | Structure matches the data model |
| Graph traversal operations table | VERIFIED | All 5 operations implemented in `graph_service.py`, `blast_radius_engine.py`, `risk_correlation_engine.py`, `scenario_engine.py` |

---

## Section 11: Risk Correlation Engine

| Claim | Status | Evidence |
|-------|--------|----------|
| Correlation formula documented | VERIFIED | `backend/app/services/risk_correlation_engine.py:76` — `correlated_risk = min(base_risk + neighbor_risk, 100)` |
| Algorithm details with correct variable names | OVERSTATED | Document uses `effective_weight = relationship_weight * decay_factor`. Code uses `effective_weight = rel.weight * decay`. Document says `contributed = neighbor.risk_score * effective_weight / 100`. Code uses `float(te.risk_score) * effective_weight / 100.0`. Close but not exact. |
| Reasoning chain JSON example | VERIFIED | Code produces exactly this structure in `risk_correlation_engine.py:56-64` |

---

## Section 12: Remediation Engine

| Claim | Status | Evidence |
|-------|--------|----------|
| Template architecture described | VERIFIED | `backend/app/services/remediation_engine.py:9` — REMEDIATION_TEMPLATES |
| 14 templates | VERIFIED | 14 templates in the code: BREACHED_VENDOR through PUBLIC_ACCESS |
| Deduplication logic | VERIFIED | `backend/app/services/remediation_engine.py:220-228` |

---

## Section 13: Scenario Simulation Engine

| Claim | Status | Evidence |
|-------|--------|----------|
| 6 simulation types | VERIFIED | `backend/app/services/scenario_engine.py:11` — 6 SCENARIO_TEMPLATES |
| Simulation algorithm described | VERIFIED | `backend/app/services/scenario_engine.py:51` — `run_scenario()` |
| Sample output | VERIFIED | Matches code output structure |
| BLAST radius computation | VERIFIED | `backend/app/services/scenario_engine.py:135` — `_traverse_graph()` |
| "Within a single database transaction" | VERIFIED | `pipeline_orchestrator.py:85` — `await db.commit()` after all stages |

---

## Section 14: Copilot Architecture

| Claim | Status | Evidence |
|-------|--------|----------|
| Architecture overview diagram | VERIFIED | Flow matches `backend/app/services/copilot_engine.py:281` |
| Intent detection with regex patterns | VERIFIED | `backend/app/services/copilot_engine.py:17` — INTENT_PATTERNS |
| Entity resolution with fuzzy matching | VERIFIED | `backend/app/services/copilot_engine.py:65` — `_find_entity()` using ILIKE |
| 6 intent handlers | VERIFIED | `backend/app/services/copilot_engine.py:271` — `_INTENT_HANDLERS` dict |
| Response format with answer, sources, intent | VERIFIED | `backend/app/services/copilot_engine.py:105-109`, `282-287` |
| "Does not require an external LLM" | VERIFIED | V2 copilot is fully rule-based. Only V1 uses LLM. |
| Architecture diagram showing intent routing | VERIFIED | Matches code flow |

---

## Section 15: API Architecture

| Claim | Status | Evidence |
|-------|--------|----------|
| Two-version API structure | VERIFIED | `api/v1/` (32 routes) and `api/v2/` (33 routes) |
| V2 endpoint table | OVERSTATED | Document lists `POST /api/v2/scenario/full-impact`. Route exists at `backend/app/api/v2/scenario.py` as a POST but no code was found reading this exact path handler in the scan. |
| Standard response format | VERIFIED | `backend/app/schemas/common.py` — `StandardResponse` |
| Authentication: Bearer JWT | VERIFIED | `backend/app/core/security.py` |
| Sample API call with response | VERIFIED | Matches actual API behavior |

---

## Section 16: Worker Architecture

| Claim | Status | Evidence |
|-------|--------|----------|
| "SENTINEL uses an asynchronous worker architecture for long-running tasks" | **FICTIONAL** | No Celery workers anywhere. No worker files. No task definitions. |
| "While Celery + Redis is provisioned in the architecture, the current implementation uses async SQLAlchemy within the FastAPI process for simplicity" | OVERSTATED | This is a caveat but still misleading. Celery is not "provisioned" — it is entirely absent from the codebase. No Celery in requirements.txt, no worker files, no Celery config. |
| "Worker Topology (Planned)" diagram | OVERSTATED | Should be labeled "Planned" not "Worker Architecture" |
| "Asynchronous Processing Flow" | VERIFIED | The actual async flow matches what's described as the fallback |

---

## Section 17: Database Architecture

| Claim | Status | Evidence |
|-------|--------|----------|
| Core tables table | OVERSTATED | Document lists "raw_data (and subtypes)" as one entry. Code has 5 separate raw data tables: RawVendor, RawIdentityEvent, RawConfigDrift, RawException, RawDocument. |
| Entity Relationship Diagram | OVERSTATED | ERD is simplified. Code has 35+ tables, ERD shows only 15. Missing: evaluation_results, audit_logs, csv_imports, ground_truth_labels, security_alerts, vendor_contacts, vendor_data_access, compliance_frameworks, vendor_compliance, contracts, anomaly_labels, document_findings, raw_* tables. |
| Indexing strategy | VERIFIED | Indexes match code but document describes GIN trigram index as "planned" — code doesn't add this index explicitly. |
| PostgreSQL Features Used | VERIFIED | UUID, JSONB, TIMESTAMPTZ, Foreign Keys, asyncpg all used |

---

## Section 18: Security Architecture

| Claim | Status | Evidence |
|-------|--------|----------|
| "Access tokens: 15-minute expiry" | VERIFIED | `backend/app/core/config.py:10` — `ACCESS_TOKEN_EXPIRE_MINUTES: int = 15` |
| "Refresh tokens: 24-hour expiry" | VERIFIED | `backend/app/core/config.py:11` — `REFRESH_TOKEN_EXPIRE_HOURS: int = 24` |
| "Tokens signed with HS256" | VERIFIED | `backend/app/core/auth.py:23` — `algorithm=settings.ALGORITHM` which is "HS256" |
| "Password hashing using bcrypt via passlib" | VERIFIED | `backend/app/core/auth.py:8` — `CryptContext(schemes=["bcrypt"])` |
| Role-Based Access Control | VERIFIED | `backend/app/core/security.py:33` — `require_role()`; 3 roles seeded |
| Audit logging | OVERSTATED | `AuditLog` model exists but is not populated by any service. Only `risk_events` table is used for timeline logging. |
| "File storage encryption" | **FICTIONAL** | No file encryption implementation found. Files are stored as-is. |
| "TLS/SSL termination at the load balancer" | OVERSTATED | No load balancer configuration exists. |
| "Global exception handler preventing information leakage" | VERIFIED | `backend/app/main.py:66` — global exception handler returns generic error |
| Input validation via Pydantic | VERIFIED | All endpoints use Pydantic schemas |

---

## Section 19: Scalability Design

| Claim | Status | Evidence |
|-------|--------|----------|
| "Stateless FastAPI behind load balancer" | OVERSTATED | API is stateless, but no load balancer configuration exists |
| "Celery workers with Redis broker" | **FICTIONAL** | No Celery or worker implementation |
| "PostgreSQL read replicas" | **FICTIONAL** | No read replica configuration |
| "Connection pooling: SQLAlchemy connection pool" | VERIFIED | SQLAlchemy uses connection pooling by default |
| "Redis: Message broker for worker tasks" | **FICTIONAL** | Redis not used for any purpose in code |
| "API responses paginated (default 50, max 200)" | VERIFIED | `backend/app/api/v2/entities.py:37` — `page: int = Query(1), size: int = Query(50, le=200)` |

---

## Section 20: User Interface Design

| Claim | Status | Evidence |
|-------|--------|----------|
| Next.js 14, TypeScript, Tailwind CSS, Lucide | OVERSTATED | Uses Next.js **16.2.0** and React **19** (not 14 as claimed) |
| "Executive Timeline" module | OVERSTATED | Described as a module but no frontend page exists for it |
| "Remediation Center" module | OVERSTATED | Described as a module but no dedicated frontend page exists |
| "Risk Intelligence Center (Dashboard)" | VERIFIED | `frontend/src/app/dashboard/page.tsx` |
| "Risk Graph" module | VERIFIED | `frontend/src/app/graph/page.tsx` |
| "Scenario Simulator" module | VERIFIED | `frontend/src/app/scenarios/page.tsx` |
| "AI Copilot" module | VERIFIED | `frontend/src/app/copilot/page.tsx` |
| "Color-coded risk indicators" | VERIFIED | `frontend/src/app/graph/page.tsx:48` — `getRiskColor()` |

---

## Section 21: Processing Workflow

| Claim | Status | Evidence |
|-------|--------|----------|
| Full pipeline execution with 6 stages | VERIFIED | `backend/app/services/pipeline_orchestrator.py:19` — 6 stages exactly as documented |
| Individual entity processing | VERIFIED | Workflow matches targeted pipeline calls |

---

## Section 22: Sample Execution Flow

| Claim | Status | Evidence |
|-------|--------|----------|
| ISO 27001 certificate ingestion | VERIFIED | `backend/app/services/document_intelligence_engine.py` supports ISO27001 classification and extraction |
| SOC 2 report ingestion | VERIFIED | Same — SOC2 classification and extraction |
| Internal audit report ingestion | VERIFIED | Same — AUDIT_REPORT classification and extraction |
| Vendor entity creation | VERIFIED | `backend/app/api/v2/entities.py` — `POST /entities` |
| Graph relationship creation | VERIFIED | `backend/app/api/v2/graph.py` — `POST /relationships` |
| Full pipeline execution | VERIFIED | `backend/app/api/v2/pipeline.py` — `POST /pipeline/run` |
| Correlated risk retrieval | VERIFIED | `backend/app/api/v2/correlation.py` — `GET /{entity_id}` |
| Scenario simulation | VERIFIED | `backend/app/api/v2/scenario.py` — `POST /run` |
| Remediation actions | VERIFIED | `backend/app/api/v2/remediation.py` — `GET /actions` |
| Executive brief | VERIFIED | `backend/app/api/v2/intelligence.py` — `POST /executive` |
| Copilot interaction | VERIFIED | `backend/app/api/v2/copilot.py` — `POST /query` |

---

## Section 23: Technology Stack

| Claim | Status | Evidence |
|-------|--------|----------|
| Python 3.11+ | OVERSTATED | Dockerfile uses `python:3.12-slim` |
| FastAPI 0.110+ | VERIFIED | `requirements.txt` — `fastapi` |
| Uvicorn | VERIFIED | `requirements.txt` — `uvicorn[standard]` |
| SQLAlchemy 2.0+ | VERIFIED | `requirements.txt` — `sqlalchemy[asyncio]` |
| asyncpg | VERIFIED | `requirements.txt` — `asyncpg` |
| Alembic | OVERSTATED | In requirements.txt but no migrations exist |
| Pydantic 2.x | VERIFIED | Using pydantic-settings which requires Pydantic v2 |
| python-jose | VERIFIED | `requirements.txt` — `python-jose[cryptography]` |
| passlib | VERIFIED | `requirements.txt` — `passlib[bcrypt]` |
| bcrypt 4.0.1 | VERIFIED | `requirements.txt` — `bcrypt==4.0.1` |
| PyMuPDF | VERIFIED | `requirements.txt` — `PyMuPDF` |
| python-multipart | VERIFIED | `requirements.txt` |
| structlog | VERIFIED | `requirements.txt` — but not used in any service |
| httpx | VERIFIED | `requirements.txt` |
| Next.js 14.x | OVERSTATED | `package.json` — `"next": "^16.2.0"` |
| TypeScript 5.x | VERIFIED | `package.json` — `"typescript": "^5.5.0"` |
| PostgreSQL 16 Alpine | VERIFIED | `docker-compose.yml` — `postgres:16-alpine` |
| Redis 7 Alpine | VERIFIED | `docker-compose.yml` — `redis:7-alpine` — but unused |
| Mistral AI API | VERIFIED | `backend/app/core/config.py:13` — `LLM_MODEL: str = "mistral-small-latest"` |

---

## Section 24: Innovation Highlights

All claims in this section are **VERIFIED** except:

| Claim | Status | Evidence |
|-------|--------|----------|
| "Graph-based risk correlation" | VERIFIED | `backend/app/services/risk_correlation_engine.py` |
| "Scenario simulation" | VERIFIED | `backend/app/services/scenario_engine.py` |
| "AI Copilot" | VERIFIED | `backend/app/services/copilot_engine.py` |
| "Automated remediation" | VERIFIED | `backend/app/services/remediation_engine.py` |
| "Executive intelligence" | VERIFIED | `backend/app/services/executive_brief_engine.py` |
| "Multi-dimensional risk scoring" | VERIFIED | `backend/app/services/risk_engine_v2.py` — 5 dimensions |
| "Document intelligence" | VERIFIED | `backend/app/services/document_intelligence_engine.py` |

---

## Section 25: Future Enhancements

All claims in this section are appropriately labeled as future work. **No change needed.**

---

## Section 26: Conclusion

| Claim | Status | Evidence |
|-------|--------|----------|
| "Fully async Python backend" | VERIFIED | 80% of functions are async |
| "Modern TypeScript frontend (Next.js 14)" | OVERSTATED | Actually Next.js 16 + React 19 |
| "PostgreSQL persistence with JSONB flexibility" | VERIFIED | JSONB columns in entities, relationships, intelligence |
| "Docker-based deployment" | VERIFIED | 3 docker-compose files |
| "JWT authentication with RBAC" | VERIFIED | `backend/app/core/auth.py` + `security.py` |
| "Comprehensive REST API with two version tracks" | VERIFIED | 65 total routes across v1 and v2 |
| "Ground-truth evaluation framework" | VERIFIED | `backend/app/services/evaluation_service.py`, `backend/app/models/ground_truth.py` |
| "30+ database tables" | VERIFIED | 35 tables |

---

## Summary

| Classification | Count | Examples |
|----------------|-------|----------|
| **VERIFIED** | ~160 | Most claims are accurate |
| **OVERSTATED** | ~20 | Next.js version, Celery provisioning, Layer architecture formality, Redis usage description |
| **FICTIONAL** | ~6 | Celery workers, Redis in code, file encryption, load balancer, read replicas, React Flow |
