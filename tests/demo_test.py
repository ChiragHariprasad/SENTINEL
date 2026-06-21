#!/usr/bin/env python3
"""LEVEL 10: DEMO TESTING — End-to-end demo flow, run 10 times"""

import requests
import sys
import time
import io

BASE = "http://localhost:8082"
V1 = f"{BASE}/api/v1"
V2 = f"{BASE}/api/v2"

passed = 0
failed = 0
run_times = []

def test(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
    else:
        failed += 1
        print(f"  ❌ {name} — {detail}")

def H(token):
    return {"Authorization": f"Bearer {token}"}

def make_pdf(text):
    return b"%%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Contents 4 0 R>>endobj\n4 0 obj<</Length %d>>stream\n%s\nendstream\nendobj\nxref\n0 5\ntrailer<</Size 5/Root 1 0 R>>\n%%%%EOF" % (len(text), text.encode())

def run_demo(run_num):
    global passed, failed
    print(f"\n{'='*60}")
    print(f"  DEMO RUN {run_num}/10")
    print(f"{'='*60}")

    start = time.time()
    local_passed = 0
    local_failed = 0
    errors = []

    # Step 1: Login
    r = requests.post(f"{V1}/auth/login", json={"email": "admin@sentinel.ai", "password": "admin123"}, timeout=10)
    if r.status_code != 200:
        errors.append("Login failed")
        return
    token = r.json()["data"]["access_token"]
    h = H(token)
    local_passed += 1

    ts = int(time.time())

    # Step 2: Upload Vendor CSV
    csv_content = f"vendor_name,category,risk_tier\nDemoVendor-{ts},Cloud,3\nDemoPartner-{ts},SaaS,2\n"
    r = requests.post(f"{V2}/ingestion/csv",
        files={"file": ("demo.csv", csv_content.encode(), "text/csv")},
        data={"csv_type": "vendor"}, headers=h, timeout=15)
    if r.status_code != 200:
        errors.append(f"CSV upload failed: {r.status_code}")
    else:
        local_passed += 1
        print(f"  ✅ CSV uploaded ({r.json()['data']['entities_created']} entities)")

    # Step 3: Create Graph (find entities, link them)
    r = requests.get(f"{V2}/entities?entity_type=VENDOR&size=2", headers=h, timeout=10)
    entities = r.json().get("data", {}).get("entities", [])
    if len(entities) >= 2:
        src, tgt = entities[0]["entity_id"], entities[1]["entity_id"]
        r = requests.post(f"{V2}/graph/relationships", json={
            "source_entity_id": src, "target_entity_id": tgt, "relationship_type": "HAS_ACCESS_TO"
        }, headers=h, timeout=10)
        if r.status_code in (200, 201, 409):
            local_passed += 1
            if r.status_code == 409:
                print(f"  ✅ Graph relationship exists (skipped)")
            else:
                print(f"  ✅ Graph relationship created")
        else:
            errors.append(f"Graph creation failed: {r.status_code}")
    else:
        errors.append("Not enough entities for graph")

    # Step 4: Calculate Risk
    if entities:
        eid = entities[0]["entity_id"]
        r = requests.post(f"{V2}/risk/calculate", json={"entity_id": eid}, headers=h, timeout=15)
        if r.status_code == 200:
            score = r.json().get("data", {}).get("overall_score", "?")
            local_passed += 1
            print(f"  ✅ Risk calculated (score={score})")
        else:
            errors.append(f"Risk calculation failed: {r.status_code}")

    # Step 5: Run Correlation
        r = requests.post(f"{V2}/correlation/run", json={"entity_id": eid}, headers=h, timeout=15)
        if r.status_code == 200:
            local_passed += 1
            print(f"  ✅ Correlation run")
        else:
            errors.append(f"Correlation failed: {r.status_code}")

    # Step 6: Show Timeline
        r = requests.get(f"{V2}/timeline/entity/{eid}", headers=h, timeout=10)
        if r.status_code == 200:
            local_passed += 1
            print(f"  ✅ Timeline loaded")
        else:
            errors.append(f"Timeline failed: {r.status_code}")

    # Step 7: Run Simulation
        r = requests.post(f"{V2}/scenario/run", json={"entity_id": eid, "scenario": "BREACH"}, headers=h, timeout=15)
        if r.status_code == 200:
            impact = r.json().get("data", {}).get("results", {}).get("impact", {})
            delta = impact.get("risk_delta", "?")
            local_passed += 1
            print(f"  ✅ Scenario run (delta=+{delta})")
        else:
            errors.append(f"Scenario failed: {r.status_code}")

        r = requests.post(f"{V2}/scenario/run", json={"entity_id": eid, "scenario": "FAILURE"}, headers=h, timeout=15)
        if r.status_code == 200:
            local_passed += 1
            print(f"  ✅ Scenario FAILURE run")
        else:
            errors.append(f"Scenario FAILURE failed: {r.status_code}")

    # Step 8: Generate Remediation
        r = requests.post(f"{V2}/remediation/generate", json={"entity_id": eid, "anomaly_type": "VENDOR_NO_CONTACT"}, headers=h, timeout=15)
        if r.status_code == 200:
            local_passed += 1
            print(f"  ✅ Remediation generated")
        else:
            errors.append(f"Remediation failed: {r.status_code}")

    # Step 9: Ask Copilot
        r = requests.post(f"{V2}/copilot/query", json={"question": "What should I focus on today?"}, headers=h, timeout=15)
        if r.status_code == 200:
            answer = r.json().get("data", {}).get("answer", "")
            local_passed += 1
            print(f"  ✅ Copilot answered ({len(answer)} chars)")
        else:
            errors.append(f"Copilot failed: {r.status_code}")

    # Step 10: Generate Executive Brief
        r = requests.post(f"{V2}/intelligence/executive", headers=h, timeout=15)
        if r.status_code == 200:
            local_passed += 1
            print(f"  ✅ Executive brief generated")
        else:
            errors.append(f"Executive brief failed: {r.status_code}")

    elapsed = time.time() - start
    run_times.append(elapsed)
    passed += local_passed
    failed += local_failed + len(errors)

    if errors:
        print(f"\n  ⚠️  Errors: {'; '.join(errors)}")
    print(f"  ⏱️  {elapsed:.1f}s | {local_passed} passed, {len(errors)} errors")
    return len(errors) == 0


print("═══ LEVEL 10: DEMO TESTING ═══")
print("Running end-to-end demo flow 10 times...\n")

successful_runs = 0
for i in range(1, 11):
    ok = run_demo(i)
    if ok:
        successful_runs += 1
    time.sleep(1)

print(f"\n{'='*60}")
print(f"  DEMO RESULTS: {successful_runs}/10 runs successful")
print(f"  Total assertions: {passed} passed, {failed} failed")
if run_times:
    print(f"  Avg time: {sum(run_times)/len(run_times):.1f}s (min={min(run_times):.1f}s, max={max(run_times):.1f}s)")
print(f"{'='*60}")

if successful_runs == 10 and failed == 0:
    print("\n🎉 READY FOR JUDGING!")
else:
    print(f"\n⚠️  {10 - successful_runs} runs had failures — investigate before demo")
    sys.exit(1)
