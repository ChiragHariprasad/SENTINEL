#!/usr/bin/env python3
"""Master test runner — runs all validation levels"""

import subprocess
import sys
import time

LEVELS = [
    ("Level 1 — API Contract Tests", "tests/api_tests/test_contract.py"),
    ("Level 2 — Business Logic Tests", "tests/engine_tests/test_business_logic.py"),
    ("Level 3 — Graph Tests", "tests/graph_tests/test_graph.py"),
    ("Level 4 — Scenario Tests", "tests/scenario_tests/test_scenarios.py"),
    ("Level 5 — PDF Tests", "tests/pdf_tests/test_pdf.py"),
    ("Level 6 — Copilot Tests (100 questions)", "tests/copilot_tests/test_copilot.py"),
]

UI_TEST = ("Level 7 — UI Tests", "tests/ui_tests/test_ui_full.mjs")
CHAOS_TEST = ("Level 9 — Chaos Tests", "tests/chaos_tests/test_chaos.py")
DEMO_TEST = ("Level 10 — Demo Test", "tests/demo_test.py")

passed = 0
failed = 0

def run_test(name, cmd):
    global passed, failed
    print(f"\n{'='*70}")
    print(f"  {name}")
    print(f"{'='*70}\n")
    start = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    elapsed = time.time() - start
    print(result.stdout)
    if result.stderr:
        print(result.stderr[:500])
    if result.returncode == 0:
        passed += 1
        print(f"  ✅ {name} — PASSED ({elapsed:.1f}s)\n")
    else:
        failed += 1
        print(f"  ❌ {name} — FAILED ({result.returncode}) ({elapsed:.1f}s)\n")

print("=" * 70)
print("  SENTINEL VALIDATION SUITE")
print("=" * 70)

# Quick healthcheck
import requests
try:
    r = requests.get("http://localhost:8082/health", timeout=5)
    print(f"\n✅ API health: {r.status_code}\n")
except:
    print("\n❌ API not available on :8082 — start services first!\n")
    sys.exit(1)

# Levels 1-6 (Python API tests)
for name, path in LEVELS:
    run_test(name, [sys.executable, path])

# Level 7 (UI — Puppeteer)
print(f"\n{'='*70}")
print(f"  {UI_TEST[0]}")
print(f"{'='*70}\n")
result = subprocess.run(["node", UI_TEST[1]], capture_output=True, text=True, timeout=120)
print(result.stdout)
if result.stderr:
    print(result.stderr[:500])
if result.returncode == 0:
    passed += 1
    print(f"  ✅ {UI_TEST[0]} — PASSED\n")
else:
    failed += 1
    print(f"  ❌ {UI_TEST[0]} — FAILED ({result.returncode})\n")

# Level 9 (Chaos — requires docker)
run_test(CHAOS_TEST[0], [sys.executable, CHAOS_TEST[1]])

# Level 10 Demo (10 runs)
run_test(DEMO_TEST[0], [sys.executable, DEMO_TEST[1]])

# Results
print(f"\n{'='*70}")
print(f"  FINAL RESULTS")
print(f"{'='*70}")
print(f"  Levels passed: {passed}/{passed + failed}")
if failed == 0:
    print(f"\n  ✅ ALL LEVELS PASSED — READY FOR JUDGING\n")
else:
    print(f"\n  ❌ {failed} level(s) have failures — investigate before demo\n")

print("Checklist:")
for name, _ in LEVELS + [UI_TEST, ("Level 8 — Load Tests", ""), CHAOS_TEST, DEMO_TEST]:
    status = "✅" if passed > len([n for n, _ in LEVELS]) else "❌"
    print(f"  {status} {name}")
sys.exit(1 if failed > 0 else 0)
