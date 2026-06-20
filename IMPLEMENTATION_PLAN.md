# SENTINEL — Final Implementation Blueprint

**Version:** 1.0
**Prepared For:** Engineering Team (3 Engineers)
**Timeline:** 6 Weeks (30 Working Days)
**Architecture:** Modular Monolith (FastAPI)
**Evaluation Focus:** vendor_registry.csv + vendor_labels.csv

---

## Table of Contents

1. [Overview](#1-overview)
2. [Architecture v3](#2-architecture-v3)
3. [Core Data Flow](#3-core-data-flow)
4. [Database Schema](#4-database-schema)
5. [API Surface](#5-api-surface)
6. [Frontend Screens](#6-frontend-screens)
7. [Week-by-Week Plan](#7-week-by-week-implementation-plan)
8. [Anomaly Detection Rules](#8-anomaly-detection-rules)
9. [Evaluation Module](#9-evaluation-module)
10. [Contract AI](#10-contract-ai)
11. [Copilot](#11-copilot)
12. [What We Are NOT Building](#12-what-we-are-not-building)
13. [Risk Register](#13-risk-register)
14. [Total Estimate](#14-total-implementation-estimate)

---

## 1. Overview

| Field | Value |
|-------|-------|
| **Project** | SENTINEL — Third-Party Risk Intelligence Platform |
| **Team** | 3 engineers |
| **Timeline** | 6 weeks (30 working days) |
| **Stack** | FastAPI, PostgreSQL, Next.js 15, Tailwind, Docker Compose |
| **AI** | Mistral/Llama API (external), no local models, no RAG, no vector DB |
| **Architecture** | Modular monolith (single FastAPI process, domain-organized modules) |
| **Evaluation** | Precision, Recall, F1, Accuracy, Confusion Matrix against vendor_labels.csv |

---

## 2. Architecture v3

```
┌─────────────────────────────────────────────────────────┐
│                   Next.js Frontend                       │
│  Dashboard | Vendors | Risk | Anomalies | Certifications│
│  Alerts | Contracts | Copilot | Reports | Evaluation     │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP (REST JSON)
                       ▼
┌─────────────────────────────────────────────────────────┐
│                 FastAPI Backend (Monolith)                │
│                                                          │
│  ┌────────┐ ┌────────┐ ┌───────┐ ┌────────┐ ┌───────┐  │
│  │ Auth   │ │Vendors │ │ Risk  │ │Anomaly │ │ Eval  │  │
│  │ Module │ │Module  │ │Module │ │ Module │ │Module │  │
│  └────────┘ └────────┘ └───────┘ └────────┘ └───────┘  │
│                                                          │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌───────┐ ┌───────┐  │
│  │ Certs  │ │Alerts  │ │Contract│ │Copilot│ │Reports│  │
│  │ Module │ │Module  │ │ Module │ │ Module│ │Module │  │
│  └────────┘ └────────┘ └────────┘ └───────┘ └───────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │  AI Layer                                         │    │
│  │  ├── Risk Scoring (weighted formula, no ML)       │    │
│  │  ├── Anomaly Detection (7 deterministic rules)    │    │
│  │  ├── Contract Analyzer (PyMuPDF + LLM → JSON)     │    │
│  │  ├── Copilot (SQL Generator + LLM Formatter)      │    │
│  │  └── Evaluation Engine (ground truth comparison)  │    │
│  └──────────────────────────────────────────────────┘    │
└──────────────────────┬──────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
   PostgreSQL 16    Redis 7      MinIO (Phase 2)
```

### Technology Decisions

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Web framework | FastAPI | Async support, Pydantic validation, auto OpenAPI docs |
| ORM | SQLAlchemy 2.0 | Mature, async support, Alembic migrations |
| Auth | bcrypt + PyJWT | No external dependency, sufficient for MVP |
| Frontend | Next.js 15 App Router | React server components, good DX |
| UI | Tailwind + ShadCN | Rapid development, accessible components |
| Charts | Recharts | React-native, simple API |
| Async tasks | FastAPI BackgroundTasks | Lightweight; reserve Celery for Phase 2 |
| PDF extraction | PyMuPDF (fitz) | Fast, no OCR dependency |
| Container | Docker Compose | Simple, no K8s overhead |
| Monitoring | Sentry + health check | Appropriate for MVP |

---

## 3. Core Data Flow

The entire system is centered around the two evaluation CSV files.

```
vendor_registry.csv          vendor_labels.csv
         │                          │
         ▼                          │
   CSV Import Module                │
   (Validate + Normalize)           │
         │                          │
         ▼                          │
   PostgreSQL (vendors table)       │
         │                          │
         ▼                          │
   Risk Engine                      │
   (Weighted Formula)               │
         │                          │
         ▼                          │
   Anomaly Engine                   │
   (7 Rules)                        │
         │                          │
         ▼                          ▼
   Evaluation Engine ◄──────────────┘
   (Compare generated vs ground truth)
         │
         ▼
   Dashboard (KPI cards: Recall, Precision, F1)
```

### Import Pipeline Detail

```
vendor_registry.csv
         ↓
   Schema Validation
   (column names, data types, required fields)
         ↓
   Field Mapping
   (CSV columns → DB columns)
         ↓
   Data Quality Checks
   (missing vendor IDs rejected, invalid dates flagged)
         ↓
   Deduplication
   (duplicate vendor_names within organization)
         ↓
   Vendor Insertion
   (PostgreSQL vendors table)
         ↓
   Automatic Risk Score Calculation
         ↓
   Automatic Anomaly Detection
         ↓
   Evaluation Metrics Update
```

---

## 4. Database Schema

### MVP Tables (20)

#### Identity & Access

```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) NOT NULL DEFAULT 'analyst',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

CREATE TABLE roles (
    role_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);
```

#### Vendor Management

```sql
CREATE TABLE vendors (
    vendor_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_name VARCHAR(255) NOT NULL,
    vendor_type VARCHAR(100),
    vendor_owner VARCHAR(255),
    annual_spend NUMERIC(12,2),
    criticality VARCHAR(50),
    contract_status VARCHAR(50),
    risk_tier VARCHAR(20),
    is_archived BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE vendor_categories (
    category_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE vendor_category_mapping (
    vendor_id UUID REFERENCES vendors(vendor_id),
    category_id UUID REFERENCES vendor_categories(category_id),
    PRIMARY KEY (vendor_id, category_id)
);

CREATE TABLE vendor_contacts (
    contact_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_id UUID REFERENCES vendors(vendor_id),
    name VARCHAR(255),
    designation VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(50)
);
```

#### Import Tracking

```sql
CREATE TABLE csv_imports (
    import_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_name VARCHAR(255),
    file_type VARCHAR(50), -- 'registry' or 'labels'
    records_processed INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'pending',
    error_log JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Risk Engine

```sql
CREATE TABLE risk_scores (
    risk_score_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_id UUID REFERENCES vendors(vendor_id),
    security_score NUMERIC(5,2),
    data_access_score NUMERIC(5,2),
    compliance_score NUMERIC(5,2),
    financial_score NUMERIC(5,2),
    contract_score NUMERIC(5,2),
    overall_score NUMERIC(5,2) NOT NULL,
    risk_tier VARCHAR(20) NOT NULL,
    generated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE risk_history (
    history_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_id UUID REFERENCES vendors(vendor_id),
    overall_score NUMERIC(5,2),
    risk_tier VARCHAR(20),
    change_reason TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Anomaly Detection

```sql
CREATE TABLE anomaly_labels (
    label_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    label_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    default_severity VARCHAR(20)
);

CREATE TABLE anomaly_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_id UUID REFERENCES vendors(vendor_id),
    anomaly_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    confidence_score NUMERIC(3,2),
    explanation TEXT,
    detected_at TIMESTAMP DEFAULT NOW()
);
```

#### Evaluation

```sql
CREATE TABLE evaluation_results (
    result_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    anomaly_type VARCHAR(100),
    severity VARCHAR(20),
    true_positives INTEGER DEFAULT 0,
    false_positives INTEGER DEFAULT 0,
    false_negatives INTEGER DEFAULT 0,
    precision NUMERIC(5,4),
    recall NUMERIC(5,4),
    f1_score NUMERIC(5,4),
    computed_at TIMESTAMP DEFAULT NOW()
);
```

#### Compliance

```sql
CREATE TABLE compliance_frameworks (
    framework_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    framework_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE certifications (
    certification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_id UUID REFERENCES vendors(vendor_id),
    certification_type VARCHAR(100) NOT NULL,
    issuer VARCHAR(255),
    issue_date DATE,
    expiry_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'active'
);

CREATE TABLE vendor_compliance (
    vendor_id UUID REFERENCES vendors(vendor_id),
    framework_id UUID REFERENCES compliance_frameworks(framework_id),
    compliance_status VARCHAR(50),
    score NUMERIC(5,2),
    PRIMARY KEY (vendor_id, framework_id)
);
```

#### Data Access

```sql
CREATE TABLE vendor_data_access (
    access_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_id UUID REFERENCES vendors(vendor_id),
    data_type VARCHAR(50),       -- PII, PCI, PHI, Financial, Confidential
    access_level VARCHAR(50),    -- Read, Write, Admin
    system_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true
);
```

#### Alerts

```sql
CREATE TABLE security_alerts (
    alert_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_id UUID REFERENCES vendors(vendor_id),
    alert_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    message TEXT,
    status VARCHAR(50) DEFAULT 'open',
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP
);
```

#### Audit

```sql
CREATE TABLE audit_logs (
    audit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    entity_type VARCHAR(50),     -- vendor, contract, alert, etc.
    entity_id UUID,
    action VARCHAR(50),          -- created, updated, deleted, resolved
    old_value JSONB,
    new_value JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Contracts

```sql
CREATE TABLE contracts (
    contract_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_id UUID REFERENCES vendors(vendor_id),
    contract_name VARCHAR(255),
    contract_type VARCHAR(100),
    start_date DATE,
    end_date DATE,
    status VARCHAR(50),
    storage_path TEXT,
    raw_text TEXT,
    ai_analysis JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Index Recommendations

```sql
CREATE INDEX idx_vendors_risk_tier ON vendors(risk_tier);
CREATE INDEX idx_vendors_vendor_name ON vendors(vendor_name);
CREATE INDEX idx_vendors_vendor_type ON vendors(vendor_type);
CREATE INDEX idx_vendors_contract_status ON vendors(contract_status);
CREATE INDEX idx_risk_scores_vendor_id ON risk_scores(vendor_id);
CREATE INDEX idx_risk_scores_generated_at ON risk_scores(generated_at DESC);
CREATE INDEX idx_risk_history_vendor_id ON risk_history(vendor_id);
CREATE INDEX idx_anomaly_events_vendor_id ON anomaly_events(vendor_id);
CREATE INDEX idx_anomaly_events_severity ON anomaly_events(severity);
CREATE INDEX idx_anomaly_events_anomaly_type ON anomaly_events(anomaly_type);
CREATE INDEX idx_certifications_vendor_id ON certifications(vendor_id);
CREATE INDEX idx_certifications_expiry_date ON certifications(expiry_date);
CREATE INDEX idx_security_alerts_status ON security_alerts(status);
CREATE INDEX idx_contracts_vendor_id ON contracts(vendor_id);
```

### Migration Strategy

- Alembic for schema migrations
- Single initial migration containing all 20 tables
- Each sprint adds incremental migrations
- Never use CASCADE deletes without review

---

## 5. API Surface

### Auth (4 endpoints)

| Method | Endpoint | Description | Priority |
|--------|----------|-------------|----------|
| POST | `/api/v1/auth/signup` | Create account | P0 |
| POST | `/api/v1/auth/login` | Get JWT | P0 |
| POST | `/api/v1/auth/refresh` | Refresh token | P0 |
| POST | `/api/v1/auth/logout` | Invalidate token | P1 |

### Users (5 endpoints)

| Method | Endpoint | Description | Priority |
|--------|----------|-------------|----------|
| GET | `/api/v1/users` | List users | P1 |
| POST | `/api/v1/users` | Create user | P1 |
| GET | `/api/v1/users/{id}` | Get user | P1 |
| PUT | `/api/v1/users/{id}` | Update user | P1 |
| GET | `/api/v1/roles` | List roles | P1 |

### Vendors (7 endpoints)

| Method | Endpoint | Description | Priority |
|--------|----------|-------------|----------|
| GET | `/api/v1/vendors` | List/search vendors | P0 |
| POST | `/api/v1/vendors` | Create vendor | P0 |
| GET | `/api/v1/vendors/{id}` | Get vendor detail | P0 |
| PUT | `/api/v1/vendors/{id}` | Update vendor | P0 |
| DELETE | `/api/v1/vendors/{id}` | Soft delete vendor | P0 |
| POST | `/api/v1/vendors/import` | CSV import | P0 |
| GET | `/api/v1/imports/{id}` | Import job status | P1 |

### Risk (4 endpoints)

| Method | Endpoint | Description | Priority |
|--------|----------|-------------|----------|
| POST | `/api/v1/risk/calculate` | Calculate score for one vendor | P0 |
| GET | `/api/v1/risk/vendors/{id}` | Get current risk score | P0 |
| GET | `/api/v1/risk/vendors/{id}/history` | Risk score history | P1 |
| POST | `/api/v1/risk/recalculate` | Recalculate all vendor scores | P1 |

### Anomalies (3 endpoints)

| Method | Endpoint | Description | Priority |
|--------|----------|-------------|----------|
| GET | `/api/v1/anomalies` | List all anomalies (filterable) | P0 |
| GET | `/api/v1/anomalies/vendor/{id}` | Anomalies for one vendor | P0 |
| GET | `/api/v1/anomalies/labels` | List supported anomaly types | P1 |

### Evaluation (2 endpoints)

| Method | Endpoint | Description | Priority |
|--------|----------|-------------|----------|
| GET | `/api/v1/evaluation/metrics` | Get evaluation metrics | P0 |
| POST | `/api/v1/evaluation/run` | Trigger evaluation run | P1 |

### Certifications (3 endpoints)

| Method | Endpoint | Description | Priority |
|--------|----------|-------------|----------|
| GET | `/api/v1/certifications` | List certifications | P1 |
| POST | `/api/v1/certifications` | Create certification | P1 |
| GET | `/api/v1/certifications/expiring` | Expiring certifications | P1 |

### Alerts (3 endpoints)

| Method | Endpoint | Description | Priority |
|--------|----------|-------------|----------|
| GET | `/api/v1/alerts` | List alerts | P1 |
| POST | `/api/v1/alerts` | Create alert | P1 |
| PATCH | `/api/v1/alerts/{id}/resolve` | Resolve alert | P2 |

### Contracts (3 endpoints)

| Method | Endpoint | Description | Priority |
|--------|----------|-------------|----------|
| POST | `/api/v1/contracts/upload` | Upload contract + AI analysis | P1 |
| GET | `/api/v1/contracts/{id}` | Get contract metadata | P1 |
| GET | `/api/v1/contracts/{id}/analysis` | Get AI analysis result | P1 |

### Copilot (1 endpoint)

| Method | Endpoint | Description | Priority |
|--------|----------|-------------|----------|
| POST | `/api/v1/copilot/query` | Natural language query | P2 |

### Reports (2 endpoints)

| Method | Endpoint | Description | Priority |
|--------|----------|-------------|----------|
| POST | `/api/v1/reports` | Generate report | P1 |
| GET | `/api/v1/reports/{id}/download` | Download report | P1 |

### Dashboard (1 endpoint)

| Method | Endpoint | Description | Priority |
|--------|----------|-------------|----------|
| GET | `/api/v1/dashboard/summary` | Aggregated dashboard data | P0 |

### Health (1 endpoint)

| Method | Endpoint | Description | Priority |
|--------|----------|-------------|----------|
| GET | `/api/v1/health` | Health check | P1 |

### Standard Response Envelope

```json
{
  "success": true,
  "data": {},
  "message": "Operation completed",
  "timestamp": "2026-06-21T10:00:00Z"
}
```

### Standard Error Response

```json
{
  "success": false,
  "error": {
    "code": "VENDOR_NOT_FOUND",
    "message": "Vendor does not exist"
  }
}
```

### Error Codes

```
VENDOR_NOT_FOUND
CONTRACT_NOT_FOUND
CERTIFICATION_EXPIRED
RISK_CALCULATION_FAILED
ANOMALY_DETECTION_FAILED
IMPORT_VALIDATION_FAILED
INSUFFICIENT_PERMISSIONS
REPORT_GENERATION_FAILED
EVALUATION_FAILED
RATE_LIMIT_EXCEEDED
INTERNAL_ERROR
```

### Authentication Strategy

- OAuth2 password flow → JWT access token (15 min) + refresh token (24 hr)
- JWT payload: `{ sub: user_id, role: "admin"|"analyst"|"executive", exp, iat }`
- Middleware: FastAPI dependency `get_current_user()`
- No session table (stateless)
- RBAC enforced at endpoint level via dependency

---

## 6. Frontend Screens

| Screen | Route | Description | Priority |
|--------|-------|-------------|----------|
| Login | `/login` | Auth page | P0 |
| Dashboard | `/dashboard` | KPI cards, risk distribution, evaluation metrics | P0 |
| Vendor List | `/vendors` | Searchable, filterable vendor table | P0 |
| Vendor Detail | `/vendors/{id}` | 360-degree vendor view (profile, risk, contracts, certs, anomalies) | P0 |
| Vendor Create | `/vendors/new` | Vendor creation form | P0 |
| CSV Import | `/import` | Upload + preview + import flow | P0 |
| Risk Register | `/risk` | Vendor ranking by risk score | P0 |
| Anomaly Center | `/anomalies` | All detected anomalies, filterable | P0 |
| Evaluation Dashboard | `/evaluation` | Precision/Recall/F1, confusion matrix | P0 |
| Certifications | `/certifications` | Cert management + expiry view | P1 |
| Alerts | `/alerts` | Alert list + management | P1 |
| Contract Upload | `/contracts/upload` | Upload contract file | P1 |
| Contract Detail | `/contracts/{id}` | View analysis results | P1 |
| Copilot Chat | `/copilot` | Natural language query interface | P2 |
| Reports | `/reports` | Generate + download reports | P1 |
| User Management | `/admin/users` | Manage users and roles | P1 |

### Navigation Structure

```
Sidebar:
├── Dashboard
├── Vendors
│   ├── Vendor List
│   └── Import CSV
├── Risk Register
├── Anomalies
├── Evaluation
├── Certifications
├── Alerts
├── Contracts
├── AI Copilot
├── Reports
└── Administration
    └── Users
```

### Role-Based Access

| Screen | Admin | Analyst | Executive |
|--------|-------|---------|-----------|
| Dashboard | ✓ | ✓ | ✓ |
| Vendors | RW | RW | R |
| Risk Register | RW | RW | R |
| Anomalies | RW | RW | R |
| Evaluation | RW | R | R |
| Certifications | RW | RW | R |
| Alerts | RW | RW | R |
| Contracts | RW | R | R |
| Copilot | ✓ | ✓ | ✓ |
| Reports | RW | RW | RW |
| Admin | ✓ | - | - |

---

## 7. Week-by-Week Implementation Plan

### Week 1: Foundation
**Theme:** Get to a working login + blank dashboard

| Engineer A | Engineer B | Engineer C |
|------------|------------|------------|
| FastAPI scaffold + config + DB setup | Next.js scaffold + Tailwind + layout | Auth APIs (signup/login/refresh/me) |
| PostgreSQL schema (20 tables) | Login page + auth context | User CRUD APIs |
| Alembic initial migration | Protected routing + sidebar shell | Docker Compose (API + DB + Redis) |
| Pydantic models for all entities | API client (Axios wrapper) | CI/CD (GitHub Actions) |

**Deliverable:** User can sign up, log in, see empty dashboard with sidebar.

**Files created:** ~20 backend files, ~15 frontend files

---

### Week 2: Vendor Registry + CSV Import
**Theme:** Get evaluation data into the system

| Engineer A | Engineer B | Engineer C |
|------------|------------|------------|
| Vendor CRUD APIs + search/filter/pagination | Vendor list page (table, search, filters) | CSV import endpoint |
| Risk scoring formula (weighted) | Vendor detail page (profile + risk tab) | Schema validation + field mapping |
| | Vendor create/edit form | Deduplication logic |
| | | Import job status tracking |

**Deliverable:** Vendors can be created individually or bulk-imported from CSV. Risk scores auto-generate.

**Validation:** Import vendor_registry.csv → verify 400 vendors in DB → verify risk scores exist.

---

### Week 3: Anomaly Detection + Evaluation
**Theme:** Core evaluation criteria

| Engineer A | Engineer B | Engineer C |
|------------|------------|------------|
| 7 rule-based anomaly detectors | Anomaly center page (list, filter by severity) | Evaluation engine (ground truth comparison) |
| Severity assignment + explanation gen | Risk register page (ranking, heatmap) | Per-label Precision/Recall/F1 |
| Anomaly event storage + APIs | Anomaly detail in vendor profile | Overall metrics + confusion matrix |
| | | Evaluation metrics API |

**Deliverable:** Anomalies detected correctly. Evaluation dashboard shows Precision/Recall/F1.

**Validation:** Import vendor_labels.csv → compare generated vs ground truth → verify Critical Recall > 90%.

---

### Week 4: Certifications + Alerts + Reports
**Theme:** Supporting features that round out the demo

| Engineer A | Engineer B | Engineer C |
|------------|------------|------------|
| Certification CRUD + expiry detection | Certification management UI | Report generation (PDF + CSV) |
| Alert engine (rule-based triggers) | Alert list + management UI | Dashboard aggregation endpoint |
| Alert email notifications | Evaluation dashboard page (KPI cards) | Report download endpoint |
| Expiring certifications API | | Dashboard summary API |

**Deliverable:** Completes the risk → alert → report loop. Evaluation metrics visible on dashboard.

**Validation:** Add certification with past expiry → verify alert generated → verify risk score updated.

---

### Week 5: Contract AI + Copilot
**Theme:** Demo "wow factor" features

| Engineer A | Engineer B | Engineer C |
|------------|------------|------------|
| Contract upload (PyMuPDF text extraction) | Contract upload UI (drag-and-drop) | Copilot SQL generator (intent → query) |
| LLM analysis prompt (structured JSON output) | Contract detail page (analysis display) | Copilot response formatter (LLM) |
| Contract storage + APIs | Contract list for vendor | Copilot API + chat UI |

**Contract AI pipeline:**
```
PDF Upload → PyMuPDF Text Extraction → LLM Prompt → Structured JSON
```

**Copilot pipeline:**
```
User Question → Intent Classification → SQL Generation → Query Execution → LLM Formatting → Response
```

**Safety for Copilot:**
- Read-only DB role for LLM-generated queries
- Reject DROP/INSERT/UPDATE/DELETE
- Try/except fallback with error message
- Append-only, no destructive operations

**Deliverable:** Upload a contract → AI extracts clauses → structured JSON returned. Ask "which vendors access PII?" → data-driven answer.

---

### Week 6: Polish + Demo
**Theme:** Make it look and feel complete

| Engineer A | Engineer B | Engineer C |
|------------|------------|------------|
| Integration + E2E tests | UI polish (loading states, empty states, errors) | Demo script + environment |
| Performance optimization (query tuning, caching) | Responsive layout fixes | README + setup documentation |
| Bug fixes | Edge case handling | Deploy to VPS or cloud |
| Seed scripts directory | Animation + transitions | Demo video recording |

**Deliverable:** Complete working demo. Deployed and accessible. All evaluation metrics visible. Judges can interact.

### Seed Scripts

Create `scripts/` directory with:

| Script | Purpose |
|--------|---------|
| `scripts/seed_vendors.py` | Load vendor_registry.csv into DB, trigger risk + anomaly engines |
| `scripts/seed_labels.py` | Load vendor_labels.csv into evaluation comparison table |
| `scripts/seed_demo_data.py` | Create sample users, certifications, contracts, alerts for demo walkthrough |

All seed scripts are idempotent (safe to re-run). Used for repeatable demos and CI testing.

**Demo script (3 minutes):**
1. Login → Dashboard shows portfolio overview + Evaluation KPI row (Critical Recall: 94%, F1: 88%) (30s)
2. Evaluation dashboard → Precision/Recall/F1 per label + confusion matrix (30s)
3. Risk Register → vendor ranking by score → click into detail (30s)
4. Anomaly center → filter by critical → show explanations (30s)
5. Contract upload → AI analysis → structured output (30s)
6. Copilot: "Which vendors access PII?" → answer (30s)
7. Reports → generate + download (30s)

---

## 8. Anomaly Detection Rules

7 deterministic rules mapped to evaluation labels.

| # | Rule Logic | Label | Severity |
|---|-----------|-------|----------|
| 1 | `breached = true AND data_access_level IN ('PII', 'PCI', 'PHI')` | BREACHED_VENDOR_HIGH_ACCESS | CRITICAL |
| 2 | `investigation_status = 'under_investigation'` | VENDOR_UNDER_INVESTIGATION | HIGH |
| 3 | `overall_risk_score > 80` | HIGH_RISK_SCORE | HIGH |
| 4 | `has_expired_certification = true` | EXPIRED_CERTIFICATION | HIGH |
| 5 | `breach_date > NOW() - INTERVAL '6 months'` | RECENTLY_BREACHED_VENDOR | HIGH |
| 6 | `contract_status = 'expired' AND has_active_access = true` | CONTRACT_EXPIRED_ACTIVE_ACCESS | MEDIUM |
| 7 | `overall_risk_score BETWEEN 60 AND 80 OR any_single_dimension > 75` | ELEVATED_RISK_VENDOR | MEDIUM |

### Implementation Notes

- Rules run after CSV import for initial scoring
- Rules run on risk recalculation trigger
- Results stored in `anomaly_events` table
- One vendor can have multiple anomalies
- Each anomaly includes an explanation field ("Why this vendor was flagged")
- Explanation is generated by template, not LLM

---

## 9. Evaluation Module

### Purpose

Compare generated anomaly labels against ground truth from `vendor_labels.csv`.

### Data Flow

```
vendor_labels.csv (ground truth)
         ↓
   Parse into dictionary: {(vendor_id, anomaly_type): severity}
         ↓
anomaly_events table (generated labels)
         ↓
   Query into dictionary: {(vendor_id, anomaly_type): severity}
         ↓
   Compare using composite key (vendor_id, anomaly_type)
         ↓
   For each anomaly type AND overall:
         ↓
   Compute metrics
```

### Metrics Computed

| Metric | Formula | Target |
|--------|---------|--------|
| Precision | TP / (TP + FP) | >80% |
| Recall | TP / (TP + FN) | >90% for Critical |
| F1 Score | 2 × (P × R) / (P + R) | >85% |
| Accuracy | (TP + TN) / (TP + TN + FP + FN) | >80% |

### Breakdown Levels

1. **Overall**: All anomaly types combined
2. **By severity**: CRITICAL, HIGH, MEDIUM
3. **By anomaly type**: Each of the 7 labels individually

### API Response

```json
GET /api/v1/evaluation/metrics

{
  "overall": {
    "precision": 0.87,
    "recall": 0.91,
    "f1_score": 0.89,
    "accuracy": 0.85
  },
  "by_severity": {
    "CRITICAL": { "precision": 0.92, "recall": 0.94, "f1_score": 0.93 },
    "HIGH": { "precision": 0.85, "recall": 0.88, "f1_score": 0.86 },
    "MEDIUM": { "precision": 0.80, "recall": 0.82, "f1_score": 0.81 }
  },
  "by_label": {
    "BREACHED_VENDOR_HIGH_ACCESS": { "precision": 0.95, "recall": 0.93, "f1_score": 0.94 },
    "EXPIRED_CERTIFICATION": { "precision": 0.90, "recall": 0.88, "f1_score": 0.89 }
  },
  "confusion_matrix": {
    "labels": ["BREACHED_VENDOR_HIGH_ACCESS", "HIGH_RISK_SCORE", ...],
    "matrix": [[95, 3, 2], [2, 88, 5], ...]
  },
  "computed_at": "2026-06-21T10:00:00Z"
}
```

### Dashboard Display

- **KPI Row**: Critical Recall (94%), Overall Precision (87%), Overall F1 (89%)
- **Per-Label Table**: Label | Precision | Recall | F1 | TP | FP | FN
- **Confusion Matrix**: Heatmap visualization
- **Last Computed**: Timestamp + "Re-evaluate" button

### When Evaluation Runs

1. On CSV import completion (auto)
2. On manual "Run Evaluation" button click
3. Whenever anomaly detection is re-run

---

## 10. Contract AI

### Pipeline

```
PDF Upload
    ↓
PyMuPDF (fitz) — Text Extraction
    ↓
LLM Prompt — Structured JSON Extraction
    ↓
JSON Stored in contracts.ai_analysis column
```

### LLM Prompt Template

```
You are a contract analyst. Extract the following from this contract text.
Return ONLY valid JSON with no additional text.

{
  "breach_notification_days": <integer or null>,
  "data_owner": "<customer|vendor|shared|null>",
  "sla_uptime": "<percentage or null>",
  "liability_cap": "<amount or null>",
  "retention_period_days": <integer or null>,
  "termination_notice_days": <integer or null>,
  "has_gdpr_compliance_clause": <boolean>,
  "has_confidentiality_clause": <boolean>,
  "risk_level": "<low|medium|high|null>",
  "key_obligations": ["obligation1", "obligation2"]
}

Contract text:
[EXTRACTED_TEXT]
```

### Implementation Notes

- Use PyMuPDF for text extraction (fast, pure Python, no OCR)
- If text extraction yields < 50 chars, return "Could not analyze: contract may be scanned"
- No OCR support for MVP (scanned PDFs = "analysis unavailable")
- Cache LLM response in the database (don't re-analyze on every read)
- Use Mistral Small or GPT-4o-mini for cost efficiency
- Timeout: 15 seconds per analysis

---

## 11. Copilot

### Architecture

```
User Question (e.g., "Which vendors access PII?")

    ↓
Step 1: Intent Classification (LLM)
    "Which vendors access PII?" → intent: "vendor_by_data_access"

    ↓
Step 2: SQL Generation (LLM)
    "vendor_by_data_access" + parameters → "SELECT v.vendor_name, v.vendor_type
     FROM vendors v JOIN vendor_data_access vda ON v.vendor_id = vda.vendor_id
     WHERE vda.data_type = 'PII' AND v.is_archived = false"

    ↓
Step 3: Query Execution (safe, read-only DB role)

    ↓
Step 4: Response Formatting (LLM)
    "Here are the vendors that access PII:
     1. Acme Cloud (Cloud Provider)
     2. DataPro Solutions (MSP)
     3. FinServ Corp (Payment Processor)"
```

### Supported Intent Types (MVP)

| Intent | Question Pattern | SQL Pattern |
|--------|-----------------|-------------|
| `vendor_by_data_access` | "Which vendors access X?" | JOIN data_access |
| `vendor_by_risk_tier` | "Show critical/red vendors" | WHERE risk_tier = 'RED' |
| `vendor_by_expired_cert` | "Which certifications expired?" | WHERE expiry_date < NOW() |
| `vendor_by_breach` | "Which vendors were breached?" | WHERE breach_count > 0 |
| `high_risk_summary` | "Show high risk vendors" | WHERE risk_score > 70 |
| `contract_expiring` | "Contracts expiring next month" | WHERE end_date BETWEEN ... |
| `vendor_count_by_type` | "How many cloud vendors?" | GROUP BY vendor_type |
| `top_risk_drivers` | "What causes most risk?" | Top risk factors |
| `general` | Fallback for unrecognized intents | Return relevant vendor data |

### Safety

- Read-only PostgreSQL role for query execution
- Query whitelist: only SELECT statements allowed
- Reject keywords: DROP, INSERT, UPDATE, DELETE, ALTER, TRUNCATE, CREATE
- Max result limit: 50 rows
- Timeout: 10 seconds per query
- Fallback: "I couldn't process that question. Try asking about vendors, risk, or certifications."

---

## 12. What We Are NOT Building

These features are explicitly postponed to Phase 2+.

| Feature | Phase | Reason |
|---------|-------|--------|
| Neo4j Knowledge Graph | Phase 2 | No value at 400 vendors. SQL joins suffice. Adds infrastructure complexity. |
| ML-based Anomaly Detection | Phase 2 | 7 deterministic rules cover evaluation labels. No training data advantage for MVP. |
| Risk Forecasting | Phase 3 | Requires 12+ months historical data and 10,000+ vendors for meaningful ML. |
| Vendor Digital Twin | Phase 4 | Concept not implementation-ready. Needs clear definition first. |
| RAG Pipeline (full) | Phase 2 | SQL Generator + LLM Formatter provides 80% value at 10% cost. |
| OCR for scanned PDFs | Phase 2 | Assume digital PDFs for MVP. OCR adds complexity with rare benefit for evaluation. |
| SSO / SAML / MFA | Phase 2 | Adds 5-7 days of work for zero visible demo value. |
| ServiceNow / Coupa / SAP | Phase 2 | Each integration is 1-2 weeks of proprietary API work. Zero value for evaluation. |
| Remediation Evidence Workflows | Phase 2 | Nice-to-have beyond MVP scope. |
| Report Scheduling | Phase 2 | Manual generation is sufficient for MVP. |
| Kubernetes | Phase 2 | Docker Compose is correct for 3 engineers. K8s for multi-team scaling. |
| Prometheus / Grafana | Phase 2 | Sentry + health check endpoint suffice for MVP monitoring. |
| Full Microservice Extraction | Phase 2 | Modular monolith until team or traffic demands separation. |
| 6 Role Types | — | Reduced to 3 (Admin, Analyst, Executive) for MVP. |
| ML-based Anomaly Detection | Phase 2 | 7 deterministic rules cover evaluation labels. See ADR-001. |

---

## 13. Risk Register

| # | Risk | Impact | Prob | Detection | Mitigation |
|---|------|--------|------|-----------|------------|
| R1 | LLM contract analysis fails on edge-case PDFs | Medium | 40% | During Week 5 testing | Fallback: "Analysis unavailable for scanned documents" |
| R2 | Copilot SQL generator creates invalid queries | Medium | 30% | During Week 5 testing | Read-only DB role, query validation, try/except fallback |
| R3 | CSV import breaks on unexpected data formatting | High | 30% | Week 2 validation | Flexible schema mapping, preview before import, clear error messages |
| R4 | Anomaly recall below 90% evaluation threshold | High | 20% | Week 3 testing | Test against vendor_labels.csv as soon as rules are implemented. Iterate daily. |
| R5 | LLM API rate limits or downtime during demo | Medium | 30% | Week 5-6 | Cache common responses. Pre-generate demo answers. Fallback response templates. |
| R6 | Scope creep (adding features mid-project) | High | 50% | Weekly review | Strict MVP scope enforcement. "Future" list for scope pushback. |
| R7 | Team member knowledge gap on LLM integration | Medium | 20% | Week 1 | Start with simple API calls. No local model deployment. Well-documented patterns. |
| R8 | Database performance with 400 vendors + 1M risk records | Low | 15% | Week 4 | Indexes defined upfront. Query optimization before Week 4. |
| R9 | JWT secret leaked in git | Critical | 10% | Continuous | .env in .gitignore, pre-commit hooks, rotate if suspected |
| R10 | Team member unavailable (sickness, etc.) | Medium | 10% | Ongoing | Cross-train: each engineer understands at least 2 modules |

---

## 14. Total Implementation Estimate

| Week | Theme | Engineering Days | Cumulative |
|------|-------|-----------------|------------|
| 1 | Foundation | 15 | 15 |
| 2 | Vendors + Import | 15 | 30 |
| 3 | Anomaly + Evaluation | 15 | 45 |
| 4 | Certs + Alerts + Reports | 15 | 60 |
| 5 | Contract + Copilot | 15 | 75 |
| 6 | Polish + Demo | 15 | 90 |
| **Total** | | **90 engineering days** | **6 weeks** |

**3 engineers × 6 weeks × 5 days = 90 engineering days** — fits exactly.

### Effort Distribution by Module

| Module | Days | % |
|--------|------|---|
| Auth + Users | 5 | 6% |
| Vendor Registry | 10 | 11% |
| CSV Import | 5 | 6% |
| Risk Engine | 7 | 8% |
| Anomaly Detection | 8 | 9% |
| Evaluation Engine | 4 | 4% |
| Certifications | 4 | 4% |
| Alerts | 5 | 6% |
| Reports | 3 | 3% |
| Contracts | 4 | 4% |
| Copilot | 5 | 6% |
| Dashboard | 5 | 6% |
| Frontend (shared) | 12 | 13% |
| DevOps + Infra | 4 | 4% |
| Testing | 6 | 7% |
| Polish + Demo | 3 | 3% |
| **Total** | **90** | **100%** |

---

## Appendix A: Project Structure

```
sentinel/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── auth.py          # JWT + password hashing
│   │   │   ├── database.py      # SQLAlchemy engine + session
│   │   │   ├── config.py        # Settings (pydantic-settings)
│   │   │   ├── security.py      # RBAC dependencies
│   │   │   └── exceptions.py    # Custom error handlers
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── vendor.py
│   │   │   ├── risk.py
│   │   │   ├── anomaly.py
│   │   │   ├── certification.py
│   │   │   ├── alert.py
│   │   │   └── contract.py
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   ├── vendor.py
│   │   │   ├── risk.py
│   │   │   ├── anomaly.py
│   │   │   ├── evaluation.py
│   │   │   ├── certification.py
│   │   │   ├── alert.py
│   │   │   ├── contract.py
│   │   │   └── copilot.py
│   │   ├── api/                 # Route handlers
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── vendors.py
│   │   │   ├── risk.py
│   │   │   ├── anomalies.py
│   │   │   ├── evaluation.py
│   │   │   ├── certifications.py
│   │   │   ├── alerts.py
│   │   │   ├── contracts.py
│   │   │   ├── copilot.py
│   │   │   ├── reports.py
│   │   │   └── dashboard.py
│   │   ├── services/            # Business logic
│   │   │   ├── vendor_service.py
│   │   │   ├── import_service.py
│   │   │   ├── risk_service.py
│   │   │   ├── anomaly_service.py
│   │   │   ├── evaluation_service.py
│   │   │   ├── certification_service.py
│   │   │   ├── alert_service.py
│   │   │   ├── contract_service.py
│   │   │   └── copilot_service.py
│   │   └── ai/                  # AI/LLM layer
│   │       ├── rules.py         # 7 anomaly rules
│   │       ├── scoring.py       # Weighted formula
│   │       ├── contract_analyzer.py
│   │       ├── copilot.py       # SQL generator + formatter
│   │       └── llm_client.py    # External LLM API wrapper
│   ├── alembic/
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── fixtures/            # Sample CSVs for testing
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── app/
│   │   ├── (auth)/
│   │   │   └── login/
│   │   └── (dashboard)/
│   │       ├── page.tsx         # Dashboard
│   │       ├── vendors/
│   │       ├── risk/
│   │       ├── anomalies/
│   │       ├── evaluation/
│   │       ├── certifications/
│   │       ├── alerts/
│   │       ├── contracts/
│   │       ├── copilot/
│   │       ├── reports/
│   │       └── admin/
│   │           └── users/
│   ├── components/
│   │   ├── ui/                  # ShadCN components
│   │   ├── charts/              # Recharts wrappers
│   │   ├── layout/              # Sidebar, Header, Shell
│   │   └── vendors/             # Vendor-specific components
│   ├── lib/
│   │   ├── api-client.ts        # Axios instance + interceptors
│   │   ├── auth-context.tsx     # Auth state management
│   │   └── utils.ts
│   └── Dockerfile
│
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## Appendix B: Key Dependencies

### Backend (requirements.txt)

```
fastapi==0.115.0
uvicorn[standard]==0.30.0
sqlalchemy==2.0.35
asyncpg==0.29.0
alembic==1.13.0
pydantic==2.9.0
pydantic-settings==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
httpx==0.27.0
PyMuPDF==1.24.0
structlog==24.4.0
sentry-sdk==2.13.0
```

### Frontend (package.json)

```json
{
  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "tailwindcss": "^3.4.0",
    "recharts": "^2.12.0",
    "lucide-react": "^0.450.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.5.0",
    "@radix-ui/react-dialog": "^1.1.0",
    "@radix-ui/react-dropdown-menu": "^2.1.0",
    "@radix-ui/react-tabs": "^1.1.0"
  }
}
```

---

## Appendix C: Demo Script (3 Minutes)

| Time | Action | Screen | What Judge Sees |
|------|--------|--------|-----------------|
| 0:00 | Login | Login | Clean login page |
| 0:10 | Dashboard appears | Dashboard | KPI cards: Total Vendors, Critical, Expiring Certs, Open Anomalies. **Evaluation KPI row at top: Critical Recall 94%, High Risk Recall 91%, F1 88%** |
| 0:25 | Click Evaluation | Evaluation | Per-label Precision/Recall/F1 table, confusion matrix heatmap |
| 0:40 | Click Risk Register | Risk | Vendor ranking by risk score, risk distribution chart |
| 0:55 | Click vendor detail | Vendor Detail | Risk score: 87 (RED), breakdown: Security 42%, Data Access 24%... |
| 1:10 | Click Anomalies | Anomalies | 2 active anomalies: BREACHED_VENDOR_HIGH_ACCESS (CRITICAL), EXPIRED_CERTIFICATION (HIGH) with explanations |
| 1:25 | Click Contracts | Contract Upload | Upload a PDF, click Analyze |
| 1:35 | Analysis appears | Contract Detail | AI extracted: breach notification 15 days, data ownership: vendor, risk level: HIGH |
| 1:50 | Click Copilot | Copilot | Type: "Which vendors access PII?" |
| 2:00 | Response appears | Copilot | "5 vendors: Acme Cloud, DataPro, FinServ..." |
| 2:15 | Click Reports | Reports | Click "Generate Risk Report" |
| 2:25 | Download | Reports | PDF downloads with complete risk register |
| 2:35 | Q&A | Any | Open to questions from judges |
| 3:00 | End | | |

---

*End of Implementation Blueprint*
