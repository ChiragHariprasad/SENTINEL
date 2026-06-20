# Technical Architecture Document (TAD)

# SENTINEL

### Security Evaluation & Networked Third-Party Intelligence Engine for Lifecycle Governance

**Version:** 1.0
**Document Type:** Technical Architecture Document (TAD)
**Architecture Style:** Cloud-Native Microservice Architecture
**System Type:** AI-Powered Third-Party Risk Management Platform

---

# 1. Architecture Overview

## Purpose

The SENTINEL architecture provides a scalable, secure, and extensible platform for vendor risk management, compliance tracking, contract intelligence, anomaly detection, and continuous third-party monitoring.

The architecture supports:

* 10,000+ vendors
* 100+ concurrent users
* Real-time risk scoring
* AI-powered contract analysis
* Knowledge graph analytics
* Continuous monitoring pipelines
* Enterprise integrations

---

# 2. High-Level Architecture

```text
                    ┌─────────────────────┐
                    │     Web Portal      │
                    │ Next.js + Tailwind  │
                    └──────────┬──────────┘
                               │
                               ▼

                    ┌─────────────────────┐
                    │     API Gateway     │
                    │      FastAPI        │
                    └──────────┬──────────┘

 ┌─────────────────┬───────────┼───────────┬─────────────────┐
 │                 │           │           │                 │
 ▼                 ▼           ▼           ▼                 ▼

Vendor        Contract      Risk       Monitoring       AI Copilot
Service       Service      Service      Service          Service

 │               │            │            │               │
 └───────────────┴────────────┴────────────┴───────────────┘
                              │
                              ▼

                    ┌─────────────────────┐
                    │ Event Bus / Queue   │
                    │ Redis + Celery      │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼─────────────────────┐
        │                      │                     │

        ▼                      ▼                     ▼

 PostgreSQL              Neo4j Graph           Object Store
 Operational DB          Knowledge Graph       Contracts/PDFs

                               │
                               ▼

                    ┌─────────────────────┐
                    │ Monitoring Stack    │
                    │ Grafana/Prometheus  │
                    └─────────────────────┘
```

---

# 3. Architecture Principles

## AP-01

API-First Design

All functionality exposed through REST APIs.

---

## AP-02

Microservice-Oriented

Independent deployment of major services.

---

## AP-03

Event-Driven Processing

Long-running AI workloads handled asynchronously.

---

## AP-04

Security by Design

RBAC, encryption, audit logging, and zero-trust principles.

---

## AP-05

Scalability

Horizontal scaling supported for all stateless services.

---

# 4. Technology Stack

## Frontend Layer

### Framework

```text
Next.js 15
React
TypeScript
```

### UI Components

```text
TailwindCSS
ShadCN
Chart.js
Plotly
```

### Authentication

```text
JWT
OAuth2
SSO
```

---

## Backend Layer

### API Services

```text
FastAPI
Python 3.12
Uvicorn
Gunicorn
```

### Async Processing

```text
Celery
Redis
```

### AI Orchestration

```text
LangChain
LlamaIndex
```

---

## Databases

### Operational Database

```text
PostgreSQL
```

Stores:

* Vendors
* Contracts
* Certifications
* Assessments
* Risk Scores
* Users

---

### Knowledge Graph

```text
Neo4j
```

Stores:

* Vendor relationships
* Data assets
* Incidents
* Dependencies

---

### Cache Layer

```text
Redis
```

Stores:

* Sessions
* Query cache
* Risk cache
* AI context cache

---

### Object Storage

```text
MinIO
```

Stores:

* Contracts
* Evidence
* Reports
* Uploaded files

---

# 5. Infrastructure Architecture

## Deployment Environment

### Development

```text
Docker Compose
```

### Production

```text
Kubernetes
```

---

## Infrastructure Components

```text
NGINX Ingress

API Gateway

Application Pods

Worker Pods

PostgreSQL Cluster

Redis Cluster

Neo4j Cluster

MinIO Cluster
```

---

# 6. Core Services

## Vendor Service

### Responsibilities

* Vendor CRUD
* Vendor search
* Vendor onboarding
* Vendor classification

### Database

PostgreSQL

---

## Contract Intelligence Service

### Responsibilities

* Contract upload
* OCR processing
* Clause extraction
* Metadata generation

### AI Models

```text
Llama 3
Gemma
Mistral
```

---

## Risk Engine Service

### Responsibilities

* Risk score generation
* Risk recalculation
* Anomaly detection

### Outputs

```text
Risk Score
Risk Tier
Severity
Anomaly Labels
Recommendations
```

---

## Monitoring Service

### Responsibilities

* Certification tracking
* Breach monitoring
* Vendor health monitoring
* Alert generation

---

## AI Copilot Service

### Responsibilities

* Natural language queries
* Risk explanations
* Report generation
* Recommendation generation

---

# 7. Data Flow Architecture

## Vendor Onboarding Flow

```text
CSV Upload

      ↓

Schema Validation

      ↓

Field Mapping

      ↓

Vendor Service

      ↓

PostgreSQL

      ↓

Risk Engine

      ↓

Initial Risk Score
```

---

## Contract Analysis Flow

```text
Contract Upload

      ↓

MinIO Storage

      ↓

OCR Extraction

      ↓

LLM Processing

      ↓

Clause Extraction

      ↓

Structured Metadata

      ↓

Risk Engine
```

---

## Monitoring Flow

```text
External Feeds

      ↓

Monitoring Service

      ↓

Event Queue

      ↓

Risk Recalculation

      ↓

Alert Generation
```

---

# 8. AI/ML Architecture

## Model Layer

### Contract Intelligence

Purpose:

Extract contractual obligations.

Models:

```text
Llama 3
Mistral
Gemma
```

Tasks:

* NER
* Clause Extraction
* Summarization

---

### Anomaly Detection

Purpose:

Detect abnormal vendor conditions.

Algorithms:

```text
Isolation Forest
Local Outlier Factor
```

Input:

```text
Vendor Registry
Risk Metrics
Compliance Data
```

Output:

```text
Anomaly Labels
Severity
Confidence
```

---

### Risk Prediction

Purpose:

Forecast future vendor risk.

Models:

```text
XGBoost
LightGBM
```

Predictions:

```text
Risk Tier
Future Risk Score
Probability of Escalation
```

---

### Embedding Service

Purpose:

Semantic search.

Model:

```text
Sentence Transformers
```

Storage:

```text
pgvector
```

---

# 9. Sample Dataset Processing

## Supported Input Files

Mandatory:

```text
vendor_registry.csv
vendor_labels.csv
```

---

## Ingestion Pipeline

```text
CSV Upload

      ↓

Schema Validation

      ↓

Field Mapping

      ↓

Data Quality Checks

      ↓

Deduplication

      ↓

Vendor Database
```

---

## Validation Rules

* Missing vendor IDs rejected
* Invalid dates flagged
* Duplicate vendors identified
* Certification dates validated

---

# 10. Risk Scoring Architecture

## Scoring Formula

```text
Risk Score =

0.35 × Security

+

0.25 × Data Access

+

0.15 × Compliance

+

0.15 × Financial

+

0.10 × Contract
```

---

## Risk Levels

```text
0-40   Green

41-70  Yellow

71-100 Red
```

---

## Anomaly Engine

Supported Labels:

```text
BREACHED_VENDOR_HIGH_ACCESS

VENDOR_UNDER_INVESTIGATION

HIGH_RISK_SCORE

EXPIRED_CERTIFICATION

RECENTLY_BREACHED_VENDOR

CONTRACT_EXPIRED_ACTIVE_ACCESS

ELEVATED_RISK_VENDOR
```

---

# 11. API Architecture

## Authentication

### POST

```http
/api/v1/auth/login
```

---

### POST

```http
/api/v1/auth/logout
```

---

## Vendor APIs

### GET

```http
/api/v1/vendors
```

List vendors.

---

### POST

```http
/api/v1/vendors
```

Create vendor.

---

### GET

```http
/api/v1/vendors/{vendor_id}
```

Get vendor details.

---

### PUT

```http
/api/v1/vendors/{vendor_id}
```

Update vendor.

---

## Risk APIs

### GET

```http
/api/v1/risk/vendors/{vendor_id}
```

Get vendor risk.

---

### POST

```http
/api/v1/risk/recalculate
```

Trigger recalculation.

---

## Contract APIs

### POST

```http
/api/v1/contracts/upload
```

Upload contract.

---

### GET

```http
/api/v1/contracts/{id}/analysis
```

Retrieve extracted clauses.

---

## Copilot APIs

### POST

```http
/api/v1/copilot/query
```

Natural language queries.

---

# 12. Knowledge Graph Architecture

## Node Types

```text
Vendor
Contract
Certification
DataAsset
Incident
BusinessUnit
System
User
```

---

## Relationship Types

```text
ACCESSES

OWNS

USES

CONTAINS

BREACHED

CERTIFIED_BY

CONNECTED_TO
```

---

## Example Query

```cypher
MATCH (v:Vendor)-[:ACCESSES]->(d:DataAsset)
WHERE d.type='PII'
RETURN v
```

---

# 13. Security Architecture

## Authentication

```text
OAuth2
JWT
SSO
```

---

## Authorization

RBAC Roles:

```text
Administrator

Vendor Risk Analyst

Compliance Officer

Procurement Manager

Auditor

Executive
```

---

## Data Protection

```text
AES-256 Encryption At Rest

TLS 1.3 In Transit
```

---

## Audit Logging

Track:

* Login
* Vendor changes
* Risk changes
* Contract uploads
* Administrative actions

---

# 14. Monitoring & Observability

## Metrics

* API latency
* Error rate
* Queue depth
* Risk processing time
* AI inference time

---

## Logging

```text
Loki
ELK
```

---

## Monitoring

```text
Prometheus
Grafana
```

---

# 15. Scalability Targets

| Component          | Target   |
| ------------------ | -------- |
| Vendors            | 10,000+  |
| Contracts          | 100,000+ |
| Concurrent Users   | 100+     |
| API Response Time  | <2 sec   |
| Dashboard Load     | <3 sec   |
| Risk Recalculation | <60 sec  |
| Contract Analysis  | <30 sec  |
| Availability       | 99.9%    |

---

# 16. Future Architecture Enhancements

## Phase 2

* ServiceNow Integration
* Coupa Integration
* SAP Ariba Integration
* Jira Service Management Integration

## Phase 3

* Vendor Digital Twin
* Fourth-Party Risk Graph
* Threat Intelligence Platform
* Multi-Tenant SaaS Architecture
* Real-Time Streaming Risk Engine

---

# 17. Architecture Summary

SENTINEL adopts a cloud-native microservice architecture built around vendor intelligence, AI-powered contract analysis, anomaly detection, continuous monitoring, and knowledge graph analytics. The architecture is designed to support enterprise-scale third-party risk management while maintaining extensibility for future predictive risk, digital twin, and ecosystem intelligence capabilities.
