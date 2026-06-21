# SENTINEL — Third-Party Risk Intelligence Platform

AI-powered vendor risk assessment, monitoring, and compliance tracking platform.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Browser (:3000/:3002)                 │
├─────────────────────────────────────────────────────────────┤
│                    Next.js Frontend                          │
│  Dashboard │ Vendors │ Risk │ Anomalies │ Evaluation │ ...  │
├─────────────────────────────────────────────────────────────┤
│                       API Gateway                            │
│                     FastAPI (:8082)                           │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────┐ ┌──────────┐ ┌─────────┐ ┌───────────────┐    │
│  │ Vendors │ │  Risk    │ │Anomalies│ │  Evaluation   │    │
│  │  CRUD   │ │ Scoring  │ │Detection│ │ & GroundTruth │    │
│  └─────────┘ └──────────┘ └─────────┘ └───────────────┘    │
│  ┌─────────┐ ┌──────────┐ ┌─────────┐ ┌───────────────┐    │
│  │ Contracts│ │  Copilot │ │  Users  │ │   Reports     │    │
│  │  + AI   │ │  (LLM)   │ │  Auth   │ │  Generation   │    │
│  └─────────┘ └──────────┘ └─────────┘ └───────────────┘    │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────┐  ┌────────────────────────┐    │
│  │     PostgreSQL 16        │  │       Redis 7          │    │
│  │    (Vendors, Risk,       │  │    (Sessions, Cache)   │    │
│  │   Anomalies, Users...)   │  │                        │    │
│  └──────────────────────────┘  └────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.13, FastAPI, SQLAlchemy (async), Pydantic v2 |
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS 3 |
| Database | PostgreSQL 16, Redis 7 |
| AI/ML | Mistral AI (LLM), PyMuPDF, Custom scoring engine |
| Auth | JWT (python-jose), bcrypt |
| Testing | Pytest, Jest, comprehensive 164-suite integration tests |
| Deployment | Docker Compose, systemd |

## Features

- **Vendor Management** — Full CRUD with CSV import, data access tracking, archiving
- **Risk Scoring** — Multi-dimensional scoring (financial, security, operational, compliance)
- **Anomaly Detection** — Automated detection rules with configurable thresholds
- **Evaluation Engine** — Ground truth comparison, precision/recall/F1 metrics
- **Contract Analysis** — PDF/TXT upload with AI-powered clause extraction
- **AI Copilot** — Natural language query interface (powered by Mistral AI)
- **Certification Tracking** — Compliance certifications with expiry management
- **Alerts & Notifications** — Configurable alert rules with severity levels
- **Reports** — CSV report generation (vendor risk register)
- **Dashboard** — Aggregated KPIs, risk tier distribution, evaluation metrics
- **User Management** — Role-based access (admin, analyst, executive)

## Quick Start

See platform-specific run instructions:

- **[Linux Run Instructions](linux-run.md)** — Ubuntu/Fedora/Arch setup
- **[Windows Run Instructions](windows-run.md)** — PowerShell/WSL setup

### Quick Viewer Mode (Docker — all platforms)

```bash
docker compose -f compose.standalone.yml up -d
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| API | http://localhost:8082 |
| PostgreSQL | localhost:5433 (sentinel/sentinel) |
| Redis | localhost:6380 |

**Login:** `admin@sentinel.ai` / `admin123`

## Test Results

**164/164 comprehensive integration tests pass (100%).**

| Suite | Tests | Status |
|-------|-------|--------|
| Health | 2 | ✅ 100% |
| Authentication | 17 | ✅ 100% |
| Vendors CRUD | 42 | ✅ 100% |
| CSV Import | 9 | ✅ 100% |
| Risk Scoring | 12 | ✅ 100% |
| Anomalies | 8 | ✅ 100% |
| Evaluation | 10 | ✅ 100% |
| Certifications | 8 | ✅ 100% |
| Alerts | 9 | ✅ 100% |
| Contracts | 9 | ✅ 100% |
| Copilot | 7 | ✅ 100% |
| Dashboard | 3 | ✅ 100% |
| Reports | 6 | ✅ 100% |
| User Management | 13 | ✅ 100% |
| System | 9 | ✅ 100% |
| **Total** | **164** | **✅ 100%** |

Also: **107/107 backend integration tests** and **19/19 frontend unit tests** all pass.

## Project Structure

```
SENTINEL/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI route handlers (15 modules)
│   │   ├── core/         # Config, auth, DB, exceptions
│   │   ├── models/        # SQLAlchemy ORM models
│   │   ├── schemas/       # Pydantic request/response schemas
│   │   ├── services/      # Business logic (scoring, AI, etc.)
│   │   └── ai/            # AI integration (copilot, analysis)
│   ├── tests/             # Integration & unit tests
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/           # Next.js App Router pages (15 routes)
│   │   ├── components/    # React components
│   │   └── lib/           # API client, auth context, utils
│   └── package.json
├── scripts/               # Test suites, seed data, smoke tests
├── compose.standalone.yml # Single-file Docker deployment
├── docs/                  # Design documents, specs
├── linux-run.md           # Linux setup guide
├── windows-run.md         # Windows setup guide
└── README.md
```

## API Endpoints

| Prefix | Description |
|--------|-------------|
| `/health` | Health check |
| `/api/v1/auth/*` | Authentication (login, signup, refresh) |
| `/api/v1/vendors/*` | Vendor CRUD, import, data access |
| `/api/v1/risk/*` | Risk scoring, history, recalculate |
| `/api/v1/anomalies` | Anomaly detection results |
| `/api/v1/evaluation/*` | Evaluation engine, ground truth labels |
| `/api/v1/certifications` | Compliance certifications |
| `/api/v1/alerts` | Alert rules and notifications |
| `/api/v1/contracts/*` | Contract upload, analysis |
| `/api/v1/copilot/*` | AI copilot query |
| `/api/v1/dashboard/*` | Dashboard KPIs and summaries |
| `/api/v1/reports` | Report generation |
| `/api/v1/users/*` | User management, roles |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://sentinel:sentinel@localhost:5432/sentinel` | PostgreSQL connection |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection |
| `SECRET_KEY` | `change-me-in-production` | JWT signing key |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed origins |
| `LLM_API_KEY` | `""` | Mistral AI API key |
| `LLM_MODEL` | `mistral-small-latest` | AI model name |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Frontend API target |
