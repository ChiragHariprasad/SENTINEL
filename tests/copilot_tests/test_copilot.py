import requests
import sys
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

print("═══ LEVEL 6: COPILOT TESTING (100 questions) ═══\n")

questions = [
    # Risk Explanation (15)
    "Why is Vendor X risky?",
    "Why is CloudBackup Inc risky?",
    "Explain risk for SecurePay Solutions",
    "What risk does Beta Inc have?",
    "Why is OldGuard Security high risk?",
    "Explain the risk of DataCloud Inc",
    "What are the risks for HealthBridge Corp?",
    "Why is CyberShield Defense risky?",
    "Why is LogiShip Logistics risky?",
    "Why is Analytix AI risky?",
    "Why is Acme Corp risky?",
    "Explain risk of CSVImportCorp",
    "What risk does CleanV have?",
    "Why is the vendor risky?",
    "Tell me about the risk of our top vendor",
    # Remediation (10)
    "How do I reduce risk for Vendor X?",
    "How to fix SecurePay risk?",
    "What actions should I take for CloudBackup Inc?",
    "How do I lower Beta Inc risk score?",
    "What remediation is available for OldGuard Security?",
    "How to mitigate DataCloud Inc risks?",
    "Reduce HealthBridge risk",
    "Fix CyberShield vulnerabilities",
    "How do I remediate LogiShip issues?",
    "What steps should I take for Analytix AI?",
    # Simulation (15)
    "What if Vendor X is breached?",
    "What happens if CloudBackup Inc fails?",
    "Simulate a breach of SecurePay",
    "What if Beta Inc is compromised?",
    "Impact of OldGuard Security breach",
    "What if DataCloud Inc goes down?",
    "What happens if HealthBridge fails?",
    "Simulate CyberShield Defense being hacked",
    "What if LogiShip Logistics is breached?",
    "What if Analytix AI has a data breach?",
    "Simulate Acme Corp failure",
    "Impact of CSVImportCorp being compromised",
    "What if CleanV is breached?",
    "What if a vendor fails?",
    "Simulate breach scenario for top vendor",
    # Prioritization (10)
    "What should I focus on today?",
    "What are the top priorities?",
    "What is the most important risk right now?",
    "What should I work on this week?",
    "What matters most currently?",
    "Show me critical risks",
    "What are the urgent issues?",
    "What needs immediate attention?",
    "Top priorities for today",
    "What should leadership focus on right now?",
    # Executive Summary (10)
    "Generate board report",
    "Create executive summary",
    "Show board-level overview",
    "What does leadership need to know?",
    "Give me an executive brief",
    "Generate a summary for the board meeting",
    "What is the portfolio risk overview?",
    "Show me the overall risk status",
    "Executive dashboard overview",
    "Board report for this quarter",
    # Entity Lookup (15)
    "Tell me about SecurePay Solutions",
    "Who is CloudBackup Inc?",
    "What is Beta Inc?",
    "Show details for OldGuard Security",
    "Find DataCloud Inc",
    "Tell me about HealthBridge Corp",
    "Who is CyberShield Defense?",
    "What is LogiShip Logistics?",
    "Show me Analytix AI",
    "Find Acme Corp",
    "Tell me about CSVImportCorp",
    "What is CleanV?",
    "Who is HappyPathVendor Updated?",
    "Show me information about ISO 27001 control",
    "Find HIPAA control",
    # General / Misc (10)
    "How is risk calculated?",
    "What data sources do you use?",
    "How does correlation work?",
    "What types of entities exist?",
    "How often is risk updated?",
    "What scenarios can I simulate?",
    "How does blast radius work?",
    "What document types are supported?",
    "What is the difference between risk and correlation?",
    "How do I interpret risk scores?",
    # Nonsense (15)
    "Bananas are blue",
    "What is the meaning of life?",
    "Purple elephants fly",
    "42",
    "!@#$%^&*()",
    "abcdefghijklmnop",
    "",
    "   ",
    "一二三四五六七八九十",
    "What is the airspeed velocity of an unladen swallow?",
    "Why did the chicken cross the road?",
    "To be or not to be",
    "Hello world this is a test question without any specific intent",
    "SQL injection DROP TABLE vendors",
    "<script>alert('xss')</script>",
]

print(f"Total questions: {len(questions)}\n")

for i, q in enumerate(questions, 1):
    try:
        r = requests.post(f"{V2}/copilot/query", json={"question": q}, headers=H, timeout=15)
        if r.status_code == 200:
            data = r.json().get("data", {})
            answer = data.get("answer", "")
            intent = data.get("intent", "unknown")
            engine = data.get("engine", "unknown")
            has_answer = len(answer) > 0
            safe = not any(err in answer.lower() for err in ["traceback", "internal server error", "unhandled"])
            test(f"Q{i}: '{q[:40]}...' → {intent}/{engine}", has_answer and safe and r.status_code == 200,
                 f"status={r.status_code}, answer_len={len(answer)}")
        else:
            test(f"Q{i}: '{q[:40]}...'", r.status_code == 200, f"got {r.status_code}")
    except requests.Timeout:
        test(f"Q{i}: '{q[:40]}...'", False, "TIMEOUT")
    except Exception as e:
        test(f"Q{i}: '{q[:40]}...'", False, str(e))

print(f"\n═══ LEVEL 6 RESULTS: {passed} passed, {failed} failed ═══")
sys.exit(1 if failed > 0 else 0)
