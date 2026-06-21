# SENTINEL Validation Suite

Structured validation strategy covering 10 levels of testing.

## Directory Structure

```
tests/
├── api_tests/          # Level 1 — API contract tests
│   └── test_contract.py
├── engine_tests/       # Level 2 — Business logic tests
│   └── test_business_logic.py
├── graph_tests/        # Level 3 — Graph propagation, cycles, scale
│   └── test_graph.py
├── scenario_tests/     # Level 4 — Scenario simulator tests
│   └── test_scenarios.py
├── pdf_tests/          # Level 5 — PDF edge case tests
│   └── test_pdf.py
├── copilot_tests/      # Level 6 — 100-question copilot test
│   └── test_copilot.py
├── ui_tests/           # Level 7 — Puppeteer UI tests
│   └── test_ui_full.mjs
├── load_tests/         # Level 8 — k6 performance tests
│   └── load_test.js
├── chaos_tests/        # Level 9 — Chaos engineering tests
│   └── test_chaos.py
├── postman_collection.json  # Postman collection for manual testing
├── demo_test.py        # Level 10 — 10-run demo verification
└── run_all.py          # Master runner
```

## Quick Start

```bash
# Run all levels (Python API tests + Puppeteer UI tests)
python tests/run_all.py
```

## Per-Level Instructions

### Level 1 — API Contract Tests
```bash
python tests/api_tests/test_contract.py
```
Also import `tests/postman_collection.json` into Postman.

### Level 2 — Business Logic
```bash
python tests/engine_tests/test_business_logic.py
```

### Level 3 — Graph Tests
```bash
python tests/graph_tests/test_graph.py
```

### Level 4 — Scenario Tests
```bash
python tests/scenario_tests/test_scenarios.py
```

### Level 5 — PDF Tests
```bash
python tests/pdf_tests/test_pdf.py
```

### Level 6 — Copilot Tests (100 questions)
```bash
python tests/copilot_tests/test_copilot.py
```

### Level 7 — UI Tests (Puppeteer)
```bash
node tests/ui_tests/test_ui_full.mjs
```
Requires frontend running on :3006.

### Level 8 — Load Tests (k6)
```bash
k6 run tests/load_tests/load_test.js
```
Install k6: https://k6.io/docs/get-started/installation/

### Level 9 — Chaos Tests
```bash
python tests/chaos_tests/test_chaos.py
```
⚠️ Temporarily stops Docker containers.

### Level 10 — Demo Test
```bash
python tests/demo_test.py
```
Runs the full demo flow 10 times.

## Requirements
- Python 3.8+
- Node 18+ (for Puppeteer tests)
- k6 (for load tests)
- Docker services running on :8082
- Frontend running on :3006
