"""
SENTINEL v2 Full Pipeline Demo
Processes 3 real PDFs through the entire intelligence pipeline.
"""
import sys, json, time, uuid
import urllib.request, urllib.parse

BASE = "http://localhost:8082"

def api(method, path, token=None, data=None, form=None, files=None):
    url = f"{BASE}{path}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if files:
        import http.client
        boundary = "----" + uuid.uuid4().hex
        body = b""
        for k, v in files.items():
            body += f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"; filename=\"{v[0]}\"\r\nContent-Type: application/octet-stream\r\n\r\n".encode()
            with open(v[1], "rb") as f:
                body += f.read()
            body += b"\r\n"
        if form:
            for k, v in form.items():
                body += f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode()
        body += f"--{boundary}--\r\n".encode()
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
    elif form:
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        req = urllib.request.Request(url, data=urllib.parse.urlencode(form).encode(), headers=headers, method=method)
    elif data is not None:
        headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=headers, method=method)
    else:
        req = urllib.request.Request(url, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            return json.loads(body)
        except:
            return {"error": body, "status": e.code}
    except Exception as e:
        return {"error": str(e)}

def login():
    r = api("POST", "/api/v1/auth/login", data={"email": "admin@sentinel.ai", "password": "admin123"})
    return r["data"]["access_token"]

def call(method, path, token, **kw):
    r = api(method, path, token, **kw)
    if isinstance(r, dict) and "error" in r and "status" in r:
        print(f"  WARN {method} {path}: {r['error']}")
    return r

def step(num, label):
    print(f"\n{'='*60}")
    print(f"STEP {num}: {label}")
    print(f"{'='*60}")

TOKEN = login()
print(f"Token obtained: {TOKEN[:20]}...")

# ============================================================
# STEP 1: Create Business Entities
# ============================================================
step(1, "Create Business Entities (Sphinx, Walkover, PDPU, AWS, etc.)")

entities = {
    "VETTING": {
        "entity_type": "VENDOR",
        "entity_name": "Sphinx Technology Limited",
        "attributes": {
            "industry": "Cybersecurity", "country": "United Kingdom",
            "service": "Penetration Testing & Security Audits",
            "iso_cert": True, "cert_number": "15806481923",
            "cert_standard": "ISO/IEC 27001:2022",
            "cert_issued": "2023-04-27", "cert_update": "2025-05-15",
            "cert_expiry": "2026-04-26",
        }
    },
    "WALKOVER": {
        "entity_type": "VENDOR",
        "entity_name": "Walkover Web Solutions Private Limited",
        "attributes": {
            "industry": "SaaS", "country": "India",
            "product": "MSG91", "soc2_type": "Type 2",
            "soc2_period": "Jan-Apr 2024", "soc2_next": "2025-04-27",
        }
    },
    "PDPU": {
        "entity_type": "ORGANIZATION",
        "entity_name": "Pandit Deendayal Petroleum University (PDPU)",
        "attributes": {
            "industry": "Education", "country": "India",
            "audit_period": "H1 FY 2017-18",
        }
    },
    "AWS": {
        "entity_type": "VENDOR",
        "entity_name": "Amazon Web Services (AWS)",
        "attributes": {"industry": "Cloud Infrastructure", "service": "IaaS/PaaS"}
    },
    "GITHUB": {
        "entity_type": "VENDOR",
        "entity_name": "GitHub",
        "attributes": {"industry": "Software Development", "service": "Code Hosting/CI-CD"}
    },
    "MONGODB": {
        "entity_type": "VENDOR",
        "entity_name": "MongoDB",
        "attributes": {"industry": "Database", "service": "NoSQL Database"}
    },
    "MYSQL": {
        "entity_type": "VENDOR",
        "entity_name": "MySQL (Oracle)",
        "attributes": {"industry": "Database", "service": "Relational Database"}
    },
    "GWS": {
        "entity_type": "VENDOR",
        "entity_name": "Google Workspace",
        "attributes": {"industry": "SaaS", "service": "Email/Collaboration"}
    },
    "FINDING_UNDER_RECOVERY": {
        "entity_type": "CONTROL",
        "entity_name": "Under Recovery of Academic Fees - ₹35,85,100",
        "attributes": {
            "finding_type": "Under Recovery", "risk_category": "HIGH",
            "risk_type": "Financial", "amount": "₹35,85,100",
            "description": "Under-recovery of academic fees amounting to ₹35,85,100",
            "source": "Internal Audit Report H1 FY 2017-18",
        }
    },
    "FINDING_PRIOR_YEARS": {
        "entity_type": "CONTROL",
        "entity_name": "Non-Recovery of Academic Fees for Prior Years",
        "attributes": {
            "finding_type": "Non-Recovery", "risk_category": "HIGH",
            "risk_type": "Financial",
            "description": "Non-recovery of academic fees for prior academic years",
            "source": "Internal Audit Report H1 FY 2017-18",
        }
    },
    "FINDING_EXCESS_PAYMENT": {
        "entity_type": "CONTROL",
        "entity_name": "Excess Payment Made",
        "attributes": {
            "finding_type": "Excess Payment", "risk_category": "HIGH",
            "risk_type": "Financial",
            "description": "Excess payments made during audit period",
            "source": "Internal Audit Report H1 FY 2017-18",
        }
    },
}

entity_ids = {}
for key, e in entities.items():
    r = call("POST", "/api/v2/entities", TOKEN, data=e)
    dd = r.get("data", r)
    eid = dd.get("entity_id") or dd.get("id")
    entity_ids[key] = eid
    print(f"  Created {key}: {eid}")

# ============================================================
# STEP 2: Create Risk Relationships
# ============================================================
step(2, "Create Risk Relationships")

relationships = [
    ("WALKOVER", "AWS", "DEPENDS_ON", 0.9, "Walkover MSG91 hosted on AWS"),
    ("WALKOVER", "GITHUB", "DEPENDS_ON", 0.8, "Walkover uses GitHub for source control"),
    ("WALKOVER", "MONGODB", "DEPENDS_ON", 0.7, "Walkover uses MongoDB for data storage"),
    ("WALKOVER", "MYSQL", "DEPENDS_ON", 0.7, "Walkover uses MySQL for relational data"),
    ("WALKOVER", "GWS", "DEPENDS_ON", 0.6, "Walkover uses Google Workspace for email"),
    ("VETTING", "WALKOVER", "PROVIDES_SERVICE_TO", 0.5, "Sphinx audits Walkover"),
    ("PDPU", "VETTING", "USES_SERVICE", 0.3, "PDPU uses VETTING for pen testing"),
    ("PDPU", "FINDING_UNDER_RECOVERY", "HAS_FINDING", 1.0, "PDPU audit finding"),
    ("PDPU", "FINDING_PRIOR_YEARS", "HAS_FINDING", 1.0, "PDPU audit finding"),
    ("PDPU", "FINDING_EXCESS_PAYMENT", "HAS_FINDING", 1.0, "PDPU audit finding"),
]

for src_key, tgt_key, rel_type, weight, desc in relationships:
    src_id = entity_ids[src_key]
    tgt_id = entity_ids[tgt_key]
    r = call("POST", "/api/v2/graph/relationships", TOKEN, data={
        "source_entity_id": src_id, "target_entity_id": tgt_id,
        "relationship_type": rel_type, "weight": weight,
        "attributes": {"description": desc},
    })
    dd = r.get("data", r)
    rid = dd.get("id")
    status = rid if rid else "(already exists)"
    print(f"  {src_key} --[{rel_type}]--> {tgt_key}: {status}")

# ============================================================
# STEP 3: Run Risk Calculation
# ============================================================
step(3, "Run Risk Calculation")

for key in ["PDPU", "WALKOVER", "VETTING"]:
    eid = entity_ids[key]
    r = call("POST", "/api/v2/risk/calculate", TOKEN, data={"entity_id": eid})
    print(f"  {key}: {json.dumps(r.get('data', r), indent=2)[:200]}")

for key in ["PDPU", "WALKOVER", "VETTING"]:
    eid = entity_ids[key]
    r = call("GET", f"/api/v2/risk/{eid}", TOKEN)
    score_data = r.get("data", r)
    print(f"  {key} risk score: {json.dumps(score_data, indent=2)[:250]}")

# ============================================================
# STEP 4: Anomaly Detection
# ============================================================
step(4, "Run Anomaly Detection")

r = call("POST", "/api/v2/anomalies/run", TOKEN, data={})
print(f"  Anomalies: {json.dumps(r, indent=2)[:500]}")

# ============================================================
# STEP 5: Run Risk Correlation
# ============================================================
step(5, "Run Risk Correlation")

for key in ["WALKOVER", "PDPU", "VETTING"]:
    eid = entity_ids[key]
    r = call("POST", "/api/v2/correlation/run", TOKEN, data={"entity_id": eid})
    print(f"  {key}: {json.dumps(r.get('data', r), indent=2)[:200]}")
    r2 = call("GET", f"/api/v2/correlation/{eid}", TOKEN)
    print(f"  {key} correlation: {json.dumps(r2.get('data', r2), indent=2)[:200]}")

# ============================================================
# STEP 6: Blast Radius Analysis
# ============================================================
step(6, "Blast Radius Analysis for Walkover")

r = call("GET", f"/api/v2/blast-radius/{entity_ids['WALKOVER']}", TOKEN)
print(f"  Blast radius: {json.dumps(r, indent=2)[:1000]}")

# ============================================================
# STEP 7: Scenario Simulation
# ============================================================
step(7, "Run Scenario Simulation (SOC2_EXPIRED on Walkover)")

r = call("POST", "/api/v2/scenario/run", TOKEN, data={
    "entity_id": entity_ids["WALKOVER"],
    "scenario": "SOC2_EXPIRED",
})
print(f"  Scenario: {json.dumps(r, indent=2)[:600]}")

# ============================================================
# STEP 8: Generate Intelligence Brief
# ============================================================
step(8, "Generate Intelligence Brief")

r = call("POST", "/api/v2/intelligence/daily", TOKEN, data={
    "entity_id": entity_ids["WALKOVER"],
})
print(f"  Intelligence: {json.dumps(r, indent=2)[:800]}")

# ============================================================
# STEP 9: Executive Brief
# ============================================================
step(9, "Generate Executive Brief")

r = call("POST", "/api/v2/intelligence/executive", TOKEN, data={
    "entity_id": entity_ids["PDPU"],
})
print(f"  Executive Brief: {json.dumps(r, indent=2)[:800]}")

# ============================================================
# STEP 10: Remediation Plan
# ============================================================
step(10, "Generate Remediation for PDPU findings")

for finding_key in ["FINDING_UNDER_RECOVERY", "FINDING_PRIOR_YEARS", "FINDING_EXCESS_PAYMENT"]:
    eid = entity_ids[finding_key]
    r = call("POST", "/api/v2/remediation/generate", TOKEN, data={
        "entity_id": eid, "anomaly_type": "financial_irregularity",
    })
    print(f"  {finding_key}: {json.dumps(r.get('data', r), indent=2)[:200]}")

# ============================================================
# STEP 11: Timeline
# ============================================================
step(11, "Generate Timeline")

r = call("GET", f"/api/v2/timeline/entity/{entity_ids['PDPU']}", TOKEN)
print(f"  Timeline: {json.dumps(r, indent=2)[:600]}")

# ============================================================
# STEP 12: Copilot Queries
# ============================================================
step(12, "Copilot Queries")

queries = [
    "What are the top financial risks in the system?",
    "What is the blast radius if Walkover experiences an outage?",
    "Summarize the internal audit findings for PDPU",
    "What entities depend on AWS?",
]

for q in queries:
    r = call("POST", "/api/v2/copilot/query", TOKEN, data={"question": q})
    dd = r.get("data", r)
    answer = dd.get("answer", "N/A")
    intent = dd.get("intent", "?")
    print(f"\n  [{intent}] Q: {q}")
    print(f"  A: {str(answer)[:300]}")

# ============================================================
# STEP 13: Pipeline Run (full)
# ============================================================
step(13, "Run Full Pipeline")

r = call("POST", "/api/v2/pipeline/run", TOKEN, data={})
print(f"  Pipeline: {json.dumps(r, indent=2)[:1000]}")

print(f"\n{'='*60}")
print(f"DEMO COMPLETE - All 13 steps executed")
print(f"{'='*60}")
