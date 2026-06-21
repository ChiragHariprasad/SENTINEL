# SENTINEL

## AI-Powered Enterprise Risk Intelligence Platform

### Verified Technical Architecture & Design Document

**Document Version:** 3.0 (Verified against codebase)  
**Classification:** Confidential — Enterprise Architecture Review  

---

## Table of Contents

1. Executive Summary  
2. Problem Statement  
3. Industry Challenges  
4. Solution Overview  
5. Platform Architecture  
6. Component Architecture  
7. Data Flow  
8. AI Pipeline  
9. Risk Intelligence Engine  
10. Risk Graph Engine  
11. Risk Correlation Engine  
12. Remediation Engine  
13. Scenario Simulation Engine  
14. Copilot Architecture  
15. API Architecture  
16. Database Architecture  
17. Security Architecture  
18. Scalability Design  
19. User Interface Design  
20. Processing Workflow  
21. Sample Execution Flow  
22. Technology Stack  
23. Innovation Highlights  
24. Future Enhancements  
25. Conclusion  

---

## 1. Executive Summary

SENTINEL is an AI-powered Enterprise Risk Intelligence Platform that transforms traditional Vendor Risk Management (VRM) from static compliance tracking into an intelligent, graph-based risk intelligence system. The platform ingests PDF documents, CSV files, JSON data, audit reports, compliance certificates, SOC reports, and security questionnaires, automatically extracting entities, controls, risks, and relationships to build a unified risk graph.

The architecture follows a service-oriented modular design on FastAPI, with async SQLAlchemy for PostgreSQL persistence, rule-based AI engines, and a modern Next.js frontend. The platform implements graph-based risk correlation, scenario simulation, automated remediation, executive intelligence reporting, and an AI-powered Copilot — all without requiring external LLM dependencies for core functionality.

**Current Status:** All core features described in this document are implemented and tested. Planned enhancements are explicitly labeled as such.

---

## 2. Problem Statement

Enterprise risk management today is fragmented across siloed tools, spreadsheets, and manual processes. Organizations manage hundreds to thousands of vendor relationships, each with complex dependencies on internal systems, data access patterns, compliance certifications, and contractual obligations. When a vendor suffers a breach, security teams must manually trace which systems are affected, which data is exposed, and which users are impacted.

The core problem is that risk propagates through interconnected systems. Traditional VRM systems treat each vendor as an isolated record and cannot model propagation paths. Organizations lack the ability to simulate "what-if" scenarios before incidents occur.

---

## 3. Industry Challenges

SENTINEL addresses six structural challenges: data fragmentation across procurement, compliance, and security tools; static risk models that ignore connected entities; limited automation in document review and risk assessment; no predictive capability for anticipating threats; compliance fragmentation across multiple frameworks; and communication gaps between technical risk data and business intelligence.

---

## 4. Solution Overview

SENTINEL provides eight core capabilities through a graph-based risk intelligence model:

| Capability | Implementation |
|---|---|
| Document Intelligence | PDF OCR + keyword classification + regex extraction. 6 document types supported. |
| Entity Extraction | Vendors, systems, users, controls, evidence, exceptions, certifications, documents. |
| Relationship Discovery | 12 typed, weighted relationship types. |
| Risk Correlation | BFS graph traversal with decay-weighted neighbor contribution. |
| Anomaly Detection | 14 rule-based detectors across vendor, identity, and config domains. |
| Remediation Orchestration | Template-based action generation with owner assignment and deduplication. |
| Scenario Simulation | 6 scenario types with blast radius computation. |
| AI Copilot | 6-intent rule-based query engine (no external LLM required for v2). |

---

## 5. Platform Architecture

The architecture follows a modular service design with independent, composable services:

```
+---------------------------------------------------------------+
|                        FRONTEND (Next.js 16)                   |
|  Dashboard | Vendors | Graph | Scenarios | Copilot | ...      |
+---------------------------+-----------------------------------+
                            |
                    API Gateway (FastAPI)
                            |
          +-----------------+------------------+
          |                                    |
+---------v---------+              +----------v----------+
|   V1 API Layer    |              |   V2 API Layer      |
|  (vendor-centric) |              |  (entity-centric)   |
|  32 routes        |              |  33 routes          |
+-------------------+              +---------------------+
          |                                    |
          +-----------------+------------------+
                            |
               +-----------v-----------+
               |    Service Layer       |
               |   (22 service modules) |
               +-----------+-----------+
                           |
              +------------+------------+
              |                         |
     +--------v--------+      +--------v--------+
     |  PostgreSQL 16   |      |  File Storage   |
     |  (35 tables)     |      |  (local / S3)   |
     +------------------+      +-----------------+
```

**Key design decisions:**
- All services share a single database (no microservice network overhead)
- Async SQLAlchemy for non-blocking database access
- JWT authentication on all endpoints (except health and login)
- Rule-based AI engines (no external LLM dependency for core risk functions)
- PDF extraction via PyMuPDF

---

## 6. Component Architecture

### 6.1 Document Intelligence Service

**File:** `backend/app/services/document_intelligence_engine.py`  
**Endpoints:** `backend/app/api/v2/documents.py`

Handles file upload, OCR via PyMuPDF, keyword-based document classification, and type-specific extraction:
- **CONTRACT:** SLA clauses, data retention, liability caps, termination terms, GDPR references
- **SOC2:** Issue/expiry dates, control IDs and descriptions
- **ISO27001:** Issue/expiry dates, control references
- **AUDIT_REPORT:** Findings, severity levels, recommendations
- **POLICY:** Policy sections, compliance obligations

The `build_graph_from_document()` function creates DOCUMENT entities linked to CONTROL entities via HAS_FINDING relationships, incorporating document findings into the risk graph.

### 6.2 Entity Service

**File:** `backend/app/services/graph_service.py` (entities portion)  
**Endpoints:** `backend/app/api/v2/entities.py`

Full CRUD for risk entities with filtering by type, status, and name search. Entities are stored in the `risk_entities` table with a flexible JSONB `attributes` column.

### 6.3 Graph Service

**File:** `backend/app/services/graph_service.py`  
**Endpoints:** `backend/app/api/v2/graph.py`

Manages typed, weighted relationships between entities. Provides two graph traversal operations:
- `get_entity_graph(entity_id, depth)` — BFS subgraph retrieval for visualization
- `get_impact_path(entity_id)` — Single-direction BFS for risk propagation paths

### 6.4 Risk Engine (V2)

**File:** `backend/app/services/risk_engine_v2.py`  
**Endpoints:** `backend/app/api/v2/risk.py`

Computes risk scores across five dimensions with entity-type-specific logic:

| Entity Type | Key Scoring Factors |
|---|---|
| VENDOR | Breach history, expired cert ratio, contract status, annual spend, data sensitivity |
| SYSTEM | Default scores (varies by dimension) |
| USER | Default scores, access level |
| CONTROL | Compliance focus |
| CONFIG | Security focus |

Risk tiers: CRITICAL (>80), HIGH (61-80), ELEVATED (41-60), LOW (<=40), MINIMAL

### 6.5 Risk Correlation Engine

**File:** `backend/app/services/risk_correlation_engine.py`  
**Endpoints:** `backend/app/api/v2/correlation.py`

Computes correlated risk by traversing the risk graph:

```
correlated_risk = min(base_risk + neighbor_risk, 100)

For each connected entity at depth <= max_depth:
    contributed = neighbor.risk_score * rel.weight * decay / 100
    neighbor_risk += contributed
```

The `reasoning` field stores per-entity contribution records for full explainability.

**Current Implementation:** BFS with depth limit (default 2). Simple decay (halved per level).  
**Planned Enhancement:** Variable decay rates per relationship type, cycle detection optimization.

### 6.6 Anomaly Engine (V2)

**File:** `backend/app/services/anomaly_engine_v2.py`  
**Endpoints:** `backend/app/api/v2/anomalies.py`

Evaluates 14 rule-based detectors against entity context:
- **Vendor domain (6):** EXPIRED_CERTIFICATION, HIGH_RISK_SCORE, UNDER_INVESTIGATION, BREACHED_VENDOR, ELEVATED_RISK, CONTRACT_EXPIRED
- **Identity domain (4):** AFTER_HOURS_ACCESS, EXCESSIVE_FAILURES, PRIVILEGE_ESCALATION, STALE_ACCOUNT
- **Config domain (4):** ENCRYPTION_DISABLED, LOGGING_DISABLED, COMPLIANCE_DRIFT, PUBLIC_ACCESS

**Current Implementation:** Rule-based detection with lambda conditions.  
**Planned Enhancement:** ML-based anomaly detection (Isolation Forest, autoencoders).

### 6.7 Remediation Engine

**File:** `backend/app/services/remediation_engine.py`  
**Endpoints:** `backend/app/api/v2/remediation.py`

Converts anomaly findings into structured action plans using 14 templates. Each template specifies actions, owner, priority, and due date. Deduplication prevents duplicate actions for the same anomaly.

### 6.8 Scenario Simulation Engine

**File:** `backend/app/services/scenario_engine.py`  
**Endpoints:** `backend/app/api/v2/scenario.py`

Supports six scenario types with deterministic risk projection:

| Scenario | Risk Increase | Severity |
|---|---|---|
| Vendor Breach | 35% | CRITICAL |
| Vendor Failure | 50% | CRITICAL |
| Contract Termination | 20% | HIGH |
| Certification Expiry | 25% | HIGH |
| Identity Compromise | 30% | CRITICAL |
| Configuration Drift | 15% | MEDIUM |

**Current Implementation:** Deterministic percentage-based projection. BFS blast radius up to depth 5.  
**Planned Enhancement:** Monte Carlo simulation with confidence intervals. Multi-event concurrent scenarios.

### 6.9 Blast Radius Engine

**File:** `backend/app/services/blast_radius_engine.py`  
**Endpoint:** `backend/app/api/v2/blast_radius.py`

BFS traversal from a source entity, classifying impacted entities by type (SYSTEM, CONTROL, USER, VENDOR) up to configurable depth (default 5).

### 6.10 Intelligence Engine

**File:** `backend/app/services/intelligence_engine.py`  
**Endpoints:** `backend/app/api/v2/intelligence.py`

Two intelligence products:
- **Daily Intelligence Snapshot:** Entity counts, risk distribution, anomaly trends
- **Priority Actions:** Unresolved critical/high anomalies + open remediation actions

### 6.11 Executive Brief Engine

**File:** `backend/app/services/executive_brief_engine.py`  
**Endpoint:** `backend/app/api/v2/intelligence.py (POST /executive)`

Generates portfolio-level executive summaries with:
- Portfolio risk score and tier distribution
- Top 5 highest-risk entities
- Anomaly overview and remediation status
- Automated strategic recommendations

### 6.12 Timeline Engine

**File:** `backend/app/services/timeline_engine.py`  
**Endpoints:** `backend/app/api/v2/timeline.py`

Aggregates events from risk score changes, anomaly detections, remediation actions, and custom risk events into a unified chronological timeline. Supports entity-level and portfolio-level views.

### 6.13 Pipeline Orchestrator

**File:** `backend/app/services/pipeline_orchestrator.py`  
**Endpoint:** `backend/app/api/v2/pipeline.py`

Coordinates 6-stage processing within a single database transaction:
1. Risk Calculation → 2. Anomaly Detection → 3. Risk Correlation → 4. Remediation → 5. Intelligence → 6. Timeline

**Current Implementation:** Synchronous async pipeline within FastAPI request lifecycle.  
**Planned Enhancement:** Delegation to Celery workers for long-running pipelines.

### 6.14 Copilot Engine (V2)

**File:** `backend/app/services/copilot_engine.py`  
**Endpoint:** `backend/app/api/v2/copilot.py`

Intent-driven query engine with 6 intents detected via regex:

| Intent | Handler |
|---|---|
| risk_explanation | Fetches correlated risk with neighbor contributions |
| remediation | Generates or lists remediation actions |
| simulation | Runs scenario simulation |
| prioritization | Returns priority actions |
| executive_summary | Generates executive brief |
| entity_lookup | Returns entity details |

**Current Implementation:** Fully rule-based. No external LLM required.  
**Planned Enhancement:** LLM integration for complex multi-intent queries.

### 6.15 Copilot Service (V1)

**File:** `backend/app/services/copilot_service.py`, `backend/app/ai/copilot.py`  
**Endpoint:** `backend/app/api/v1/copilot/query`

LLM-based SQL generation using Mistral API. Maps natural language questions to SQL queries against the database. Falls back to template-based responses when LLM is unavailable.

---

## 7. Data Flow

### 7.1 Document Ingestion

```
Upload PDF → Extract text (PyMuPDF) → Classify document type
→ Run type-specific extraction → Store findings
→ Build graph entities and relationships
```

### 7.2 Risk Intelligence Pipeline

```
Score entity (5 dimensions) → Store score + history
→ Detect anomalies (14 rules) → Run risk correlation (BFS)
→ Generate remediation actions → Update intelligence snapshots
→ Record timeline events
```

### 7.3 Scenario Simulation

```
Select entity + scenario type → Fetch current risk
→ Traverse graph (BFS, depth 5) → Project risks
→ Compute blast radius → Store results → Return to UI
```

---

## 8. AI Pipeline

SENTINEL uses a combination of rule-based intelligence and optional LLM integration:

| Component | Approach | LLM Required? |
|---|---|---|
| Document Classification | Keyword frequency scoring | No |
| Entity Extraction | Regex pattern matching | No |
| Risk Scoring | Weighted formula | No |
| Risk Correlation | BFS graph traversal | No |
| Anomaly Detection | Rule conditions (lambdas) | No |
| Remediation | Template-based | No |
| Copilot V2 | Intent detection (regex) + service dispatch | No |
| Copilot V1 | Intent matching + SQL generation | Yes (Mistral) |
| Contract Analysis | Structured extraction | Yes (Mistral, with mock fallback) |

---

## 9. Risk Intelligence Engine

Three automated intelligence products:

**Daily Intelligence Snapshot** (`intelligence_engine.py:generate_daily_intelligence()`):
- Entity counts, average risk score, critical/high lists, anomaly distribution

**Priority Actions** (`intelligence_engine.py:generate_priorities()`):
- Unresolved critical/high anomalies, open actions, sorted by severity

**Executive Brief** (`executive_brief_engine.py:generate_executive_brief()`):
- Portfolio risk score, tier distribution, top risks, recommendations

---

## 10. Risk Graph Engine

The risk graph models the enterprise ecosystem as a directed graph:

- **Nodes:** 8 entity types (VENDOR, USER, SYSTEM, CONTROL, EVIDENCE, EXCEPTION, CONFIG, DOCUMENT)
- **Edges:** 12 relationship types with weights (USES 0.8, DEPENDS_ON 0.7, HAS_ACCESS_TO 1.0, etc.)
- **Traversal:** BFS with configurable depth

**Current Implementation:** Nodes are displayed as a searchable list with expandable cards showing connected entities and relationship details. Each node shows a color-coded risk indicator.

---

## 11. Risk Correlation Engine

**File:** `backend/app/services/risk_correlation_engine.py`

Traverses the risk graph to compute the complete risk exposure of each entity, accounting for contributions from connected entities.

**Algorithm:**
1. Start with entity's base risk score
2. BFS through outbound relationships (up to depth 2)
3. For each connected entity: `contribution = neighbor_score * rel_weight * decay / 100`
4. `correlated_risk = min(base + neighbor_contributions, 100)`
5. Store with full reasoning chain (each contribution recorded with entity name, score, relationship, weight)

**Sample reasoning output:**
```json
{
  "base_risk": 45.0,
  "neighbor_risk": 12.35,
  "correlated_risk": 57.35,
  "contributions": [{
    "entity_name": "Primary Storage",
    "entity_type": "SYSTEM",
    "risk_score": 75.0,
    "relationship": "DEPENDS_ON",
    "weight": 0.7,
    "contributed_score": 5.25
  }]
}
```

---

## 12. Remediation Engine

**File:** `backend/app/services/remediation_engine.py`

14 remediation templates map anomaly types to structured action plans:

| Anomaly Type | Owner | Priority |
|---|---|---|
| BREACHED_VENDOR | Security Team | CRITICAL |
| EXPIRED_CERTIFICATION | Compliance Team | HIGH |
| PRIVILEGE_ESCALATION | Security Team | CRITICAL |
| ENCRYPTION_DISABLED | Infrastructure Team | CRITICAL |
| PUBLIC_ACCESS | Security Team | CRITICAL |
| COMPLIANCE_DRIFT | Compliance Team | HIGH |
| (9 more) | ... | ... |

Each run deduplicates against existing open actions for the same entity+anomaly combination.

---

## 13. Scenario Simulation Engine

**File:** `backend/app/services/scenario_engine.py`

Executes what-if analysis by:
1. Validating entity and scenario type
2. Computing current risk score
3. Traversing graph (BFS, depth 5) to find impacted entities
4. Applying scenario-specific risk increase to source entity
5. Applying reduced increase (50%) to impacted entities
6. Computing blast radius by entity type counts
7. Storing complete scenario result

---

## 14. Copilot Architecture

### Current Implementation (Rule-based, V2)

```
User Question → Intent Detection (regex, 6 patterns)
→ Entity Resolution (ILIKE search) → Handler Dispatch
→ Engine Execution → Response Formatting
```

No external LLM required. All responses are generated from the platform's own data through its APIs.

### V1 Copilot (LLM-based)

The V1 copilot (`backend/app/ai/copilot.py`) uses Mistral API for SQL generation from natural language, with template fallback when the LLM is unavailable. This is a separate endpoint at `/api/v1/copilot/query`.

---

## 15. API Architecture

Two API versions:

| Version | Prefix | Routes | Focus |
|---|---|---|---|
| V1 | `/api/v1` | 32 | Vendor-centric operations |
| V2 | `/api/v2` | 33 | Entity-centric intelligence |

**All endpoints require Bearer JWT authentication** except:
- `GET /api/v1/health`
- `POST /api/v1/auth/signup`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`

**Standard response format:**
```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

---

## 16. Database Architecture

**Database:** PostgreSQL 16 via asyncpg  
**Tables:** 35 tables across v1 and v2 models

**Core tables (V2 architecture):**
- `risk_entities` — Unified graph nodes with JSONB attributes
- `risk_relationships` — Typed, weighted edges between entities
- `risk_scores_v2` — Entity risk scores (5 dimensions)
- `correlated_risks` — Graph-based correlated risk with reasoning
- `anomaly_events_v2` — Detected anomalies with severity and explanation
- `remediation_actions` — Generated action plans
- `scenario_runs` — Simulation results
- `intelligence_snapshots` — Daily intelligence and executive briefs
- `risk_events` — Timeline events

**Key design features:**
- UUID primary keys throughout
- JSONB for flexible attribute storage
- FK constraints for referential integrity
- Indexed foreign keys for graph traversal performance

---

## 17. Security Architecture

| Component | Implementation |
|---|---|
| Authentication | JWT access tokens (15min) + refresh tokens (24hr) |
| Password hashing | bcrypt via passlib |
| Token signing | HS256 |
| RBAC | 3 roles: admin, analyst, executive |
| API Security | Bearer token required on all routes (except 4 public) |
| Input validation | Pydantic schemas on all endpoints |
| Error handling | Global exception handler (no info leakage) |
| CORS | Configurable origins |
| File storage | Local filesystem or S3/MinIO |

---

## 18. Scalability Design

**Current Implementation:**
- Stateless FastAPI service (can be horizontally scaled behind load balancer)
- Async database operations prevent connection blocking
- Paginated API responses (default 50, max 200)
- Connection pooling via SQLAlchemy

**Planned Enhancement:**
- Celery workers for long-running tasks (large document processing, full pipeline)
- Redis for caching and rate limiting
- PostgreSQL read replicas for reporting queries
- Time-based partitioning for event tables

---

## 19. User Interface Design

**Framework:** Next.js 16.2 + React 19 + TypeScript + Tailwind CSS  
**Pages implemented:**

| Page | Route | Description |
|---|---|---|
| Login | `/login` | Email/password authentication |
| Dashboard | `/dashboard` | Portfolio KPIs, evaluation metrics, risk distribution |
| Vendors | `/vendors` | Searchable/filterable registry with CRUD |
| Risk Register | `/risk` | Vendors ranked by risk score |
| Risk Graph | `/graph` | Entity graph with expandable node cards |
| Scenario Simulator | `/scenarios` | Entity selector, scenario run, results |
| AI Copilot | `/copilot` | Chat interface with suggestion chips |
| Anomalies | `/anomalies` | Anomaly search and severity view |
| Alerts | `/alerts` | Alert management with resolve action |
| Certifications | `/certifications` | Certification status tracking |
| Contracts | `/contracts` | Upload and AI analysis |
| Evaluation | `/evaluation` | Precision/recall/F1 metrics |
| Reports | `/reports` | Generated report listing |
| CSV Import | `/import` | Bulk vendor import |
| Admin Users | `/admin/users` | User management |

---

## 20. Processing Workflow

### Full Pipeline

```
POST /api/v2/pipeline/run
  Stage 1: Risk Calculation (all active entities)
  Stage 2: Anomaly Detection (all active entities)
  Stage 3: Risk Correlation (all scored entities)
  Stage 4: Remediation Generation (new anomalies)
  Stage 5: Intelligence Snapshots (daily, priorities, executive)
  Stage 6: Timeline Recording (all scored entities)
```

All stages run within a single database transaction. Failure at any stage triggers a full rollback.

---

## 21. Sample Execution Flow

Demonstrated with ISO 27001 certificate, SOC 2 report, and audit report:

1. **Upload documents:** 3 POST calls to `/api/v2/documents/upload`
2. **Analyze:** `/api/v2/documents/{id}/analyze` — extracts findings
3. **Build graph:** `/api/v2/documents/{id}/build-graph` — creates entities + relationships
4. **Create vendor entity:** `POST /api/v2/entities`
5. **Create relationships:** `POST /api/v2/graph/relationships`
6. **Run pipeline:** `POST /api/v2/pipeline/run` — risk scoring, anomaly detection, correlation, remediation, intelligence
7. **View results:** Correlation, scenario, remediation, executive brief, copilot endpoints

All steps are verified against implemented API endpoints.

---

## 22. Technology Stack

### Backend
| Technology | Version | Purpose |
|---|---|---|
| Python | 3.12 | Runtime |
| FastAPI | Latest | Web framework |
| Uvicorn | Latest | ASGI server |
| SQLAlchemy | 2.x (async) | ORM |
| asyncpg | Latest | PostgreSQL async driver |
| PyMuPDF (fitz) | Latest | PDF text extraction |
| python-jose | Latest | JWT handling |
| passlib | Latest | Password hashing |
| httpx | Latest | Async HTTP (LLM calls) |

### Frontend
| Technology | Version | Purpose |
|---|---|---|
| Next.js | 16.2 | React framework |
| React | 19 | UI library |
| TypeScript | 5.x | Type safety |
| Tailwind CSS | 3.x | Styling |
| Lucide React | Latest | Icons |
| recharts | Latest | Charts |

### Infrastructure
| Technology | Version | Purpose |
|---|---|---|
| PostgreSQL | 16 Alpine | Database |
| Redis | 7 Alpine | Configured, not yet used in code |
| Docker | Latest | Containerization |
| MinIO | Latest | S3-compatible storage (standalone) |

### AI/LLM
| Technology | Purpose | Status |
|---|---|---|
| Mistral AI | V1 copilot + contract analysis | Optional, with fallback |
| Rule engine | V2 copilot, anomaly detection, scoring | Primary, no LLM needed |

---

## 23. Innovation Highlights

### Graph-Based Risk Correlation
Traditional VRM: Isolated vendor scoring → SENTINEL: BFS traversal with weighted neighbor contributions and explainable reasoning chain.

### Scenario Simulation
Traditional VRM: Reactive incident response → SENTINEL: 6 deterministic what-if scenarios with blast radius computation.

### Rule-Based AI Copilot
Traditional VRM: Manual dashboard navigation → SENTINEL: 6-intent conversational interface, fully rule-based, zero external dependencies.

### Automated Remediation
Traditional VRM: Manual ticket creation → SENTINEL: 14 template-driven action plans with owner assignment and deduplication.

### Automated Executive Intelligence
Traditional VRM: Manual report compilation → SENTINEL: Portfolio risk summary with automated strategic recommendations.

### Multi-Dimensional Risk Scoring
Traditional VRM: Single-dimension scoring → SENTINEL: 5 dimensions (security, compliance, operational, financial, access) with entity-type-specific algorithms.

### Document Intelligence
Traditional VRM: Manual document review → SENTINEL: Automated PDF classification, extraction, and graph incorporation.

---

## 24. Future Enhancements

These features are planned but not yet implemented:

- **Celery Workers:** Delegation of long-running tasks to background workers
- **Redis Caching:** Cache intelligence snapshots and frequent queries
- **ML Anomaly Detection:** Complement rule-based detection with ML models
- **WebSocket Push:** Real-time notifications for new anomalies
- **React Flow Graph:** Visual canvas-based graph exploration
- **Executive Timeline Page:** Dedicated frontend for timeline visualization
- **Remediation Center Page:** Standalone remediation management UI
- **Advanced Graph Analytics:** Community detection, centrality analysis
- **SOAR Integration:** ServiceNow, Jira, PagerDuty connectors
- **Multi-Tenancy:** Organization-level isolation
- **Compliance Framework Mapping:** Automated control-to-framework alignment

---

## 25. Conclusion

SENTINEL delivers a complete risk intelligence platform with:

| Aspect | Detail |
|---|---|
| Backend services | 22 modules, 80% async |
| API endpoints | 65 across v1 (32) and v2 (33) |
| Database tables | 35 with JSONB, UUID, FK constraints |
| AI rules | 14 deterministic detectors across 3 domains |
| Remediation templates | 14 with owner, priority, due date |
| Scenario types | 6 with BFS blast radius |
| Copilot intents | 6 with fully rule-based execution |
| Frontend pages | 15 with loading/error/empty states |
| Test files | 20+ backend + 5 frontend + E2E + load + chaos |
| Authentication | JWT with RBAC (3 roles) |
| LLM integration | Optional (Mistral), with fallback for all features |

The platform is containerized via Docker Compose with PostgreSQL persistence, ready for deployment and evaluation.

---

*Document prepared for Enterprise Architecture Review — Verified against codebase v3.0*  
*SENTINEL Platform — Confidential*
