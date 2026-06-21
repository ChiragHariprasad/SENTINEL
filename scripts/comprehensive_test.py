"""
SENTINEL Comprehensive Test Suite
Tests: 15 happy path + 15 edge cases + 15 negative/validation
Output: test_results.md
"""

import argparse
import csv
import io
import json
import os
import sys
import time
import traceback
import uuid as uuid_mod
from datetime import date, datetime, timedelta, timezone

import httpx

# ── configuration ──────────────────────────────────────────────
BASE = "http://localhost:8082"
RESULTS = []

PASS_EMOJI = "✅"
FAIL_EMOJI = "❌"
SKIP_EMOJI = "⏭️"


def assert_eq(a, b, msg=""):
    if a != b:
        raise AssertionError(f"Expected {b!r}, got {a!r}" + (f" — {msg}" if msg else ""))


def assert_in(key, container, msg=""):
    if key not in container:
        raise AssertionError(f"Expected key {key!r} not in response" + (f" — {msg}" if msg else ""))


def assert_true(val, msg=""):
    if not val:
        raise AssertionError(f"Expected truthy value" + (f" — {msg}" if msg else ""))


# ── helpers ────────────────────────────────────────────────────


class TestRun:
    def __init__(self):
        self.token = None
        self.headers = {}
        self.vendor_ids = []
        self.saved = {}

    def login(self):
        r = httpx.post(f"{BASE}/api/v1/auth/login", json={
            "email": "admin@sentinel.ai", "password": "admin123"
        }, timeout=10)
        r.raise_for_status()
        self.token = r.json()["data"]["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def get(self, path, **kw):
        h = kw.pop("headers", {})
        return httpx.get(f"{BASE}{path}", headers={**self.headers, **h}, timeout=10, **kw)

    def post(self, path, **kw):
        h = kw.pop("headers", {})
        return httpx.post(f"{BASE}{path}", headers={**self.headers, **h}, timeout=10, **kw)

    def put(self, path, **kw):
        h = kw.pop("headers", {})
        return httpx.put(f"{BASE}{path}", headers={**self.headers, **h}, timeout=10, **kw)

    def delete(self, path, **kw):
        h = kw.pop("headers", {})
        return httpx.delete(f"{BASE}{path}", headers={**self.headers, **h}, timeout=10, **kw)

    def patch(self, path, **kw):
        h = kw.pop("headers", {})
        return httpx.patch(f"{BASE}{path}", headers={**self.headers, **h}, timeout=10, **kw)

    def upload(self, path, files, **kw):
        return httpx.post(f"{BASE}{path}", files=files, headers=self.headers, timeout=15, **kw)


ctx = TestRun()


def test(category, case, description, fn):
    """Run a single test case and record result."""
    start = time.time()
    try:
        fn()
        dur = time.time() - start
        RESULTS.append({"category": category, "case": case, "description": description,
                         "status": "PASS", "duration": f"{dur:.3f}s", "detail": ""})
        print(f"  {PASS_EMOJI} [{category:>2}] {case:>2}. {description}")
    except Exception as e:
        dur = time.time() - start
        tb = traceback.format_exc()
        detail = str(e).split("\n")[0][:120]
        RESULTS.append({"category": category, "case": case, "description": description,
                         "status": "FAIL", "duration": f"{dur:.3f}s", "detail": detail})
        print(f"  {FAIL_EMOJI} [{category:>2}] {case:>2}. {description} — {detail}")


# ═══════════════════════════════════════════════════════════════════
# SECTION 1 – Happy Path (Functional Tests)
# ═══════════════════════════════════════════════════════════════════

def happy_path():
    print("\n─── Happy Path Tests ──────────────────────────────\n")

    def hp_01():
        r = ctx.post("/api/v1/auth/signup", json={
            "email": f"newuser_{int(time.time())}@test.com",
            "password": "SecurePass123!",
            "first_name": "New",
            "last_name": "User",
        })
        assert_eq(r.status_code, 200)
        assert_in("access_token", r.json()["data"])
    test("HP", 1, "Signup new user with valid credentials", hp_01)

    def hp_02():
        r = ctx.post("/api/v1/auth/login", json={
            "email": "admin@sentinel.ai", "password": "admin123",
        })
        assert_eq(r.status_code, 200)
        assert_in("access_token", r.json()["data"])
        assert_eq(r.json()["data"]["role"], "admin")
    test("HP", 2, "Login with valid admin credentials", hp_02)

    def hp_03():
        r = ctx.post("/api/v1/auth/refresh", json={
            "refresh_token": ctx.token,
        })
        assert_eq(r.status_code, 200)
        assert_in("access_token", r.json()["data"])
    test("HP", 3, "Refresh access token", hp_03)

    def hp_04():
        r = ctx.post("/api/v1/vendors", json={
            "vendor_name": "HappyPathVendor Inc",
            "vendor_type": "SaaS",
            "criticality": "HIGH",
            "contract_status": "active",
            "annual_spend": 1500000,
        })
        assert_eq(r.status_code, 200)
        data = r.json()["data"]
        assert_in("vendor_id", data)
        ctx.saved["hp_vendor_id"] = data["vendor_id"]
        assert_eq(data["vendor_name"], "HappyPathVendor Inc")
    test("HP", 4, "Create vendor with all required fields", hp_04)

    def hp_05():
        r = ctx.get("/api/v1/vendors")
        assert_eq(r.status_code, 200)
        data = r.json()["data"]
        assert_in("items", data)
        assert_in("total", data)
        assert_true(data["total"] > 0)
    test("HP", 5, "List vendors with pagination", hp_05)

    def hp_06():
        vid = ctx.saved.get("hp_vendor_id")
        r = ctx.get(f"/api/v1/vendors/{vid}")
        assert_eq(r.status_code, 200)
        assert_eq(r.json()["data"]["vendor_name"], "HappyPathVendor Inc")
    test("HP", 6, "Get single vendor by ID", hp_06)

    def hp_07():
        vid = ctx.saved.get("hp_vendor_id")
        r = ctx.put(f"/api/v1/vendors/{vid}", json={
            "vendor_name": "HappyPathVendor Updated",
            "annual_spend": 2000000,
        })
        assert_eq(r.status_code, 200)
        assert_eq(r.json()["data"]["vendor_name"], "HappyPathVendor Updated")
    test("HP", 7, "Update vendor name and spend", hp_07)

    def hp_08():
        ts = int(time.time())
        csv_content = "vendor_name,vendor_type,criticality,contract_status,annual_spend\n" \
                      f"CSVImportCorp_{ts},SaaS,HIGH,active,800000\n" \
                      f"CSVImportLLC_{ts},Consulting,MEDIUM,active,300000\n"
        r = ctx.upload("/api/v1/vendors/import",
                       files={"file": ("vendors.csv", csv_content, "text/csv")})
        assert_eq(r.status_code, 200, f"import response: {r.text[:200]}")
        assert_eq(r.json()["data"]["processed"], 2)
        ctx.saved["import_job_id"] = r.json()["data"]["job_id"]
    test("HP", 8, "Import vendors from CSV", hp_08)

    def hp_09():
        vid = ctx.saved.get("hp_vendor_id")
        r = ctx.post(f"/api/v1/risk/calculate?vendor_id={vid}")
        assert_eq(r.status_code, 200)
        data = r.json()["data"]
        assert_in("overall_score", data)
        assert_in("risk_tier", data)
        ctx.saved["risk_score"] = data["overall_score"]
    test("HP", 9, "Calculate risk score for a vendor", hp_09)

    def hp_10():
        r = ctx.post("/api/v1/risk/recalculate")
        assert_eq(r.status_code, 200)
        assert_in("message", r.json())
    test("HP", 10, "Recalculate risk scores for all vendors", hp_10)

    def hp_11():
        r = ctx.get("/api/v1/anomalies")
        assert_eq(r.status_code, 200)
        assert_in("items", r.json()["data"])
        print(f"\n         (anomalies detected: {len(r.json()['data']['items'])})", end="")
    test("HP", 11, "List anomaly detection results", hp_11)

    def hp_12():
        r = ctx.post("/api/v1/evaluation/run")
        assert_eq(r.status_code, 200)
        data = r.json()["data"]
        if data.get("metrics"):
            print(f"\n         (P={data['metrics'].get('precision','?')} "
                  f"R={data['metrics'].get('recall','?')} "
                  f"F1={data['metrics'].get('f1_score','?')})", end="")
    test("HP", 12, "Run evaluation metrics computation", hp_12)

    def hp_13():
        labels_csv = f"vendor_id,anomaly_type,severity\n{ctx.saved.get('hp_vendor_id')},ELEVATED_RISK,HIGH\n"
        r = ctx.upload("/api/v1/evaluation/upload-labels",
                       files={"file": ("labels.csv", labels_csv, "text/csv")})
        assert_eq(r.status_code, 200)
        assert_true(r.json()["data"]["loaded"] >= 1, f"loaded={r.json()['data']['loaded']}")
        ctx.saved["labels_loaded"] = r.json()["data"]["loaded"]
    test("HP", 13, "Upload ground truth labels CSV", hp_13)

    def hp_14():
        r = ctx.get("/api/v1/dashboard/summary")
        assert_eq(r.status_code, 200)
        data = r.json()["data"]
        assert_in("total_vendors", data)
        assert_in("risk_distribution", data)
        assert_true(data["total_vendors"] > 0)
    test("HP", 14, "Get dashboard summary with all KPIs", hp_14)

    def hp_15():
        # Find any active vendor for cert creation
        r = ctx.get("/api/v1/vendors")
        vendors = r.json()["data"]["items"]
        if not vendors:
            raise AssertionError("No vendors available")
        vid = vendors[0]["vendor_id"]
        r = ctx.post("/api/v1/certifications", json={
            "vendor_id": str(vid),
            "certification_type": "SOC 2 Type II",
            "issuer": "AICPA",
            "issue_date": "2025-01-01",
            "expiry_date": (date.today() + timedelta(days=365)).isoformat(),
            "status": "active",
        })
        assert_eq(r.status_code, 200)
        assert_in("certification_id", r.json()["data"])
    test("HP", 15, "Create certification for a vendor", hp_15)


# ═══════════════════════════════════════════════════════════════════
# SECTION 2 – Edge Cases
# ═══════════════════════════════════════════════════════════════════

def edge_cases():
    print("\n\n─── Edge Case Tests ───────────────────────────────\n")

    def ec_01():
        r = ctx.post("/api/v1/auth/login", json={
            "email": "admin@sentinel.ai", "password": "WRONG_PASSWORD_XYZ",
        })
        assert_eq(r.status_code, 401)
    test("EC", 1, "Login with correct email but wrong password", ec_01)

    def ec_02():
        r = ctx.post("/api/v1/auth/signup", json={
            "email": "admin@sentinel.ai", "password": "SomePass123!",
        })
        assert_eq(r.status_code, 409)
    test("EC", 2, "Signup with duplicate email address", ec_02)

    def ec_03():
        r = httpx.get(f"{BASE}/api/v1/vendors", timeout=10)
        assert_eq(r.status_code, 403)
    test("EC", 3, "Access protected route without auth token", ec_03)

    def ec_04():
        r = ctx.get("/api/v1/vendors",
                     headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2MDAwMDAwMDB9.invalid"})
        assert_eq(r.status_code, 401)
    test("EC", 4, "Access protected route with invalid/expired token", ec_04)

    def ec_05():
        fake_uuid = uuid_mod.uuid4()
        r = ctx.get(f"/api/v1/vendors/{fake_uuid}")
        assert_eq(r.status_code, 404)
    test("EC", 5, "Get nonexistent vendor (valid UUID not in DB)", ec_05)

    def ec_06():
        r = ctx.get("/api/v1/vendors?page=9999&size=100")
        assert_eq(r.status_code, 200)
        items = r.json()["data"]["items"]
        assert_eq(len(items), 0)
    test("EC", 6, "List vendors with extreme pagination (page 9999)", ec_06)

    def ec_07():
        long_name = "A" * 255
        r = ctx.post("/api/v1/vendors", json={
            "vendor_name": long_name,
            "vendor_type": "SaaS",
        })
        assert_eq(r.status_code, 200)
        ctx.saved["long_name_vendor_id"] = r.json()["data"]["vendor_id"]
        assert_eq(len(r.json()["data"]["vendor_name"]), 255)
    test("EC", 7, "Create vendor with maximum-length name (255 chars)", ec_07)

    def ec_08():
        r = ctx.post(f"/api/v1/risk/calculate?vendor_id={str(uuid_mod.uuid4())}")
        assert_eq(r.status_code, 404)
    test("EC", 8, "Calculate risk for nonexistent vendor", ec_08)

    def ec_09():
        vid = ctx.saved.get("long_name_vendor_id")
        r = ctx.post(f"/api/v1/risk/calculate?vendor_id={vid}")
        assert_eq(r.status_code, 200)
        r2 = ctx.get(f"/api/v1/risk/vendors/{vid}")
        assert_eq(r2.status_code, 200)
        data = r2.json()["data"]
        assert_true(data.get("overall_score", 0) >= 0)
    test("EC", 9, "Get risk for vendor with minimal data (zero scores)", ec_09)

    def ec_10():
        # This vendor should have zero anomalies
        vid = ctx.saved.get("long_name_vendor_id")
        r = ctx.get(f"/api/v1/anomalies/vendor/{vid}")
        assert_eq(r.status_code, 200)
        items = r.json()["data"].get("items", [])
        assert_eq(len(items), 0)
    test("EC", 10, "List anomalies for vendor with no anomalies", ec_10)

    def ec_11():
        r = ctx.get("/api/v1/evaluation/metrics")
        assert_eq(r.status_code, 200)
        data = r.json()["data"]
        if data.get("metrics"):
            print(f"\n         (P={data['metrics'].get('precision','?')} "
                  f"R={data['metrics'].get('recall','?')})", end="")
    test("EC", 11, "Get evaluation metrics without running evaluation", ec_11)

    def ec_12():
        r = ctx.get("/api/v1/certifications/expiring")
        assert_eq(r.status_code, 200)
        assert_in("items", r.json()["data"])
    test("EC", 12, "List expiring certifications (may be empty)", ec_12)

    def ec_13():
        r = ctx.post("/api/v1/certifications", json={
            "vendor_id": str(ctx.saved.get("hp_vendor_id")),
            "certification_type": "PCI DSS",
            "expiry_date": "2020-01-01",
            "status": "active",
        })
        assert_eq(r.status_code, 200)
        assert_eq(r.json()["data"]["status"], "active")
    test("EC", 13, "Create certification with past expiry date", ec_13)

    def ec_14():
        r = ctx.post("/api/v1/copilot/query", json={"question": ""})
        # Empty question may be accepted or rejected — just document behavior
        assert_true(r.status_code in (200, 422), f"Got {r.status_code}")
        ctx.saved["copilot_empty_response"] = r.status_code
    test("EC", 14, "Copilot query with empty question string", ec_14)

    def ec_15():
        r = ctx.post("/api/v1/alerts", json={
            "vendor_id": str(ctx.saved.get("hp_vendor_id")),
            "alert_type": "SECURITY_BREACH",
            "severity": "CRITICAL",
            "message": "",
        })
        assert_eq(r.status_code, 200, f"create alert: {r.text[:100]}")
        aid = r.json()["data"]["alert_id"]
        r2 = ctx.patch(f"/api/v1/alerts/{aid}/resolve")
        assert_eq(r2.status_code, 200, f"resolve alert: {r2.text[:100]}")
    test("EC", 15, "Create and resolve an alert", ec_15)


# ═══════════════════════════════════════════════════════════════════
# SECTION 3 – Negative / Wrong Input Tests
# ═══════════════════════════════════════════════════════════════════

def negative_tests():
    print("\n\n─── Negative / Wrong Input Tests ──────────────────\n")

    def ng_01():
        r = ctx.post("/api/v1/auth/signup", json={
            "email": f"notanemail_{int(time.time())}", "password": "SecurePass123!",
        })
        assert_eq(r.status_code, 422)
    test("NG", 1, "Signup with invalid email format", ng_01)

    def ng_02():
        r = ctx.post("/api/v1/auth/signup", json={
            "email": f"short_{int(time.time())}@test.com",
            "password": "Ab1!",
        })
        assert_eq(r.status_code, 422)
    test("NG", 2, "Signup with too-short password (< 8 chars)", ng_02)

    def ng_03():
        r = ctx.post("/api/v1/auth/signup", json={"password": "SecurePass123!"})
        assert_eq(r.status_code, 422)
    test("NG", 3, "Signup with missing email field", ng_03)

    def ng_04():
        r = ctx.post("/api/v1/auth/signup", json={"email": f"nopass_{int(time.time())}@test.com"})
        assert_eq(r.status_code, 422)
    test("NG", 4, "Signup with missing password field", ng_04)

    def ng_05():
        r = ctx.post("/api/v1/vendors", json={
            "vendor_name": "",
            "vendor_type": "SaaS",
        })
        assert_eq(r.status_code, 422)
    test("NG", 5, "Create vendor with empty name", ng_05)

    def ng_06():
        r = ctx.post("/api/v1/vendors", json={
            "vendor_name": "BadCriticalityVendor",
            "criticality": "SUPER_DUPER_CRITICAL",
        })
        assert_eq(r.status_code, 422)
    test("NG", 6, "Create vendor with invalid criticality value", ng_06)

    def ng_07():
        r = ctx.post("/api/v1/vendors", json={
            "vendor_name": "NegativeSpendVendor",
            "annual_spend": -50000,
        })
        assert_eq(r.status_code, 422)
    test("NG", 7, "Create vendor with negative annual spend", ng_07)

    def ng_08():
        r = ctx.upload("/api/v1/vendors/import",
                       files={"file": ("bad.csv", "not,valid,csv\nline", "text/csv")})
        assert_eq(r.status_code, 400)
    test("NG", 8, "Import CSV with invalid format/headers", ng_08)

    def ng_09():
        r = ctx.upload("/api/v1/vendors/import",
                       files={"file": ("empty.csv", "", "text/csv")})
        assert_eq(r.status_code, 400)
    test("NG", 9, "Import empty CSV file", ng_09)

    def ng_10():
        r = ctx.post("/api/v1/risk/calculate", json={"vendor_id": "not-a-uuid-at-all"})
        assert_eq(r.status_code, 422)
    test("NG", 10, "Calculate risk with invalid vendor_id format", ng_10)

    def ng_11():
        bad_csv = "vendor_id,anomaly_type\nnot-a-uuid,ELEVATED_RISK\n"
        r = ctx.upload("/api/v1/evaluation/upload-labels",
                       files={"file": ("bad_labels.csv", bad_csv, "text/csv")})
        assert_eq(r.status_code, 400)
    test("NG", 11, "Upload labels CSV with invalid vendor_id format", ng_11)

    def ng_12():
        r = ctx.upload("/api/v1/evaluation/upload-labels",
                       files={"file": ("labels.csv",
                                       f"vendor_id,anomaly_type\n{str(uuid_mod.uuid4())},ELEVATED_RISK\n",
                                       "text/csv")})
        assert_eq(r.status_code, 400)
    test("NG", 12, "Upload labels referencing nonexistent vendor", ng_12)

    def ng_13():
        r = ctx.post("/api/v1/certifications", json={
            "vendor_id": str(ctx.saved.get("hp_vendor_id")),
            "certification_type": "ISO 27001",
            "expiry_date": "2020-01-01",
            "status": "INVALID_STATUS",
        })
        assert_eq(r.status_code, 422)
    test("NG", 13, "Create certification with invalid status value", ng_13)

    def ng_14():
        r = ctx.upload("/api/v1/contracts/upload",
                       files={"file": ("not_a_contract.txt", b"this is text not a pdf", "text/plain"),
                              "vendor_id": (None, str(ctx.saved.get("hp_vendor_id")))})
        assert_eq(r.status_code, 400)
    test("NG", 14, "Upload non-PDF file as contract", ng_14)

    def ng_15():
        r = ctx.post("/api/v1/copilot/query", json={"question": ""})
        assert_eq(r.status_code, 422)
    test("NG", 15, "Copilot query with empty question JSON", ng_15)


# ═══════════════════════════════════════════════════════════════════
# REPORT GENERATION
# ═══════════════════════════════════════════════════════════════════

def generate_report():
    total = len(RESULTS)
    passed = sum(1 for r in RESULTS if r["status"] == "PASS")
    failed = sum(1 for r in RESULTS if r["status"] == "FAIL")

    lines = []
    lines.append("# SENTINEL Comprehensive Test Report")
    lines.append("")
    lines.append(f"- **Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    lines.append(f"- **Target:** `{BASE}`")
    lines.append(f"- **Total Tests:** {total}")
    lines.append(f"- **Passed:** {passed}")
    lines.append(f"- **Failed:** {failed}")
    lines.append(f"- **Pass Rate:** {passed / total * 100:.1f}%" if total else "- **Pass Rate:** N/A")
    lines.append("")

    # Per-category summary
    categories = {}
    for r in RESULTS:
        categories.setdefault(r["category"], {"total": 0, "passed": 0, "failed": 0})
        categories[r["category"]]["total"] += 1
        if r["status"] == "PASS":
            categories[r["category"]]["passed"] += 1
        else:
            categories[r["category"]]["failed"] += 1

    lines.append("## Summary by Category")
    lines.append("")
    lines.append("| Category | Total | Passed | Failed | Rate |")
    lines.append("|----------|-------|--------|--------|------|")
    cat_names = {"HP": "Happy Path", "EC": "Edge Cases", "NG": "Negative Tests"}
    for cat in ["HP", "EC", "NG"]:
        if cat in categories:
            c = categories[cat]
            rate = c["passed"] / c["total"] * 100 if c["total"] else 0
            lines.append(f"| {cat_names.get(cat, cat)} | {c['total']} | {c['passed']} | {c['failed']} | {rate:.1f}% |")
    lines.append("")

    # Detailed results
    lines.append("## Detailed Results")
    lines.append("")
    section_order = [("HP", "Happy Path Tests"), ("EC", "Edge Case Tests"), ("NG", "Negative / Wrong Input Tests")]
    for cat_code, cat_title in section_order:
        items = [r for r in RESULTS if r["category"] == cat_code]
        if not items:
            continue
        lines.append(f"### {cat_title}")
        lines.append("")
        lines.append("| # | Description | Status | Duration | Detail |")
        lines.append("|---|-------------|--------|----------|--------|")
        for r in items:
            status_icon = PASS_EMOJI if r["status"] == "PASS" else FAIL_EMOJI
            detail = r["detail"].replace("|", "/") if r["detail"] else ""
            lines.append(f"| {r['case']} | {r['description']} | {status_icon} {r['status']} | {r['duration']} | {detail} |")
        lines.append("")

    # Failures section
    failed_items = [r for r in RESULTS if r["status"] == "FAIL"]
    if failed_items:
        lines.append("## Failed Tests Details")
        lines.append("")
        for r in failed_items:
            lines.append(f"### [{r['category']}] Case {r['case']}: {r['description']}")
            lines.append("")
            lines.append(f"- **Duration:** {r['duration']}")
            lines.append(f"- **Error:** {r['detail']}")
            lines.append("")

    lines.append("---")
    lines.append(f"_Generated by SENTINEL Comprehensive Test Suite on {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}_")
    lines.append("")

    report = "\n".join(lines)

    # Write to file
    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "test_results.md")
    with open(report_path, "w") as f:
        f.write(report)
    print(f"\n\n📄 Report written to: {report_path}")
    return report


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    global BASE
    parser = argparse.ArgumentParser(description="SENTINEL Comprehensive Test Suite")
    parser.add_argument("--base-url", default=BASE, help=f"API base URL (default: {BASE})")
    args = parser.parse_args()

    BASE = args.base_url.rstrip("/")

    print("═" * 56)
    print("  SENTINEL Comprehensive Test Suite")
    print("═" * 56)
    print(f"\n  Target: {BASE}")
    print(f"  Time:   {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")

    # Authenticate
    print("\n─── Setup: Authenticate ───────────────────────────")
    try:
        ctx.login()
        print(f"  {PASS_EMOJI} Authenticated as admin@sentinel.ai")
    except Exception as e:
        print(f"  {FAIL_EMOJI} Authentication failed: {e}")
        sys.exit(1)

    # Run test sections
    happy_path()
    edge_cases()
    negative_tests()

    # Results
    total = len(RESULTS)
    passed = sum(1 for r in RESULTS if r["status"] == "PASS")
    failed = sum(1 for r in RESULTS if r["status"] == "FAIL")

    print("\n" + "═" * 56)
    print(f"  RESULTS: {total} total | {PASS_EMOJI} {passed} passed | {FAIL_EMOJI} {failed} failed")
    if failed:
        print(f"\n  Failed cases:")
        for r in RESULTS:
            if r["status"] == "FAIL":
                print(f"    {FAIL_EMOJI} [{r['category']}] Case {r['case']}: {r['description']}")
                print(f"       → {r['detail']}")

    # Generate report
    generate_report()

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
