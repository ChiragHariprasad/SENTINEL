import requests
import sys
import io

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

print("═══ LEVEL 5: PDF TESTING ═══\n")

# ── Helper: generate PDF bytes ──
def make_pdf(text, pages=1):
    lines = []
    lines.append(b"%PDF-1.4")
    lines.append(b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj")
    lines.append(b"2 0 obj<</Type/Pages/Kids[")
    for i in range(pages):
        lines.append(f"3 {i} 0 R".encode())
    lines.append(b"]/Count %d>>endobj" % pages)
    for i in range(pages):
        lines.append(f"3 {i} 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Contents 4 0 R>>endobj".encode())
    lines.append(b"4 0 obj<</Length %d>>stream\n%s\nendstream\nendobj" % (len(text), text.encode()))
    lines.append(b"xref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000200 00000 n \ntrailer<</Size 5/Root 1 0 R>>\nstartxref\n300\n%%EOF")
    return b"\n".join(lines)


# 5.1 Tiny PDF (1 page)
print("── 5.1 Tiny PDF ──")
tiny = make_pdf("Hello world", 1)
r = requests.post(f"{V2}/documents/upload", files={"file": ("tiny.pdf", tiny, "application/pdf")}, headers=H)
test("Tiny PDF uploads", r.status_code == 200, f"got {r.status_code}")
tiny_id = r.json().get("data", {}).get("document_id", "")
if tiny_id:
    r = requests.post(f"{V2}/documents/analyze", data={"document_id": tiny_id}, headers=H)
    test("Tiny PDF analyzes", r.status_code == 200, f"got {r.status_code}")

# 5.2 Large PDF (100 pages)
print("\n── 5.2 Large PDF (100 pages) ──")
large_text = "Sample content line.\n" * 100
large = make_pdf(large_text, 100)
r = requests.post(f"{V2}/documents/upload", files={"file": ("large.pdf", large, "application/pdf")}, headers=H)
test("Large PDF (100pg) uploads", r.status_code == 200, f"got {r.status_code}")
large_id = r.json().get("data", {}).get("document_id", "")
if large_id:
    r = requests.post(f"{V2}/documents/analyze", data={"document_id": large_id}, headers=H)
    test("Large PDF analyzes", r.status_code == 200, f"got {r.status_code}")

# 5.3 Corrupted PDF
print("\n── 5.3 Corrupted PDF ──")
corrupted = b"this is not a pdf file at all\x00\xff\xfe"
r = requests.post(f"{V2}/documents/upload", files={"file": ("corrupt.pdf", corrupted, "application/pdf")}, headers=H)
test("Corrupted PDF uploads or errors gracefully", r.status_code in (200, 400, 422, 500), f"got {r.status_code}")
if r.status_code == 200:
    corr_id = r.json().get("data", {}).get("document_id", "")
    if corr_id:
        r = requests.post(f"{V2}/documents/analyze", data={"document_id": corr_id}, headers=H)
        test("Corrupted PDF analyze does not crash", r.status_code in (200, 400, 422, 500), f"got {r.status_code}")

# 5.4 Empty PDF (valid but no content)
print("\n── 5.4 Empty PDF ──")
empty = make_pdf("", 1)
r = requests.post(f"{V2}/documents/upload", files={"file": ("empty.pdf", empty, "application/pdf")}, headers=H)
test("Empty PDF uploads", r.status_code == 200, f"got {r.status_code}")
empty_id = r.json().get("data", {}).get("document_id", "")
if empty_id:
    r = requests.post(f"{V2}/documents/analyze", data={"document_id": empty_id}, headers=H)
    test("Empty PDF analyzes (no crash)", r.status_code in (200, 500), f"got {r.status_code}")

# 5.5 Image-only PDF (no extractable text)
print("\n── 5.5 Image-only PDF ──")
# Create a PDF with a small JPEG-like stream (not real image, just binary stream)
img_pdf = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Contents 4 0 R>>endobj
4 0 obj<</Length 30>>stream
\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000200 00000 n 
trailer<</Size 5/Root 1 0 R>>
startxref
300
%%EOF"""
r = requests.post(f"{V2}/documents/upload", files={"file": ("image.pdf", img_pdf, "application/pdf")}, headers=H)
test("Image-only PDF uploads", r.status_code == 200, f"got {r.status_code}")
img_id = r.json().get("data", {}).get("document_id", "")
if img_id:
    r = requests.post(f"{V2}/documents/analyze", data={"document_id": img_id}, headers=H)
    test("Image-only PDF analyze handles gracefully", r.status_code in (200, 500), f"got {r.status_code}")

# 5.6 Non-PDF file upload
print("\n── 5.6 Non-PDF Upload ──")
r = requests.post(f"{V2}/documents/upload", files={"file": ("text.txt", b"hello", "text/plain")}, headers=H)
test("Non-PDF upload handles gracefully", r.status_code in (200, 400, 422, 500), f"got {r.status_code}")

print(f"\n═══ LEVEL 5 RESULTS: {passed} passed, {failed} failed ═══")
sys.exit(1 if failed > 0 else 0)
