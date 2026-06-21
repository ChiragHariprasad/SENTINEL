# SENTINEL — Windows Run Instructions

Two modes: **Viewer** (just run, uses Docker) and **Editor** (run with hot-reload for development).

---

## Viewer Mode — Quick Start (Docker)

For users who just want to see the app running.

### Prerequisites

- Docker Desktop for Windows (WSL2 backend recommended)
- Git for Windows

### Steps

Open **PowerShell** or **Command Prompt**:

```powershell
:: 1. Clone the repository
git clone <repo-url> SENTINEL
cd SENTINEL

:: 2. Start all services
docker compose -f compose.standalone.yml up -d

:: 3. Verify health
curl http://localhost:8082/health
```

### Access

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| API Docs | http://localhost:8082/docs |
| Health | http://localhost:8082/health |

**Login:** `admin@sentinel.ai` / `admin123`

### Stop

```powershell
docker compose -f compose.standalone.yml down
```

### Seed Demo Data

```powershell
docker compose -f compose.standalone.yml exec api python -m scripts.seed_demo_data
docker compose -f compose.standalone.yml exec api python -m scripts.seed_vendors
docker compose -f compose.standalone.yml exec api python -m scripts.seed_labels
```

---

## Editor Mode — Development Setup (Hot Reload)

For developers who want to modify code and see changes instantly.

### Prerequisites

- Git for Windows
- Python 3.12+ (install from python.org — check "Add to PATH")
- Node.js 20+ (install from nodejs.org)
- Docker Desktop for Windows (for PostgreSQL and Redis only)
- **PowerShell** (run as administrator for port forwarding)

### 1. Clone and Prepare

Open **PowerShell**:

```powershell
git clone <repo-url> SENTINEL
cd SENTINEL
```

### 2. Backend Setup

```powershell
:: Create virtual environment
python -m venv venv

:: Activate it
.\venv\Scripts\Activate.ps1

:: If you get a execution policy error, run:
:: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

:: Install dependencies
pip install -r backend\requirements.txt

:: Install additional test dependencies
pip install pytest pytest-asyncio httpx
```

### 3. Frontend Setup

```powershell
cd frontend
npm install
cd ..
```

### 4. Start Database Services (Docker)

```powershell
:: Start only PostgreSQL and Redis (no API/Frontend containers)
docker compose -f compose.standalone.yml up -d postgres redis

:: Wait for containers to become healthy
Start-Sleep -Seconds 5
```

### 5. Start Backend (Hot Reload)

Open a **new PowerShell window** (keep the venv activated):

```powershell
cd SENTINEL\backend
.\venv\Scripts\Activate.ps1

$env:DATABASE_URL = "postgresql+asyncpg://sentinel:sentinel@localhost:5433/sentinel"
$env:REDIS_URL = "redis://localhost:6380/0"
$env:SECRET_KEY = "sentinel-dev-key-change-in-production"
$env:CORS_ORIGINS = '["http://localhost:3000","http://localhost:3002"]'

uvicorn app.main:app --host 0.0.0.0 --port 8082 --reload
```

The API starts at `http://localhost:8082` with auto-reload on code changes.

> **Note:** If using **Command Prompt** instead of PowerShell, use `set DATABASE_URL=...` instead of `$env:DATABASE_URL = "..."`.

### 6. Start Frontend (Hot Reload)

Open a **third terminal** (PowerShell):

```powershell
cd SENTINEL\frontend
$env:NEXT_PUBLIC_API_URL = "http://localhost:8082"

:: Option A: Dev server with hot reload
npm run dev -- -p 3002

:: Option B: Production build
npm run build
npm start -- -p 3002
```

The frontend starts at `http://localhost:3002` with hot reload.

### 7. Verify

```powershell
:: Health check
curl http://localhost:8082/health

:: Login test
curl -X POST http://localhost:8082/api/v1/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"admin@sentinel.ai\",\"password\":\"admin123\"}"
```

---

## Running Tests

### Backend Integration Tests

```powershell
cd SENTINEL\backend
.\venv\Scripts\Activate.ps1
python -m pytest tests/ -v
```

### Frontend Unit Tests

```powershell
cd SENTINEL\frontend
npm test
```

### Comprehensive API Test Suite

```powershell
:: Ensure API is running on :8082
python scripts\comprehensive_v2.py

:: Run a single suite
python scripts\comprehensive_v2.py --suite vendors

:: Smoke test (30-step pipeline)
python scripts\smoke_test.py --base-url http://localhost:8082
```

---

## Resetting Everything

```powershell
:: Stop Docker services and delete volumes
docker compose -f compose.standalone.yml down -v

:: Recreate database from scratch
docker compose -f compose.standalone.yml up -d postgres redis
Start-Sleep -Seconds 5
```

### Common Issues

| Issue | Fix |
|-------|-----|
| `venv\Scripts\Activate.ps1` cannot be loaded | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first |
| Port conflict on 5433 | Edit `compose.standalone.yml` to change the mapped port |
| Port conflict on 6380 | Edit `compose.standalone.yml` to change the mapped port |
| `'uvicorn' is not recognized` | Ensure venv is activated and `pip install` completed |
| `password authentication failed` | Ensure `DATABASE_URL` env var is set correctly (use port 5433) |
| CORS errors in browser | Ensure `CORS_ORIGINS` includes your frontend URL (`http://localhost:3002`) |
| Docker Desktop not starting | Enable WSL2 backend in Docker Desktop Settings > Resources > WSL Integration |
| `NEXT_PUBLIC_API_URL` not working | Restart the dev server after setting the env var (Next.js reads it at startup) |
