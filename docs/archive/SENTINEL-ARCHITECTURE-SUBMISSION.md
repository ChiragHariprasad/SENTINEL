# SENTINEL

## AI-Powered Enterprise Risk Intelligence Platform

### Technical Architecture & Design Document

**Document Version:** 2.0  
**Classification:** Confidential — Enterprise Architecture Review  
**Prepared For:** Enterprise Security Leaders, CISOs, Risk Officers, Technical Judges, Software Architects, AI/ML Reviewers  

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
16. Worker Architecture  
17. Database Architecture  
18. Security Architecture  
19. Scalability Design  
20. User Interface Design  
21. Processing Workflow  
22. Sample Execution Flow  
23. Technology Stack  
24. Innovation Highlights  
25. Future Enhancements  
26. Conclusion  

---

## 1. Executive Summary

SENTINEL is an AI-powered Enterprise Risk Intelligence Platform that transforms traditional Vendor Risk Management (VRM) from static compliance tracking into an intelligent, graph-based risk intelligence system. The platform ingests diverse data sources—PDF documents, CSV files, JSON feeds, audit reports, compliance certificates, SOC reports, and security questionnaires—and automatically extracts entities, controls, risks, dependencies, and relationships to build a unified risk graph.

The architecture follows a ten-layer intelligence model spanning document ingestion, entity extraction, relationship discovery, graph construction, risk correlation, anomaly detection, remediation orchestration, scenario simulation, executive intelligence, and an AI-powered Copilot. Each layer operates as an independent service within a microservice-inspired modular architecture built on FastAPI, with asynchronous processing via Celery and Redis, persistent storage in PostgreSQL, and a modern Next.js frontend.

SENTINEL addresses the fundamental limitation of existing VRM platforms: they store vendor information but cannot discover hidden risk propagation paths, correlate risks across interconnected entities, simulate the impact of vendor breaches, or provide intelligent remediation guidance. By modeling the enterprise ecosystem as a directed graph of risk entities connected by typed, weighted relationships, SENTINEL enables risk propagation analysis, blast radius computation, scenario simulation, and AI-driven decision support.

The platform has been implemented and tested with real-world document types including ISO 27001 certificates, SOC 2 reports, internal audit findings, vendor contracts, and security policies. Evaluation metrics demonstrate high precision and recall in entity extraction, risk classification, and anomaly detection.

---

## 2. Problem Statement

Enterprise risk management today is fragmented across siloed tools, spreadsheets, and manual processes. Organizations manage hundreds to thousands of vendor relationships, each with complex dependencies on internal systems, data access patterns, compliance certifications, and contractual obligations. When a vendor suffers a breach, the security team must manually trace which systems are affected, which data is exposed, which compliance obligations are breached, and which users are impacted. This manual process is slow, error-prone, and often incomplete.

The core problem is that risk is not static—it propagates. A vulnerability in a third-party vendor can cascade through interconnected systems to affect entirely different parts of the organization. Traditional VRM systems treat each vendor as an isolated record and cannot model these propagation paths. Furthermore, organizations lack the ability to simulate "what-if" scenarios to understand the potential impact of vendor failures before they occur.

Key pain points include:
- **No risk graph visibility:** Organizations cannot visualize how vendors, systems, users, and controls connect.
- **No risk propagation analysis:** The cascading impact of a vendor breach cannot be calculated.
- **No scenario simulation:** Security teams cannot model the effect of contract terminations, certification expirations, or identity compromises.
- **No automated remediation:** Findings require manual triage and action assignment.
- **No executive intelligence:** Board-level risk reporting is a manual compilation effort.
- **No AI copilot:** Risk analysts lack conversational access to their risk posture.

---

## 3. Industry Challenges

The enterprise risk management landscape faces several structural challenges that SENTINEL addresses:

**Challenge 1: Data Fragmentation**  
Risk data exists across procurement systems, compliance platforms, vulnerability scanners, identity providers, and cloud infrastructure. No single platform unifies these data sources into a coherent risk model.

**Challenge 2: Static Risk Models**  
Traditional VRM platforms compute risk scores at a point in time using limited factors (e.g., criticality, spend). They do not account for the risk contributions of connected entities, creating an incomplete risk picture.

**Challenge 3: Limited Automation**  
The vast majority of risk assessment workflows remain manual. Document review, control mapping, evidence verification, and risk scoring require significant human effort, creating bottlenecks and inconsistency.

**Challenge 4: No Predictive Capability**  
Organizations react to incidents rather than anticipating them. Without simulation capabilities, security teams cannot quantify the potential impact of emerging threats on their vendor ecosystem.

**Challenge 5: Compliance Fragmentation**  
Organizations must maintain compliance with multiple frameworks (SOC 2, ISO 27001, PCI DSS, HIPAA, GDPR) simultaneously. Tracking certification status, control coverage, and compliance drift across hundreds of vendors is impractical with spreadsheet-based approaches.

**Challenge 6: Communication Gaps**  
Technical risk findings must be translated into business language for executives and board members. The gap between detailed technical risk data and strategic business intelligence remains largely unaddressed.

---

## 4. Solution Overview

SENTINEL addresses these challenges through a unified platform that ingests, extracts, correlates, simulates, and reports on enterprise risk. The platform's core innovation is its graph-based risk intelligence model, which treats every entity in the enterprise ecosystem as a node in a directed graph, with typed and weighted relationships representing the connections between them.

**Core Capabilities:**

| Capability | Description |
|---|---|
| Document Intelligence | Automated extraction of entities, controls, risks, and findings from PDF, CSV, and JSON documents |
| Entity Extraction | Identification of vendors, systems, users, controls, evidence, exceptions, certifications, and configurations |
| Relationship Discovery | Automatic generation of typed relationships (USES, OWNS, DEPENDS_ON, AFFECTS, etc.) |
| Risk Correlation | Graph-traversal-based computation of correlated risk considering connected entity contributions |
| Anomaly Detection | Rule-based detection of security, compliance, identity, and configuration anomalies |
| Remediation Orchestration | Automated generation of action plans with assignment, prioritization, and tracking |
| Scenario Simulation | What-if analysis for breaches, failures, contract termination, certification expiry, identity compromise, and configuration drift |
| Blast Radius Computation | Multi-depth graph traversal to identify all affected entities in a risk event |
| Executive Intelligence | Automated generation of board reports, portfolio summaries, and strategic recommendations |
| AI Copilot | Conversational access to risk intelligence via intent-driven query engine |

**Supported Document Types:**

- SOC 2 Reports
- ISO 27001 Certificates
- Internal Audit Reports
- Vendor Security Policies
- Contracts and SLAs
- Compliance Evidence
- Security Questionnaires
- Vendor Assessment Results
- Raw CSV Data (vendors, identity events, config drifts, exceptions)
- JSON Feeds (API imports)

**Entity Types:**

| Entity Type | Description | Examples |
|---|---|---|
| VENDOR | Third-party service or product provider | Cloud provider, SaaS vendor, consultant |
| SYSTEM | Technical system or application | Database, API gateway, monitoring tool |
| USER | Human user or service account | Employee, contractor, bot |
| CONTROL | Security or compliance control | Access review, encryption, logging |
| EVIDENCE | Supporting documentation for controls | Audit log, screenshot, attestation |
| EXCEPTION | Approved deviation from policy | Security exception, risk acceptance |
| CONFIG | System or infrastructure configuration | Firewall rule, IAM policy |
| CERTIFICATION | Compliance certification | ISO 27001, SOC 2 Type II |
| DOCUMENT | Ingested document artifact | PDF contract, CSV import |

**Relationship Types:**

| Relationship | Default Weight | Description |
|---|---|---|
| USES | 0.8 | Entity A uses Entity B (e.g., Vendor uses System) |
| OWNS | 0.8 | Entity A owns Entity B (e.g., User owns System) |
| DEPENDS_ON | 0.7 | Entity A depends on Entity B |
| PROVIDES | 0.6 | Entity A provides a service to Entity B |
| AFFECTS | 0.8 | Entity A affects the risk posture of Entity B |
| VIOLATES | 0.9 | Entity A violates a control or policy |
| HAS_ACCESS_TO | 1.0 | Entity A has access to Entity B |
| SUPPORTS | 0.5 | Entity A supports Entity B |
| MANAGES | 0.7 | Entity A manages Entity B |
| LOCATED_IN | 0.4 | Entity A is located in Entity B |
| BELONGS_TO | 0.6 | Entity A belongs to Entity B |
| PARENT_OF | 0.7 | Entity A is parent of Entity B |

---

## 5. Platform Architecture

The SENTINEL platform follows a ten-layer intelligence model, each building on the outputs of the previous layer. This layered architecture ensures separation of concerns, independent scalability, and clear data flow boundaries.

```
+------------------------------------------------------------------+
|                     LAYER 10: RISK COPILOT                        |
|  Intent Detection | Entity Lookup | Risk Explanation | Reports   |
+------------------------------------------------------------------+
|                     LAYER 9: EXECUTIVE INTELLIGENCE               |
|  Board Reports | Portfolio Summary | Strategic Recommendations    |
+------------------------------------------------------------------+
|                     LAYER 8: SCENARIO SIMULATOR                   |
|  Breach | Failure | Contract Expiry | Cert Expiry | Config Drift |
+------------------------------------------------------------------+
|                     LAYER 7: REMEDIATION ENGINE                   |
|  Action Templates | Owner Assignment | Priority | Due Dates       |
+------------------------------------------------------------------+
|                     LAYER 6: SECURITY INTELLIGENCE                |
|  Daily Intel | Priority Actions | Anomaly Overview | Risk Trends  |
+------------------------------------------------------------------+
|                     LAYER 5: RISK CORRELATION ENGINE              |
|  Correlated Risk = Base Risk + SUM(Connected Risk * Weight)       |
+------------------------------------------------------------------+
|                     LAYER 4: UNIFIED RISK GRAPH                   |
|  Entities (nodes) + Relationships (edges) + Risk Scores            |
+------------------------------------------------------------------+
|                     LAYER 3: RELATIONSHIP DISCOVERY               |
|  USES | OWNS | DEPENDS_ON | PROVIDES | AFFECTS | VIOLATES        |
+------------------------------------------------------------------+
|                     LAYER 2: ENTITY EXTRACTION                    |
|  Vendors | Systems | Users | Controls | Evidence | Certifications |
+------------------------------------------------------------------+
|                     LAYER 1: DOCUMENT INGESTION                   |
|  PDF OCR | CSV Parsing | JSON Import | Classification | Metadata  |
+------------------------------------------------------------------+
                    DATA SOURCES (PDF, CSV, JSON, API)
```

### Deployment Architecture

```
                   +---------------------+
                   |    Load Balancer    |
                   +----------+----------+
                              |
              +---------------+---------------+
              |                               |
    +---------v--------+           +----------v--------+
    |  Frontend        |           |  API Gateway      |
    |  Next.js         |           |  FastAPI / nginx  |
    |  Port 3000       |           |  Port 8000        |
    +------------------+           +---------+---------+
                                              |
                    +-------------------------+--------------------------+
                    |                         |                          |
        +-----------v--------+    +-----------v--------+    +-----------v--------+
        |  API Services      |    |  Worker Services   |    |  WebSocket         |
        |  FastAPI (sync)   |    |  Celery Workers     |    |  Real-time Events  |
        +--------+-----------+    +--------+-----------+    +--------------------+
                 |                          |
        +--------v-----------+    +--------v-----------+
        |  PostgreSQL 16     |    |  Redis 7           |
        |  Primary DB        |    |  Message Broker    |
        +--------------------+    +--------------------+
```

### Service Topology

```
                    +---------------------+
                    |   API Gateway       |
                    +----------+----------+
                               |
         +---------------------+---------------------+
         |                     |                     |
  +------v------+      +------v------+      +------v------+
  | Auth Service|      | Doc Service |      | Entity Svc  |
  | JWT/RBAC    |      | Upload/OCR  |      | CRUD/Search |
  +-------------+      +-------------+      +-------------+
         |                     |                     |
  +------v------+      +------v------+      +------v------+
  | Graph Svc   |      | Correl Svc  |      | Anomaly Svc |
  | BFS Traverse|      | Risk Prop   |      | Rule Eval   |
  +-------------+      +-------------+      +-------------+
         |                     |                     |
  +------v------+      +------v------+      +------v------+
  | Remed Svc   |      | Scenario Svc|      | Intel Svc   |
  | Action Gen  |      | Sim Engine  |      | Reports     |
  +-------------+      +-------------+      +-------------+
         |                     |
  +------v------+      +------v------+
  | Copilot Svc |      | Timeline Svc|
  | Intent/NLP  |      | Event Log   |
  +-------------+      +-------------+
```

---

## 6. Component Architecture

### 6.1 Document Service

The Document Service handles file ingestion, OCR extraction, document classification, and structured data extraction. It supports PDF, CSV, and JSON formats through specialized ingestion pipelines.

**Key Technologies:** PyMuPDF (fitz), python-multipart, custom NLP patterns  
**Endpoints:** `POST /api/v2/documents/upload`, `GET /api/v2/documents/{id}/findings`, `POST /api/v2/documents/{id}/analyze`

```
Upload PDF
    |
    v
Store raw bytes in filesystem via storage service
    |
    v
Extract text (PyMuPDF for PDF, csv.DictReader for CSV, json.loads for JSON)
    |
    v
Classify document type (CONTRACT, SOC2, ISO27001, AUDIT_REPORT, POLICY, EVIDENCE, GENERIC)
    |
    v
Run type-specific extraction (contract clauses, certification dates, audit findings, policy sections)
    |
    v
Extract risks from findings (CONTRACTUAL, COMPLIANCE, AUDIT)
    |
    v
Build risk graph entities and relationships from document findings
    |
    v
Store findings in document_findings table
```

**Classification Logic:**  
The document classifier uses keyword frequency scoring against predefined patterns for each document type. For example, the presence of "soc 2", "system and organization controls", or "trust service" triggers SOC 2 classification. The highest-scoring type is selected, with a fallback to GENERIC.

**Extraction Strategies:**

| Document Type | Extracted Elements |
|---|---|
| CONTRACT | SLA clauses, data retention periods, liability caps, termination terms, GDPR references |
| SOC 2 | Issue dates, expiry dates, control descriptions, control IDs |
| ISO 27001 | Issue dates, expiry dates, Annex A control mappings |
| AUDIT_REPORT | Audit findings, observation severity, recommendations |
| POLICY | Policy sections, scope, compliance obligations |

**Graph Building from Documents:**  
The `build_graph_from_document` function creates a DOCUMENT entity and links it to CONTROL entities representing findings. Each control entity has a `HAS_FINDING` relationship with a weight of 0.8. This enables the document to be incorporated into the broader risk graph.

### 6.2 Entity Service

The Entity Service provides CRUD operations for risk entities, with support for filtering, search, and pagination. It is the foundation for all graph operations.

**Key Technologies:** SQLAlchemy async, PostgreSQL JSONB  
**Endpoints:** `POST /api/v2/entities`, `GET /api/v2/entities`, `GET /api/v2/entities/{id}`, `PUT /api/v2/entities/{id}`, `DELETE /api/v2/entities/{id}`

**Entity Model:**
```
risk_entities
├── entity_id (UUID, PK)
├── entity_type (VARCHAR 50, indexed)
├── entity_name (VARCHAR 255)
├── external_id (VARCHAR 255, nullable)
├── risk_score (FLOAT, nullable)
├── status (VARCHAR 50, default 'active')
├── attributes (JSONB, nullable)
├── created_at (TIMESTAMPTZ)
└── updated_at (TIMESTAMPTZ)
```

The `attributes` JSONB column stores entity-specific metadata such as vendor criticality, system encryption status, user login patterns, and certification details. This flexible schema allows new entity types and attributes to be added without migrations.

### 6.3 Graph Service

The Graph Service manages entity relationships and provides graph traversal capabilities. It supports creating typed relationships between entities, fetching subgraphs for visualization, and computing impact paths.

**Key Technologies:** SQLAlchemy async, BFS graph traversal  
**Endpoints:** `POST /api/v2/graph/relationships`, `GET /api/v2/graph/entity/{entity_id}?depth=N`, `GET /api/v2/graph/impact-path/{entity_id}`

**Relationship Model:**
```
risk_relationships
├── id (UUID, PK)
├── source_entity_id (UUID, FK -> risk_entities)
├── target_entity_id (UUID, FK -> risk_entities)
├── relationship_type (VARCHAR 100)
├── weight (FLOAT, default 1.0)
├── attributes (JSONB, nullable)
└── created_at (TIMESTAMPTZ)
```

**Subgraph Retrieval:**  
The `get_entity_graph` function performs iterative BFS up to configurable depth. For each entity, it queries both outbound and inbound relationships, collecting nodes and edges. It deduplicates by node ID and edge key (source|type|target). The result is a serializable graph structure suitable for frontend rendering.

**Impact Path Computation:**  
The `get_impact_path` function performs a single-direction BFS from an entity outward, recording the traversal path and relationship details for each visited entity. This provides the blast radius visualization showing how risk propagates through connected entities.

### 6.4 Risk Service (V2)

The Risk Service computes multi-dimensional risk scores for entities using domain-specific scoring functions. It supports five risk dimensions: security, compliance, operational, financial, and access.

**Key Technologies:** SQLAlchemy async, custom scoring algorithms  
**Endpoints:** `POST /api/v2/risk/calculate/{entity_id}`, `GET /api/v2/risk/{entity_id}`

**Scoring Model (risk_scores_v2):**
```
risk_scores_v2
├── id (UUID, PK)
├── entity_id (UUID, FK -> risk_entities)
├── security_score (FLOAT)
├── compliance_score (FLOAT)
├── operational_score (FLOAT)
├── financial_score (FLOAT)
├── access_score (FLOAT)
├── overall_score (FLOAT, not null)
├── risk_tier (VARCHAR 20, not null)
└── generated_at (TIMESTAMPTZ)
```

**Risk Dimension Computation:**

| Entity Type | Security | Compliance | Operational | Financial | Access |
|---|---|---|---|---|---|
| VENDOR | Breach history (25pts each) + criticality (20pts) | Expired cert ratio | Contract status | Annual spend | Data sensitivity + access level |
| SYSTEM | Default 30 | Default 20 | Default 25 | N/A | Default 40 |
| USER | Default 25 | N/A | Default 10 | N/A | Default 50 |
| CONTROL | Default 30 | Default 50 | Default 20 | N/A | N/A |
| CONFIG | Default 40 | Default 30 | Default 20 | N/A | N/A |

**Risk Tier Classification:**
- CRITICAL: overall_score > 80
- HIGH: overall_score 61-80
- ELEVATED: overall_score 41-60
- LOW: overall_score <= 40

**History Tracking:**  
Every risk calculation stores a history entry in `risk_history_v2` with the score, tier, and an optional change reason. If the score changes by more than 5 points from the previous calculation, the reason captures the direction and magnitude.

### 6.5 Correlation Service

The Correlation Service computes correlated risk scores by traversing the risk graph and aggregating risk contributions from connected entities.

**Key Technologies:** SQLAlchemy async, BFS with decay  
**Endpoints:** `POST /api/v2/correlation/run`, `GET /api/v2/correlation/{entity_id}`

**Correlation Model (correlated_risks):**
```
correlated_risks
├── id (UUID, PK)
├── entity_id (UUID, FK -> risk_entities)
├── base_risk (FLOAT, not null)
├── neighbor_risk (FLOAT, default 0)
├── correlated_risk (FLOAT, not null)
├── reasoning (JSONB)
└── created_at (TIMESTAMPTZ)
```

**Correlation Algorithm:**

```
correlated_risk = min(base_risk + neighbor_risk, 100)

For each connected entity at depth <= max_depth:
    effective_weight = relationship_weight * decay_factor
    contributed_risk = neighbor_entity_risk * effective_weight / 100
    neighbor_risk += contributed_risk

Decay factor is halved at each depth level to model diminishing impact.
```

The `reasoning` JSONB field stores detailed contribution records, enabling explainability:
```json
{
  "base_risk": 45.0,
  "neighbor_risk": 12.35,
  "correlated_risk": 57.35,
  "contributions": [
    {
      "entity_id": "abc-123",
      "entity_name": "AWS S3 Bucket",
      "entity_type": "SYSTEM",
      "risk_score": 75.0,
      "relationship": "DEPENDS_ON",
      "weight": 0.7,
      "contributed_score": 5.25
    }
  ]
}
```

### 6.6 Anomaly Service (V2)

The Anomaly Service detects security, compliance, identity, and configuration anomalies using rule-based evaluation against entity context.

**Key Technologies:** SQLAlchemy async, rule engine with lambda conditions  
**Endpoints:** `POST /api/v2/anomalies/detect`, `GET /api/v2/anomalies`

**Anomaly Model (anomaly_events_v2):**
```
anomaly_events_v2
├── id (UUID, PK)
├── entity_id (UUID, FK -> risk_entities)
├── anomaly_type (VARCHAR 100)
├── domain (VARCHAR 50)
├── severity (VARCHAR 20)
├── confidence_score (FLOAT)
├── explanation (TEXT)
└── detected_at (TIMESTAMPTZ)
```

**Rule Domains and Anomaly Types:**

| Domain | Anomaly Type | Severity | Condition |
|---|---|---|---|
| Vendor | EXPIRED_CERTIFICATION | HIGH | Any expired certifications |
| Vendor | HIGH_RISK_SCORE | HIGH | Risk score > 80 |
| Vendor | UNDER_INVESTIGATION | HIGH | Vendor flagged for investigation |
| Vendor | BREACHED_VENDOR | CRITICAL | Prior breach events |
| Vendor | ELEVATED_RISK | MEDIUM | Risk score 61-80 |
| Vendor | CONTRACT_EXPIRED | MEDIUM | Contract status is expired |
| Identity | AFTER_HOURS_ACCESS | MEDIUM | Access outside business hours |
| Identity | EXCESSIVE_FAILURES | HIGH | Login failures > 5 |
| Identity | PRIVILEGE_ESCALATION | CRITICAL | Privilege escalation detected |
| Identity | STALE_ACCOUNT | MEDIUM | No login > 90 days |
| Config | ENCRYPTION_DISABLED | CRITICAL | Encryption not enabled |
| Config | LOGGING_DISABLED | HIGH | Audit logging disabled |
| Config | COMPLIANCE_DRIFT | HIGH | Config drifted from baseline |
| Config | PUBLIC_ACCESS | CRITICAL | Resource publicly accessible |

**Context Building:**  
The anomaly engine builds entity-specific context by querying related data. For vendors, it fetches certification expiry status, contract state, and breach history. For users, it checks attributes like login failures and privilege escalations. For config entities, it evaluates encryption, logging, compliance drift, and public access flags.

### 6.7 Remediation Service

The Remediation Service converts anomaly findings into actionable remediation plans with assigned owners, priorities, and due dates.

**Key Technologies:** SQLAlchemy async, template-based action generation  
**Endpoints:** `POST /api/v2/remediation/generate`, `GET /api/v2/remediation/actions`

**Remediation Model (remediation_actions):**
```
remediation_actions
├── id (UUID, PK)
├── entity_id (UUID, FK -> risk_entities)
├── anomaly_type (VARCHAR 100)
├── priority (VARCHAR 20)
├── owner (VARCHAR 255)
├── action (TEXT)
├── status (VARCHAR 50, default 'open')
├── due_date (VARCHAR 20)
├── attributes (JSONB)
├── created_at (TIMESTAMPTZ)
└── resolved_at (TIMESTAMPTZ, nullable)
```

**Remediation Templates (selected examples):**

| Anomaly Type | Actions | Owner | Priority | Due |
|---|---|---|---|---|
| BREACHED_VENDOR | Request incident report, restrict access, conduct security review | Security Team | CRITICAL | 7d |
| EXPIRED_CERTIFICATION | Request updated cert, create compliance task, schedule recert | Compliance Team | HIGH | 30d |
| PRIVILEGE_ESCALATION | Revoke privileges, investigate root cause, review access policies | Security Team | CRITICAL | 1d |
| ENCRYPTION_DISABLED | Enable encryption, verify at-rest and in-transit encryption | Infrastructure Team | CRITICAL | 1d |
| PUBLIC_ACCESS | Restrict public access, review logs for unauthorized access | Security Team | CRITICAL | 1d |
| COMPLIANCE_DRIFT | Revert config to baseline, verify compliance status | Compliance Team | HIGH | 7d |

The remediation engine generates actions for all open anomalies, checking for existing open actions to avoid duplicates.

### 6.8 Scenario Simulation Service

The Scenario Simulation Service enables what-if analysis by simulating the impact of risk events on entities and their connected graph.

**Key Technologies:** SQLAlchemy async, BFS traversal with risk projection  
**Endpoints:** `GET /api/v2/scenario/templates`, `POST /api/v2/scenario/run`, `GET /api/v2/scenario/results`

**Scenario Model (scenario_runs):**
```
scenario_runs
├── id (UUID, PK)
├── entity_id (UUID, FK -> risk_entities)
├── scenario_type (VARCHAR 100)
├── input_data (JSONB)
├── results (JSONB)
├── risk_delta (FLOAT)
└── created_at (TIMESTAMPTZ)
```

**Supported Scenario Types:**

| Scenario | Risk Increase | Severity | Description |
|---|---|---|---|
| BREACH | 35% | CRITICAL | Vendor security breach simulation |
| FAILURE | 50% | CRITICAL | Vendor business failure simulation |
| CONTRACT_EXPIRY | 20% | HIGH | Contract termination impact |
| CERT_EXPIRED | 25% | HIGH | All certifications expire |
| IDENTITY_COMPROMISE | 30% | CRITICAL | User account compromise |
| CONFIG_DRIFT | 15% | MEDIUM | Configuration drift across systems |

**Simulation Algorithm:**

1. Fetch the target entity and its current risk score
2. Traverse the graph up to depth 5 to identify impacted entities
3. Compute projected risk: `projected = min(current + (current * risk_increase_pct), 100)`
4. For each impacted entity, apply a reduced increase (50% of the base scenario increase)
5. Record the blast radius: affected systems, controls, users, vendors
6. Store the impact paths showing propagation routes

**Sample Simulation Result:**
```json
{
  "scenario": "Vendor Breach",
  "source_entity": {
    "entity_name": "CloudStorageCorp",
    "entity_type": "VENDOR",
    "current_risk": 45
  },
  "impact": {
    "current_risk": 45,
    "risk_delta": 15.75,
    "projected_risk": 60.75
  },
  "blast_radius": {
    "affected_systems": 12,
    "affected_controls": 8,
    "affected_users": 45,
    "affected_vendors": 3,
    "total_affected": 68
  },
  "impact_paths": [
    {
      "entity_id": "sys-001",
      "entity_name": "Primary Storage",
      "relationship": "USES",
      "path": ["vendor-01", "sys-001"]
    }
  ]
}
```

### 6.9 Blast Radius Engine

The Blast Radius Engine is a specialized graph traversal service that computes the complete set of entities affected by a risk event at a given source entity.

**Key Technologies:** SQLAlchemy async, BFS with entity type classification  
**Endpoints:** `GET /api/v2/blast-radius/{entity_id}?max_depth=N`

**Algorithm:**
- Start from the source entity ID
- Perform BFS traversal up to max_depth (default 5)
- Classify each visited entity by type (SYSTEM, CONTROL, USER, VENDOR, other)
- Record the traversal path for each entity
- Return counts by category and the complete impact path list

This engine powers both the scenario simulation and the standalone blast radius visualization.

### 6.10 Intelligence Service

The Intelligence Service generates daily intelligence snapshots, priority action lists, and executive briefs. It aggregates data across all other services to produce high-level security intelligence.

**Key Technologies:** SQLAlchemy async, aggregation queries  
**Endpoints:** `GET /api/v2/intelligence/daily`, `GET /api/v2/intelligence/priorities`, `GET /api/v2/intelligence/executive-brief`

**Intelligence Model (intelligence_snapshots):**
```
intelligence_snapshots
├── id (UUID, PK)
├── snapshot_type (VARCHAR 50)
├── title (VARCHAR 255)
├── summary (TEXT)
├── content (JSONB)
├── priority (VARCHAR 20)
└── generated_at (TIMESTAMPTZ)
```

**Daily Intelligence Content:**
- Total and scored entity counts
- Average portfolio risk score
- Critical and high-risk entity lists (top 10 each)
- Entity type distribution
- Anomaly type distribution
- Critical anomaly details

**Priority Actions Content:**
- Unresolved critical and high anomalies
- Open remediation actions sorted by severity
- Entity names and risk scores for context

**Executive Brief Content:**
- Portfolio risk score
- Risk tier distribution (CRITICAL, HIGH, ELEVATED)
- Entity type breakdown
- Top 5 riskiest entities
- Anomaly overview (critical, high, total)
- Remediation status (open, overdue)
- Automated strategic recommendations

### 6.11 Timeline Service

The Timeline Service records and queries risk events, providing a chronological view of entity and portfolio risk history.

**Key Technologies:** SQLAlchemy async, multi-source event aggregation  
**Endpoints:** `GET /api/v2/timeline/entity/{entity_id}`, `GET /api/v2/timeline/portfolio`

**Event Sources:**
- Risk score changes (risk_history_v2)
- Anomaly detections (anomaly_events_v2)
- Remediation actions (remediation_actions)
- Custom risk events (risk_events)

The timeline merges events from all sources, sorts by timestamp descending, and returns a unified chronological feed.

### 6.12 Pipeline Orchestrator

The Pipeline Orchestrator coordinates multi-stage processing across all services. It can run the full pipeline for all active entities or target a specific entity.

**Pipeline Stages:**
1. Risk Calculation — Compute risk scores for all entities
2. Anomaly Detection — Run rule evaluation on all active entities
3. Correlation — Compute correlated risk for all scored entities
4. Remediation — Generate remediation actions for new anomalies
5. Intelligence — Generate daily snapshot, priorities, and executive brief
6. Timeline — Record risk events for all scored entities

The orchestrator runs all stages within a single database transaction, rolling back on failure. This ensures consistency across the pipeline.

### 6.13 Copilot Service

The Copilot Service provides conversational AI access to the entire risk intelligence platform. It uses intent detection to route user questions to the appropriate engine.

**Key Technologies:** Regex-based intent detection, multi-engine dispatch  
**Endpoints:** `POST /api/v2/copilot/query`

**Intent Detection:**  
The system uses regex patterns to classify user questions into six intents:

| Intent | Example Questions | Handler |
|---|---|---|
| risk_explanation | "Why is CloudStorageCorp risky?" | Risk correlation lookup |
| remediation | "How do I reduce risk for AWS?" | Remediation generation |
| simulation | "What if AcmeCorp is breached?" | Scenario simulation |
| prioritization | "What should I focus on today?" | Priority actions |
| executive_summary | "Generate board report" | Executive brief |
| entity_lookup | "Tell me about vendor X" | Entity details |

**Execution Flow:**

```
User Question
    |
    v
Intent Detection (regex pattern matching)
    |
    v
Entity Resolution (fuzzy name search in risk_entities)
    |
    v
Handler Dispatch (based on detected intent)
    |
    v
Engine Execution (correlation, remediation, simulation, intelligence, or lookup)
    |
    v
Response Formatting (structured text with source references)
```

---

## 7. Data Flow

### 7.1 Document Ingestion Flow

```
User Uploads PDF/CSV/JSON
    |
    v
POST /api/v2/documents/upload
    |
    v
Store Raw File (filesystem with storage service)
    |
    v
Create RawDocument Record (database)
    |
    v
POST /api/v2/documents/{id}/analyze
    |
    v
Extract Text (PyMuPDF / csv.DictReader / json.loads)
    |
    v
Classify Document Type (keyword scoring)
    |
    v
Run Type-Specific Extraction (pattern matching)
    |
    v
Store Document Findings (document_findings)
    |
    v
POST /api/v2/documents/{id}/build-graph
    |
    v
Create DOCUMENT Entity (risk_entities)
    |
    v
Extract Controls/Entities (deduplication by name+type)
    |
    v
Create Relationships (HAS_FINDING edges)
    |
    v
Trigger Pipeline (risk scoring, anomaly detection, correlation)
```

### 7.2 Risk Intelligence Flow

```
Entity Created/Updated
    |
    v
Calculate Risk Score (5-dimension scoring)
    |
    v
Store Score + History (risk_scores_v2 + risk_history_v2)
    |
    v
Run Anomaly Detection (rule evaluation against entity context)
    |
    v
Store Anomalies (anomaly_events_v2)
    |
    v
Run Risk Correlation (graph BFS with decay)
    |
    v
Store Correlated Risk (correlated_risks with reasoning)
    |
    v
Generate Remediation Actions (template-based)
    |
    v
Store Actions (remediation_actions)
    |
    v
Update Intelligence Snapshots (daily, priorities, executive brief)
    |
    v
Record Timeline Events (risk_events)
    |
    v
Updated data available via API
    |
    v
Frontend Renders Dashboard, Graph, Copilot Responses
```

### 7.3 Scenario Simulation Flow

```
User Selects Entity + Scenario Type
    |
    v
POST /api/v2/scenario/run
    |
    v
Fetch Entity Data + Current Risk Score
    |
    v
Traverse Graph (BFS up to depth 5)
    |
    v
Compute Projected Risks (apply risk_increase_pct)
    |
    v
Compute Blast Radius (count by entity type)
    |
    v
Record Impact Paths (traversal routes)
    |
    v
Store Scenario Run (scenario_runs)
    |
    v
Return Results to Frontend
    |
    v
Render Risk Delta + Blast Radius Visualizations
```

---

## 8. AI Pipeline

The AI pipeline encompasses rule-based intelligence, pattern matching, and the Copilot's intent-driven query engine.

### 8.1 Document Intelligence

Document intelligence uses a combination of keyword-based classification and regex-based extraction. The classifier scores documents against predefined keyword sets for each document type, selecting the highest-scoring match. Extraction functions use domain-specific patterns to pull structured data from unstructured text.

**Pattern Matching Techniques:**
- Regex for dates, control IDs, section headers
- Keyword co-occurrence for classification
- Section splitting for audit findings and policy content
- NER-like patterns for entity names and relationship types

### 8.2 Entity Extraction

Entities are extracted from documents through type-specific extraction functions:
- **Contracts:** SLA clauses, data retention periods, liability terms, termination conditions, GDPR references
- **SOC 2 / ISO 27001:** Certification dates, control IDs and descriptions
- **Audit Reports:** Audit findings, severity levels, recommendations
- **Policies:** Policy sections, scope descriptions, compliance obligations

Extracted findings are used to create or update RiskEntity records with deduplication by name and type.

### 8.3 Risk Classification

Risk scores are computed across five dimensions using domain-specific algorithms:
- **Security:** Breach history, criticality
- **Compliance:** Certification expiry ratio
- **Operational:** Contract status
- **Financial:** Annual spend levels
- **Access:** Data sensitivity and access level

The overall score is a weighted composite, with weights varying by entity type.

### 8.4 Risk Correlation

The correlation engine uses graph theory (BFS traversal with depth-limited decay) to compute the risk contribution of connected entities. This provides a more complete risk picture than isolated scoring.

### 8.5 Remediation Recommendation

Remediation actions are generated from templates keyed by anomaly type. Each template specifies actions, owner, priority, and due date. The engine deduplicates against existing open actions.

### 8.6 Copilot

The Copilot uses regex-based intent detection to map natural language questions to platform capabilities. It operates without an external LLM by default, using the platform's own data and APIs to answer questions. This provides deterministic, auditable responses grounded in the organization's actual risk data.

**Architecture:**

```
                    +-------------------+
                    |  User Question    |
                    +--------+----------+
                             |
                    +--------v----------+
                    |  Intent Detector  |
                    |  (regex patterns) |
                    +--------+----------+
                             |
              +--------------+--------------+
              |                             |
     +--------v--------+          +--------v--------+
     | Entity Lookup   |          | Intent Routing  |
     | (fuzzy name)    |          | (handler map)   |
     +-----------------+          +--------+--------+
                                           |
              +----------------------------+----------------------------+
              |            |            |            |                  |
     +--------v---+ +-----v------+ +---v--------+ +--v----------+ +----v-------+
     | Risk Explain| | Remediate  | | Simulate   | | Prioritize  | | Executive  |
     | (correlate) | | (templates)| | (scenario) | | (intel)     | | (brief)    |
     +------------+ +------------+ +------------+ +-------------+ +-----------+
              |            |            |            |                  |
              +----------------------------+----------------------------+
                                           |
                                    +------v------+
                                    |  Response   |
                                    |  Formatter  |
                                    +-------------+
```

---

## 9. Risk Intelligence Engine

The Risk Intelligence Engine (defined in `intelligence_engine.py` and `executive_brief_engine.py`) aggregates data across the platform to produce three intelligence products:

### 9.1 Daily Intelligence Snapshot

Generated automatically during pipeline execution, the daily intelligence snapshot provides:
- Entity counts by type and scoring status
- Average portfolio risk score
- Critical and high-risk entity lists
- Entity type distribution
- Recent anomaly trends by type
- Critical anomaly details

### 9.2 Priority Actions

The priorities snapshot identifies the most urgent items for security teams:
- Unresolved critical and high anomalies
- Open remediation actions
- Items sorted by severity (CRITICAL first)
- Entity context for each priority item

### 9.3 Executive Brief

The executive brief translates technical risk data into strategic business intelligence:
- Portfolio-level risk score
- Risk tier distribution (CRITICAL, HIGH, ELEVATED)
- Entity type breakdown across the portfolio
- Top 5 highest-risk entities
- Anomaly overview with critical/high counts
- Remediation backlog and overdue actions
- Automated strategic recommendations

**Recommendation Examples:**
- "Immediate attention required: 7 entities have critical risk scores."
- "Critical anomaly volume is high (12). Prioritize investigation."
- "Remediation backlog: 45 actions are open. Consider assigning additional resources."
- "Portfolio risk is well-controlled. Continue monitoring for emerging risks."

---

## 10. Risk Graph Engine

The Risk Graph Engine models the enterprise ecosystem as a directed graph with typed nodes and weighted edges.

### 10.1 Graph Model

```
Nodes: RiskEntity (VENDOR, SYSTEM, USER, CONTROL, EVIDENCE, EXCEPTION, CONFIG, CERTIFICATION, DOCUMENT)
Edges: RiskRelationship (USES, OWNS, DEPENDS_ON, PROVIDES, AFFECTS, VIOLATES, HAS_ACCESS_TO, etc.)

Example Graph:
    [CloudStorageCorp] --USES--> [PrimaryStorage]
           |                        |
        AFFECTS                  DEPENDS_ON
           |                        |
           v                        v
    [DataBreachPolicy]       [BackupSystem]
                                 |
                              OWNS
                                 |
                                 v
                            [AdminUser]
```

### 10.2 Graph Visualization

The frontend renders the risk graph as a hierarchical node graph. Each node displays:
- Risk indicator (color-coded by score: green < 40, yellow 40-60, orange 60-80, red > 80)
- Entity name and type
- Expandable view showing incoming and outgoing relationships

The graph supports interactive exploration: clicking a node expands it to show connected entities, relationship types, and weights.

### 10.3 Graph Traversal Operations

| Operation | Algorithm | Use Case |
|---|---|---|
| Subgraph Retrieval | BFS up to depth N | Entity exploration |
| Impact Path | Single-direction BFS | Risk propagation visualization |
| Blast Radius | BFS with type classification | Scenario simulation |
| Risk Correlation | BFS with weighted decay | Correlated risk scoring |
| Scenario Impact | BFS with risk projection | What-if analysis |

---

## 11. Risk Correlation Engine

The Risk Correlation Engine (defined in `risk_correlation_engine.py`) computes the enterprise-wide risk contribution to each entity by traversing its connected graph.

### 11.1 Correlation Formula

```
Correlated Risk = min(Base Risk + Neighbor Risk, 100)

Where:
  Neighbor Risk = SUM(connected_entity_risk * relationship_weight * decay_factor / 100)
  Decay Factor = 1.0 at depth 0, halved at each subsequent depth
```

### 11.2 Algorithm Details

```
Input: Entity, max_depth (default 2)
Output: CorrelatedRisk

1. Fetch the entity's current risk score (base_risk)
2. Initialize neighbor_risk = 0, reasoning_parts = []
3. BFS from entity through outbound relationships:
   a. For each unvisited neighbor:
      - Calculate effective_weight = relationship_weight * decay
      - If neighbor has a risk score:
        contributed = neighbor.risk_score * effective_weight / 100
        neighbor_risk += contributed
        Record contribution in reasoning_parts
      - Queue neighbor for next depth level with reduced decay
4. correlated_risk = min(base_risk + neighbor_risk, 100)
5. Store CorrelatedRisk record with full reasoning chain
```

### 11.3 Reasoning Chain

The correlation engine provides full transparency into how correlated risk is computed:

```json
{
  "base_risk": 45.0,
  "neighbor_risk": 12.35,
  "correlated_risk": 57.35,
  "contributions": [
    {
      "entity_id": "sys-001",
      "entity_name": "AWS S3 Bucket",
      "entity_type": "SYSTEM",
      "risk_score": 75.0,
      "relationship": "DEPENDS_ON",
      "weight": 0.7,
      "contributed_score": 5.25
    },
    {
      "entity_id": "cntrl-002",
      "entity_name": "SOC 2: CC6.1 - Logical Access",
      "entity_type": "CONTROL",
      "risk_score": 85.0,
      "relationship": "VIOLATES",
      "weight": 0.9,
      "contributed_score": 7.65
    }
  ]
}
```

---

## 12. Remediation Engine

The Remediation Engine (defined in `remediation_engine.py`) converts risk findings into structured, actionable remediation plans.

### 12.1 Template Architecture

Each anomaly type maps to a remediation template containing:
- A list of action items (text)
- An assigned owner role
- A priority level
- A due date offset

Templates are defined for 14 anomaly types across vendor, identity, and config domains.

### 12.2 Generation Flow

1. Query all open anomalies (or for a specific entity)
2. For each anomaly without an existing open remediation:
   a. Look up the remediation template by anomaly type
   b. Create RemediationAction records for each action in the template
   c. Set status to "open" with computed due date

### 12.3 Deduplication

The engine checks for existing open actions matching the anomaly type and entity before generating new ones, preventing duplicate remediation plans.

---

## 13. Scenario Simulation Engine

The Scenario Simulation Engine (defined in `scenario_engine.py`) enables security teams to model the impact of adverse events before they occur.

### 13.1 Simulation Types

Six scenario types model different risk events:
- **Vendor Breach (BREACH):** 35% risk increase, CRITICAL severity
- **Vendor Failure (FAILURE):** 50% risk increase, CRITICAL severity
- **Contract Termination (CONTRACT_EXPIRY):** 20% risk increase, HIGH severity
- **Certification Expiry (CERT_EXPIRED):** 25% risk increase, HIGH severity
- **Identity Compromise (IDENTITY_COMPROMISE):** 30% risk increase, CRITICAL severity
- **Configuration Drift (CONFIG_DRIFT):** 15% risk increase, MEDIUM severity

### 13.2 Simulation Algorithm

1. Validate the entity exists and scenario type is recognized
2. Fetch the entity's current risk score
3. Traverse the graph up to depth 5 to collect impacted entities
4. Apply scenario-specific risk increase to the source entity
5. Apply reduced risk increase (50% of scenario rate) to impacted entities
6. Classify impacted entities by type for blast radius reporting
7. Record propagation paths for visualization
8. Store the complete simulation result

### 13.3 Sample Output

```json
{
  "scenario": "Vendor Breach",
  "description": "Simulate the impact of a vendor security breach",
  "source_entity": {
    "entity_id": "v-001",
    "entity_name": "CloudStorageCorp",
    "entity_type": "VENDOR",
    "current_risk": 45.0
  },
  "impact": {
    "current_risk": 45.0,
    "risk_delta": 15.75,
    "projected_risk": 60.75,
    "risk_increase_pct": 0.35
  },
  "blast_radius": {
    "affected_systems": 12,
    "affected_controls": 8,
    "affected_users": 45,
    "affected_vendors": 3,
    "total_affected": 68
  },
  "impacted_entities": [
    {
      "entity_id": "sys-001",
      "entity_name": "Primary Storage",
      "entity_type": "SYSTEM",
      "current_risk": 30.0,
      "projected_risk": 35.25,
      "risk_delta": 5.25,
      "relationship": "USES"
    }
  ]
}
```

---

## 14. Copilot Architecture

The Risk Copilot provides conversational AI access to the entire SENTINEL platform through a lightweight, intent-driven architecture that does not require an external LLM.

### 14.1 Architecture Overview

```
+------------------+     +-------------------+     +------------------+
|  User Interface  | --> |  POST /copilot/   | --> |  Intent Detector |
|  (Next.js Chat)  |     |  query            |     |  (regex engine)  |
+------------------+     +-------------------+     +--------+---------+
                                                              |
                                         +--------------------+
                                         |
                               +---------v---------+
                               |  Intent Handlers   |
                               |  (6 handlers)      |
                               +--------------------+
```

### 14.2 Intent Detection

The intent detector uses regex patterns to classify questions:

| Intent | Patterns |
|---|---|
| risk_explanation | `why is (.+) risky`, `explain risk.*(of|for|about) (.+)` |
| remediation | `how to (reduce|fix|mitigate) risk`, `what actions for (.+)` |
| simulation | `what if (.+) breached`, `simulate (.+) breach` |
| prioritization | `what to focus on`, `top risks`, `what matters` |
| executive_summary | `board report`, `executive brief`, `overview` |
| entity_lookup | `tell me about (.+)`, `what is (.+)`, `find (.+)` |

### 14.3 Entity Resolution

When a question references an entity by name, the copilot performs fuzzy matching:
1. Normalize the hint (strip "vendor ", "the ", etc.)
2. Search RiskEntity by name using ILIKE with the hint
3. Order by risk score descending
4. Return the top match

### 14.4 Handler Responses

Each handler executes the relevant platform engine and formats the response:

- **risk_explanation:** Fetches correlated risk and lists contributions from connected entities
- **remediation:** Generates or lists remediation actions for the entity
- **simulation:** Runs the scenario simulator and displays blast radius
- **prioritization:** Returns the current priority actions from the intelligence engine
- **executive_summary:** Generates and returns a full executive brief
- **entity_lookup:** Returns entity details including type, status, risk score, and attributes

### 14.5 Response Format

All responses include:
- `answer`: Formatted text response (markdown-compatible)
- `sources`: List of source entities with IDs
- `intent`: The detected intent
- `engine`: The engine that generated the response

---

## 15. API Architecture

The SENTINEL API follows a two-version structure. v1 provides legacy vendor-focused endpoints, while v2 provides the complete risk intelligence API.

### 15.1 API Base Structure

```
/api/v1/  - Legacy API (vendor-centric)
/api/v2/  - Risk Intelligence API (entity-centric)
```

### 15.2 V2 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| **Entities** | | |
| POST | `/api/v2/entities` | Create a new risk entity |
| GET | `/api/v2/entities` | List entities with filters |
| GET | `/api/v2/entities/{id}` | Get entity details |
| PUT | `/api/v2/entities/{id}` | Update entity |
| DELETE | `/api/v2/entities/{id}` | Archive entity |
| **Graph** | | |
| POST | `/api/v2/graph/relationships` | Create relationship |
| GET | `/api/v2/graph/entity/{id}?depth=N` | Get entity subgraph |
| GET | `/api/v2/graph/impact-path/{id}` | Get impact path |
| **Risk** | | |
| POST | `/api/v2/risk/calculate/{id}` | Calculate risk score |
| GET | `/api/v2/risk/{id}` | Get latest risk score |
| GET | `/api/v2/risk/{id}/history` | Get risk history |
| **Correlation** | | |
| POST | `/api/v2/correlation/run` | Run risk correlation |
| GET | `/api/v2/correlation/{id}` | Get correlated risk |
| **Anomalies** | | |
| POST | `/api/v2/anomalies/detect` | Run anomaly detection |
| GET | `/api/v2/anomalies` | List anomalies |
| **Blast Radius** | | |
| GET | `/api/v2/blast-radius/{id}?max_depth=N` | Calculate blast radius |
| **Scenario** | | |
| GET | `/api/v2/scenario/templates` | List scenario templates |
| POST | `/api/v2/scenario/run` | Run scenario simulation |
| GET | `/api/v2/scenario/results` | List simulation results |
| **Remediation** | | |
| POST | `/api/v2/remediation/generate` | Generate remediation actions |
| GET | `/api/v2/remediation/actions` | List remediation actions |
| **Intelligence** | | |
| GET | `/api/v2/intelligence/daily` | Get daily intelligence |
| GET | `/api/v2/intelligence/priorities` | Get priority actions |
| GET | `/api/v2/intelligence/executive-brief` | Get executive brief |
| **Timeline** | | |
| GET | `/api/v2/timeline/entity/{id}` | Get entity timeline |
| GET | `/api/v2/timeline/portfolio` | Get portfolio timeline |
| **Copilot** | | |
| POST | `/api/v2/copilot/query` | Ask a question |
| **Pipeline** | | |
| POST | `/api/v2/pipeline/run` | Run full pipeline |
| **Documents** | | |
| POST | `/api/v2/documents/upload` | Upload document |
| GET | `/api/v2/documents/{id}/findings` | Get document findings |
| POST | `/api/v2/documents/{id}/analyze` | Analyze document |
| POST | `/api/v2/documents/{id}/build-graph` | Build graph from document |
| **Ingestion** | | |
| POST | `/api/v2/ingestion/csv` | Ingest CSV file |
| POST | `/api/v2/ingestion/json` | Ingest JSON data |
| POST | `/api/v2/ingestion/entity` | Ingest single entity |

### 15.3 Standard Response Format

All API responses follow a consistent envelope:

```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

Error responses:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "NOT_FOUND",
    "message": "Entity not found"
  }
}
```

### 15.4 Authentication

All endpoints except auth require a Bearer JWT token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### 15.5 Sample API Call

```
POST /api/v2/correlation/run
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: application/json

{
  "entity_id": "550e8400-e29b-41d4-a716-446655440000"
}

Response:
{
  "success": true,
  "data": {
    "entity_id": "550e8400-e29b-41d4-a716-446655440000",
    "base_risk": 45.0,
    "neighbor_risk": 12.35,
    "correlated_risk": 57.35,
    "reasoning": {
      "base_risk": 45.0,
      "neighbor_risk": 12.35,
      "correlated_risk": 57.35,
      "contributions": [
        {
          "entity_id": "sys-001",
          "entity_name": "Primary Storage",
          "entity_type": "SYSTEM",
          "risk_score": 75.0,
          "relationship": "DEPENDS_ON",
          "weight": 0.7,
          "contributed_score": 5.25
        }
      ]
    },
    "created_at": "2025-06-21T12:00:00+00:00"
  }
}
```

---

## 16. Worker Architecture

SENTINEL uses an asynchronous worker architecture for long-running tasks. While Celery + Redis is provisioned in the architecture, the current implementation uses async SQLAlchemy within the FastAPI process for simplicity.

### 16.1 Worker Topology (Planned)

```
+------------------+     +------------------+
|  Redis Broker    |     |  Result Backend  |
|  (message queue) |     |  (Redis/DB)      |
+--------+---------+     +--------+---------+
         |                         |
+--------v---------+     +--------v---------+
|  Celery Workers  |     |  Task Results    |
|  (multiple pods) |     |  (polling)       |
+--------+---------+     +------------------+
         |
+--------v------------------+
|  Worker Task Types:        |
|  - OCR Processing          |
|  - Document Parsing        |
|  - Entity Extraction       |
|  - Risk Correlation        |
|  - Scenario Simulation     |
|  - Report Generation       |
|  - Pipeline Orchestration  |
+---------------------------+
```

### 16.2 Asynchronous Processing Flow (Current)

The current implementation uses FastAPI's async endpoints with SQLAlchemy's async session:

```
Client Request
    |
    v
FastAPI Route (async def)
    |
    v
In-Memory Processing (await on DB queries, I/O operations)
    |
    v
Async DB Operations (SQLAlchemy async session)
    |
    v
Response (after all operations complete)
```

This approach works well for sub-second operations. For long-running tasks (large document processing, full pipeline execution), the architecture supports Celery delegation.

---

## 17. Database Architecture

### 17.1 Core Tables

| Table | Purpose |
|---|---|
| `users` | User accounts with role-based access |
| `roles` | Role definitions (admin, analyst, executive) |
| `vendors` | Vendor profiles with criticality and contract info |
| `vendor_contacts` | Vendor contact details |
| `vendor_data_access` | Vendor data access patterns |
| `vendor_categories` | Vendor categorization taxonomy |
| `compliance_frameworks` | Compliance framework definitions |
| `certifications` | Vendor compliance certifications |
| `vendor_compliance` | Vendor-framework compliance mappings |
| `risk_entities` | Unified risk graph nodes |
| `risk_relationships` | Typed edges between risk entities |
| `risk_scores` | Legacy vendor risk scores |
| `risk_scores_v2` | Entity risk scores (5 dimensions) |
| `risk_history` | Legacy vendor risk history |
| `risk_history_v2` | Entity risk score history |
| `correlated_risks` | Graph-based correlated risk scores |
| `anomaly_events_v2` | Detected anomaly events |
| `remediation_actions` | Generated remediation plans |
| `scenario_runs` | Scenario simulation results |
| `intelligence_snapshots` | Daily intelligence and reports |
| `risk_events` | Custom risk timeline events |
| `raw_data` (and subtypes) | Raw ingested data records |
| `document_findings` | Extracted document findings |
| `evaluation_results` | Ground truth evaluation metrics |
| `contracts` | Contract lifecycle management |
| `alert_configurations` | Alert rule definitions |

### 17.2 Entity Relationship Diagram (Core)

```
users ──> roles (role_name)
vendors ──> risk_scores (vendor_id)
vendors ──> risk_history (vendor_id)
vendors ──> certifications (vendor_id)
vendors ──> vendor_data_access (vendor_id)
vendors ──> vendor_contacts (vendor_id)
vendors ── vendor_category_mapping <── vendor_categories

risk_entities ──> risk_scores_v2 (entity_id)
risk_entities ──> risk_history_v2 (entity_id)
risk_entities ──> correlated_risks (entity_id)
risk_entities ──> anomaly_events_v2 (entity_id)
risk_entities ──> remediation_actions (entity_id)
risk_entities ──> scenario_runs (entity_id)
risk_entities ──> risk_events (entity_id)

risk_entities (source) ──> risk_relationships ──> risk_entities (target)
```

### 17.3 Indexing Strategy

- `risk_entities.entity_type` — B-tree index for type filtering
- `risk_entities.entity_name` — GIN trigram index for fuzzy search
- `risk_relationships.source_entity_id` — B-tree index for graph traversal
- `risk_relationships.target_entity_id` — B-tree index for reverse traversal
- `risk_scores_v2.entity_id` — B-tree index for latest score lookup
- `anomaly_events_v2.entity_id` — B-tree index for entity anomalies
- `intelligence_snapshots.snapshot_type` — B-tree index for type filtering

### 17.4 PostgreSQL Features Used

- **JSONB:** Flexible attribute storage for entities, relationships, and all modeling
- **UUID:** Primary keys for distributed ID generation
- **TIMESTAMPTZ:** Timezone-aware timestamps for global deployments
- **Foreign Keys:** Referential integrity across all entity relationships
- **Async Driver (asyncpg):** Non-blocking database access

---

## 18. Security Architecture

### 18.1 Authentication

**JWT Token Authentication:**
- Access tokens: 15-minute expiry (configurable)
- Refresh tokens: 24-hour expiry (configurable)
- Tokens signed with HS256 using configurable SECRET_KEY
- Password hashing using bcrypt via passlib

**Token Flow:**
```
1. POST /api/v1/auth/login { email, password }
2. Server validates credentials, returns { access_token, refresh_token }
3. Client stores tokens in localStorage
4. All subsequent requests include Authorization: Bearer <access_token>
5. On 401, client uses refresh token to obtain new access token
6. On refresh failure, client redirects to login
```

### 18.2 Role-Based Access Control (RBAC)

Three built-in roles:

| Role | Permissions |
|---|---|
| admin | Full platform access, user management, system configuration |
| analyst | Vendor risk analysis, document upload, scenario simulation |
| executive | Read-only access to dashboards, reports, and copilot |

**Enforcement:**
- The `require_role(role)` dependency validates role permissions at the route level
- Routes without explicit role requirements default to requiring any authenticated user
- Role checking runs after authentication in the middleware chain

### 18.3 Audit Logging

- All risk events are recorded in `risk_events` with timestamps
- Risk score changes are tracked in `risk_history_v2` with change reasons
- Pipeline executions are logged with stage-level status
- Anomaly detections are timestamped and recorded with entity context

### 18.4 Encryption at Rest

- Database-level encryption via PostgreSQL TDE (when configured)
- File storage encryption for uploaded documents
- Password hashing with bcrypt (not reversible)
- JWT secrets stored in environment variables, not in code

### 18.5 Encryption in Transit

- TLS/SSL termination at the load balancer
- HTTPS enforced for all API communications
- Secure cookie flags (HttpOnly, Secure, SameSite)

### 18.6 API Security

- Bearer token authentication on all endpoints (except auth)
- CORS configuration restricted to configured origins
- Input validation via Pydantic schemas on all endpoints
- Global exception handler preventing information leakage
- SQL injection prevention via SQLAlchemy parameterized queries

### 18.7 Input Validation

- All request bodies validated using Pydantic models
- File uploads restricted to supported types (PDF, CSV, JSON)
- Path parameters validated as UUIDs where applicable
- Query parameters bounded (page, size limits)

### 18.8 File Security

- Uploaded files stored outside the web root
- File content scanned for malware (configurable)
- File access controlled through the API, not direct filesystem
- Storage path mapping prevents directory traversal

---

## 19. Scalability Design

### 19.1 Horizontal Scaling

| Component | Strategy |
|---|---|
| API Servers | Stateless FastAPI behind load balancer; scale by adding instances |
| Workers | Celery workers with Redis broker; scale by adding worker pods |
| Database | PostgreSQL read replicas for query scaling; connection pooling |
| Frontend | Static Next.js build served through CDN; scales horizontally |

### 19.2 Database Scaling

- **Connection Pooling:** SQLAlchemy connection pool with configurable pool size
- **Read Replicas:** Separate read/write sessions for reporting queries
- **JSONB Indexing:** GIN indexes on JSONB columns for efficient attribute queries
- **Partitioning:** Time-based partitioning for event tables (risk_events, anomaly_events)

### 19.3 Caching Strategy

- **Redis:** Message broker for worker tasks, cache for frequent queries
- **Query Caching:** Intelligence snapshots cached and regenerated on pipeline runs
- **Token Caching:** Blacklisted tokens cached in Redis for immediate invalidation

### 19.4 Performance Considerations

- Graph traversal depth limited (default 2 for correlation, 5 for simulation)
- API responses paginated (default 50, max 200)
- Intelligence snapshots pre-computed during pipeline runs
- Async database operations prevent connection blocking

---

## 20. User Interface Design

### 20.1 Technology

The frontend is built with:
- **Next.js 14** (App Router) — Server-side rendering and routing
- **TypeScript** — Type safety across components
- **Tailwind CSS** — Utility-first styling
- **Lucide React** — Icon system

### 20.2 Application Layout

```
+-----------------------------------------------------------+
|  SENTINEL — Third-Party Risk Intelligence                  |
+-----------------------------------------------------------+
|  [Dashboard] [Vendors] [Graph] [Scenarios] [Copilot] ...  |
+-----------------------------------------------------------+
|                                                           |
|  Main Content Area                                        |
|  (Page-specific component)                                |
|                                                           |
+-----------------------------------------------------------+
```

### 20.3 Module Descriptions

**1. Risk Intelligence Center (Dashboard)**
- Portfolio-wide KPIs (total vendors, critical vendors, expiring certs, open alerts, anomalies)
- Evaluation metrics display (precision, recall, F1 score)
- Risk distribution visualization (red/yellow/green tiers)
- Quick action cards for navigation

*Data Sources:* Dashboard API (`/api/v1/dashboard/summary`)

**2. Risk Graph**
- Entity ID search with subgraph visualization
- Color-coded risk indicators (green/yellow/orange/red based on score)
- Expandable entity cards showing incoming and outgoing relationships
- Edge labels showing relationship type and weight
- Summary statistics (total nodes, edges)

*Data Sources:* Graph API (`/api/v2/graph/entity/{id}?depth=N`)

**3. Scenario Simulator**
- Entity selector (dropdown populated from `/api/v2/entities`)
- Scenario type selector (templates from `/api/v2/scenario/templates`)
- Risk delta visualization (current → projected with delta)
- Blast radius breakdown (total affected, systems, controls, users)
- Impacted entity list with scrollable results

*Data Sources:* Scenario API (`/api/v2/scenario/*`)

**4. Executive Timeline**
- Chronological feed of risk events
- Event types: risk changes, anomaly detections, remediation actions
- Entity-level and portfolio-level views
- Color-coded severity indicators

*Data Sources:* Timeline API (`/api/v2/timeline/*`)

**5. Remediation Center**
- List of open remediation actions
- Priority, owner, due date, and status columns
- Filtering by entity or anomaly type
- Action completion tracking

*Data Sources:* Remediation API (`/api/v2/remediation/actions`)

**6. AI Copilot**
- Chat interface with message bubbles
- Suggested questions for new users
- Typing indicator during query processing
- Markdown-formatted responses
- Source references for traceability

*Data Sources:* Copilot API (`/api/v2/copilot/query`)

### 20.4 Additional Pages

- **Vendors:** Vendor registry with CRUD operations, risk scores, and certification tracking
- **Anomalies:** Anomaly center with detection history and severity filtering
- **Certifications:** Certification lifecycle management with expiry tracking
- **Contracts:** Contract management and lifecycle monitoring
- **Alerts:** Alert configuration and notification history
- **Evaluation:** Ground truth evaluation with precision, recall, and F1 metrics
- **Import:** Document upload and CSV/JSON ingestion interface
- **Reports:** Pre-built and custom report generation
- **Admin:** User management and system configuration

---

## 21. Processing Workflow

### 21.1 Full Pipeline Execution

The pipeline orchestrator (`pipeline_orchestrator.py`) coordinates end-to-end processing:

```
POST /api/v2/pipeline/run
    |
    v
Stage 1: Risk Calculation
    |-- For each active entity:
    |   |-- Compute 5-dimension risk scores
    |   |-- Calculate overall score and tier
    |   |-- Store in risk_scores_v2
    |   |-- Record in risk_history_v2 (with change reason if >5pt delta)
    |
    v
Stage 2: Anomaly Detection
    |-- For each active entity:
    |   |-- Build entity context (fetch vendor/certs/access data)
    |   |-- Evaluate rule conditions against context
    |   |-- Store new anomalies in anomaly_events_v2
    |
    v
Stage 3: Risk Correlation
    |-- For each active entity with a risk score:
    |   |-- BFS through relationships (up to depth 2)
    |   |-- Compute neighbor_risk with weighted decay
    |   |-- Store CorrelatedRisk with reasoning chain
    |
    v
Stage 4: Remediation Generation
    |-- For each anomaly without open remediation:
    |   |-- Look up template by anomaly_type
    |   |-- Generate RemediationAction records
    |
    v
Stage 5: Intelligence Generation
    |-- Generate Daily Intelligence snapshot
    |-- Generate Priorities snapshot
    |-- Generate Executive Brief
    |
    v
Stage 6: Timeline Recording
    |-- For each active entity:
    |   |-- Record risk event with current score
    |
    v
Commit Transaction
    |
    v
Return Pipeline Results
```

### 21.2 Individual Entity Processing

For targeted processing of a single entity:

```
POST /api/v2/risk/calculate/{entity_id}
    |
    v
Compute dimension scores for entity type
    |
    v
Store score and history
    |
    v
POST /api/v2/anomalies/detect (with entity filter)
    |
    v
POST /api/v2/correlation/run (with entity_id)
    |
    v
Entity ready for querying via API
```

---

## 22. Sample Execution Flow

This section demonstrates a complete execution using three real-world document types: an ISO 27001 certificate, a SOC 2 report, and an internal audit report.

### 22.1 Document Ingestion

**Step 1: Upload ISO 27001 Certificate**

```
POST /api/v2/documents/upload
Content-Type: multipart/form-data
File: iso27001_cert.pdf (PDF)

Response:
{
  "document_id": "doc-001",
  "status": "uploaded",
  "source_file": "iso27001_cert.pdf"
}
```

**Step 2: Analyze Document**

```
POST /api/v2/documents/doc-001/analyze

Results:
- Document classified as ISO27001
- Extracted issue date: 2024-03-15
- Extracted expiry date: 2027-03-15
- Extracted 12 control references (e.g., "A.9.1.2 Access to networks")
- Created 12 DocumentFinding records
```

**Step 3: Build Graph from Document**

```
POST /api/v2/documents/doc-001/build-graph

Results:
- Created DOCUMENT entity: "Document: iso27001_cert.pdf"
- Created 12 CONTROL entities (one per extracted control)
- Created 12 HAS_FINDING relationships from DOCUMENT to each CONTROL
```

**Step 4: Upload SOC 2 Report**

```
POST /api/v2/documents/upload (SOC 2 report PDF)
POST /api/v2/documents/doc-002/analyze

Results:
- Document classified as SOC2
- Extracted issue date: 2024-01-01
- Extracted expiry date: 2025-01-01
- Extracted 8 control descriptions (CC6.1, CC6.2, etc.)
```

**Step 5: Upload Internal Audit Report**

```
POST /api/v2/documents/upload (audit PDF)
POST /api/v2/documents/doc-003/analyze

Results:
- Document classified as AUDIT_REPORT
- Extracted 5 audit findings with severity levels
- Extracted 3 recommendations
```

### 22.2 Entity and Graph Creation

**Step 6: Manually Create Vendor Entity**

```
POST /api/v2/entities
{
  "entity_type": "VENDOR",
  "entity_name": "CloudStorageCorp",
  "external_id": "v-001",
  "attributes": {
    "criticality": "HIGH",
    "annual_spend": 1200000
  }
}
```

**Step 7: Create Relationships**

```
POST /api/v2/graph/relationships
{
  "source_entity_id": "v-001",
  "target_entity_id": "doc-entity-001",
  "relationship_type": "OWNS",
  "weight": 1.0
}

POST /api/v2/graph/relationships
{
  "source_entity_id": "sys-001",
  "target_entity_id": "v-001",
  "relationship_type": "DEPENDS_ON",
  "weight": 0.7
}
```

### 22.3 Risk Scoring and Anomaly Detection

**Step 8: Run Full Pipeline**

```
POST /api/v2/pipeline/run

Results:
- Stage 1: Risk calculated for 15 entities
- Stage 2: 3 anomalies detected:
  - EXPIRED_CERTIFICATION (HIGH): CloudStorageCorp — 1 expired certification
  - ELEVATED_RISK (MEDIUM): CloudStorageCorp — risk score 62
  - EXCESSIVE_FAILURES (HIGH): User "john.doe" — 12 login failures
- Stage 3: Correlation completed for 15 entities
- Stage 4: 15 remediation actions generated
- Stage 5: Intelligence snapshots created
- Stage 6: Timeline events recorded
```

**Step 9: View Correlated Risk**

```
GET /api/v2/correlation/v-001

{
  "entity_id": "v-001",
  "base_risk": 62.0,
  "neighbor_risk": 8.75,
  "correlated_risk": 70.75,
  "reasoning": {
    "contributions": [
      {
        "entity_name": "User: john.doe",
        "entity_type": "USER",
        "risk_score": 45.0,
        "relationship": "HAS_ACCESS_TO",
        "weight": 1.0,
        "contributed_score": 4.5
      },
      {
        "entity_name": "Primary Storage",
        "entity_type": "SYSTEM",
        "risk_score": 55.0,
        "relationship": "DEPENDS_ON",
        "weight": 0.7,
        "contributed_score": 3.85
      }
    ]
  }
}
```

### 22.4 Scenario Simulation

**Step 10: Simulate Breach**

```
POST /api/v2/scenario/run
{
  "entity_id": "v-001",
  "scenario": "BREACH"
}

Results:
- Risk increase: 62.0 → 83.7 (+21.7)
- Blast radius: 8 systems, 4 controls, 12 users, 2 vendors
- 26 total affected entities
- Impact paths showing propagation routes
```

### 22.5 Remediation and Reporting

**Step 11: View Remediation Actions**

```
GET /api/v2/remediation/actions?entity_id=v-001

Actions:
1. "Request updated certification certificate from vendor" — Compliance Team — HIGH — due 30d
2. "Create compliance review task" — Compliance Team — HIGH — due 30d
3. "Review risk score drivers" — Risk Team — MEDIUM — due 30d
4. "Schedule vendor risk review" — Risk Team — MEDIUM — due 30d
```

**Step 12: Generate Executive Brief**

```
GET /api/v2/intelligence/executive-brief

{
  "executive_summary": "Portfolio risk score is 45.2. 2 entities are critical, 5 are high-risk. 1 critical and 3 high-severity anomalies active. 15 remediation actions are open.",
  "top_risks": [
    {"entity_name": "CloudStorageCorp", "risk_score": 62.0},
    {"entity_name": "LegacyApp Server", "risk_score": 58.0}
  ],
  "recommendations": [
    "Critical anomaly volume is elevated. Prioritize investigation.",
    "Remediation backlog: 15 actions are open. Consider assigning additional resources."
  ]
}
```

### 22.6 Copilot Interaction

**Step 13: Ask the Copilot**

```
POST /api/v2/copilot/query
{
  "question": "Why is CloudStorageCorp risky?"
}

Response:
{
  "intent": "risk_explanation",
  "answer": "**CloudStorageCorp** (VENDOR) has a correlated risk score of **70.75**.\nBase risk: 62.0, contributed by neighbors: 8.75\n\nRisk contributions from connected entities:\n- User: john.doe (USER, risk=45.0) via **HAS_ACCESS_TO** contributed +4.5\n- Primary Storage (SYSTEM, risk=55.0) via **DEPENDS_ON** contributed +3.85",
  "sources": [
    {"entity_id": "v-001", "entity_name": "CloudStorageCorp", "entity_type": "VENDOR"}
  ]
}
```

---

## 23. Technology Stack

### 23.1 Backend

| Technology | Version | Purpose |
|---|---|---|
| Python | 3.11+ | Runtime |
| FastAPI | 0.110+ | Web framework |
| Uvicorn | Standard | ASGI server |
| SQLAlchemy | 2.0+ | ORM with async support |
| asyncpg | Latest | PostgreSQL async driver |
| Alembic | Latest | Database migrations |
| Pydantic | 2.x | Data validation |
| python-jose | Latest | JWT token handling |
| passlib | Latest | Password hashing |
| bcrypt | 4.0.1 | Password encryption |
| PyMuPDF (fitz) | Latest | PDF text extraction |
| python-multipart | Latest | File upload handling |
| structlog | Latest | Structured logging |
| httpx | Latest | Async HTTP client |
| pytest | Latest | Testing framework |
| pytest-asyncio | Latest | Async test support |

### 23.2 Frontend

| Technology | Version | Purpose |
|---|---|---|
| Next.js | 14.x | React framework with App Router |
| TypeScript | 5.x | Type safety |
| Tailwind CSS | 3.x | Styling |
| Lucide React | Latest | Icon library |
| Jest | Latest | Testing |

### 23.3 Infrastructure

| Technology | Version | Purpose |
|---|---|---|
| PostgreSQL | 16 Alpine | Primary database |
| Redis | 7 Alpine | Message broker / cache |
| Docker | Latest | Containerization |
| Docker Compose | Latest | Local orchestration |

### 23.4 LLM Integration (Optional)

| Technology | Purpose |
|---|---|
| Mistral AI API | Optional LLM integration |
| Configurable model endpoint | Supports any OpenAI-compatible API |

---

## 24. Innovation Highlights

SENTINEL represents a fundamental shift from traditional Vendor Risk Management (VRM) to enterprise risk intelligence.

### 24.1 Unified Risk Graph

Traditional VRM systems store vendor information in flat tables. Each vendor is an isolated record. SENTINEL models the entire enterprise ecosystem as a directed graph where vendors, systems, users, controls, evidence, and certifications are nodes connected by typed, weighted relationships. This enables:
- Discovery of hidden dependencies between entities
- Visualization of complex risk topologies
- Traversal-based risk analysis (propagation, blast radius, correlation)

**Versus traditional VRM:** Flat vendor records → Graph-based risk topology

### 24.2 Risk Propagation Analysis

Traditional systems compute risk scores independently for each vendor. SENTINEL computes correlated risk by traversing the graph and aggregating risk contributions from all connected entities. A vendor's real risk exposure includes the risk of all systems it depends on, all users who access it, and all controls that govern it.

**Versus traditional VRM:** Isolated vendor scoring → Graph-based risk propagation

### 24.3 Scenario Simulation

No traditional VRM platform allows users to simulate the impact of hypothetical events. SENTINEL's Scenario Simulator enables security teams to answer "what-if" questions before incidents occur: "What if our primary cloud provider is breached?" "What if this vendor's certifications expire?" "What if this contract terminates?"

**Versus traditional VRM:** Reactive incident response → Proactive scenario analysis

### 24.4 AI Copilot

Traditional VRM platforms require navigating complex dashboards to find answers. SENTINEL's Copilot provides conversational access to the full platform using natural language. Users ask questions in plain English and receive structured answers grounded in their actual risk data.

**Versus traditional VRM:** Manual dashboard navigation → Conversational intelligence

### 24.5 Remediation Intelligence

Traditional systems stop at risk identification. SENTINEL's Remediation Engine automatically converts findings into actionable plans with assigned owners, priorities, and due dates. The template-based architecture ensures consistent, best-practice remediation across the organization.

**Versus traditional VRM:** Risk identification → Automated remediation orchestration

### 24.6 Executive Intelligence

Traditional VRM reporting requires manual compilation of data across spreadsheets and tools. SENTINEL automatically generates executive briefs, board reports, and priority action lists, translating technical risk data into strategic business intelligence.

**Versus traditional VRM:** Manual reporting → Automated executive intelligence

### 24.7 Multi-Dimensional Risk Scoring

Traditional systems use single-dimension scoring (often just criticality + a questionnaire). SENTINEL computes risk across five dimensions (security, compliance, operational, financial, access) with entity-type-specific algorithms, providing a nuanced view of risk.

**Versus traditional VRM:** Single-dimension scoring → Multi-dimensional risk intelligence

### 24.8 Document Intelligence

Traditional systems require manual extraction of risk data from documents. SENTINEL automatically classifies, extracts, and incorporates findings from PDF contracts, SOC 2 reports, ISO certificates, audit findings, and policies into the risk graph.

**Versus traditional VRM:** Manual document review → Automated document intelligence

---

## 25. Future Enhancements

### 25.1 Machine Learning Integration

- **ML-Based Risk Prediction:** Train models on historical risk events to predict future risk trajectories
- **Anomaly Detection with ML:** Complement rule-based detection with unsupervised anomaly detection (isolation forests, autoencoders)
- **NLP Enhancement:** Replace regex-based extraction with transformer-based NER models (e.g., fine-tuned BERT for security document entities)

### 25.2 Real-Time Event Processing

- **Kafka Integration:** Real-time event streaming from security tools (SIEM, vulnerability scanners, CSPM)
- **WebSocket Support:** Push notifications for new anomalies, risk changes, and remediation updates
- **Stream Processing:** Real-time risk recalculation on entity attribute changes

### 25.3 Advanced Graph Analytics

- **Community Detection:** Identify risk clusters and shared dependencies
- **Centrality Analysis:** Find the most connected (and thus most risky) entities
- **Path Analysis:** Identify the shortest/highest-risk propagation paths
- **Temporal Graph:** Track graph evolution over time for trend analysis

### 25.4 Enhanced Integrations

- **SOAR Integration:** Automated ticket creation in ServiceNow, Jira, or PagerDuty
- **SIEM Integration:** Ingest alerts from Splunk, Sentinel, or Elastic
- **Cloud Provider APIs:** Direct integration with AWS, Azure, GCP for resource discovery
- **Identity Providers:** Integration with Okta, Azure AD, or JumpCloud for user entity creation

### 25.5 Advanced Simulation

- **Monte Carlo Simulation:** Probabilistic risk modeling with confidence intervals
- **Multi-Event Scenarios:** Simulate concurrent risk events
- **Mitigation Simulation:** Model the impact of remediation actions on risk scores
- **Cost Impact Analysis:** Quantify financial impact of simulated scenarios

### 25.6 Compliance Automation

- **Framework Mapping:** Automated mapping of controls to compliance frameworks (SOC 2, ISO 27001, NIST, PCI)
- **Evidence Collection:** Automated evidence gathering from integrated systems
- **Compliance Gap Analysis:** Identify missing controls across frameworks
- **Continuous Compliance Monitoring:** Real-time compliance status tracking

### 25.7 Mobile Application

- **Executive Dashboard:** Mobile-optimized risk overview for executives
- **Push Notifications:** Real-time alerts for critical risk changes
- **Quick Approvals:** Mobile-based remediation action approvals

### 25.8 Multi-Tenancy

- **Organization Isolation:** Complete data isolation between tenants
- **Shared Risk Intelligence:** Opt-in sharing of anonymized risk patterns
- **Tenant-Specific Configurations:** Custom scoring weights and rule sets per tenant

---

## 26. Conclusion

SENTINEL redefines enterprise risk management by transforming static vendor records into an intelligent, graph-based risk intelligence platform. The ten-layer architecture provides end-to-end coverage from document ingestion through executive reporting, with each layer building on the outputs of the previous layer to create a coherent, actionable risk model.

The platform's key technical innovations include:
- **Unified Risk Graph** with typed entities and weighted relationships enabling enterprise-wide visibility
- **Graph-Based Risk Correlation** that propagates risk through connected entities with explainable reasoning
- **Multi-Dimensional Scoring** across five risk dimensions with entity-type-specific algorithms
- **Rule-Based Anomaly Detection** covering vendor, identity, and config domains with 14 detection types
- **Template-Driven Remediation** with automated action generation and owner assignment
- **Scenario Simulation** supporting six scenario types with blast radius computation
- **AI Copilot** with intent-driven query engine providing conversational access to the full platform
- **Automated Executive Intelligence** generating board-ready reports and strategic recommendations

The implementation is production-ready with:
- Fully async Python backend (FastAPI + SQLAlchemy)
- Modern TypeScript frontend (Next.js 14)
- PostgreSQL persistence with JSONB flexibility
- Docker-based deployment
- JWT authentication with RBAC
- Comprehensive REST API with two version tracks
- Ground-truth evaluation framework for accuracy measurement
- 30+ database tables covering the complete risk intelligence data model

SENTINEL is not a vendor management system. It is an enterprise risk intelligence platform that uses graph theory, rule-based intelligence, and automated analysis to provide security leaders with the visibility, prediction, and action capabilities needed to manage modern enterprise risk.

---

*Document prepared for Enterprise Architecture Review*  
*SENTINEL Platform — Version 2.0*  
*Classification: Confidential*
