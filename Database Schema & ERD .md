# Database Schema & ERD

# SENTINEL

### Security Evaluation & Networked Third-Party Intelligence Engine for Lifecycle Governance

**Version:** 1.0
**Document Type:** Database Schema & Entity Relationship Design (ERD)
**Database:** PostgreSQL 16 + Neo4j

---

# 1. Database Architecture

SENTINEL uses a hybrid data architecture:

### PostgreSQL

Stores:

* Operational Data
* Vendor Records
* Risk Assessments
* Contracts
* Compliance Data
* Audit Logs
* Users

### Neo4j

Stores:

* Vendor Relationships
* System Dependencies
* Data Lineage
* Incident Relationships
* Fourth-Party Risk Connections

---

# 2. High-Level ERD

```text
Organization
    │
    ├── Users
    │
    ├── Business Units
    │
    ├── Vendors
    │       │
    │       ├── Contracts
    │       ├── Certifications
    │       ├── Assessments
    │       ├── Risk Scores
    │       ├── Incidents
    │       ├── Remediation Tasks
    │       └── Data Access Records
    │
    ├── Systems
    │
    ├── Data Assets
    │
    └── Audit Logs
```

---

# 3. Core Entity Inventory

| Module            | Tables |
| ----------------- | ------ |
| Identity & Access | 6      |
| Vendor Management | 8      |
| Contracts         | 5      |
| Compliance        | 5      |
| Risk Engine       | 7      |
| Monitoring        | 4      |
| Remediation       | 5      |
| Reporting         | 2      |
| Audit             | 3      |
| Total             | 45+    |

---

# 4. Identity & Access Management

## organizations

```sql
organization_id UUID PK
name VARCHAR(255)
industry VARCHAR(100)
country VARCHAR(100)
created_at TIMESTAMP
```

---

## users

```sql
user_id UUID PK
organization_id UUID FK

first_name VARCHAR(100)
last_name VARCHAR(100)

email VARCHAR(255)
password_hash TEXT

role_id UUID FK

status VARCHAR(20)

created_at TIMESTAMP
last_login TIMESTAMP
```

---

## roles

```sql
role_id UUID PK

role_name VARCHAR(100)

description TEXT
```

---

## permissions

```sql
permission_id UUID PK

permission_name VARCHAR(255)
module_name VARCHAR(100)
```

---

## role_permissions

```sql
role_permission_id UUID PK

role_id UUID FK
permission_id UUID FK
```

---

## sessions

```sql
session_id UUID PK

user_id UUID FK

jwt_token TEXT
expires_at TIMESTAMP
```

---

# 5. Vendor Management Module

## vendors

```sql
vendor_id UUID PK

organization_id UUID FK

vendor_name VARCHAR(255)

vendor_type VARCHAR(100)

vendor_owner UUID FK

annual_spend NUMERIC

criticality VARCHAR(50)

contract_status VARCHAR(50)

risk_tier VARCHAR(20)

created_at TIMESTAMP
updated_at TIMESTAMP
```

---

## vendor_contacts

```sql
contact_id UUID PK

vendor_id UUID FK

name VARCHAR(255)
designation VARCHAR(100)

email VARCHAR(255)
phone VARCHAR(50)
```

---

## vendor_categories

```sql
category_id UUID PK

category_name VARCHAR(100)
description TEXT
```

---

## vendor_category_mapping

```sql
mapping_id UUID PK

vendor_id UUID FK
category_id UUID FK
```

---

## vendor_assessments

```sql
assessment_id UUID PK

vendor_id UUID FK

assessment_date DATE

assessor_id UUID FK

overall_score NUMERIC

comments TEXT
```

---

## vendor_labels

```sql
label_id UUID PK

vendor_id UUID FK

anomaly_type VARCHAR(100)

severity VARCHAR(50)

explanation TEXT
```

Supports:

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

## vendor_import_jobs

```sql
job_id UUID PK

file_name VARCHAR(255)

records_processed INTEGER

records_failed INTEGER

status VARCHAR(50)

created_at TIMESTAMP
```

---

# 6. Contract Intelligence Module

## contracts

```sql
contract_id UUID PK

vendor_id UUID FK

contract_name VARCHAR(255)

contract_type VARCHAR(100)

start_date DATE
end_date DATE

status VARCHAR(50)

storage_path TEXT

created_at TIMESTAMP
```

---

## contract_clauses

```sql
clause_id UUID PK

contract_id UUID FK

clause_type VARCHAR(100)

clause_text TEXT

risk_level VARCHAR(50)
```

---

## contract_obligations

```sql
obligation_id UUID PK

contract_id UUID FK

obligation_type VARCHAR(100)

description TEXT

due_date DATE
```

---

## contract_versions

```sql
version_id UUID PK

contract_id UUID FK

version_number INTEGER

storage_path TEXT

uploaded_at TIMESTAMP
```

---

## contract_ai_analysis

```sql
analysis_id UUID PK

contract_id UUID FK

model_name VARCHAR(100)

summary TEXT

confidence_score NUMERIC

generated_at TIMESTAMP
```

---

# 7. Compliance Module

## certifications

```sql
certification_id UUID PK

vendor_id UUID FK

certification_type VARCHAR(100)

issuer VARCHAR(255)

issue_date DATE
expiry_date DATE

status VARCHAR(50)
```

---

## compliance_frameworks

```sql
framework_id UUID PK

framework_name VARCHAR(100)

description TEXT
```

Examples:

```text
GDPR
SOC2
ISO27001
PCI-DSS
HIPAA
ISO27701
```

---

## vendor_compliance

```sql
vendor_compliance_id UUID PK

vendor_id UUID FK

framework_id UUID FK

compliance_status VARCHAR(50)

score NUMERIC
```

---

## compliance_evidence

```sql
evidence_id UUID PK

vendor_id UUID FK

framework_id UUID FK

document_path TEXT

uploaded_at TIMESTAMP
```

---

# 8. Risk Engine Module

## risk_scores

```sql
risk_score_id UUID PK

vendor_id UUID FK

security_score NUMERIC

data_access_score NUMERIC

compliance_score NUMERIC

financial_score NUMERIC

contract_score NUMERIC

overall_score NUMERIC

risk_tier VARCHAR(20)

generated_at TIMESTAMP
```

---

## risk_history

```sql
history_id UUID PK

vendor_id UUID FK

old_score NUMERIC
new_score NUMERIC

change_reason TEXT

created_at TIMESTAMP
```

---

## risk_factors

```sql
factor_id UUID PK

vendor_id UUID FK

factor_name VARCHAR(255)

factor_weight NUMERIC

factor_score NUMERIC
```

---

## anomaly_events

```sql
event_id UUID PK

vendor_id UUID FK

anomaly_type VARCHAR(100)

severity VARCHAR(50)

confidence_score NUMERIC

detected_at TIMESTAMP
```

---

## risk_predictions

```sql
prediction_id UUID PK

vendor_id UUID FK

predicted_score NUMERIC

predicted_risk_tier VARCHAR(20)

prediction_date DATE
```

---

# 9. Monitoring Module

## breach_events

```sql
breach_id UUID PK

vendor_id UUID FK

breach_date DATE

breach_source VARCHAR(255)

description TEXT

severity VARCHAR(50)
```

---

## security_alerts

```sql
alert_id UUID PK

vendor_id UUID FK

alert_type VARCHAR(100)

severity VARCHAR(50)

message TEXT

status VARCHAR(50)

created_at TIMESTAMP
```

---

## monitoring_sources

```sql
source_id UUID PK

source_name VARCHAR(255)

source_type VARCHAR(100)

endpoint TEXT
```

---

## monitoring_jobs

```sql
job_id UUID PK

source_id UUID FK

status VARCHAR(50)

executed_at TIMESTAMP
```

---

# 10. Data Access Module

## systems

```sql
system_id UUID PK

system_name VARCHAR(255)

system_type VARCHAR(100)

owner_id UUID FK
```

---

## data_assets

```sql
asset_id UUID PK

asset_name VARCHAR(255)

data_type VARCHAR(100)

classification VARCHAR(100)
```

Examples:

```text
PII
PCI
PHI
CONFIDENTIAL
PUBLIC
```

---

## vendor_system_access

```sql
access_id UUID PK

vendor_id UUID FK

system_id UUID FK

access_type VARCHAR(100)

active BOOLEAN
```

---

## vendor_data_access

```sql
data_access_id UUID PK

vendor_id UUID FK

asset_id UUID FK

access_level VARCHAR(100)
```

---

# 11. Remediation Module

## remediation_cases

```sql
case_id UUID PK

vendor_id UUID FK

title VARCHAR(255)

severity VARCHAR(50)

status VARCHAR(50)

created_at TIMESTAMP
```

---

## remediation_tasks

```sql
task_id UUID PK

case_id UUID FK

assigned_to UUID FK

due_date DATE

status VARCHAR(50)
```

---

## remediation_evidence

```sql
evidence_id UUID PK

task_id UUID FK

file_path TEXT

uploaded_at TIMESTAMP
```

---

## remediation_comments

```sql
comment_id UUID PK

case_id UUID FK

user_id UUID FK

comment TEXT

created_at TIMESTAMP
```

---

# 12. Reporting Module

## reports

```sql
report_id UUID PK

report_type VARCHAR(100)

generated_by UUID FK

generated_at TIMESTAMP

storage_path TEXT
```

---

## report_exports

```sql
export_id UUID PK

report_id UUID FK

export_format VARCHAR(50)

created_at TIMESTAMP
```

---

# 13. Audit Module

## audit_logs

```sql
audit_id UUID PK

user_id UUID FK

action VARCHAR(255)

entity_type VARCHAR(100)

entity_id UUID

timestamp TIMESTAMP
```

---

## login_history

```sql
login_id UUID PK

user_id UUID FK

ip_address VARCHAR(100)

login_time TIMESTAMP
```

---

## activity_history

```sql
activity_id UUID PK

user_id UUID FK

activity_type VARCHAR(255)

details JSONB

created_at TIMESTAMP
```

---

# 14. Neo4j Knowledge Graph Schema

## Nodes

```text
Vendor
Contract
Certification
Incident
System
DataAsset
BusinessUnit
User
Organization
```

---

## Relationships

```text
(Vendor)-[:ACCESSES]->(System)

(Vendor)-[:USES]->(DataAsset)

(Vendor)-[:HAS_CONTRACT]->(Contract)

(Vendor)-[:CERTIFIED_BY]->(Certification)

(Vendor)-[:INVOLVED_IN]->(Incident)

(System)-[:CONTAINS]->(DataAsset)

(BusinessUnit)-[:OWNS]->(Vendor)

(User)-[:MANAGES]->(Vendor)
```

---

# 15. Critical ERD Relationships

```text
Organization
     │
     ├── Users
     │
     ├── Vendors
     │      ├── Contracts
     │      ├── Certifications
     │      ├── Risk Scores
     │      ├── Incidents
     │      ├── Remediation Cases
     │      └── Data Access
     │
     ├── Systems
     │      └── Data Assets
     │
     └── Audit Logs
```

---

# 16. Database Scalability Targets

| Entity              | Capacity    |
| ------------------- | ----------- |
| Vendors             | 10,000+     |
| Contracts           | 100,000+    |
| Risk Records        | 1,000,000+  |
| Audit Events        | 50,000,000+ |
| Alerts              | 5,000,000+  |
| Users               | 100,000+    |
| Graph Relationships | 10,000,000+ |

---

# 17. Database Summary

The SENTINEL database architecture combines PostgreSQL for transactional workloads and Neo4j for relationship intelligence. The schema supports vendor lifecycle management, compliance tracking, contract intelligence, anomaly detection, risk analytics, monitoring, remediation workflows, AI-generated insights, and enterprise-scale auditability while maintaining extensibility for future Digital Twin and Fourth-Party Risk capabilities.
