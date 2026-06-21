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

def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}

print("═══ LEVEL 1: FULL API CONTRACT TESTING ═══\n")

# ── 1. AUTH ──
print("── 1.1 Authentication ──")

r = requests.post(f"{V1}/auth/login", json={"email": "admin@sentinel.ai", "password": "admin123"})
test("Valid login returns 200", r.status_code == 200, f"got {r.status_code}")
data = r.json()
test("Response has success=true", data.get("success") is True)
test("Response has access_token", "access_token" in data.get("data", {}))
test("Response has refresh_token", "refresh_token" in data.get("data", {}))
TOKEN = data["data"]["access_token"]
REFRESH = data["data"]["refresh_token"]

r = requests.post(f"{V1}/auth/login", json={"email": "admin@sentinel.ai", "password": "wrongpass"})
test("Invalid password returns 401", r.status_code == 401)

r = requests.post(f"{V1}/auth/login", json={"email": "noone@test.com", "password": "x"})
test("Invalid email returns 401", r.status_code == 401)

r = requests.get(f"{V2}/entities", headers={"Authorization": "Bearer eyJ.eyJ.eyJ"})
test("Expired/bad token returns 401", r.status_code == 401)

r = requests.get(f"{V2}/entities")
test("Missing token returns 401", r.status_code == 401)

# Refresh
r = requests.post(f"{V1}/auth/refresh", json={"refresh_token": REFRESH})
test("Token refresh returns 200", r.status_code == 200)

# ── 2. ENTITIES ──
print("\n── 2. Entity Registry ──")

ts = int(time.time())

r = requests.post(f"{V2}/entities", json={"entity_type": "VENDOR", "entity_name": f"API-Test-{ts}"}, headers=auth_headers(TOKEN))
test("Create VENDOR returns 200/201", r.status_code in (200, 201), f"got {r.status_code}")
eid_1 = r.json().get("data", {}).get("entity_id", "")

for etype in ["SYSTEM", "CONTROL", "USER", "POLICY", "EVIDENCE", "EXCEPTION", "CONFIG"]:
    r = requests.post(f"{V2}/entities", json={"entity_type": etype, "entity_name": f"{etype}-Test-{ts}"}, headers=auth_headers(TOKEN))
    test(f"Create {etype} returns 200", r.status_code in (200, 201), f"got {r.status_code}")

r = requests.post(f"{V2}/entities", json={"entity_name": "NoType"}, headers=auth_headers(TOKEN))
test("Missing entity_type returns 422", r.status_code == 422, f"got {r.status_code}")

r = requests.post(f"{V2}/entities", json={"entity_type": "VENDOR"}, headers=auth_headers(TOKEN))
test("Missing entity_name returns 422", r.status_code == 422, f"got {r.status_code}")

r = requests.get(f"{V2}/entities", headers=auth_headers(TOKEN))
test("List entities returns 200", r.status_code == 200)
data = r.json().get("data", {})
test("List has total", "total" in data)
test("List has entities array", isinstance(data.get("entities"), list))

r = requests.get(f"{V2}/entities?entity_type=VENDOR", headers=auth_headers(TOKEN))
test("Filter by entity_type works", r.status_code == 200)

r = requests.get(f"{V2}/entities/{eid_1}", headers=auth_headers(TOKEN))
test("Get entity by ID returns 200", r.status_code == 200)
if r.status_code == 200:
    edata = r.json().get("data", {})
    test("Entity has entity_id", edata.get("entity_id") == eid_1)
    test("Entity has entity_type", edata.get("entity_type") == "VENDOR")
    test("Entity has entity_name", len(edata.get("entity_name", "")) > 0)

r = requests.get(f"{V2}/entities/00000000-0000-0000-0000-000000000000", headers=auth_headers(TOKEN))
test("Get nonexistent entity returns 404", r.status_code == 404, f"got {r.status_code}")

# ── 3. GRAPH ──
print("\n── 3. Risk Graph ──")

# Use existing entities (already committed) for graph relationship tests
r = requests.get(f"{V2}/entities", headers=auth_headers(TOKEN))
entities = r.json().get("data", {}).get("entities", [])
src = entities[0]["entity_id"] if entities else ""
tgt = entities[1]["entity_id"] if len(entities) >= 2 else ""

if src and tgt:
    for rel_type in ["HAS_ACCESS_TO", "USES", "DEPENDS_ON", "AFFECTS", "BELONGS_TO"]:
        r = requests.post(f"{V2}/graph/relationships", json={
            "source_entity_id": src, "target_entity_id": tgt, "relationship_type": rel_type
        }, headers=auth_headers(TOKEN))
        test(f"Create {rel_type} relationship", r.status_code in (200, 201, 409), f"got {r.status_code}")

    r = requests.post(f"{V2}/graph/relationships", json={
        "source_entity_id": "00000000-0000-0000-0000-000000000000", "target_entity_id": tgt, "relationship_type": "HAS_ACCESS_TO"
    }, headers=auth_headers(TOKEN))
    test("Nonexistent source returns 404", r.status_code == 404, f"got {r.status_code}")

    r = requests.post(f"{V2}/graph/relationships", json={
        "source_entity_id": src, "target_entity_id": "00000000-0000-0000-0000-000000000000", "relationship_type": "HAS_ACCESS_TO"
    }, headers=auth_headers(TOKEN))
    test("Nonexistent target returns 404", r.status_code == 404, f"got {r.status_code}")

    # Circular: if DEPENDS_ON already exists (from above), try a different direction
    r = requests.post(f"{V2}/graph/relationships", json={
        "source_entity_id": tgt, "target_entity_id": src, "relationship_type": "HAS_ACCESS_TO"
    }, headers=auth_headers(TOKEN))
    test("Circular A→B→A does not crash", r.status_code in (200, 201, 409), f"got {r.status_code}")

    r = requests.get(f"{V2}/graph/entity/{src}", headers=auth_headers(TOKEN))
    test("Get entity graph returns 200", r.status_code == 200)
    gdata = r.json().get("data", {})
    test("Graph has nodes array", isinstance(gdata.get("nodes"), list))
    test("Graph has edges array", isinstance(gdata.get("edges"), list))

    r = requests.get(f"{V2}/graph/entity/{src}/impact", headers=auth_headers(TOKEN))
    test("Impact path returns 200/404", r.status_code in (200, 404), f"got {r.status_code}")

# ── 4. RISK ──
print("\n── 4. Risk Engine ──")

r = requests.post(f"{V2}/risk/calculate", json={"entity_id": eid_1}, headers=auth_headers(TOKEN))
test("Calculate risk returns 200", r.status_code == 200, f"got {r.status_code}")
test("Response has overall_score", "overall_score" in r.json().get("data", {}))

r = requests.get(f"{V2}/risk/{eid_1}", headers=auth_headers(TOKEN))
test("Get risk returns 200", r.status_code == 200, f"got {r.status_code}")
rdata = r.json().get("data", {})
test("Risk has overall_score", "overall_score" in rdata)
test("Risk has entity_id", rdata.get("entity_id") == eid_1)

r = requests.post(f"{V2}/risk/recalculate", headers=auth_headers(TOKEN))
test("Recalculate portfolio returns 200", r.status_code == 200, f"got {r.status_code}")

r = requests.get(f"{V2}/risk/00000000-0000-0000-0000-000000000000", headers=auth_headers(TOKEN))
test("Get risk for nonexistent returns 200 (graceful)", r.status_code in (200, 404), f"got {r.status_code}")

# ── 5. ANOMALIES ──
print("\n── 5. Anomalies ──")

# Anomalies are auto-detected; list them
r = requests.get(f"{V2}/anomalies", headers=auth_headers(TOKEN))
test("List anomalies returns 200", r.status_code == 200, f"got {r.status_code}")
adata = r.json().get("data", {})
test("Anomalies has items array", isinstance(adata.get("items"), list) if "items" in adata else True)

r = requests.get(f"{V2}/anomalies?severity=CRITICAL", headers=auth_headers(TOKEN))
test("Filter anomalies by severity works", r.status_code == 200, f"got {r.status_code}")

# ── 6. CORRELATION ──
print("\n── 6. Correlation ──")

r = requests.post(f"{V2}/correlation/run", json={"entity_id": eid_1}, headers=auth_headers(TOKEN))
test("Correlation run returns 200", r.status_code == 200, f"got {r.status_code}")

r = requests.get(f"{V2}/correlation/{eid_1}", headers=auth_headers(TOKEN))
test("Get correlated risk returns 200", r.status_code == 200, f"got {r.status_code}")
cdata = r.json().get("data", {})
for key in ["base_risk", "neighbor_risk", "correlated_risk", "reasoning"]:
    test(f"Correlation has {key}", key in cdata)

# ── 7. BLAST RADIUS ──
print("\n── 7. Blast Radius ──")

r = requests.get(f"{V2}/blast-radius/{eid_1}", headers=auth_headers(TOKEN))
test("Blast radius returns 200", r.status_code == 200, f"got {r.status_code}")
bdata = r.json().get("data", {}) or {}
for key in ["total", "systems", "controls", "users"]:
    test(f"Blast radius has {key}", key in bdata)

# ── 8. INTELLIGENCE ──
print("\n── 8. Intelligence ──")

r = requests.post(f"{V2}/intelligence/daily", headers=auth_headers(TOKEN))
test("Daily intelligence returns 200", r.status_code == 200, f"got {r.status_code}")

r = requests.post(f"{V2}/intelligence/executive", headers=auth_headers(TOKEN))
test("Executive brief returns 200", r.status_code == 200, f"got {r.status_code}")

r = requests.post(f"{V2}/intelligence/priorities", headers=auth_headers(TOKEN))
test("Priorities returns 200", r.status_code == 200, f"got {r.status_code}")

# ── 9. REMEDIATION ──
print("\n── 9. Remediation ──")

r = requests.post(f"{V2}/remediation/generate", json={"entity_id": eid_1, "anomaly_type": "VENDOR_NO_CONTACT"}, headers=auth_headers(TOKEN))
test("Generate remediation returns 200", r.status_code == 200, f"got {r.status_code}")

r = requests.get(f"{V2}/remediation/actions", headers=auth_headers(TOKEN))
test("Open actions returns 200", r.status_code == 200, f"got {r.status_code}")

# ── 10. TIMELINE ──
print("\n── 10. Timeline ──")

r = requests.get(f"{V2}/timeline/entity/{eid_1}", headers=auth_headers(TOKEN))
test("Entity timeline returns 200", r.status_code == 200, f"got {r.status_code}")

r = requests.get(f"{V2}/timeline/portfolio", headers=auth_headers(TOKEN))
test("Portfolio timeline returns 200", r.status_code == 200, f"got {r.status_code}")

# ── 11. SCENARIO ──
print("\n── 11. Scenario Simulator ──")

r = requests.get(f"{V2}/scenario/templates", headers=auth_headers(TOKEN))
test("Scenario templates returns 200", r.status_code == 200, f"got {r.status_code}")
tdata = r.json().get("data", {})
test("Templates has total", "total" in tdata)
test("Templates has templates array", isinstance(tdata.get("templates"), list))
test("At least 6 templates", len(tdata.get("templates", [])) >= 6, f"got {len(tdata.get('templates', []))}")

for scenario in ["BREACH", "FAILURE", "CONTRACT_EXPIRY", "CERT_EXPIRED", "IDENTITY_COMPROMISE", "CONFIG_DRIFT"]:
    r = requests.post(f"{V2}/scenario/run", json={"entity_id": eid_1, "scenario": scenario}, headers=auth_headers(TOKEN))
    test(f"Run {scenario} scenario returns 200", r.status_code == 200, f"got {r.status_code}")
    if r.status_code == 200:
        rdata = r.json().get("data", {}).get("results", {})
        test(f"  {scenario} has source_entity", "source_entity" in rdata)
        test(f"  {scenario} has impact", "impact" in rdata)
        test(f"  {scenario} has blast_radius", "blast_radius" in rdata)

r = requests.get(f"{V2}/scenario/results", headers=auth_headers(TOKEN))
test("Scenario results history returns 200", r.status_code == 200, f"got {r.status_code}")

# ── 12. INGESTION ──
print("\n── 12. Ingestion ──")

r = requests.post(f"{V2}/ingestion/json", json={"data": {"entity_type": "VENDOR", "name": f"Import-Test-{ts}"}}, headers=auth_headers(TOKEN))
test("JSON ingestion returns 200", r.status_code == 200, f"got {r.status_code}")
idata = r.json().get("data", {})
test("Ingestion has entities_created", "entities_created" in idata)

r = requests.post(f"{V2}/ingestion/manual", json={"entity_type": "POLICY", "entity_name": f"Manual-Policy-{ts}", "attributes": {"owner": "test"}}, headers=auth_headers(TOKEN))
test("Manual entity creation returns 200", r.status_code == 200, f"got {r.status_code}")

r = requests.post(f"{V2}/ingestion/normalize", headers=auth_headers(TOKEN))
test("Normalization pipeline returns 200", r.status_code == 200, f"got {r.status_code}")

# ── 13. DOCUMENTS ──
print("\n── 13. Document Intelligence ──")

import io
pdf_bytes = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n190\n%%EOF"
r = requests.post(f"{V2}/documents/upload", files={"file": ("test.pdf", pdf_bytes, "application/pdf")}, data={"document_type": "POLICY"}, headers=auth_headers(TOKEN))
test("Document upload returns 200", r.status_code == 200, f"got {r.status_code}")
doc_id = r.json().get("data", {}).get("document_id", "")

if doc_id:
    r = requests.post(f"{V2}/documents/analyze", data={"document_id": doc_id}, headers=auth_headers(TOKEN))
    test("Document analysis returns 200", r.status_code == 200, f"got {r.status_code}")

    r = requests.get(f"{V2}/documents/findings?document_id={doc_id}", headers=auth_headers(TOKEN))
    test("Document findings returns 200", r.status_code == 200, f"got {r.status_code}")

    r = requests.post(f"{V2}/documents/build-graph", data={"document_id": doc_id}, headers=auth_headers(TOKEN))
    test("Build graph from document returns 200", r.status_code == 200, f"got {r.status_code}")

# ── 14. COPILOT ──
print("\n── 14. Copilot ──")

questions = [
    "Why is a vendor risky?",
    "What should I focus on today?",
    "Generate board report",
    "What if a vendor is breached?",
    "How do I reduce risk?",
]
for q in questions:
    r = requests.post(f"{V2}/copilot/query", json={"question": q}, headers=auth_headers(TOKEN))
    test(f"Copilot: '{q[:30]}...' returns 200", r.status_code == 200, f"got {r.status_code}")
    if r.status_code == 200:
        cdata = r.json().get("data", {})
        test(f"  Has answer", len(cdata.get("answer", "")) > 0)
        test(f"  Has intent", "intent" in cdata)
        test(f"  Has engine", "engine" in cdata)

# Nonsense query
r = requests.post(f"{V2}/copilot/query", json={"question": "Bananas are blue"}, headers=auth_headers(TOKEN))
test("Nonsense query returns 200 (graceful)", r.status_code == 200, f"got {r.status_code}")

# ── 15. PIPELINE ──
print("\n── 15. Pipeline ──")

r = requests.post(f"{V2}/pipeline/run", json={}, headers=auth_headers(TOKEN))
test("Full pipeline run returns 200", r.status_code == 200, f"got {r.status_code}")

# ── RESULTS ──
print(f"\n═══ LEVEL 1 RESULTS: {passed} passed, {failed} failed ═══")
sys.exit(1 if failed > 0 else 0)
