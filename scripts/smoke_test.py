"""
End-to-end smoke test for SENTINEL API.

Tests the full pipeline:
  1. Health check
  2. Signup / Login
  3. CSV import
  4. Risk calculation
  5. Anomaly detection
  6. Evaluation metrics
  7. Ground truth label upload
  8. Dashboard summary

Usage:
    python scripts/smoke_test.py [--base-url http://localhost:8000]
"""

import argparse
import csv
import io
import sys
import time
import httpx

BASE = "http://localhost:8000"
PASS = 0
FAIL = 0


def ok(msg: str):
    global PASS
    PASS += 1
    print(f"  ✓ {msg}")


def fail(msg: str, detail: str = ""):
    global FAIL
    FAIL += 1
    print(f"  ✗ {msg}" + (f" — {detail}" if detail else ""))


def check(label: str, condition: bool, detail: str = ""):
    if condition:
        ok(label)
    else:
        fail(label, detail)


def main(base_url: str):
    global PASS, FAIL
    PASS = 0
    FAIL = 0
    client = httpx.Client(base_url=base_url, timeout=30)

    print("\n🔍 SENTINEL Smoke Test\n")
    print(f"Target: {base_url}\n")

    # 1. Health check
    print("1. Health Check")
    r = client.get("/health")
    check("GET /health returns 200", r.status_code == 200)
    check("  body has status=healthy", r.json().get("data", {}).get("status") == "healthy")

    # 2. Signup
    print("\n2. Authentication")
    import uuid
    test_email = f"smoke-{uuid.uuid4().hex[:8]}@test.com"
    r = client.post("/api/v1/auth/signup", json={
        "email": test_email,
        "password": "SmokeTest123!",
    })
    check("POST /auth/signup returns 200", r.status_code == 200)
    auth_data = r.json().get("data", {})
    token = auth_data.get("access_token", "")
    check("  access_token received", bool(token))
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Login
    r = client.post("/api/v1/auth/login", json={
        "email": test_email,
        "password": "SmokeTest123!",
    })
    check("POST /auth/login returns 200", r.status_code == 200)

    # 4. CSV Import
    print("\n3. CSV Import")
    vendor_count = 5
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["vendor_name", "vendor_type", "criticality", "contract_status", "annual_spend"])
    for i in range(vendor_count):
        writer.writerow([f"SmokeVendor-{i}", "SaaS", "HIGH" if i < 2 else "MEDIUM", "active", 500000])
    output.seek(0)

    r = client.post(
        "/api/v1/vendors/import",
        files={"file": ("vendors.csv", output.getvalue().encode("utf-8"), "text/csv")},
        headers=headers,
    )
    check("POST /vendors/import returns 200", r.status_code == 200)
    import_data = r.json().get("data", {})
    check(f"  processed {vendor_count} vendors", import_data.get("processed") == vendor_count)

    # 5. List vendors
    print("\n4. Vendor Registry")
    r = client.get("/api/v1/vendors", headers=headers)
    check("GET /vendors returns 200", r.status_code == 200)
    total = r.json().get("data", {}).get("total", 0)
    check(f"  total vendors = {total}", total >= vendor_count)

    first_vendor_id = r.json()["data"]["items"][0]["vendor_id"]

    # 6. Risk calculation
    print("\n5. Risk Scoring")
    r = client.post(f"/api/v1/risk/calculate?vendor_id={first_vendor_id}", headers=headers)
    check("POST /risk/calculate returns 200", r.status_code == 200)
    risk_data = r.json().get("data", {})
    check("  overall_score present", "overall_score" in risk_data)
    check("  risk_tier present", "risk_tier" in risk_data)

    # 7. Recalculate all
    r = client.post("/api/v1/risk/recalculate", headers=headers)
    check("POST /risk/recalculate returns 200", r.status_code == 200)

    # 8. Anomalies
    print("\n6. Anomaly Detection")
    r = client.get("/api/v1/anomalies", headers=headers)
    check("GET /anomalies returns 200", r.status_code == 200)
    anomaly_count = r.json().get("data", {}).get("count", 0)
    print(f"  anomalies detected: {anomaly_count}")

    # 9. Evaluation
    print("\n7. Evaluation Metrics")
    r = client.post("/api/v1/evaluation/run", headers=headers)
    check("POST /evaluation/run returns 200", r.status_code == 200)
    eval_data = r.json().get("data", {})
    check("  evaluation metrics computed", eval_data.get("overall", {}).get("f1_score", -1) >= 0)
    check(f"  ground_truth_source = {eval_data.get('ground_truth_source', 'N/A')}", True)

    r = client.get("/api/v1/evaluation/metrics", headers=headers)
    check("GET /evaluation/metrics returns 200", r.status_code == 200)

    # 10. Upload ground truth labels
    print("\n8. Ground Truth Labels")
    gt_csv = io.StringIO()
    gt_writer = csv.writer(gt_csv)
    gt_writer.writerow(["vendor_id", "anomaly_type", "severity"])
    gt_writer.writerow([first_vendor_id, "HIGH_RISK_SCORE", "HIGH"])
    gt_csv.seek(0)

    r = client.post(
        "/api/v1/evaluation/upload-labels",
        files={"file": ("vendor_labels.csv", gt_csv.getvalue().encode("utf-8"), "text/csv")},
        headers=headers,
    )
    check("POST /evaluation/upload-labels returns 200", r.status_code == 200)
    label_data = r.json().get("data", {})
    check(f"  loaded {label_data.get('loaded', 0)} labels", label_data.get("loaded", 0) > 0)

    # 11. Re-run evaluation with ground truth
    r = client.post("/api/v1/evaluation/run", headers=headers)
    check("POST /evaluation/run (with ground truth) returns 200", r.status_code == 200)
    eval2 = r.json().get("data", {})
    check("  ground_truth_source = vendor_labels.csv", eval2.get("ground_truth_source") == "vendor_labels.csv")

    # 12. Dashboard
    print("\n9. Dashboard")
    r = client.get("/api/v1/dashboard/summary", headers=headers)
    check("GET /dashboard/summary returns 200", r.status_code == 200)
    dash = r.json().get("data", {})
    check("  total_vendors > 0", dash.get("total_vendors", 0) > 0)
    check("  evaluation_summary present", dash.get("evaluation_summary") is not None)

    # 13. Certifications
    print("\n10. Certifications")
    r = client.post("/api/v1/certifications", headers=headers, json={
        "vendor_id": first_vendor_id,
        "certification_type": "SOC 2 Type II",
        "issuer": "AICPA",
        "expiry_date": "2027-12-31",
    })
    check("POST /certifications returns 200", r.status_code == 200)

    # 14. Alerts
    print("\n11. Alerts")
    r = client.post("/api/v1/alerts", headers=headers, json={
        "vendor_id": first_vendor_id,
        "alert_type": "BREACH",
        "severity": "HIGH",
        "message": "Smoke test alert",
    })
    check("POST /alerts returns 200", r.status_code == 200)

    # 15. Contracts
    print("\n12. Contracts")
    r = client.post(
        "/api/v1/contracts/upload",
        data={"vendor_id": first_vendor_id, "contract_name": "Smoke Contract"},
        files={"file": ("contract.txt", b"This is a test contract with terms for smoke testing purposes.", "text/plain")},
        headers=headers,
    )
    check("POST /contracts/upload returns 200", r.status_code == 200)

    # 16. Copilot
    print("\n13. Copilot")
    r = client.post("/api/v1/copilot/query", headers=headers, json={
        "question": "List all vendors",
    })
    check("POST /copilot/query returns 200", r.status_code == 200)

    # 17. Reports
    print("\n14. Reports")
    r = client.post("/api/v1/reports", headers=headers, params={"report_type": "vendor_risk_register"})
    check("POST /reports returns CSV", r.status_code == 200 and "text/csv" in r.headers.get("content-type", ""))

    # Summary
    print(f"\n{'='*50}")
    total = PASS + FAIL
    print(f"Results: {PASS}/{total} passed, {FAIL}/{total} failed")
    if FAIL > 0:
        print("❌ SMOKE TEST FAILED")
        sys.exit(1)
    else:
        print("✅ ALL SMOKE TESTS PASSED")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SENTINEL Smoke Test")
    parser.add_argument("--base-url", default=BASE, help=f"Base URL (default: {BASE})")
    args = parser.parse_args()
    main(args.base_url)
