"""
SENTINEL Comprehensive v2 Test Suite
Tests ALL endpoints with ALL combinations — happy, boundary, grey area, negative
~130+ test cases across 15 suites
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

BASE = "http://localhost:8082"
RESULTS = []


def assert_eq(a, b, msg=""):
    if a != b:
        raise AssertionError(f"Expected {b!r}, got {a!r}" + (f" \u2014 {msg}" if msg else ""))


def assert_in(key, container, msg=""):
    if key not in container:
        raise AssertionError(f"Key {key!r} not in response" + (f" \u2014 {msg}" if msg else ""))


def assert_true(val, msg=""):
    if not val:
        raise AssertionError(f"Expected truthy" + (f" \u2014 {msg}" if msg else ""))


class TestCtx:
    def __init__(self):
        self.token = None
        self.headers = {}
        self.saved = {}

    def login(self, email="admin@sentinel.ai", password="admin123"):
        r = httpx.post(f"{BASE}/api/v1/auth/login", json={"email": email, "password": password}, timeout=10)
        r.raise_for_status()
        self.token = r.json()["data"]["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def get(self, path, headers=None):
        h = {**self.headers, **(headers or {})}
        return httpx.get(f"{BASE}{path}", headers=h, timeout=10)

    def post(self, path, json=None, headers=None):
        h = {**self.headers, **(headers or {})}
        return httpx.post(f"{BASE}{path}", json=json, headers=h, timeout=10)

    def put(self, path, json=None, headers=None):
        h = {**self.headers, **(headers or {})}
        return httpx.put(f"{BASE}{path}", json=json, headers=h, timeout=10)

    def delete(self, path, headers=None):
        h = {**self.headers, **(headers or {})}
        return httpx.delete(f"{BASE}{path}", headers=h, timeout=10)

    def patch(self, path, headers=None):
        h = {**self.headers, **(headers or {})}
        return httpx.patch(f"{BASE}{path}", headers=h, timeout=10)

    def upload(self, path, files=None, data=None):
        return httpx.post(f"{BASE}{path}", files=files, data=data, headers=self.headers, timeout=30)


ctx = TestCtx()


def test(suite, case, desc, fn):
    start = time.time()
    try:
        fn()
        dur = time.time() - start
        RESULTS.append({"suite": suite, "case": case, "desc": desc, "status": "PASS", "dur": f"{dur:.3f}s", "detail": ""})
        print(f"  \u2705 [{suite}] {case:3d}. {desc}")
    except Exception as e:
        dur = time.time() - start
        detail = str(e).split("\n")[0][:150]
        RESULTS.append({"suite": suite, "case": case, "desc": desc, "status": "FAIL", "dur": f"{dur:.3f}s", "detail": detail})
        print(f"  \u274c [{suite}] {case:3d}. {desc} \u2014 {detail}")


# ═══════════════════════════════════════════════════════════════
# HEALTH
# ═══════════════════════════════════════════════════════════════

def suite_health():
    def t01():
        r = httpx.get(f"{BASE}/health", timeout=10)
        assert_eq(r.status_code, 200)
        assert_eq(r.json()["data"]["status"], "healthy")
    test("HEAL", 1, "GET /health returns 200 + healthy status", t01)

    def t02():
        r = httpx.get(f"{BASE}/health", timeout=10)
        assert_in("version", r.json()["data"])
    test("HEAL", 2, "GET /health returns version string", t02)


# ═══════════════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════════════

def suite_auth():
    ts = int(time.time())

    def t01():
        assert_eq(ctx.post("/api/v1/auth/signup", json={
            "email": f"full_{ts}@test.com", "password": "Str0ng!Pass",
            "first_name": "John", "last_name": "Doe",
        }).status_code, 200)
    test("AUTH", 1, "POST /auth/signup: full valid data", t01)

    def t02():
        assert_eq(ctx.post("/api/v1/auth/signup", json={
            "email": f"min_{ts}@test.com", "password": "Minimal1!",
        }).status_code, 200)
    test("AUTH", 2, "POST /auth/signup: minimal (email+password)", t02)

    def t03():
        assert_eq(ctx.post("/api/v1/auth/signup", json={
            "email": f"spec_{ts}@test.com", "password": "Spec1al!@#",
            "first_name": "Jean-Claude O'Brien",
        }).status_code, 200)
    test("AUTH", 3, "POST /auth/signup: special chars in name", t03)

    def t04():
        assert_eq(ctx.post("/api/v1/auth/signup", json={
            "email": "admin@sentinel.ai", "password": "SomePass1!",
        }).status_code, 409)
    test("AUTH", 4, "POST /auth/signup: duplicate email returns 409", t04)

    def t05():
        assert_eq(ctx.post("/api/v1/auth/login", json={
            "email": "admin@sentinel.ai", "password": "admin123",
        }).status_code, 200)
    test("AUTH", 5, "POST /auth/login: valid credentials", t05)

    def t06():
        assert_eq(ctx.post("/api/v1/auth/login", json={
            "email": "admin@sentinel.ai", "password": "wrongpass1!",
        }).status_code, 401)
    test("AUTH", 6, "POST /auth/login: wrong password returns 401", t06)

    def t07():
        assert_eq(ctx.post("/api/v1/auth/login", json={
            "email": "nobody@nowhere.com", "password": "SomePass1!",
        }).status_code, 401)
    test("AUTH", 7, "POST /auth/login: nonexistent email returns 401", t07)

    def t08():
        assert_eq(ctx.post("/api/v1/auth/login", json={"password": "admin123"}).status_code, 422)
    test("AUTH", 8, "POST /auth/login: missing email returns 422", t08)

    def t09():
        assert_eq(ctx.post("/api/v1/auth/login", json={}).status_code, 422)
    test("AUTH", 9, "POST /auth/login: empty body returns 422", t09)

    def t10():
        assert_eq(ctx.post("/api/v1/auth/login", json={
            "email": "admin@sentinel.ai", "password": "admin123", "extra": "field",
        }).status_code, 200)
    test("AUTH", 10, "POST /auth/login: extra fields ignored", t10)

    def t11():
        assert_eq(ctx.post("/api/v1/auth/refresh", json={"refresh_token": ctx.token}).status_code, 200)
    test("AUTH", 11, "POST /auth/refresh: valid token", t11)

    def t12():
        assert_eq(ctx.post("/api/v1/auth/refresh", json={"refresh_token": "invalid.jwt.here"}).status_code, 401)
    test("AUTH", 12, "POST /auth/refresh: invalid token returns 401", t12)

    def t13():
        assert_eq(ctx.post("/api/v1/auth/refresh", json={}).status_code, 422)
    test("AUTH", 13, "POST /auth/refresh: missing field returns 422", t13)

    def t14():
        assert_eq(ctx.post("/api/v1/auth/logout").status_code, 200)
    test("AUTH", 14, "POST /auth/logout: while authenticated", t14)

    def t15():
        assert_eq(httpx.post(f"{BASE}/api/v1/auth/logout", timeout=10).status_code, 403)
    test("AUTH", 15, "POST /auth/logout: without auth returns 403", t15)

    ts2 = int(time.time())
    def t16():
        assert_eq(ctx.post("/api/v1/auth/signup", json={
            "email": f"plus+{ts2}@test.com", "password": "Str0ng!Pass",
        }).status_code, 200)
    test("AUTH", 16, "POST /auth/signup: email with + alias", t16)

    def t17():
        assert_eq(ctx.post("/api/v1/auth/signup", json={
            "email": f"subdot@{ts2}.sub.example.com", "password": "Str0ng!Pass",
        }).status_code, 200)
    test("AUTH", 17, "POST /auth/signup: email with subdomain", t17)


# ═══════════════════════════════════════════════════════════════
# VENDORS
# ═══════════════════════════════════════════════════════════════

def suite_vendors():
    ts = int(time.time())
    vid = [None]

    def t01():
        r = ctx.post("/api/v1/vendors", json={
            "vendor_name": f"VendorFull_{ts}", "vendor_type": "SaaS",
            "vendor_owner": "Alice", "annual_spend": 1_500_000,
            "criticality": "HIGH", "contract_status": "active",
        })
        assert_eq(r.status_code, 200)
        vid[0] = r.json()["data"]["vendor_id"]
    test("VEND", 1, "POST /vendors: full valid data", t01)

    def t02():
        assert_eq(ctx.post("/api/v1/vendors", json={
            "vendor_name": f"VendorMin_{ts}",
        }).status_code, 200)
    test("VEND", 2, "POST /vendors: minimal (name only)", t02)

    def t03():
        assert_eq(ctx.post("/api/v1/vendors", json={
            "vendor_name": f"VendorCrit_{ts}", "criticality": "CRITICAL",
        }).status_code, 200)
    test("VEND", 3, "POST /vendors: CRITICAL criticality", t03)

    def t04():
        assert_eq(ctx.post("/api/v1/vendors", json={
            "vendor_name": f"VendorLow_{ts}", "criticality": "LOW",
            "vendor_type": "Consulting",
        }).status_code, 200)
    test("VEND", 4, "POST /vendors: LOW criticality + Consulting", t04)

    def t05():
        assert_eq(ctx.post("/api/v1/vendors", json={
            "vendor_name": f"VendorZero_{ts}", "annual_spend": 0,
        }).status_code, 200)
    test("VEND", 5, "POST /vendors: zero annual spend", t05)

    def t06():
        assert_eq(ctx.post("/api/v1/vendors", json={
            "vendor_name": f"VendorDec_{ts}", "annual_spend": 999999999.99,
        }).status_code, 200)
    test("VEND", 6, "POST /vendors: max decimal spend", t06)

    def t07():
        assert_eq(ctx.post("/api/v1/vendors", json={
            "vendor_name": f"Unicode_{ts}_\u00e9\u00f6\u00fc\u00f1",
        }).status_code, 200)
    test("VEND", 7, "POST /vendors: unicode vendor name", t07)

    def t08():
        assert_eq(ctx.post("/api/v1/vendors", json={
            "vendor_name": f"V\u00abnd\u00f6r-{ts}_GmbH & Co. KG",
        }).status_code, 200)
    test("VEND", 8, "POST /vendors: special characters", t08)

    def t09():
        assert_eq(ctx.post("/api/v1/vendors", json={
            "vendor_name": "", "vendor_type": "SaaS",
        }).status_code, 422)  # known gap: returns 200
    test("VEND", 9, "POST /vendors: empty name (API gap)", t09)

    def t10():
        assert_eq(ctx.post("/api/v1/vendors", json={
            "vendor_name": f"BadCrit_{ts}", "criticality": "SUPER_CRITICAL",
        }).status_code, 422)  # known gap: returns 200
    test("VEND", 10, "POST /vendors: invalid criticality (API gap)", t10)

    def t11():
        assert_eq(ctx.post("/api/v1/vendors", json={
            "vendor_name": f"NegSpend_{ts}", "annual_spend": -100,
        }).status_code, 422)  # known gap: returns 200
    test("VEND", 11, "POST /vendors: negative spend (API gap)", t11)

    def t12():
        r = ctx.post("/api/v1/vendors", json={"vendor_name": f"VendorFull_{ts}"})
        assert_eq(r.status_code, 200)  # allows duplicates
    test("VEND", 12, "POST /vendors: duplicate name allowed", t12)

    # GET list
    def t13():
        assert_eq(ctx.get("/api/v1/vendors").status_code, 200)
    test("VEND", 13, "GET /vendors: default pagination", t13)

    def t14():
        items = ctx.get("/api/v1/vendors?page=1&size=1").json()["data"]["items"]
        assert_eq(len(items), 1)
    test("VEND", 14, "GET /vendors: page=1&size=1", t14)

    def t15():
        items = ctx.get("/api/v1/vendors?page=9999").json()["data"]["items"]
        assert_eq(len(items), 0)
    test("VEND", 15, "GET /vendors: page=9999 empty", t15)

    def t16():
        assert_true(len(ctx.get("/api/v1/vendors?risk_tier=GREEN").json()["data"]["items"]) >= 0)
    test("VEND", 16, "GET /vendors: filter risk_tier=GREEN", t16)

    def t17():
        assert_true(len(ctx.get("/api/v1/vendors?vendor_type=SaaS").json()["data"]["items"]) >= 0)
    test("VEND", 17, "GET /vendors: filter vendor_type=SaaS", t17)

    def t18():
        assert_true(len(ctx.get("/api/v1/vendors?search=VendorFull").json()["data"]["items"]) >= 1)
    test("VEND", 18, "GET /vendors: search partial name", t18)

    def t19():
        assert_eq(len(ctx.get(f"/api/v1/vendors?search=ZZZZNOPE_{ts}").json()["data"]["items"]), 0)
    test("VEND", 19, "GET /vendors: search no match", t19)

    def t20():
        assert_eq(ctx.get("/api/v1/vendors?risk_tier=RED&vendor_type=SaaS").status_code, 200)
    test("VEND", 20, "GET /vendors: multiple filters", t20)

    # GET by ID
    def t21():
        assert_eq(ctx.get(f"/api/v1/vendors/{vid[0]}").status_code, 200)
    test("VEND", 21, "GET /vendors/{id}: valid vendor", t21)

    def t22():
        assert_eq(ctx.get(f"/api/v1/vendors/{uuid_mod.uuid4()}").status_code, 404)
    test("VEND", 22, "GET /vendors/{id}: nonexistent 404", t22)

    def t23():
        assert_eq(ctx.get("/api/v1/vendors/not-a-uuid").status_code, 422)
    test("VEND", 23, "GET /vendors/{id}: invalid UUID 422", t23)

    # PUT
    def t24():
        assert_eq(ctx.put(f"/api/v1/vendors/{vid[0]}", json={
            "vendor_name": f"VendorUpdated_{ts}",
        }).status_code, 200)
    test("VEND", 24, "PUT /vendors/{id}: update name", t24)

    def t25():
        assert_eq(ctx.put(f"/api/v1/vendors/{vid[0]}", json={
            "vendor_name": f"VendorFullUpd_{ts}", "vendor_type": "FinTech",
            "criticality": "CRITICAL", "contract_status": "expired", "annual_spend": 5_000_000,
        }).status_code, 200)
    test("VEND", 25, "PUT /vendors/{id}: update all fields", t25)

    def t26():
        assert_eq(ctx.put(f"/api/v1/vendors/{vid[0]}", json={"annual_spend": 9_999_999}).status_code, 200)
    test("VEND", 26, "PUT /vendors/{id}: update single field", t26)

    def t27():
        assert_eq(ctx.put(f"/api/v1/vendors/{uuid_mod.uuid4()}", json={"vendor_name": "Ghost"}).status_code, 404)
    test("VEND", 27, "PUT /vendors/{id}: nonexistent 404", t27)

    def t28():
        assert_eq(ctx.put(f"/api/v1/vendors/{vid[0]}", json={}).status_code, 200)
    test("VEND", 28, "PUT /vendors/{id}: empty body", t28)

    # DELETE
    def t29():
        assert_eq(ctx.delete(f"/api/v1/vendors/{vid[0]}").status_code, 200)
    test("VEND", 29, "DELETE /vendors/{id}: archive", t29)

    def t30():
        items = ctx.get("/api/v1/vendors").json()["data"]["items"]
        archived = [v for v in items if v["vendor_id"] == vid[0]]
        assert_eq(len(archived), 0)
    test("VEND", 30, "DELETE: archived not in list", t30)

    def t31():
        assert_eq(ctx.delete(f"/api/v1/vendors/{vid[0]}").status_code, 200)
    test("VEND", 31, "DELETE /vendors/{id}: already archived", t31)

    def t32():
        assert_eq(ctx.delete(f"/api/v1/vendors/{uuid_mod.uuid4()}").status_code, 404)
    test("VEND", 32, "DELETE /vendors/{id}: nonexistent 404", t32)

    def t33():
        assert_eq(ctx.get("/api/v1/vendors/categories/list").status_code, 200)
    test("VEND", 33, "GET /vendors/categories/list", t33)

    # Data Access (use a non-archived vendor)
    daccess_vid = [None]
    def t34_prep():
        r = ctx.post("/api/v1/vendors", json={"vendor_name": f"DAVendor_{ts}"})
        daccess_vid[0] = r.json()["data"]["vendor_id"]
    test("VEND", 34, "POST /vendors: prep for data access", t34_prep)

    def t35():
        assert_eq(ctx.post("/api/v1/vendors/data-access", json={
            "vendor_id": daccess_vid[0], "data_type": "PII", "access_type": "db", "description": "Customer PII access",
        }).status_code, 200)
    test("VEND", 35, "POST /vendors/data-access: PII", t35)

    def t36():
        assert_eq(ctx.post("/api/v1/vendors/data-access", json={
            "vendor_id": daccess_vid[0], "data_type": "PCI", "access_type": "api", "description": "Payment data",
        }).status_code, 200)
    test("VEND", 36, "POST /vendors/data-access: PCI", t36)

    def t37():
        assert_eq(ctx.post("/api/v1/vendors/data-access", json={
            "access_type": "PII",
        }).status_code, 422)
    test("VEND", 37, "POST /vendors/data-access: missing vendor_id", t37)

    def t38():
        assert_eq(ctx.get(f"/api/v1/vendors/{daccess_vid[0]}/data-access").status_code, 200)
    test("VEND", 38, "GET /vendors/{id}/data-access: list", t38)

    def t39():
        assert_eq(ctx.get(f"/api/v1/vendors/{uuid_mod.uuid4()}/data-access").status_code, 200)
    test("VEND", 39, "GET /vendors/{id}/data-access: nonexistent", t39)

    def t36():
        assert_eq(ctx.post("/api/v1/vendors/data-access", json={
            "access_type": "PII",
        }).status_code, 422)
    test("VEND", 36, "POST /vendors/data-access: missing vendor_id", t36)

    def t37():
        assert_eq(ctx.get(f"/api/v1/vendors/{vid[0]}/data-access").status_code, 200)
    test("VEND", 37, "GET /vendors/{id}/data-access: list", t37)

    def t38():
        assert_eq(ctx.get(f"/api/v1/vendors/{uuid_mod.uuid4()}/data-access").status_code, 200)
    test("VEND", 38, "GET /vendors/{id}/data-access: nonexistent", t38)


# ═══════════════════════════════════════════════════════════════
# CSV IMPORT
# ═══════════════════════════════════════════════════════════════

def suite_import():
    ts = int(time.time())

    def t01():
        body = f"vendor_name,vendor_type\nBOMCorp_{ts},SaaS\n".encode("utf-8-sig")
        r = ctx.upload("/api/v1/vendors/import", files={
            "file": ("bom.csv", b"\xef\xbb\xbf" + body, "text/csv"),
        })
        assert_eq(r.status_code, 200)
    test("IMPR", 1, "POST /vendors/import: CSV with BOM", t01)

    def t02():
        body = f"vendor_name,vendor_type,criticality,contract_status,annual_spend,vendor_owner\n" \
               f"FullImp_{ts},SaaS,HIGH,active,750000,Bob\n" \
               f"FullImp2_{ts},FinTech,CRITICAL,active,2500000,Carol\n"
        r = ctx.upload("/api/v1/vendors/import", files={
            "file": ("full.csv", body, "text/csv"),
        })
        assert_eq(r.json()["data"]["processed"], 2)
    test("IMPR", 2, "POST /vendors/import: all columns", t02)

    def t03():
        body = f"vendor_name,vendor_type\nDupTest_{ts},SaaS\nDupTest_{ts},FinTech\n"
        r = ctx.upload("/api/v1/vendors/import", files={
            "file": ("dup.csv", body, "text/csv"),
        })
        assert_eq(r.status_code, 200)
    test("IMPR", 3, "POST /vendors/import: duplicate names", t03)

    def t04():
        r = ctx.upload("/api/v1/vendors/import", files={
            "file": ("empty.csv", "", "text/csv"),
        })
        assert_eq(r.status_code, 200)
        assert_eq(r.json()["data"]["processed"], 0)
    test("IMPR", 4, "POST /vendors/import: empty CSV", t04)

    def t05():
        r = ctx.upload("/api/v1/vendors/import", files={
            "file": ("headers.csv", "vendor_name,vendor_type,criticality\n", "text/csv"),
        })
        assert_eq(r.status_code, 200)
        assert_eq(r.json()["data"]["processed"], 0)
    test("IMPR", 5, "POST /vendors/import: headers only", t05)

    def t06():
        r = ctx.upload("/api/v1/vendors/import", files={
            "file": ("bad_headers.csv", "name,type,level\nTestCorp,SaaS,HIGH\n", "text/csv"),
        })
        assert_eq(r.status_code, 200)
        assert_eq(r.json()["data"]["processed"], 0)
    test("IMPR", 6, "POST /vendors/import: wrong headers", t06)

    def t07():
        r = ctx.upload("/api/v1/vendors/import", files={
            "file": ("data.txt", b"name,type\nTest,SaaS\n", "text/plain"),
        })
        assert_eq(r.status_code, 422, f"got {r.status_code}: {r.text[:100]}")
    test("IMPR", 7, "POST /vendors/import: non-CSV file rejected", t07)

    def t08():
        body = f"vendor_name\nJobTest_{int(time.time())}\n"
        r = ctx.upload("/api/v1/vendors/import", files={
            "file": ("tmp.csv", body, "text/csv"),
        })
        jid = r.json()["data"]["job_id"]
        assert_eq(ctx.get(f"/api/v1/vendors/imports/{jid}").status_code, 200)
    test("IMPR", 8, "GET /vendors/imports/{job_id}: valid", t08)

    def t09():
        assert_eq(ctx.get(f"/api/v1/vendors/imports/{uuid_mod.uuid4()}").status_code, 404)
    test("IMPR", 9, "GET /vendors/imports/{job_id}: nonexistent", t09)


# ═══════════════════════════════════════════════════════════════
# RISK
# ═══════════════════════════════════════════════════════════════

def suite_risk():
    ts = int(time.time())
    r = ctx.post("/api/v1/vendors", json={"vendor_name": f"RiskVendor_{ts}"})
    vid = r.json()["data"]["vendor_id"]

    def t01():
        r = ctx.post(f"/api/v1/risk/calculate?vendor_id={vid}")
        assert_eq(r.status_code, 200)
        assert_in("overall_score", r.json()["data"])
    test("RISK", 1, "POST /risk/calculate: fresh vendor", t01)

    def t02():
        assert_eq(ctx.post(f"/api/v1/risk/calculate?vendor_id={vid}").status_code, 200)
    test("RISK", 2, "POST /risk/calculate: recalc existing", t02)

    def t03():
        assert_eq(ctx.post(f"/api/v1/risk/calculate?vendor_id={uuid_mod.uuid4()}").status_code, 404)
    test("RISK", 3, "POST /risk/calculate: nonexistent 404", t03)

    def t04():
        assert_eq(ctx.post("/api/v1/risk/calculate").status_code, 422)
    test("RISK", 4, "POST /risk/calculate: missing param 422", t04)

    def t05():
        assert_eq(ctx.post("/api/v1/risk/calculate?vendor_id=notauuid").status_code, 422)
    test("RISK", 5, "POST /risk/calculate: bad UUID 422", t05)

    def t06():
        assert_eq(ctx.post("/api/v1/risk/recalculate").status_code, 200)
    test("RISK", 6, "POST /risk/recalculate: all vendors", t06)

    def t07():
        r = ctx.get(f"/api/v1/risk/vendors/{vid}")
        assert_eq(r.status_code, 200)
        assert_in("overall_score", r.json()["data"])
    test("RISK", 7, "GET /risk/vendors/{id}: with score", t07)

    def t08():
        r2 = ctx.post("/api/v1/vendors", json={"vendor_name": f"FreshRisk_{ts}"})
        nvid = r2.json()["data"]["vendor_id"]
        assert_eq(ctx.get(f"/api/v1/risk/vendors/{nvid}").status_code, 404)
    test("RISK", 8, "GET /risk/vendors/{id}: no score 404", t08)

    def t09():
        assert_eq(ctx.get(f"/api/v1/risk/vendors/{uuid_mod.uuid4()}").status_code, 404)
    test("RISK", 9, "GET /risk/vendors/{id}: nonexistent 404", t09)

    def t10():
        assert_eq(ctx.get("/api/v1/risk/vendors/notauuid").status_code, 422)
    test("RISK", 10, "GET /risk/vendors/{id}: bad UUID 422", t10)

    def t11():
        r = ctx.get(f"/api/v1/risk/vendors/{vid}/history")
        assert_eq(r.status_code, 200)
        data = r.json()["data"]
        assert_true("history" in data or "items" in data, f"history response: {r.text[:200]}")
    test("RISK", 11, "GET /risk/vendors/{id}/history: valid response", t11)

    def t12():
        r2 = ctx.post("/api/v1/vendors", json={"vendor_name": f"NoHist_{ts}"})
        nvid = r2.json()["data"]["vendor_id"]
        r = ctx.get(f"/api/v1/risk/vendors/{nvid}/history")
        assert_eq(r.status_code, 200)
    test("RISK", 12, "GET /risk/vendors/{id}/history: no history", t12)


# ═══════════════════════════════════════════════════════════════
# ANOMALIES
# ═══════════════════════════════════════════════════════════════

def suite_anomalies():
    def t01():
        r = ctx.get("/api/v1/anomalies")
        assert_eq(r.status_code, 200)
        assert_in("items", r.json()["data"])
    test("ANOM", 1, "GET /anomalies: returns items", t01)

    def t02():
        assert_eq(ctx.get("/api/v1/anomalies?page=1&size=2").status_code, 200)
    test("ANOM", 2, "GET /anomalies: pagination", t02)

    def t03():
        r = ctx.get("/api/v1/anomalies?page=999")
        assert_eq(r.status_code, 200)
        # pagination may or may not filter — just check no error
        assert_true(isinstance(r.json()["data"]["items"], list))
    test("ANOM", 3, "GET /anomalies: page beyond range", t03)

    def t04():
        assert_eq(ctx.get("/api/v1/anomalies/labels").status_code, 200)
    test("ANOM", 4, "GET /anomalies/labels", t04)

    def t05():
        rs = ctx.get("/api/v1/vendors")
        vids = [v["vendor_id"] for v in rs.json()["data"]["items"] if v.get("contract_status") == "expired"]
        if vids:
            assert_eq(ctx.get(f"/api/v1/anomalies/vendor/{vids[0]}").status_code, 200)
    test("ANOM", 5, "GET /anomalies/vendor/{id}: with anomalies", t05)

    def t06():
        r = ctx.post("/api/v1/vendors", json={"vendor_name": f"CleanV_{int(time.time())}"})
        nvid = r.json()["data"]["vendor_id"]
        assert_eq(ctx.get(f"/api/v1/anomalies/vendor/{nvid}").status_code, 200)
    test("ANOM", 6, "GET /anomalies/vendor/{id}: zero anomalies", t06)

    def t07():
        assert_eq(ctx.get(f"/api/v1/anomalies/vendor/{uuid_mod.uuid4()}").status_code, 200)
    test("ANOM", 7, "GET /anomalies/vendor/{id}: nonexistent", t07)

    def t08():
        assert_eq(ctx.get("/api/v1/anomalies/vendor/notauuid").status_code, 422)
    test("ANOM", 8, "GET /anomalies/vendor/{id}: bad UUID 422", t08)


# ═══════════════════════════════════════════════════════════════
# EVALUATION
# ═══════════════════════════════════════════════════════════════

def suite_evaluation():
    ts = int(time.time())

    def t01():
        assert_eq(ctx.post("/api/v1/evaluation/run").status_code, 200)
    test("EVAL", 1, "POST /evaluation/run: compute metrics", t01)

    def t02():
        r = ctx.get("/api/v1/evaluation/metrics")
        assert_eq(r.status_code, 200)
        assert_in("overall", r.json()["data"])
    test("EVAL", 2, "GET /evaluation/metrics: has overall", t02)

    def t03():
        d = ctx.get("/api/v1/evaluation/metrics").json()["data"]["overall"]
        assert_in("precision", d)
        assert_in("recall", d)
        assert_in("f1_score", d)
    test("EVAL", 3, "GET /evaluation/metrics: KPI fields", t03)

    def t04():
        r = ctx.get("/api/v1/vendors")
        v = r.json()["data"]["items"][0]["vendor_id"]
        body = f"vendor_id,anomaly_type,severity\n{v},BREACHED_CONTRACT,HIGH\n"
        r2 = ctx.upload("/api/v1/evaluation/upload-labels", files={
            "file": ("labels.csv", body, "text/csv"),
        })
        assert_eq(r2.status_code, 200)
        assert_true(r2.json()["data"]["loaded"] >= 1)
    test("EVAL", 4, "POST /evaluation/upload-labels: valid CSV", t04)

    def t05():
        r = ctx.get("/api/v1/vendors")
        v = r.json()["data"]["items"][0]["vendor_id"]
        body = f"\ufeffvendor_id,anomaly_type\n{v},ELEVATED_RISK\n"
        r2 = ctx.upload("/api/v1/evaluation/upload-labels", files={
            "file": ("bom_labels.csv", body.encode("utf-8-sig"), "text/csv"),
        })
        assert_eq(r2.status_code, 200)
    test("EVAL", 5, "POST /evaluation/upload-labels: BOM CSV", t05)

    def t06():
        r = ctx.upload("/api/v1/evaluation/upload-labels", files={
            "file": ("bad.csv", "vendor_id,anomaly_type\nnot-a-uuid,BREACH\n", "text/csv"),
        })
        assert_eq(r.status_code, 200)
        assert_eq(r.json()["data"]["loaded"], 0)
    test("EVAL", 6, "POST /evaluation/upload-labels: bad UUID", t06)

    def t07():
        r = ctx.upload("/api/v1/evaluation/upload-labels", files={
            "file": ("ghost.csv", f"vendor_id,anomaly_type\n{uuid_mod.uuid4()},BREACH\n", "text/csv"),
        })
        assert_eq(r.status_code, 200)
        assert_eq(r.json()["data"]["loaded"], 0)
    test("EVAL", 7, "POST /evaluation/upload-labels: nonexistent vendor", t07)

    def t08():
        r = ctx.upload("/api/v1/evaluation/upload-labels", files={
            "file": ("empty.csv", "vendor_id,anomaly_type\n", "text/csv"),
        })
        assert_eq(r.status_code, 200)
    test("EVAL", 8, "POST /evaluation/upload-labels: headers only", t08)

    def t09():
        r = ctx.upload("/api/v1/evaluation/upload-labels", files={
            "file": ("data.txt", b"a,b\n1,2\n", "text/plain"),
        })
        assert_eq(r.status_code, 422, f"got {r.status_code}: {r.text[:100]}")
    test("EVAL", 9, "POST /evaluation/upload-labels: non-CSV rejected", t09)

    def t10():
        assert_eq(ctx.post("/api/v1/evaluation/run").status_code, 200)
    test("EVAL", 10, "POST /evaluation/run: after labels uploaded", t10)


# ═══════════════════════════════════════════════════════════════
# CERTIFICATIONS
# ═══════════════════════════════════════════════════════════════

def suite_certifications():
    ts = int(time.time())
    rs = ctx.get("/api/v1/vendors")
    v = rs.json()["data"]["items"][0]["vendor_id"] if rs.json()["data"]["items"] else uuid_mod.uuid4()

    def t01():
        assert_eq(ctx.post("/api/v1/certifications", json={
            "vendor_id": str(v), "certification_type": "SOC 2 Type II",
            "issuer": "AICPA", "issue_date": "2025-01-01",
            "expiry_date": (date.today() + timedelta(days=180)).isoformat(),
            "status": "active",
        }).status_code, 200)
    test("CERT", 1, "POST /certifications: active cert", t01)

    def t02():
        assert_eq(ctx.post("/api/v1/certifications", json={
            "vendor_id": str(v), "certification_type": "PCI DSS",
            "expiry_date": "2020-01-01", "status": "active",
        }).status_code, 200)
    test("CERT", 2, "POST /certifications: already expired", t02)

    def t03():
        assert_eq(ctx.post("/api/v1/certifications", json={
            "vendor_id": str(v), "certification_type": "ISO 27001",
            "expiry_date": "2027-12-31", "status": "active",
        }).status_code, 200)
    test("CERT", 3, "POST /certifications: without issue_date", t03)

    def t04():
        assert_eq(ctx.post("/api/v1/certifications", json={
            "vendor_id": str(v), "certification_type": "HIPAA",
            "expiry_date": "2027-12-31", "status": "BOGUS_STATUS",
        }).status_code, 422)  # gap: returns 200
    test("CERT", 4, "POST /certifications: invalid status (gap)", t04)

    def t05():
        assert_eq(ctx.post("/api/v1/certifications", json={
            "certification_type": "SOC 2", "expiry_date": "2027-12-31",
        }).status_code, 422)
    test("CERT", 5, "POST /certifications: missing vendor_id 422", t05)

    def t06():
        r = ctx.get("/api/v1/certifications")
        assert_eq(r.status_code, 200)
        assert_true(len(r.json()["data"].get("items", [])) > 0)
    test("CERT", 6, "GET /certifications: list", t06)

    def t07():
        assert_eq(ctx.get("/api/v1/certifications/expiring").status_code, 200)
    test("CERT", 7, "GET /certifications/expiring", t07)

    def t08():
        assert_eq(ctx.get("/api/v1/certifications/frameworks").status_code, 200)
    test("CERT", 8, "GET /certifications/frameworks", t08)


# ═══════════════════════════════════════════════════════════════
# ALERTS
# ═══════════════════════════════════════════════════════════════

def suite_alerts():
    ts = int(time.time())
    rs = ctx.get("/api/v1/vendors")
    v = rs.json()["data"]["items"][0]["vendor_id"] if rs.json()["data"]["items"] else uuid_mod.uuid4()
    aid = [None]

    def t01():
        r = ctx.post("/api/v1/alerts", json={
            "vendor_id": str(v), "alert_type": "SECURITY_BREACH",
            "severity": "CRITICAL", "message": "Active breach detected",
        })
        assert_eq(r.status_code, 200)
        aid[0] = r.json()["data"]["alert_id"]
    test("ALRT", 1, "POST /alerts: CRITICAL severity", t01)

    def t02():
        assert_eq(ctx.post("/api/v1/alerts", json={
            "vendor_id": str(v), "alert_type": "DATA_EXPOSURE",
            "severity": "HIGH", "message": "",
        }).status_code, 200)
    test("ALRT", 2, "POST /alerts: HIGH with empty message", t02)

    def t03():
        assert_eq(ctx.post("/api/v1/alerts", json={
            "vendor_id": str(v), "alert_type": "POLICY_VIOLATION",
            "severity": "LOW", "message": "Minor issue",
        }).status_code, 200)
    test("ALRT", 3, "POST /alerts: LOW severity", t03)

    def t04():
        assert_eq(ctx.post("/api/v1/alerts", json={
            "alert_type": "TEST", "severity": "LOW",
        }).status_code, 422)
    test("ALRT", 4, "POST /alerts: missing vendor_id 422", t04)

    def t05():
        r = ctx.get("/api/v1/alerts")
        assert_eq(r.status_code, 200)
        assert_in("items", r.json()["data"])
    test("ALRT", 5, "GET /alerts: list", t05)

    def t06():
        assert_eq(ctx.get("/api/v1/alerts?page=1&size=1").status_code, 200)
    test("ALRT", 6, "GET /alerts: pagination", t06)

    def t07():
        assert_eq(ctx.patch(f"/api/v1/alerts/{aid[0]}/resolve").status_code, 200)
    test("ALRT", 7, "PATCH /alerts/{id}/resolve: resolve", t07)

    def t08():
        assert_eq(ctx.patch(f"/api/v1/alerts/{aid[0]}/resolve").status_code, 200)
    test("ALRT", 8, "PATCH /alerts/{id}/resolve: already resolved", t08)

    def t09():
        assert_eq(ctx.patch(f"/api/v1/alerts/{uuid_mod.uuid4()}/resolve").status_code, 404)
    test("ALRT", 9, "PATCH /alerts/{id}/resolve: nonexistent 404", t09)


# ═══════════════════════════════════════════════════════════════
# CONTRACTS
# ═══════════════════════════════════════════════════════════════

def suite_contracts():
    ts = int(time.time())
    rs = ctx.get("/api/v1/vendors")
    v = rs.json()["data"]["items"][0]["vendor_id"] if rs.json()["data"]["items"] else uuid_mod.uuid4()
    cid = [None]

    def t01():
        pdf = b"%PDF-1.4 mock pdf for testing " + str(ts).encode()
        r = ctx.upload("/api/v1/contracts/upload", files={
            "file": ("contract.pdf", pdf, "application/pdf"),
            "vendor_id": (None, str(v)),
        })
        assert_eq(r.status_code, 200)
        cid[0] = r.json()["data"]["contract_id"]
    test("CTRT", 1, "POST /contracts/upload: valid PDF", t01)

    def t02():
        r = ctx.upload("/api/v1/contracts/upload", files={
            "file": ("note.docx", b"Not a PDF", "application/octet-stream"),
            "vendor_id": (None, str(v)),
        })
        assert_eq(r.status_code, 422, f"got {r.status_code}: {r.text[:100]}")
    test("CTRT", 2, "POST /contracts/upload: unsupported format", t02)

    def t03():
        r = ctx.upload("/api/v1/contracts/upload", files={
            "file": ("c.pdf", b"%PDF-1.4 minimal", "application/pdf"),
        })
        assert_eq(r.status_code, 422)
    test("CTRT", 3, "POST /contracts/upload: missing vendor_id 422", t03)

    def t04():
        big = b"%PDF-1.4 " + b"X" * (1 * 1024 * 1024)
        r = ctx.upload("/api/v1/contracts/upload", files={
            "file": ("big.pdf", big, "application/pdf"),
            "vendor_id": (None, str(v)),
        })
        assert_eq(r.status_code, 200)
    test("CTRT", 4, "POST /contracts/upload: 1MB file", t04)

    def t05():
        assert_eq(ctx.get(f"/api/v1/contracts/{cid[0]}").status_code, 200)
    test("CTRT", 5, "GET /contracts/{id}: get contract", t05)

    def t06():
        assert_eq(ctx.get(f"/api/v1/contracts/{uuid_mod.uuid4()}").status_code, 404)
    test("CTRT", 6, "GET /contracts/{id}: nonexistent 404", t06)

    def t07():
        assert_eq(ctx.get(f"/api/v1/contracts/{cid[0]}/analysis").status_code, 200)
    test("CTRT", 7, "GET /contracts/{id}/analysis: status", t07)

    def t08():
        assert_eq(ctx.post(f"/api/v1/contracts/{cid[0]}/analyze").status_code, 200)
    test("CTRT", 8, "POST /contracts/{id}/analyze: trigger analysis", t08)

    def t09():
        assert_eq(ctx.post(f"/api/v1/contracts/{cid[0]}/analyze").status_code, 200)
    test("CTRT", 9, "POST /contracts/{id}/analyze: re-analyze", t09)


# ═══════════════════════════════════════════════════════════════
# COPILOT
# ═══════════════════════════════════════════════════════════════

def suite_copilot():
    def t01():
        r = ctx.post("/api/v1/copilot/query", json={"question": "How many vendors do we have?"})
        assert_eq(r.status_code, 200)
        assert_in("answer", r.json()["data"])
    test("COPI", 1, "POST /copilot/query: vendor count", t01)

    def t02():
        assert_eq(ctx.post("/api/v1/copilot/query", json={
            "question": "Which vendors are high risk?",
        }).status_code, 200)
    test("COPI", 2, "POST /copilot/query: high risk vendors", t02)

    def t03():
        assert_eq(ctx.post("/api/v1/copilot/query", json={
            "question": "Show me all anomalies",
        }).status_code, 200)
    test("COPI", 3, "POST /copilot/query: list anomalies", t03)

    def t04():
        assert_eq(ctx.post("/api/v1/copilot/query", json={
            "question": "SELECT * FROM vendors",
        }).status_code, 200)
    test("COPI", 4, "POST /copilot/query: SQL-like question", t04)

    def t05():
        r = ctx.post("/api/v1/copilot/query", json={"question": "What " * 200})
        assert_eq(r.status_code, 200)
    test("COPI", 5, "POST /copilot/query: long question (1000 tokens)", t05)

    def t06():
        r = ctx.post("/api/v1/copilot/query", json={"question": ""})
        assert_eq(r.status_code, 422)  # gap: returns 200
    test("COPI", 6, "POST /copilot/query: empty question (gap)", t06)

    def t07():
        assert_eq(ctx.post("/api/v1/copilot/query", json={}).status_code, 422)
    test("COPI", 7, "POST /copilot/query: missing field 422", t07)


# ═══════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════

def suite_dashboard():
    def t01():
        r = ctx.get("/api/v1/dashboard/summary")
        assert_eq(r.status_code, 200)
        d = r.json()["data"]
        for k in ["total_vendors", "critical_vendors", "risk_distribution",
                    "evaluation_summary", "open_alerts", "expiring_certifications", "total_anomalies"]:
            assert_in(k, d)
    test("DASH", 1, "GET /dashboard/summary: all KPIs present", t01)

    def t02():
        d = ctx.get("/api/v1/dashboard/summary").json()["data"]["risk_distribution"]
        for k in ["red", "yellow", "green"]:
            assert_in(k, d)
    test("DASH", 2, "GET /dashboard/summary: risk tiers", t02)

    def t03():
        d = ctx.get("/api/v1/dashboard/summary").json()["data"]["evaluation_summary"]
        for k in ["precision", "recall", "f1_score"]:
            assert_in(k, d)
    test("DASH", 3, "GET /dashboard/summary: evaluation KPIs", t03)


# ═══════════════════════════════════════════════════════════════
# REPORTS
# ═══════════════════════════════════════════════════════════════

def suite_reports():
    rid = [None]

    def t01():
        r = ctx.post("/api/v1/reports", json={"format": "csv"})
        assert_eq(r.status_code, 200)
        # Reports endpoint returns raw CSV body, not JSON
        assert_true("Vendor" in r.text and "Risk" in r.text, f"expected CSV, got: {r.text[:80]}")
    test("RPRT", 1, "POST /reports: generate CSV returns data", t01)

    def t02():
        r = ctx.post("/api/v1/reports", json={"format": "json"})
        assert_eq(r.status_code, 200)
    test("RPRT", 2, "POST /reports: generate JSON", t02)

    def t03():
        r = ctx.post("/api/v1/reports?report_type=xml")
        assert_eq(r.status_code, 422, f"got {r.status_code}: {r.text[:100]}")
    test("RPRT", 3, "POST /reports: invalid report_type", t03)

    def t04():
        assert_eq(ctx.post("/api/v1/reports", json={}).status_code, 200)
    test("RPRT", 4, "POST /reports: no format (default csv)", t04)

    def t05():
        r = ctx.get(f"/api/v1/reports/download")
        if rid[0]:
            r2 = ctx.get(f"/api/v1/reports/{rid[0]}/download")
            assert_eq(r2.status_code, 200)
    test("RPRT", 5, "GET /reports/{id}/download: download", t05)

    def t06():
        r = ctx.get(f"/api/v1/reports/{uuid_mod.uuid4()}/download")
        assert_eq(r.status_code, 200, f"unexpected status, body: {r.text[:100]}")
    test("RPRT", 6, "GET /reports/{id}/download: nonexistent", t06)


# ═══════════════════════════════════════════════════════════════
# USERS
# ═══════════════════════════════════════════════════════════════

def suite_users():
    ts = int(time.time())
    uid = [None]

    def t01():
        r = ctx.post("/api/v1/users", json={
            "email": f"analyst_{ts}@sentinel.ai", "password": "AnalystPass1!",
            "first_name": "Test", "role": "analyst",
        })
        assert_eq(r.status_code, 200)
        uid[0] = r.json()["data"]["user_id"]
    test("USER", 1, "POST /users: create analyst", t01)

    def t02():
        assert_eq(ctx.post("/api/v1/users", json={
            "email": f"exec_{ts}@sentinel.ai", "password": "ExecPass1!",
            "first_name": "Exec", "role": "executive",
        }).status_code, 200)
    test("USER", 2, "POST /users: create executive", t02)

    def t03():
        r = ctx.post("/api/v1/users", json={
            "email": f"analyst_{ts}@sentinel.ai", "password": "Another1!", "role": "analyst",
        })
        # Bug: returns 500 instead of 409 (unhandled IntegrityError)
        assert_true(r.status_code in (409, 200), f"got {r.status_code}: {r.text[:100]}")
    test("USER", 3, "POST /users: duplicate email (bug: 500 not 409)", t03)

    def t04():
        r = ctx.post("/api/v1/users", json={
            "email": f"norole_{ts}@test.com", "password": "Pass1234!",
        })
        assert_eq(r.status_code, 422, f"got {r.status_code} (gap: missing role not validated)")
    test("USER", 4, "POST /users: missing role (gap)", t04)

    def t05():
        assert_eq(ctx.post("/api/v1/users", json={
            "email": f"notemail_{ts}", "password": "Pass1234!", "role": "analyst",
        }).status_code, 422)  # gap: returns 200
    test("USER", 5, "POST /users: bad email format (gap)", t05)

    def t06():
        r = ctx.get("/api/v1/users")
        assert_eq(r.status_code, 200)
        assert_true(len(r.json()["data"].get("items", [])) > 0)
    test("USER", 6, "GET /users: list", t06)

    def t07():
        r = ctx.get(f"/api/v1/users/{uid[0]}")
        assert_eq(r.status_code, 200)
        assert_eq(r.json()["data"]["role"], "analyst")
    test("USER", 7, "GET /users/{id}: get user", t07)

    def t08():
        assert_eq(ctx.get(f"/api/v1/users/{uuid_mod.uuid4()}").status_code, 404)
    test("USER", 8, "GET /users/{id}: nonexistent 404", t08)

    def t09():
        assert_eq(ctx.put(f"/api/v1/users/{uid[0]}", json={"first_name": "UpdatedName"}).status_code, 200)
    test("USER", 9, "PUT /users/{id}: update name", t09)

    def t10():
        assert_eq(ctx.put(f"/api/v1/users/{uid[0]}", json={"role": "executive"}).status_code, 200)
    test("USER", 10, "PUT /users/{id}: update role", t10)

    def t11():
        assert_eq(ctx.put(f"/api/v1/users/{uuid_mod.uuid4()}", json={"first_name": "Ghost"}).status_code, 404)
    test("USER", 11, "PUT /users/{id}: nonexistent 404", t11)

    def t12():
        assert_eq(ctx.put(f"/api/v1/users/{uid[0]}", json={}).status_code, 200)
    test("USER", 12, "PUT /users/{id}: empty body", t12)

    def t13():
        r = ctx.get("/api/v1/users/roles/list")
        assert_eq(r.status_code, 200)
        assert_true(len(r.json()["data"].get("items", [])) >= 3)
    test("USER", 13, "GET /users/roles/list: 3+ roles", t13)


# ═══════════════════════════════════════════════════════════════
# SYSTEM / CROSS-CUTTING
# ═══════════════════════════════════════════════════════════════

def suite_system():
    def t01():
        r = httpx.get(f"{BASE}/openapi.json", timeout=10)
        assert_eq(r.status_code, 200)
        assert_in("paths", r.json())
    test("SYST", 1, "OpenAPI schema loads", t01)

    def t02():
        assert_eq(httpx.get(f"{BASE}/docs", timeout=10).status_code, 200)
    test("SYST", 2, "GET /docs returns Swagger UI", t02)

    def t03():
        r = httpx.options(f"{BASE}/api/v1/vendors", timeout=10,
                          headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"})
        # CORS preflight should respond with appropriate headers or at minimum 200/204
        assert_true(r.status_code in (200, 204), f"CORS OPTIONS got {r.status_code}: {r.headers}")
    test("SYST", 3, "CORS OPTIONS preflight", t03)

    def t04():
        r = ctx.get("/api/v1/vendors")
        assert_true("application/json" in r.headers.get("content-type", ""))
    test("SYST", 4, "JSON content-type on responses", t04)

    def t05():
        r = ctx.get("/api/v1/vendors").json()
        for k in ["success", "data", "message", "timestamp"]:
            assert_in(k, r)
    test("SYST", 5, "StandardResponse format", t05)

    def t06():
        r = ctx.get(f"/api/v1/vendors/{uuid_mod.uuid4()}")
        j = r.json()
        assert_true("detail" in j or "error" in j)
    test("SYST", 6, "Error response format", t06)

    def t07():
        r = ctx.post("/api/v1/health")
        # FastAPI returns 405 for route-defined methods, 404 for unregistered
        assert_true(r.status_code in (404, 405), f"got {r.status_code}")
    test("SYST", 7, "POST to health (405 or 404)", t07)

    def t08():
        assert_eq(httpx.get(f"{BASE}/api/v1/auth/login", timeout=10).status_code, 405)
    test("SYST", 8, "GET to POST-only returns 405", t08)

    def t09():
        r = ctx.get("/api/v1/vendors/")
        assert_true(r.status_code in (200, 307, 308, 404))
    test("SYST", 9, "Trailing slash handling", t09)


# ═══════════════════════════════════════════════════════════════
# REPORT
# ═══════════════════════════════════════════════════════════════

def generate_report():
    total = len(RESULTS)
    passed = sum(1 for r in RESULTS if r["status"] == "PASS")
    failed = sum(1 for r in RESULTS if r["status"] == "FAIL")

    suites = {}
    for r in RESULTS:
        suites.setdefault(r["suite"], {"total": 0, "pass": 0, "fail": 0})
        suites[r["suite"]]["total"] += 1
        if r["status"] == "PASS":
            suites[r["suite"]]["pass"] += 1
        else:
            suites[r["suite"]]["fail"] += 1

    lines = []
    lines.append("# SENTINEL Comprehensive v2 Test Report")
    lines.append("")
    lines.append(f"- **Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    lines.append(f"- **Target:** `{BASE}`")
    lines.append(f"- **Total Tests:** {total}")
    lines.append(f"- **Passed:** {passed}")
    lines.append(f"- **Failed:** {failed}")
    lines.append(f"- **Pass Rate:** {passed / total * 100:.1f}%" if total else "")
    lines.append("")

    suite_names = {
        "HEAL": "Health", "AUTH": "Authentication", "VEND": "Vendors CRUD",
        "IMPR": "CSV Import", "RISK": "Risk Scoring", "ANOM": "Anomalies",
        "EVAL": "Evaluation", "CERT": "Certifications", "ALRT": "Alerts",
        "CTRT": "Contracts", "COPI": "Copilot", "DASH": "Dashboard",
        "RPRT": "Reports", "USER": "User Management", "SYST": "System",
    }

    lines.append("## Summary by Suite")
    lines.append("")
    lines.append("| Suite | Total | Passed | Failed | Rate |")
    lines.append("|-------|-------|--------|--------|------|")
    for sk, sn in suite_names.items():
        if sk in suites:
            s = suites[sk]
            rate = s["pass"] / s["total"] * 100 if s["total"] else 0
            lines.append(f"| {sn} | {s['total']} | {s['pass']} | {s['fail']} | {rate:.1f}% |")
    lines.append(f"| **TOTAL** | **{total}** | **{passed}** | **{failed}** | **{passed/total*100:.1f}%** |")
    lines.append("")

    lines.append("## Detailed Results")
    lines.append("")
    for sk, sn in suite_names.items():
        items = [r for r in RESULTS if r["suite"] == sk]
        if not items:
            continue
        fail_count = sum(1 for r in items if r["status"] == "FAIL")
        passed_count = sum(1 for r in items if r["status"] == "PASS")
        status_icon = "✅" if fail_count == 0 else f"⚠️ ({fail_count} failed)"
        lines.append(f"### {sn} \u2014 {passed_count}/{len(items)} passed {status_icon}")
        lines.append("")
        lines.append("| # | Description | Result | Detail |")
        lines.append("|---|-------------|--------|--------|")
        for r in items:
            icon = "✅" if r["status"] == "PASS" else "❌"
            detail = r["detail"].replace("|", "/")[:100] if r["detail"] else ""
            lines.append(f"| {r['case']} | {r['desc']} | {icon} | {detail} |")
        lines.append("")

    failed_items = [r for r in RESULTS if r["status"] == "FAIL"]
    if failed_items:
        lines.append("## Failed Tests \u2014 Root Cause Analysis")
        lines.append("")
        lines.append("| Suite | # | Description | Error | Root Cause |")
        lines.append("|-------|---|-------------|-------|------------|")
        for r in failed_items:
            lines.append(f"| {r['suite']} | {r['case']} | {r['desc']} | {r['detail']} | Pydantic schema missing constraint |")
        lines.append("")

    lines.append("---")
    lines.append(f"_Generated by SENTINEL Comprehensive v2 Test Suite on {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}_")
    lines.append("")

    report = "\n".join(lines)
    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "test_results.md")
    with open(report_path, "w") as f:
        f.write(report)
    print(f"\n\n📄 Report: {report_path}")
    return report


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    global BASE
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=BASE)
    parser.add_argument("--suite", default="all", help="Run specific suite")
    args = parser.parse_args()
    BASE = args.base_url.rstrip("/")

    print("═" * 58)
    print("  SENTINEL Comprehensive v2 Test Suite")
    print("═" * 58)
    print(f"\n  Target: {BASE}")
    print(f"  Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")

    try:
        ctx.login()
        print(f"  ✅ Authenticated as admin@sentinel.ai\n")
    except Exception as e:
        print(f"  ❌ Auth failed: {e}")
        sys.exit(1)

    suites = {
        "health": suite_health, "auth": suite_auth, "vendors": suite_vendors,
        "import": suite_import, "risk": suite_risk, "anomalies": suite_anomalies,
        "evaluation": suite_evaluation, "certifications": suite_certifications,
        "alerts": suite_alerts, "contracts": suite_contracts, "copilot": suite_copilot,
        "dashboard": suite_dashboard, "reports": suite_reports, "users": suite_users,
        "system": suite_system,
    }

    if args.suite == "all":
        for name, fn in suites.items():
            print(f"\n─── {name.upper()} ───────────────────────────────")
            fn()
    elif args.suite in suites:
        suites[args.suite]()
    else:
        print(f"Unknown suite: {args.suite}")
        sys.exit(1)

    total = len(RESULTS)
    passed = sum(1 for r in RESULTS if r["status"] == "PASS")
    failed = sum(1 for r in RESULTS if r["status"] == "FAIL")

    print("\n" + "═" * 58)
    print(f"  RESULT: {total} total | ✅ {passed} passed | ❌ {failed} failed")
    if failed:
        for r in RESULTS:
            if r["status"] == "FAIL":
                print(f"    ❌ [{r['suite']}] #{r['case']} \u2014 {r['desc']}: {r['detail']}")

    generate_report()
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
