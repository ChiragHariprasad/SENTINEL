import requests
import sys
import time
import json

BASE = "http://localhost:8082"
V1 = f"{BASE}/api/v1"
V2 = f"{BASE}/api/v2"

passed = 0
failed = 0

def test(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  ✅ {name}")
    else:
        failed += 1
        print(f"  ❌ {name} — {detail}")

TOKEN = requests.post(f"{V1}/auth/login", json={"email":"admin@sentinel.ai","password":"admin123"}).json()["data"]["access_token"]
H = {"Authorization": f"Bearer {TOKEN}"}

print("═══ LEVEL 4: SCENARIO TESTING ═══\n")

ts = int(time.time())

# Create test vendor with attributes to ensure risk
r = requests.post(f"{V2}/entities", json={
    "entity_type": "VENDOR", "entity_name": f"ScenarioVendor-{ts}",
    "attributes": {"category": "cloud", "risk_tier": "critical"}
}, headers=H)
vid = r.json()["data"]["entity_id"]

# Calculate risk first
requests.post(f"{V2}/risk/calculate", json={"entity_id": vid}, headers=H)

# Create connected entities for blast radius
e_types = ["SYSTEM", "CONTROL", "USER", "CONTROL", "CONTROL", "CONTROL"]
neighbors = []
for et in e_types:
    r = requests.post(f"{V2}/entities", json={"entity_type": et, "entity_name": f"SceneNeighbor-{ts}-{len(neighbors)}"}, headers=H)
    nid = r.json()["data"]["entity_id"]
    neighbors.append(nid)
    requests.post(f"{V2}/graph/relationships", json={
        "source_entity_id": vid, "target_entity_id": nid, "relationship_type": "AFFECTS"
    }, headers=H)
    requests.post(f"{V2}/risk/calculate", json={"entity_id": nid}, headers=H)

scenarios = [
    ("BREACH", "Vendor Breach"),
    ("FAILURE", "Vendor Failure"),
    ("CONTRACT_EXPIRY", "Contract Termination"),
    ("CERT_EXPIRED", "Certification Expiry"),
    ("IDENTITY_COMPROMISE", "Identity Compromise"),
    ("CONFIG_DRIFT", "Configuration Drift"),
]

for scenario_id, scenario_name in scenarios:
    print(f"\n── {scenario_name} ──")
    r = requests.post(f"{V2}/scenario/run", json={"entity_id": vid, "scenario": scenario_id}, headers=H)
    test(f"Returns 200", r.status_code == 200, f"got {r.status_code}")

    if r.status_code != 200:
        continue

    data = r.json().get("data", {})
    results = data.get("results", {})
    source = results.get("source_entity", {})
    impact = results.get("impact", {})
    br = results.get("blast_radius", {})

    test("Has source_entity", bool(source), str(source)[:80])
    test("Has impact data", bool(impact), str(impact)[:80])
    test("Has blast_radius", bool(br), str(br)[:80])

    if impact:
        test("Has current_risk", "current_risk" in impact)
        test("Has projected_risk", "projected_risk" in impact)
        test("Has risk_delta", "risk_delta" in impact)
        if "projected_risk" in impact and "current_risk" in impact:
            test("Projected >= Current", impact["projected_risk"] >= impact["current_risk"],
                f"{impact['projected_risk']} >= {impact['current_risk']}")
            test("Delta positive", impact.get("risk_delta", 0) >= 0, f"delta={impact.get('risk_delta')}")

    if br:
        test("Has total_affected", "total_affected" in br)
        test("Has affected_systems", "affected_systems" in br)
        test("Has affected_controls", "affected_controls" in br)
        test("Has affected_users", "affected_users" in br)
        test("Total >= 0", br.get("total_affected", -1) >= 0, f"total={br.get('total_affected')}")

    test("Has impacted_entities list", "impacted_entities" in results, str(results.get("impacted_entities", ""))[:60])

    print(f"  {impact.get('current_risk', '?')} → {impact.get('projected_risk', '?')} (+{impact.get('risk_delta', '?')}) | "
          f"Blast: {br.get('total_affected', '?')} total ({br.get('affected_systems', '?')} sys, "
          f"{br.get('affected_controls', '?')} ctrl, {br.get('affected_users', '?')} usr)")

# Verify results are persisted
r = requests.get(f"{V2}/scenario/results", headers=H)
test("Scenario results history has entries", r.status_code == 200)
rdata = r.json().get("data", {})
test("At least 6 runs recorded", rdata.get("total", 0) >= 6, f"got {rdata.get('total')}")

print(f"\n═══ LEVEL 4 RESULTS: {passed} passed, {failed} failed ═══")
sys.exit(1 if failed > 0 else 0)
