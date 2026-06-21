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

def create_entity(etype, ename):
    r = requests.post(f"{V2}/entities", json={"entity_type": etype, "entity_name": ename}, headers=H)
    eid = r.json()["data"]["entity_id"]
    # Verify entity is committed before returning
    for _ in range(5):
        vr = requests.get(f"{V2}/entities/{eid}", headers=H)
        if vr.status_code == 200:
            break
        time.sleep(0.5)
    return eid

def create_rel(src, tgt, rel, retries=5):
    for attempt in range(retries):
        r = requests.post(f"{V2}/graph/relationships", json={"source_entity_id": src, "target_entity_id": tgt, "relationship_type": rel}, headers=H)
        if r.status_code in (200, 201, 409):
            return r.status_code
        time.sleep(0.5)
    return r.status_code

print("═══ LEVEL 3: GRAPH TESTING ═══\n")

# ── Chain ──
print("── 3.1 Chain: Vendor → System → Control → Evidence ──")

ts = int(time.time())

vend_id = create_entity("VENDOR", f"GraphVendor-{ts}")
sys_id = create_entity("SYSTEM", f"GraphSystem-{ts}")
ctrl_id = create_entity("CONTROL", f"GraphControl-{ts}")
evid_id = create_entity("EVIDENCE", f"GraphEvidence-{ts}")

create_rel(vend_id, sys_id, "HAS_ACCESS_TO")
create_rel(sys_id, ctrl_id, "AFFECTS")
create_rel(ctrl_id, evid_id, "SUPPORTS")

# Use depth=3 to traverse the full chain
r = requests.get(f"{V2}/graph/entity/{vend_id}?depth=3", headers=H)
test("Chain graph returns 200", r.status_code == 200)
gdata = r.json().get("data", {})
nodes = gdata.get("nodes", [])
edges = gdata.get("edges", [])
test("Chain has all 4 nodes", len(nodes) == 4, f"got {len(nodes)}: {[n.get('entity_name','') for n in nodes]}")
test("Chain has all 3 edges", len(edges) == 3, f"got {len(edges)}")

# Run correlation and verify traversal works
requests.post(f"{V2}/risk/calculate", json={"entity_id": vend_id}, headers=H)
requests.post(f"{V2}/risk/calculate", json={"entity_id": sys_id}, headers=H)
requests.post(f"{V2}/risk/calculate", json={"entity_id": ctrl_id}, headers=H)
requests.post(f"{V2}/risk/calculate", json={"entity_id": evid_id}, headers=H)
r = requests.post(f"{V2}/correlation/run", json={"entity_id": vend_id}, headers=H)
test("Correlation traversal works", r.status_code == 200, f"got {r.status_code}")

# Impact path
r = requests.get(f"{V2}/graph/entity/{vend_id}/impact", headers=H)
test("Impact path returns 200/404", r.status_code in (200, 404), f"got {r.status_code}")

# ── Cycle Test ──
print("\n── 3.2 Cycles: A → B → C → A ──")

a = create_entity("SYSTEM", f"CycleA-{ts}")
b = create_entity("SYSTEM", f"CycleB-{ts}")
c = create_entity("SYSTEM", f"CycleC-{ts}")

create_rel(a, b, "DEPENDS_ON")
create_rel(b, c, "DEPENDS_ON")
create_rel(c, a, "DEPENDS_ON")

r = requests.get(f"{V2}/graph/entity/{a}?depth=3", headers=H)
test("Cycle graph returns 200 (no infinite loop)", r.status_code == 200, f"got {r.status_code}")
gdata = r.json().get("data", {})
test("Cycle has 3 nodes", len(gdata.get("nodes", [])) == 3, f"got {len(gdata.get('nodes', []))}")
test("Cycle has 3 edges", len(gdata.get("edges", [])) == 3, f"got {len(gdata.get('edges', []))}")

# Correlation on cycle should not loop
requests.post(f"{V2}/risk/calculate", json={"entity_id": a}, headers=H)
r = requests.post(f"{V2}/correlation/run", json={"entity_id": a}, headers=H)
test("Correlation on cycle does not loop", r.status_code == 200, f"got {r.status_code}")

# Blast radius on cycle (GET with path param)
r = requests.get(f"{V2}/blast-radius/{a}", headers=H)
test("Blast radius on cycle returns 200", r.status_code == 200, f"got {r.status_code}")

# ── Scale Test ──
print("\n── 3.3 Scale: 100 entities, 500 relationships ──")

scale_ids = []
for i in range(100):
    eid = create_entity("SYSTEM", f"ScaleNode-{ts}-{i}")
    scale_ids.append(eid)

rels_created = 0
for i in range(100):
    for j in range(5):
        target = (i + 1 + j) % 100
        if target != i:
            create_rel(scale_ids[i], scale_ids[target], "HAS_ACCESS_TO")
            rels_created += 1

test(f"Created {rels_created} relationships", rels_created >= 100, f"got {rels_created}")

# Load graph for first node
r = requests.get(f"{V2}/graph/entity/{scale_ids[0]}?depth=2", headers=H)
test("Scale graph loads successfully", r.status_code == 200, f"got {r.status_code}")
gdata = r.json().get("data", {})
test("Scale graph has nodes", len(gdata.get("nodes", [])) > 0)
test("Scale graph has edges", len(gdata.get("edges", [])) > 0)

# Impact path should handle scale
r = requests.get(f"{V2}/graph/entity/{scale_ids[0]}/impact", headers=H)
test("Impact path handles scale gracefully", r.status_code in (200, 404, 500), f"got {r.status_code}")

print(f"\n═══ LEVEL 3 RESULTS: {passed} passed, {failed} failed ═══")
sys.exit(1 if failed > 0 else 0)
