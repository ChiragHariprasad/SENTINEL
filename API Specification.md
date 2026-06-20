# API Specification

# SENTINEL

### Security Evaluation & Networked Third-Party Intelligence Engine for Lifecycle Governance

**Version:** 1.0
**Specification Type:** REST API Specification
**Protocol:** HTTPS
**Format:** JSON
**Authentication:** OAuth2 + JWT
**API Version:** v1

---

# 1. API Overview

Base URL

```http
https://api.sentinel.ai/api/v1
```

Content Type

```http
Content-Type: application/json
```

Response Format

```json
{
  "success": true,
  "data": {},
  "message": "Operation completed",
  "timestamp": "2026-06-21T10:00:00Z"
}
```

---

# 2. Authentication & Authorization

## Login

### POST

```http
/auth/login
```

Request

```json
{
  "email": "analyst@company.com",
  "password": "********"
}
```

Response

```json
{
  "success": true,
  "access_token": "jwt_token",
  "refresh_token": "refresh_token",
  "expires_in": 3600,
  "role": "Vendor Risk Analyst"
}
```

---

## Refresh Token

### POST

```http
/auth/refresh
```

Request

```json
{
  "refresh_token": "refresh_token"
}
```

---

## Logout

### POST

```http
/auth/logout
```

Headers

```http
Authorization: Bearer <token>
```

---

# 3. Authorization Model

| Role                | Access                  |
| ------------------- | ----------------------- |
| Administrator       | Full Access             |
| Vendor Risk Analyst | Vendor/Risk Modules     |
| Compliance Officer  | Compliance Modules      |
| Procurement Manager | Vendor/Contract Modules |
| Auditor             | Read-Only Access        |
| Executive           | Dashboard & Reports     |

---

# 4. Standard Headers

Request

```http
Authorization: Bearer <JWT>

Content-Type: application/json

X-Correlation-ID: uuid
```

Response

```http
X-Request-ID: uuid
```

---

# 5. Vendor Management APIs

## Create Vendor

### POST

```http
/vendors
```

Request

```json
{
  "vendor_name": "Acme Cloud",
  "vendor_type": "Cloud Provider",
  "annual_spend": 500000,
  "criticality": "HIGH",
  "business_owner": "Security Team"
}
```

Response

```json
{
  "vendor_id": "VEN-001",
  "status": "created"
}
```

---

## Get Vendor

### GET

```http
/vendors/{vendor_id}
```

Response

```json
{
  "vendor_id": "VEN-001",
  "vendor_name": "Acme Cloud",
  "risk_tier": "RED",
  "overall_score": 87
}
```

---

## Search Vendors

### GET

```http
/vendors
```

Query Parameters

```http
?page=1
&size=20
&risk_tier=RED
&vendor_type=Cloud
```

Response

```json
{
  "total": 250,
  "items": []
}
```

---

## Update Vendor

### PUT

```http
/vendors/{vendor_id}
```

---

## Delete Vendor

### DELETE

```http
/vendors/{vendor_id}
```

Soft delete only.

---

# 6. Bulk Import APIs

## Upload Vendor Registry

### POST

```http
/vendors/import
```

Content Type

```http
multipart/form-data
```

Parameters

```text
file
mapping_template
```

Supported Files

```text
vendor_registry.csv
vendor_labels.csv
xlsx
json
```

Response

```json
{
  "job_id": "JOB-1001",
  "status": "processing"
}
```

---

## Import Status

### GET

```http
/imports/{job_id}
```

Response

```json
{
  "job_id": "JOB-1001",
  "processed": 400,
  "failed": 3,
  "status": "completed"
}
```

---

# 7. Contract Intelligence APIs

## Upload Contract

### POST

```http
/contracts/upload
```

Content Type

```http
multipart/form-data
```

Parameters

```text
file
vendor_id
contract_type
```

Response

```json
{
  "contract_id": "CON-101",
  "analysis_status": "queued"
}
```

---

## Get Contract Analysis

### GET

```http
/contracts/{contract_id}/analysis
```

Response

```json
{
  "contract_id": "CON-101",
  "breach_notification_days": 15,
  "data_ownership": "vendor",
  "sla_uptime": "99.9%",
  "risk_level": "HIGH"
}
```

---

## Extracted Clauses

### GET

```http
/contracts/{contract_id}/clauses
```

Response

```json
{
  "clauses": [
    {
      "type": "Breach Notification",
      "risk": "HIGH"
    }
  ]
}
```

---

# 8. Compliance APIs

## Create Certification

### POST

```http
/certifications
```

Request

```json
{
  "vendor_id": "VEN-001",
  "certification_type": "SOC2",
  "expiry_date": "2027-06-01"
}
```

---

## List Certifications

### GET

```http
/certifications
```

---

## Expiring Certifications

### GET

```http
/certifications/expiring
```

Query

```http
?days=60
```

Response

```json
{
  "vendors": []
}
```

---

# 9. Risk Engine APIs

## Calculate Risk

### POST

```http
/risk/calculate
```

Request

```json
{
  "vendor_id": "VEN-001"
}
```

Response

```json
{
  "risk_score": 89,
  "risk_tier": "RED",
  "severity": "CRITICAL"
}
```

---

## Get Vendor Risk

### GET

```http
/risk/vendors/{vendor_id}
```

Response

```json
{
  "vendor_id": "VEN-001",
  "overall_score": 89,
  "risk_tier": "RED",
  "last_updated": "2026-06-21"
}
```

---

## Risk History

### GET

```http
/risk/vendors/{vendor_id}/history
```

Response

```json
{
  "history": []
}
```

---

# 10. Anomaly Detection APIs

## List Anomalies

### GET

```http
/anomalies
```

Query

```http
?severity=CRITICAL
```

Response

```json
{
  "count": 15,
  "items": []
}
```

---

## Get Vendor Anomalies

### GET

```http
/anomalies/vendor/{vendor_id}
```

Response

```json
{
  "vendor_id": "VEN-001",
  "anomalies": [
    {
      "type": "BREACHED_VENDOR_HIGH_ACCESS",
      "severity": "CRITICAL",
      "confidence": 0.94
    }
  ]
}
```

---

## Supported Labels

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

# 11. Monitoring APIs

## Create Alert

### POST

```http
/alerts
```

---

## List Alerts

### GET

```http
/alerts
```

Query

```http
?status=open
```

---

## Resolve Alert

### PATCH

```http
/alerts/{alert_id}/resolve
```

Response

```json
{
  "status": "resolved"
}
```

---

# 12. Remediation APIs

## Create Case

### POST

```http
/remediation/cases
```

Request

```json
{
  "vendor_id": "VEN-001",
  "title": "Expired SOC2"
}
```

---

## Create Task

### POST

```http
/remediation/tasks
```

---

## Upload Evidence

### POST

```http
/remediation/evidence
```

---

## Close Case

### PATCH

```http
/remediation/cases/{case_id}/close
```

---

# 13. Knowledge Graph APIs

## Vendor Relationships

### GET

```http
/graph/vendor/{vendor_id}
```

Response

```json
{
  "nodes": [],
  "edges": []
}
```

---

## Graph Search

### POST

```http
/graph/query
```

Request

```json
{
  "query": "Which vendors access customer PII?"
}
```

Response

```json
{
  "results": []
}
```

---

# 14. AI Copilot APIs

## Ask Copilot

### POST

```http
/copilot/query
```

Request

```json
{
  "question": "Which vendors have expired certifications?"
}
```

Response

```json
{
  "answer": "...",
  "sources": []
}
```

---

## Generate Report

### POST

```http
/copilot/report
```

Request

```json
{
  "report_type": "Executive Risk Summary"
}
```

---

# 15. Reporting APIs

## Generate Report

### POST

```http
/reports
```

Request

```json
{
  "report_type": "Vendor Risk Register"
}
```

Response

```json
{
  "report_id": "REP-1001",
  "status": "queued"
}
```

---

## Download Report

### GET

```http
/reports/{report_id}/download
```

---

# 16. Integration APIs

## ServiceNow Integration

### POST

```http
/integrations/servicenow/ticket
```

Request

```json
{
  "vendor_id": "VEN-001",
  "severity": "CRITICAL"
}
```

---

## Coupa Sync

### POST

```http
/integrations/coupa/sync
```

---

## SAP Ariba Sync

### POST

```http
/integrations/ariba/sync
```

---

# 17. Webhook Events

## Supported Events

```text
vendor.created

vendor.updated

vendor.deleted

risk.score.updated

anomaly.detected

contract.uploaded

contract.analyzed

certification.expiring

alert.created

alert.resolved

remediation.case.created
```

---

# 18. Error Handling

## Standard Error Response

```json
{
  "success": false,
  "error": {
    "code": "VENDOR_NOT_FOUND",
    "message": "Vendor does not exist"
  }
}
```

---

## HTTP Status Codes

| Code | Meaning               |
| ---- | --------------------- |
| 200  | Success               |
| 201  | Created               |
| 202  | Accepted              |
| 400  | Bad Request           |
| 401  | Unauthorized          |
| 403  | Forbidden             |
| 404  | Not Found             |
| 409  | Conflict              |
| 422  | Validation Error      |
| 429  | Rate Limited          |
| 500  | Internal Server Error |

---

## Business Error Codes

```text
VENDOR_NOT_FOUND

CONTRACT_NOT_FOUND

CERTIFICATION_EXPIRED

RISK_CALCULATION_FAILED

ANOMALY_DETECTION_FAILED

IMPORT_VALIDATION_FAILED

INSUFFICIENT_PERMISSIONS

REPORT_GENERATION_FAILED

INTEGRATION_FAILURE
```

---

# 19. Rate Limits

| Endpoint Type     | Limit   |
| ----------------- | ------- |
| Authentication    | 10/min  |
| Standard APIs     | 1000/hr |
| AI Copilot        | 100/hr  |
| Report Generation | 50/hr   |
| File Uploads      | 100/day |

---

# 20. OpenAPI Metadata

```yaml
openapi: 3.1.0
info:
  title: SENTINEL API
  version: 1.0.0
  description: Third-Party Risk Intelligence Platform API

servers:
  - url: https://api.sentinel.ai/api/v1

security:
  - bearerAuth: []

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

---

# 21. API Summary

| Category        | Endpoints |
| --------------- | --------- |
| Authentication  | 3         |
| Vendors         | 5         |
| Imports         | 2         |
| Contracts       | 3         |
| Compliance      | 3         |
| Risk            | 3         |
| Anomalies       | 2         |
| Monitoring      | 3         |
| Remediation     | 4         |
| Knowledge Graph | 2         |
| AI Copilot      | 2         |
| Reports         | 2         |
| Integrations    | 3         |
| Total           | 34+       |

The API architecture is designed around REST principles, JWT authentication, OpenAPI compatibility, enterprise integrations, and scalable asynchronous processing to support large-scale third-party risk management operations.
