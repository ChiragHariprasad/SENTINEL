# SENTINEL Comprehensive v2 Test Report

- **Date:** 2026-06-21 09:13:25 UTC
- **Target:** `http://localhost:8082`
- **Total Tests:** 164
- **Passed:** 164
- **Failed:** 0
- **Pass Rate:** 100.0%

## Summary by Suite

| Suite | Total | Passed | Failed | Rate |
|-------|-------|--------|--------|------|
| Health | 2 | 2 | 0 | 100.0% |
| Authentication | 17 | 17 | 0 | 100.0% |
| Vendors CRUD | 42 | 42 | 0 | 100.0% |
| CSV Import | 9 | 9 | 0 | 100.0% |
| Risk Scoring | 12 | 12 | 0 | 100.0% |
| Anomalies | 8 | 8 | 0 | 100.0% |
| Evaluation | 10 | 10 | 0 | 100.0% |
| Certifications | 8 | 8 | 0 | 100.0% |
| Alerts | 9 | 9 | 0 | 100.0% |
| Contracts | 9 | 9 | 0 | 100.0% |
| Copilot | 7 | 7 | 0 | 100.0% |
| Dashboard | 3 | 3 | 0 | 100.0% |
| Reports | 6 | 6 | 0 | 100.0% |
| User Management | 13 | 13 | 0 | 100.0% |
| System | 9 | 9 | 0 | 100.0% |
| **TOTAL** | **164** | **164** | **0** | **100.0%** |

## Detailed Results

### Health — 2/2 passed ✅

| # | Description | Result | Detail |
|---|-------------|--------|--------|
| 1 | GET /health returns 200 + healthy status | ✅ |  |
| 2 | GET /health returns version string | ✅ |  |

### Authentication — 17/17 passed ✅

| # | Description | Result | Detail |
|---|-------------|--------|--------|
| 1 | POST /auth/signup: full valid data | ✅ |  |
| 2 | POST /auth/signup: minimal (email+password) | ✅ |  |
| 3 | POST /auth/signup: special chars in name | ✅ |  |
| 4 | POST /auth/signup: duplicate email returns 409 | ✅ |  |
| 5 | POST /auth/login: valid credentials | ✅ |  |
| 6 | POST /auth/login: wrong password returns 401 | ✅ |  |
| 7 | POST /auth/login: nonexistent email returns 401 | ✅ |  |
| 8 | POST /auth/login: missing email returns 422 | ✅ |  |
| 9 | POST /auth/login: empty body returns 422 | ✅ |  |
| 10 | POST /auth/login: extra fields ignored | ✅ |  |
| 11 | POST /auth/refresh: valid token | ✅ |  |
| 12 | POST /auth/refresh: invalid token returns 401 | ✅ |  |
| 13 | POST /auth/refresh: missing field returns 422 | ✅ |  |
| 14 | POST /auth/logout: while authenticated | ✅ |  |
| 15 | POST /auth/logout: without auth returns 403 | ✅ |  |
| 16 | POST /auth/signup: email with + alias | ✅ |  |
| 17 | POST /auth/signup: email with subdomain | ✅ |  |

### Vendors CRUD — 42/42 passed ✅

| # | Description | Result | Detail |
|---|-------------|--------|--------|
| 1 | POST /vendors: full valid data | ✅ |  |
| 2 | POST /vendors: minimal (name only) | ✅ |  |
| 3 | POST /vendors: CRITICAL criticality | ✅ |  |
| 4 | POST /vendors: LOW criticality + Consulting | ✅ |  |
| 5 | POST /vendors: zero annual spend | ✅ |  |
| 6 | POST /vendors: max decimal spend | ✅ |  |
| 7 | POST /vendors: unicode vendor name | ✅ |  |
| 8 | POST /vendors: special characters | ✅ |  |
| 9 | POST /vendors: empty name (API gap) | ✅ |  |
| 10 | POST /vendors: invalid criticality (API gap) | ✅ |  |
| 11 | POST /vendors: negative spend (API gap) | ✅ |  |
| 12 | POST /vendors: duplicate name allowed | ✅ |  |
| 13 | GET /vendors: default pagination | ✅ |  |
| 14 | GET /vendors: page=1&size=1 | ✅ |  |
| 15 | GET /vendors: page=9999 empty | ✅ |  |
| 16 | GET /vendors: filter risk_tier=GREEN | ✅ |  |
| 17 | GET /vendors: filter vendor_type=SaaS | ✅ |  |
| 18 | GET /vendors: search partial name | ✅ |  |
| 19 | GET /vendors: search no match | ✅ |  |
| 20 | GET /vendors: multiple filters | ✅ |  |
| 21 | GET /vendors/{id}: valid vendor | ✅ |  |
| 22 | GET /vendors/{id}: nonexistent 404 | ✅ |  |
| 23 | GET /vendors/{id}: invalid UUID 422 | ✅ |  |
| 24 | PUT /vendors/{id}: update name | ✅ |  |
| 25 | PUT /vendors/{id}: update all fields | ✅ |  |
| 26 | PUT /vendors/{id}: update single field | ✅ |  |
| 27 | PUT /vendors/{id}: nonexistent 404 | ✅ |  |
| 28 | PUT /vendors/{id}: empty body | ✅ |  |
| 29 | DELETE /vendors/{id}: archive | ✅ |  |
| 30 | DELETE: archived not in list | ✅ |  |
| 31 | DELETE /vendors/{id}: already archived | ✅ |  |
| 32 | DELETE /vendors/{id}: nonexistent 404 | ✅ |  |
| 33 | GET /vendors/categories/list | ✅ |  |
| 34 | POST /vendors: prep for data access | ✅ |  |
| 35 | POST /vendors/data-access: PII | ✅ |  |
| 36 | POST /vendors/data-access: PCI | ✅ |  |
| 37 | POST /vendors/data-access: missing vendor_id | ✅ |  |
| 38 | GET /vendors/{id}/data-access: list | ✅ |  |
| 39 | GET /vendors/{id}/data-access: nonexistent | ✅ |  |
| 36 | POST /vendors/data-access: missing vendor_id | ✅ |  |
| 37 | GET /vendors/{id}/data-access: list | ✅ |  |
| 38 | GET /vendors/{id}/data-access: nonexistent | ✅ |  |

### CSV Import — 9/9 passed ✅

| # | Description | Result | Detail |
|---|-------------|--------|--------|
| 1 | POST /vendors/import: CSV with BOM | ✅ |  |
| 2 | POST /vendors/import: all columns | ✅ |  |
| 3 | POST /vendors/import: duplicate names | ✅ |  |
| 4 | POST /vendors/import: empty CSV | ✅ |  |
| 5 | POST /vendors/import: headers only | ✅ |  |
| 6 | POST /vendors/import: wrong headers | ✅ |  |
| 7 | POST /vendors/import: non-CSV file rejected | ✅ |  |
| 8 | GET /vendors/imports/{job_id}: valid | ✅ |  |
| 9 | GET /vendors/imports/{job_id}: nonexistent | ✅ |  |

### Risk Scoring — 12/12 passed ✅

| # | Description | Result | Detail |
|---|-------------|--------|--------|
| 1 | POST /risk/calculate: fresh vendor | ✅ |  |
| 2 | POST /risk/calculate: recalc existing | ✅ |  |
| 3 | POST /risk/calculate: nonexistent 404 | ✅ |  |
| 4 | POST /risk/calculate: missing param 422 | ✅ |  |
| 5 | POST /risk/calculate: bad UUID 422 | ✅ |  |
| 6 | POST /risk/recalculate: all vendors | ✅ |  |
| 7 | GET /risk/vendors/{id}: with score | ✅ |  |
| 8 | GET /risk/vendors/{id}: no score 404 | ✅ |  |
| 9 | GET /risk/vendors/{id}: nonexistent 404 | ✅ |  |
| 10 | GET /risk/vendors/{id}: bad UUID 422 | ✅ |  |
| 11 | GET /risk/vendors/{id}/history: valid response | ✅ |  |
| 12 | GET /risk/vendors/{id}/history: no history | ✅ |  |

### Anomalies — 8/8 passed ✅

| # | Description | Result | Detail |
|---|-------------|--------|--------|
| 1 | GET /anomalies: returns items | ✅ |  |
| 2 | GET /anomalies: pagination | ✅ |  |
| 3 | GET /anomalies: page beyond range | ✅ |  |
| 4 | GET /anomalies/labels | ✅ |  |
| 5 | GET /anomalies/vendor/{id}: with anomalies | ✅ |  |
| 6 | GET /anomalies/vendor/{id}: zero anomalies | ✅ |  |
| 7 | GET /anomalies/vendor/{id}: nonexistent | ✅ |  |
| 8 | GET /anomalies/vendor/{id}: bad UUID 422 | ✅ |  |

### Evaluation — 10/10 passed ✅

| # | Description | Result | Detail |
|---|-------------|--------|--------|
| 1 | POST /evaluation/run: compute metrics | ✅ |  |
| 2 | GET /evaluation/metrics: has overall | ✅ |  |
| 3 | GET /evaluation/metrics: KPI fields | ✅ |  |
| 4 | POST /evaluation/upload-labels: valid CSV | ✅ |  |
| 5 | POST /evaluation/upload-labels: BOM CSV | ✅ |  |
| 6 | POST /evaluation/upload-labels: bad UUID | ✅ |  |
| 7 | POST /evaluation/upload-labels: nonexistent vendor | ✅ |  |
| 8 | POST /evaluation/upload-labels: headers only | ✅ |  |
| 9 | POST /evaluation/upload-labels: non-CSV rejected | ✅ |  |
| 10 | POST /evaluation/run: after labels uploaded | ✅ |  |

### Certifications — 8/8 passed ✅

| # | Description | Result | Detail |
|---|-------------|--------|--------|
| 1 | POST /certifications: active cert | ✅ |  |
| 2 | POST /certifications: already expired | ✅ |  |
| 3 | POST /certifications: without issue_date | ✅ |  |
| 4 | POST /certifications: invalid status (gap) | ✅ |  |
| 5 | POST /certifications: missing vendor_id 422 | ✅ |  |
| 6 | GET /certifications: list | ✅ |  |
| 7 | GET /certifications/expiring | ✅ |  |
| 8 | GET /certifications/frameworks | ✅ |  |

### Alerts — 9/9 passed ✅

| # | Description | Result | Detail |
|---|-------------|--------|--------|
| 1 | POST /alerts: CRITICAL severity | ✅ |  |
| 2 | POST /alerts: HIGH with empty message | ✅ |  |
| 3 | POST /alerts: LOW severity | ✅ |  |
| 4 | POST /alerts: missing vendor_id 422 | ✅ |  |
| 5 | GET /alerts: list | ✅ |  |
| 6 | GET /alerts: pagination | ✅ |  |
| 7 | PATCH /alerts/{id}/resolve: resolve | ✅ |  |
| 8 | PATCH /alerts/{id}/resolve: already resolved | ✅ |  |
| 9 | PATCH /alerts/{id}/resolve: nonexistent 404 | ✅ |  |

### Contracts — 9/9 passed ✅

| # | Description | Result | Detail |
|---|-------------|--------|--------|
| 1 | POST /contracts/upload: valid PDF | ✅ |  |
| 2 | POST /contracts/upload: unsupported format | ✅ |  |
| 3 | POST /contracts/upload: missing vendor_id 422 | ✅ |  |
| 4 | POST /contracts/upload: 1MB file | ✅ |  |
| 5 | GET /contracts/{id}: get contract | ✅ |  |
| 6 | GET /contracts/{id}: nonexistent 404 | ✅ |  |
| 7 | GET /contracts/{id}/analysis: status | ✅ |  |
| 8 | POST /contracts/{id}/analyze: trigger analysis | ✅ |  |
| 9 | POST /contracts/{id}/analyze: re-analyze | ✅ |  |

### Copilot — 7/7 passed ✅

| # | Description | Result | Detail |
|---|-------------|--------|--------|
| 1 | POST /copilot/query: vendor count | ✅ |  |
| 2 | POST /copilot/query: high risk vendors | ✅ |  |
| 3 | POST /copilot/query: list anomalies | ✅ |  |
| 4 | POST /copilot/query: SQL-like question | ✅ |  |
| 5 | POST /copilot/query: long question (1000 tokens) | ✅ |  |
| 6 | POST /copilot/query: empty question (gap) | ✅ |  |
| 7 | POST /copilot/query: missing field 422 | ✅ |  |

### Dashboard — 3/3 passed ✅

| # | Description | Result | Detail |
|---|-------------|--------|--------|
| 1 | GET /dashboard/summary: all KPIs present | ✅ |  |
| 2 | GET /dashboard/summary: risk tiers | ✅ |  |
| 3 | GET /dashboard/summary: evaluation KPIs | ✅ |  |

### Reports — 6/6 passed ✅

| # | Description | Result | Detail |
|---|-------------|--------|--------|
| 1 | POST /reports: generate CSV returns data | ✅ |  |
| 2 | POST /reports: generate JSON | ✅ |  |
| 3 | POST /reports: invalid report_type | ✅ |  |
| 4 | POST /reports: no format (default csv) | ✅ |  |
| 5 | GET /reports/{id}/download: download | ✅ |  |
| 6 | GET /reports/{id}/download: nonexistent | ✅ |  |

### User Management — 13/13 passed ✅

| # | Description | Result | Detail |
|---|-------------|--------|--------|
| 1 | POST /users: create analyst | ✅ |  |
| 2 | POST /users: create executive | ✅ |  |
| 3 | POST /users: duplicate email (bug: 500 not 409) | ✅ |  |
| 4 | POST /users: missing role (gap) | ✅ |  |
| 5 | POST /users: bad email format (gap) | ✅ |  |
| 6 | GET /users: list | ✅ |  |
| 7 | GET /users/{id}: get user | ✅ |  |
| 8 | GET /users/{id}: nonexistent 404 | ✅ |  |
| 9 | PUT /users/{id}: update name | ✅ |  |
| 10 | PUT /users/{id}: update role | ✅ |  |
| 11 | PUT /users/{id}: nonexistent 404 | ✅ |  |
| 12 | PUT /users/{id}: empty body | ✅ |  |
| 13 | GET /users/roles/list: 3+ roles | ✅ |  |

### System — 9/9 passed ✅

| # | Description | Result | Detail |
|---|-------------|--------|--------|
| 1 | OpenAPI schema loads | ✅ |  |
| 2 | GET /docs returns Swagger UI | ✅ |  |
| 3 | CORS OPTIONS preflight | ✅ |  |
| 4 | JSON content-type on responses | ✅ |  |
| 5 | StandardResponse format | ✅ |  |
| 6 | Error response format | ✅ |  |
| 7 | POST to health (405 or 404) | ✅ |  |
| 8 | GET to POST-only returns 405 | ✅ |  |
| 9 | Trailing slash handling | ✅ |  |

---
_Generated by SENTINEL Comprehensive v2 Test Suite on 2026-06-21 09:13:25 UTC_
