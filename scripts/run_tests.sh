#!/bin/bash
set -e

echo "================================================"
echo "  SENTINEL Test Runner"
echo "================================================"

# 1. Backend unit tests (no DB needed)
echo ""
echo "▸ Backend unit tests..."
cd "$(dirname "$0")/../backend"
python -m pytest tests/test_auth.py tests/test_rules.py tests/test_scoring.py tests/test_evaluation.py -v --tb=short
echo "  ✓ Backend unit tests passed"

# 2. Frontend unit tests
echo ""
echo "▸ Frontend unit tests..."
cd "$(dirname "$0")/../frontend"
npx jest --verbose
echo "  ✓ Frontend unit tests passed"

# 3. Frontend build check
echo ""
echo "▸ Frontend build check..."
npm run build 2>&1 | tail -5
echo "  ✓ Frontend build passed"

# 4. Backend import check
echo ""
echo "▸ Backend import check..."
cd "$(dirname "$0")/../backend"
python -c "
from app.api.router import api_router
routes = [r.path for r in api_router.routes]
print(f'  {len(set(routes))} unique API routes registered')
"
echo "  ✓ Backend imports OK"

echo ""
echo "================================================"
echo "  ✅ ALL TESTS PASSED"
echo "================================================"
