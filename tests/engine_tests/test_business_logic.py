import requests
import sys
import time

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

def create_entity(etype, name, attrs=None):
    body = {"entity_type": etype, "entity_name": name}
    if attrs:
        body["attributes"] = attrs
    r = requests.post(f"{V2}/entities", json=body, headers=H)
    eid = r.json().get("data", {}).get("entity_id", "")
    # Verify entity is committed
    for _ in range(5):
        vr = requests.get(f"{V2}/entities/{eid}", headers=H)
        if vr.status_code == 200:
            break
        time.sleep(0.5)
    return eid

print("═══ LEVEL 2: BUSINESS LOGIC TESTING ═══\n")

ts = int(time.time())

# ── Risk Engine ──
print("── Risk Engine ──")

# Low risk vendor (pure v2 — no linked v1 Vendor record, so default scores are used)
low_id = create_entity("VENDOR", f"LowRiskLogic-{ts}")
requests.post(f"{V2}/risk/calculate", json={"entity_id":low_id}, headers=H)
r = requests.get(f"{V2}/risk/{low_id}", headers=H)
low_score = r.json().get("data", {}).get("overall_score") if r.json().get("data") else None
test("Low-risk vendor scored", low_score is not None)
test("Score is >= 0", low_score is not None and low_score >= 0, f"score={low_score}")

# SYSTEM (always has default scores of 30+20+25+40=115/400 → ~29)
sys_id = create_entity("SYSTEM", f"SystemRisk-{ts}")
requests.post(f"{V2}/risk/calculate", json={"entity_id":sys_id}, headers=H)
r = requests.get(f"{V2}/risk/{sys_id}", headers=H)
sys_score = r.json().get("data", {}).get("overall_score") if r.json().get("data") else None
test("System scored", sys_score is not None)
test("System has score > 0", sys_score is not None and sys_score > 0, f"score={sys_score}")

# Correlation Engine
print("\n── Correlation Engine ──")

# Vendor A → System X
va = create_entity("VENDOR", f"CorrVendorA-{ts}", {"risk_tier":"critical"})
sx = create_entity("SYSTEM", f"SystemX-{ts}")

requests.post(f"{V2}/graph/relationships", json={"source_entity_id":va,"target_entity_id":sx,"relationship_type":"HAS_ACCESS_TO"}, headers=H)
requests.post(f"{V2}/risk/calculate", json={"entity_id":va}, headers=H)
requests.post(f"{V2}/risk/calculate", json={"entity_id":sx}, headers=H)
requests.post(f"{V2}/correlation/run", json={"entity_id":va}, headers=H)

r = requests.get(f"{V2}/correlation/{va}", headers=H)
cdata = r.json().get("data", {})
test("Correlated risk has base_risk", "base_risk" in cdata)
test("Correlated risk has neighbor_risk", "neighbor_risk" in cdata)
test("Correlated risk has correlated_risk", "correlated_risk" in cdata)

# No relationship → correlated == base
iso = create_entity("VENDOR", f"IsolatedLogic-{ts}")
requests.post(f"{V2}/risk/calculate", json={"entity_id":iso}, headers=H)
requests.post(f"{V2}/correlation/run", json={"entity_id":iso}, headers=H)
r = requests.get(f"{V2}/correlation/{iso}", headers=H)
idata = r.json().get("data", {})
test("Isolated entity has neighbor_risk=0", idata.get("neighbor_risk") == 0, f"got {idata.get('neighbor_risk')}")

# History & Timeline
print("\n── History & Timeline ──")
r = requests.get(f"{V2}/timeline/entity/{va}", headers=H)
test("Entity timeline returns 200", r.status_code == 200)
r = requests.get(f"{V2}/timeline/portfolio", headers=H)
test("Portfolio timeline returns 200", r.status_code == 200)

# Intelligence
print("\n── Intelligence Pipeline ──")
r = requests.post(f"{V2}/intelligence/daily", headers=H)
test("Daily intelligence has summary", "summary" in r.json().get("data", {}))
r = requests.post(f"{V2}/intelligence/priorities", headers=H)
test("Priorities returns 200", r.status_code == 200)

print(f"\n═══ LEVEL 2 RESULTS: {passed} passed, {failed} failed ═══")
sys.exit(1 if failed > 0 else 0)
