# AI/ML Design Document

# SENTINEL

### Security Evaluation & Networked Third-Party Intelligence Engine for Lifecycle Governance

**Version:** 1.0
**Document Type:** AI/ML System Design Document
**Architecture Type:** Hybrid AI + Rules + Knowledge Graph Intelligence Platform

---

# 1. AI Vision

## Objective

SENTINEL uses Artificial Intelligence to transform vendor risk management from a static compliance process into a continuously learning risk intelligence system.

The AI layer performs:

* Contract Understanding
* Risk Prediction
* Anomaly Detection
* Vendor Intelligence Generation
* Knowledge Graph Reasoning
* Executive Risk Summarization
* Remediation Recommendations

---

# 2. AI Architecture Overview

```text
                           Vendor Data
                                │
                                ▼

      ┌──────────────────────────────────────────┐
      │           Feature Engineering            │
      └──────────────────────────────────────────┘
                                │

      ┌───────────────┬──────────────┬──────────────┐
      ▼               ▼              ▼

 Risk Engine    Anomaly Engine   Contract AI

      ▼               ▼              ▼

      └───────────────┬──────────────┘
                      ▼

              Knowledge Graph

                      ▼

                AI Copilot

                      ▼

           Recommendations
```

---

# 3. AI Module Inventory

| Module | Purpose                   |
| ------ | ------------------------- |
| AIM-01 | Risk Scoring              |
| AIM-02 | Anomaly Detection         |
| AIM-03 | Contract Intelligence     |
| AIM-04 | Vendor Intelligence       |
| AIM-05 | Knowledge Graph Reasoning |
| AIM-06 | AI Copilot                |
| AIM-07 | Risk Forecasting          |
| AIM-08 | Recommendation Engine     |

---

# 4. AIM-01 Risk Scoring Engine

## Objective

Generate a continuous vendor risk score.

---

## Inputs

```text
Vendor Type

Annual Spend

Data Access Level

Certification Status

Contract Risk

Breach History

Assessment Results

Compliance Status
```

---

## Feature Vector

```text
Security Score

Compliance Score

Data Access Score

Financial Score

Contract Score

Breach Count

Expired Certifications

Critical System Access
```

---

## Initial MVP Model

### Hybrid Weighted Model

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

## Phase 2 Model

### XGBoost Regressor

Purpose:

Predict future vendor risk.

---

## Outputs

```text
Risk Score

Risk Tier

Confidence Score

Risk Trend
```

---

# 5. AIM-02 Anomaly Detection Engine

## Objective

Identify abnormal or high-risk vendor conditions.

---

## Challenge Labels

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

## Architecture

```text
Vendor Features

↓

Rule Engine

↓

Isolation Forest

↓

Severity Engine

↓

Explanation Engine
```

---

## Stage 1

### Rule-Based Detection

Examples:

```python
if breach_recent and pii_access:
    label = "BREACHED_VENDOR_HIGH_ACCESS"

if contract_expired and access_active:
    label = "CONTRACT_EXPIRED_ACTIVE_ACCESS"
```

---

## Stage 2

### ML-Based Outlier Detection

Model:

```text
Isolation Forest
```

Purpose:

Detect unknown vendor risk patterns.

---

## Features

```text
Risk Score

Spend

Access Scope

Incident Count

Certifications

Compliance Score
```

---

## Outputs

```text
Anomaly Type

Severity

Confidence

Recommended Action
```

---

# 6. AIM-03 Contract Intelligence Engine

## Objective

Transform unstructured contracts into structured risk intelligence.

---

# Pipeline

```text
PDF

↓

OCR

↓

Text Extraction

↓

Clause Detection

↓

LLM Analysis

↓

Structured Metadata
```

---

## OCR Layer

### Preferred

```text
PyMuPDF
```

---

### Fallback

```text
Tesseract OCR
```

---

# Clause Extraction

## Categories

```text
SLA

Data Ownership

Breach Notification

Liability

Termination

Retention

Compliance Requirements
```

---

# NLP Model

### MVP

```text
Llama 3 8B

or

Mistral 7B
```

---

# Prompt Output

```json
{
  "breach_notification_days": 30,
  "data_owner": "vendor",
  "risk_level": "high"
}
```

---

# Contract Risk Generation

Each extracted clause contributes to:

```text
Contract Risk Score
```

---

# 7. AIM-04 Vendor Intelligence Engine

## Objective

Generate enriched vendor profiles.

---

## Sources

```text
Vendor Registry

Contracts

Compliance Data

Incidents

Assessments

Monitoring Events
```

---

## Output

```text
Vendor Summary

Risk Narrative

Risk Drivers

Trend Analysis
```

---

## Example

```text
Vendor risk increased 12%
due to expired ISO27001 certification
and newly detected breach event.
```

---

# 8. AIM-05 Knowledge Graph Intelligence

## Objective

Enable relationship-based risk reasoning.

---

# Graph Structure

```text
Vendor

↓

System

↓

Data Asset

↓

Incident

↓

Compliance Impact
```

---

## Node Types

```text
Vendor

Contract

System

Incident

Certification

Data Asset
```

---

## Relationship Types

```text
ACCESSES

USES

CONTAINS

OWNS

BREACHED

CERTIFIED_BY
```

---

## AI Reasoning Queries

Examples:

```text
Which vendors access PII?

Which breached vendors
access critical systems?

Which expired certifications
affect GDPR compliance?
```

---

# 9. AIM-06 AI Copilot

## Objective

Provide conversational access to vendor intelligence.

---

# Architecture

```text
User Question

↓

Embedding Generation

↓

Vector Search

↓

Knowledge Graph Retrieval

↓

LLM

↓

Response
```

---

## RAG Pipeline

### Embeddings

```text
BGE Large

or

Sentence Transformers
```

---

### Vector Store

```text
pgvector
```

---

### Retriever

```text
Hybrid Search

Semantic + Metadata
```

---

## Supported Queries

```text
Show critical vendors.

Which vendors have expired certifications?

Generate audit report.

Who accesses customer PII?
```

---

# 10. AIM-07 Risk Forecasting Engine

## Objective

Predict future vendor risk escalation.

---

## Inputs

```text
Historical Risk Scores

Certification History

Incidents

Contract Events

Compliance Changes
```

---

## Model

### MVP

```text
Gradient Boosting
```

---

### Advanced

```text
XGBoost

LightGBM
```

---

## Outputs

```text
Predicted Risk Score

Probability of Escalation

Predicted Tier
```

---

# 11. AIM-08 Recommendation Engine

## Objective

Provide actionable recommendations.

---

## Inputs

```text
Risk Score

Anomalies

Contract Analysis

Compliance Status
```

---

## Outputs

### Security

```text
Require SOC2 Type II
```

---

### Compliance

```text
Renew ISO27001
```

---

### Contract

```text
Add 72-hour breach clause
```

---

### Monitoring

```text
Increase review frequency
```

---

# 12. Training Strategy

## Available Challenge Data

### vendor_registry.csv

```text
400 Vendors
```

---

### vendor_labels.csv

```text
Ground Truth Labels
```

---

## Dataset Usage

### Supervised Learning

Used For:

```text
Risk Classification

Severity Prediction
```

---

### Evaluation

Used For:

```text
Precision

Recall

F1 Score
```

---

# 13. Feature Engineering

## Security Features

```text
Breach Count

Recent Breach

Incident Severity
```

---

## Compliance Features

```text
Expired Certifications

Certification Count

Framework Coverage
```

---

## Access Features

```text
PII Access

PCI Access

Critical System Access
```

---

## Business Features

```text
Annual Spend

Vendor Criticality

Contract Value
```

---

# 14. Explainable AI (XAI)

## Requirement

All AI outputs must be explainable.

---

## Risk Explanation Example

```text
Risk Score = 89

Contributors:

Security Risk: 42%

PII Access: 24%

Expired SOC2: 18%

Recent Breach: 16%
```

---

## SHAP Integration

Phase 2:

```text
SHAP Values
```

Used for:

* Risk prediction explainability
* Executive reporting

---

# 15. Model Evaluation

## Contract Intelligence

| Metric                     | Target |
| -------------------------- | ------ |
| Clause Extraction Accuracy | >90%   |
| Obligation Detection       | >85%   |
| Summary Accuracy           | >85%   |

---

## Risk Engine

| Metric         | Target |
| -------------- | ------ |
| Score Accuracy | >80%   |
| Tier Accuracy  | >85%   |

---

## Anomaly Detection

| Metric    | Target |
| --------- | ------ |
| Precision | >80%   |
| Recall    | >90%   |
| F1        | >85%   |

---

## Challenge-Specific Targets

| Metric                    | Target |
| ------------------------- | ------ |
| Critical Vendor Recall    | >90%   |
| High Risk Recall          | >85%   |
| Breached Vendor Detection | >95%   |

---

# 16. MLOps Architecture

## Experiment Tracking

```text
MLflow
```

---

## Model Registry

```text
MLflow Registry
```

---

## Monitoring

```text
Prometheus

Grafana
```

---

## Drift Detection

Monitor:

```text
Feature Drift

Label Drift

Prediction Drift
```

---

# 17. AI Governance

## Human-in-the-Loop

Required For:

```text
Risk Overrides

Contract Approval

Critical Vendor Classification
```

---

## Auditability

Store:

```text
Model Version

Input Features

Predictions

Prompts

Outputs
```

---

## Compliance

Support:

```text
GDPR

SOC2

ISO27001

NIST
```

---

# 18. Future AI Roadmap

## Phase 2

```text
Risk Forecasting

SHAP Explainability

Financial Risk Prediction
```

---

## Phase 3

```text
Vendor Digital Twin

Autonomous Risk Reviews

Supply Chain Intelligence

Fourth-Party Risk Prediction
```

---

# 19. AI/ML Architecture Summary

SENTINEL employs a hybrid intelligence architecture combining deterministic rules, machine learning models, large language models, retrieval-augmented generation, and graph-based reasoning. The platform is designed to maximize recall for critical vendor risks while maintaining explainability, auditability, and compliance, enabling organizations to proactively manage third-party risk at enterprise scale.
