# SENTINEL v2 — Linux / macOS Run Instructions

## Prerequisites

- **Docker 24+** + **Docker Compose v2**
- **Python 3.10+**
- **Node.js 18+** (for Puppeteer UI tests)
- **k6** (for load tests — optional)

```bash
# Debian/Ubuntu
sudo apt install docker.io docker-compose-v2 python3 python3-pip nodejs npm

# macOS
brew install docker python node
```

## Quick Start

```bash
# 1. Clone and enter the project
git clone <repo-url> SENTINEL
cd SENTINEL

# 2. Environment
cp .env.example .env

# 3. Start services
docker compose -f compose.standalone.yml up -d

# 4. Verify
docker compose -f compose.standalone.yml ps

# 5. Test login
curl -s -X POST http://localhost:8082/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@sentinel.ai","password":"admin123"}'

# 6. Open docs
open http://localhost:8082/docs
open http://localhost:3000
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

```bash
# 13-step end-to-end pipeline demo
python3 tests/full_demo.py
```

Creates 11 entities, 10 relationships, runs risk scoring, anomaly detection, correlation, blast radius, SOC2 scenario simulation, intelligence briefs, remediation, timeline, copilot Q&A, and the 6-stage pipeline.

## Run Tests

```bash
# All Python tests
python3 tests/run_all.py

# Individual levels
python3 tests/api_tests/test_contract.py    # Level 1 (127 tests)
python3 tests/engine_tests/test_business_logic.py    # Level 2 (12 tests)
python3 tests/graph_tests/test_graph.py     # Level 3 (15 tests)
python3 tests/demo_test.py                  # Level 10 (110 tests)
```

```bash
# UI tests
node tests/ui_tests/test_ui_full.mjs

# Load tests
k6 run tests/load_tests/load_test.js
```

## Common Commands

```bash
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
| `docker: not found` | https://docs.docker.com/engine/install/ |
| API 404 on v2 routes | `docker compose restart api` |
| DB connection refused | Wait 10s for Postgres health check |
| Port clash | Edit port mappings in `compose.standalone.yml` |

---

[← Back to README](README.md) | [Windows Instructions →](RUN-WINDOWS.md)
