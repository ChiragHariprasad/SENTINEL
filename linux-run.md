# SENTINEL — Linux Run Instructions

Two modes: **Viewer** (just run, uses Docker) and **Editor** (run with hot-reload for development).

---

## Viewer Mode — Quick Start (Docker)

For users who just want to see the app running.

### Prerequisites

- Docker Engine 24+ and Docker Compose plugin
- Git

### Steps

```bash
# 1. Clone the repository
git clone <repo-url> SENTINEL
cd SENTINEL

# 2. Start all services
docker compose -f compose.standalone.yml up -d

# 3. Verify health
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

```bash
docker compose -f compose.standalone.yml down
```

### Seed Demo Data

```bash
docker compose -f compose.standalone.yml exec api python -m scripts.seed_demo_data
docker compose -f compose.standalone.yml exec api python -m scripts.seed_vendors
docker compose -f compose.standalone.yml exec api python -m scripts.seed_labels
```

---

## Editor Mode — Development Setup (Hot Reload)

For developers who want to modify code and see changes instantly.

### Prerequisites

- Git
- Python 3.12+
- Node.js 20+
- npm
- Docker Engine 24+ (for PostgreSQL and Redis only)

### 1. Clone and Prepare

```bash
git clone <repo-url> SENTINEL
cd SENTINEL
```

### 2. Backend Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Install additional test dependencies
pip install pytest pytest-asyncio httpx
```

### 3. Frontend Setup

```bash
cd frontend
npm install
cd ..
```

### 4. Start Database Services (Docker)

```bash
# Start only PostgreSQL and Redis (no API/Frontend containers)
docker compose -f compose.standalone.yml up -d postgres redis

# Wait for healthy
sleep 5
```

### 5. Start Backend (Hot Reload)

```bash
cd backend
export DATABASE_URL="postgresql+asyncpg://sentinel:sentinel@localhost:5433/sentinel"
export REDIS_URL="redis://localhost:6380/0"
export SECRET_KEY="sentinel-dev-key-change-in-production"
export CORS_ORIGINS='["http://localhost:3000","http://localhost:3002"]'

uvicorn app.main:app --host 0.0.0.0 --port 8082 --reload
```

The API starts at `http://localhost:8082` with auto-reload on code changes.

### 6. Start Frontend (Hot Reload)

Open a **new terminal**:

```bash
cd SENTINEL/frontend
export NEXT_PUBLIC_API_URL=http://localhost:8082

# Option A: Dev server with hot reload
npm run dev -- -p 3002

# Option B: Production build
npm run build && npm start -- -p 3002
```

The frontend starts at `http://localhost:3002` with hot reload.

### 7. Verify

```bash
# Health check
curl http://localhost:8082/health

# Login test
curl -X POST http://localhost:8082/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@sentinel.ai","password":"admin123"}'
```

---

## Running Tests

### Backend Integration Tests

```bash
cd backend
source venv/bin/activate
python -m pytest tests/ -v
```

### Frontend Unit Tests

```bash
cd frontend
npm test
```

### Comprehensive API Test Suite

```bash
# Ensure API is running on :8082
python scripts/comprehensive_v2.py

# Run a single suite
python scripts/comprehensive_v2.py --suite vendors

# Smoke test (30-step pipeline)
python scripts/smoke_test.py --base-url http://localhost:8082
```

---

## Resetting Everything

```bash
# Stop Docker services and delete volumes
docker compose -f compose.standalone.yml down -v

# Recreate database from scratch
docker compose -f compose.standalone.yml up -d postgres redis
sleep 5

# Reset database tables (if API is running)
curl -X POST http://localhost:8082/api/v1/vendors  # auto-creates tables via SQLAlchemy
```

### Common Issues

| Issue | Fix |
|-------|-----|
| Port conflict on 5433 | Edit `compose.standalone.yml` to change the mapped port |
| Port conflict on 6380 | Edit `compose.standalone.yml` to change the mapped port |
| `ModuleNotFoundError: No module named 'app'` | Run commands from the `backend/` directory |
| `password authentication failed` | Ensure `DATABASE_URL` env var is set correctly |
| CORS errors in browser | Ensure `CORS_ORIGINS` includes your frontend URL |
