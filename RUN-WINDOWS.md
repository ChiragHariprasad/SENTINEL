# SENTINEL v2 — Windows Run Instructions

## Prerequisites

- **Docker Desktop 4.x+** (WSL2 backend recommended)
- **Python 3.10+** (check "Add to PATH" during install)
- **Node.js 18+**
- **Git**
- **k6** (for load tests — optional)

## Quick Start

```powershell
# 1. Clone and enter the project
git clone <repo-url> SENTINEL
cd SENTINEL

# 2. Environment
copy .env.example .env

# 3. Start services
docker compose -f compose.standalone.yml up -d

# 4. Verify
docker compose -f compose.standalone.yml ps

# 5. Test login
curl.exe -s -X POST http://localhost:8082/api/v1/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"admin@sentinel.ai\",\"password\":\"admin123\"}"

# 6. Open docs
start http://localhost:8082/docs
start http://localhost:3000
```

## Services

| Service | URL | Login |
|---------|-----|-------|
| API | http://localhost:8082 | `admin@sentinel.ai` / `admin123` |
| Frontend | http://localhost:3000 | same |
| Swagger | http://localhost:8082/docs | — |
| PostgreSQL | localhost:5433 | `sentinel` / `sentinel` |
| Redis | localhost:6380 | — |

## Run the Demo

```powershell
# 13-step end-to-end pipeline demo
python tests\full_demo.py
```

Creates 11 entities, 10 relationships, runs risk scoring, anomaly detection, correlation, blast radius, SOC2 scenario simulation, intelligence briefs, remediation, timeline, copilot Q&A, and the 6-stage pipeline.

## Run Tests

```powershell
# All Python tests
python tests\run_all.py

# Individual levels
python tests\api_tests\test_contract.py    # Level 1 (127 tests)
python tests\engine_tests\test_business_logic.py    # Level 2 (12 tests)
python tests\graph_tests\test_graph.py     # Level 3 (15 tests)
python tests\demo_test.py                  # Level 10 (110 tests)
```

```powershell
# UI tests
node tests\ui_tests\test_ui_full.mjs

# Load tests
k6 run tests\load_tests\load_test.js
```

## Common Commands

```powershell
# Logs
docker compose -f compose.standalone.yml logs -f api

# Restart
docker compose -f compose.standalone.yml restart api

# Stop
docker compose -f compose.standalone.yml down

# Full reset
docker compose -f compose.standalone.yml down -v
docker compose -f compose.standalone.yml up -d
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `docker` not recognized | Start Docker Desktop from Start Menu |
| `docker compose` fails | Use `docker-compose` (older Desktop) or update |
| API 404 on v2 routes | `docker compose restart api` |
| `python` not found | Use `py` or reinstall with "Add to PATH" |
| DB connection refused | Wait 15s for Postgres health check |
| Port clash | Edit port mappings in `compose.standalone.yml` |
| Paths with spaces | Quote them: `"Test Files\doc.pdf"` |

---

[← Back to README](README.md) | [Linux Instructions →](RUN-LINUX.md)
