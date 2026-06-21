"""
Seed script: Create demo data for walkthrough and presentation.

Usage:
    python scripts/seed_demo_data.py

Creates:
    10 demo vendors with realistic risk profiles
    Data access records (PII, PCI, FINANCIAL)
    Certifications (SOC2, ISO27001) with some expiring
    Contracts with AI analysis results
    Security alerts
    Risk scores and anomaly events
    Evaluation metrics

Idempotent: uses vendor_name as dedup key.
"""

import asyncio
import os
import sys
from datetime import date, timedelta, datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.core.database import async_session_factory, engine, Base
from app.models.user import User, Role
from app.models.vendor import Vendor, VendorDataAccess
from app.models.risk import RiskScore, RiskHistory
from app.models.anomaly import AnomalyEvent, AnomalyLabel
from app.models.evaluation import EvaluationResult
from app.models.ground_truth import GroundTruthLabel
from app.models.compliance import Certification, ComplianceFramework
from app.models.alert import SecurityAlert
from app.models.contract import Contract
from app.core.auth import hash_password
from app.ai.scoring import calculate_weighted_score
from app.services.anomaly_service import run_anomaly_detection, build_vendor_context
from app.services.evaluation_service import compute_evaluation
from sqlalchemy import select


DEMO_VENDORS = [
    {"name": "DataCloud Inc", "type": "SaaS", "criticality": "HIGH", "spend": 2500000, "owner": "Alice Chen", "contract": "active"},
    {"name": "SecurePay Solutions", "type": "FinTech", "criticality": "CRITICAL", "spend": 4200000, "owner": "Bob Kumar", "contract": "active"},
    {"name": "LogiShip Logistics", "type": "Logistics", "criticality": "MEDIUM", "spend": 750000, "owner": "Carol Davis", "contract": "active"},
    {"name": "Analytix AI", "type": "SaaS", "criticality": "HIGH", "spend": 1800000, "owner": "David Park", "contract": "active"},
    {"name": "OldGuard Security", "type": "Security", "criticality": "HIGH", "spend": 950000, "owner": "Eve Martin", "contract": "expired"},
    {"name": "QuickRetail Systems", "type": "RetailTech", "criticality": "LOW", "spend": 200000, "owner": "Frank Lee", "contract": "active"},
    {"name": "HealthBridge Corp", "type": "Healthcare", "criticality": "CRITICAL", "spend": 3800000, "owner": "Grace Kim", "contract": "active"},
    {"name": "Northeast IT Services", "type": "MSP", "criticality": "MEDIUM", "spend": 600000, "owner": "Henry Wang", "contract": "active"},
    {"name": "PixelCreative Agency", "type": "Marketing", "criticality": "LOW", "spend": 150000, "owner": "Iris Zhang", "contract": "active"},
    {"name": "CyberShield Defense", "type": "Security", "criticality": "HIGH", "spend": 1100000, "owner": "Jack Brown", "contract": "active"},
]

DATA_ACCESS_MAP = {
    "DataCloud Inc": [("PII", "Read"), ("PCI", "Read"), ("FINANCIAL", "Write")],
    "SecurePay Solutions": [("PII", "Admin"), ("PCI", "Admin"), ("FINANCIAL", "Admin")],
    "HealthBridge Corp": [("PHI", "Admin"), ("PII", "Write")],
    "Analytix AI": [("PII", "Read"), ("FINANCIAL", "Read")],
    "OldGuard Security": [("PII", "Admin"), ("PCI", "Admin")],
    "CyberShield Defense": [("PII", "Read")],
    "LogiShip Logistics": [],
    "QuickRetail Systems": [("FINANCIAL", "Read")],
    "Northeast IT Services": [("PII", "Read")],
    "PixelCreative Agency": [],
}

CERT_MAP = {
    "DataCloud Inc": [("SOC 2 Type II", "AICPA", 180), ("ISO 27001", "BSI", 90)],
    "SecurePay Solutions": [("PCI DSS", "PCI Council", 60), ("SOC 2 Type II", "AICPA", -10)],
    "HealthBridge Corp": [("HIPAA", "HHS", 120), ("ISO 27001", "BSI", 200)],
    "Analytix AI": [("SOC 2 Type I", "AICPA", 30)],
    "OldGuard Security": [("SOC 2 Type II", "AICPA", -30), ("ISO 27001", "BSI", -60)],
    "CyberShield Defense": [("ISO 27001", "BSI", 45)],
}

ALERT_MAP = {
    "OldGuard Security": ("CONTRACT_EXPIRED", "CRITICAL", "Contract expired with active data access"),
    "SecurePay Solutions": ("BREACH_RISK", "HIGH", "PCI admin access with expiring cert"),
}

CONTRACT_MAP = {
    "DataCloud Inc": "DataCloud Master Services Agreement. Includes standard SLA of 99.9% uptime. Breach notification within 72 hours. Annual security assessment required. GDPR clause applies.",
    "SecurePay Solutions": "SecurePay Payment Processing Agreement. SLA: 99.99% uptime. Liability cap of $5M. Breach notification within 24 hours. PCI DSS compliance required.",
    "HealthBridge Corp": "HealthBridge Data Processing Agreement. HIPAA compliance required. BA agreement included. Breach notification within 72 hours. Data retention: 7 years.",
    "OldGuard Security": "OldGuard Security Consulting Agreement. Contract expired 2025-03-15. No auto-renewal.",
}


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as db:
        # Ensure roles exist
        for role_name in ["admin", "analyst", "executive"]:
            r = await db.execute(select(Role).where(Role.role_name == role_name))
            if not r.scalar_one_or_none():
                db.add(Role(role_name=role_name, description=f"{role_name.capitalize()} role"))
        await db.flush()

        # Ensure users
        users_data = [
            ("admin@sentinel.ai", "admin123", "Admin", "admin"),
            ("analyst@sentinel.ai", "analyst123", "Analyst User", "analyst"),
            ("executive@sentinel.ai", "executive123", "Executive User", "executive"),
        ]
        for email, pw, name, role in users_data:
            r = await db.execute(select(User).where(User.email == email))
            if not r.scalar_one_or_none():
                db.add(User(email=email, password_hash=hash_password(pw), first_name=name, role=role))
        await db.flush()

        # Ensure anomaly labels
        labels = [
            ("BREACHED_VENDOR_HIGH_ACCESS", "CRITICAL"),
            ("VENDOR_UNDER_INVESTIGATION", "HIGH"),
            ("HIGH_RISK_SCORE", "HIGH"),
            ("EXPIRED_CERTIFICATION", "HIGH"),
            ("RECENTLY_BREACHED_VENDOR", "HIGH"),
            ("CONTRACT_EXPIRED_ACTIVE_ACCESS", "MEDIUM"),
            ("ELEVATED_RISK_VENDOR", "MEDIUM"),
        ]
        for name, sev in labels:
            r = await db.execute(select(AnomalyLabel).where(AnomalyLabel.label_name == name))
            if not r.scalar_one_or_none():
                db.add(AnomalyLabel(label_name=name, default_severity=sev))
        await db.flush()

        # Ensure compliance frameworks
        frameworks = ["SOC 2 Type I", "SOC 2 Type II", "ISO 27001", "PCI DSS", "HIPAA", "FedRAMP"]
        for fw in frameworks:
            r = await db.execute(select(ComplianceFramework).where(ComplianceFramework.framework_name == fw))
            if not r.scalar_one_or_none():
                db.add(ComplianceFramework(framework_name=fw))
        await db.flush()

        # Create vendors
        vendor_map = {}
        for v in DEMO_VENDORS:
            r = await db.execute(select(Vendor).where(Vendor.vendor_name == v["name"]))
            existing = r.scalar_one_or_none()
            if existing:
                vendor_map[v["name"]] = existing
                continue
            vendor = Vendor(
                vendor_name=v["name"],
                vendor_type=v["type"],
                criticality=v["criticality"],
                annual_spend=v["spend"],
                vendor_owner=v["owner"],
                contract_status=v["contract"],
            )
            db.add(vendor)
            await db.flush()
            vendor_map[v["name"]] = vendor

        await db.flush()
        print(f"Seeded {len(vendor_map)} vendors")

        # Data access
        for vname, accesses in DATA_ACCESS_MAP.items():
            vendor = vendor_map.get(vname)
            if not vendor:
                continue
            prev = await db.execute(select(VendorDataAccess).where(VendorDataAccess.vendor_id == vendor.vendor_id))
            if prev.scalars().first():
                continue
            for dtype, level in accesses:
                db.add(VendorDataAccess(vendor_id=vendor.vendor_id, data_type=dtype, access_level=level, is_active=True))
        await db.flush()
        print("Seeded data access records")

        # Certifications
        for vname, certs in CERT_MAP.items():
            vendor = vendor_map.get(vname)
            if not vendor:
                continue
            prev = await db.execute(select(Certification).where(Certification.vendor_id == vendor.vendor_id))
            if prev.scalars().first():
                continue
            for ctype, issuer, days_until_expiry in certs:
                exp = date.today() + timedelta(days=days_until_expiry)
                db.add(Certification(
                    vendor_id=vendor.vendor_id,
                    certification_type=ctype,
                    issuer=issuer,
                    issue_date=date.today() - timedelta(days=365),
                    expiry_date=exp,
                    status="active" if days_until_expiry > 0 else "expired",
                ))
        await db.flush()
        print("Seeded certifications")

        # Contracts
        for vname, text in CONTRACT_MAP.items():
            vendor = vendor_map.get(vname)
            if not vendor:
                continue
            prev = await db.execute(select(Contract).where(Contract.vendor_id == vendor.vendor_id))
            if prev.scalars().first():
                continue
            db.add(Contract(
                vendor_id=vendor.vendor_id,
                contract_name=f"{vname} Service Agreement",
                contract_type="MSA",
                start_date=date.today() - timedelta(days=365),
                end_date=date.today() + timedelta(days=730),
                status="active" if vendor.contract_status == "active" else "expired",
                raw_text=text,
                ai_analysis={
                    "breach_notification_days": 72,
                    "sla_uptime": "99.9%",
                    "risk_level": "medium",
                    "key_obligations": [
                        "Maintain compliance certifications",
                        "Notify within 72 hours of breach",
                        "Annual security assessment",
                    ],
                },
            ))
        await db.flush()
        print("Seeded contracts")

        # Alerts
        for vname, (atype, sev, msg) in ALERT_MAP.items():
            vendor = vendor_map.get(vname)
            if not vendor:
                continue
            prev = await db.execute(select(SecurityAlert).where(SecurityAlert.vendor_id == vendor.vendor_id))
            if prev.scalars().first():
                continue
            db.add(SecurityAlert(
                vendor_id=vendor.vendor_id,
                alert_type=atype,
                severity=sev,
                status="open",
                message=msg,
            ))
        await db.flush()
        print("Seeded alerts")

        # Calculate risk scores for all vendors
        for vname, vendor in vendor_map.items():
            prev_risk = await db.execute(
                select(RiskScore).where(RiskScore.vendor_id == vendor.vendor_id).limit(1)
            )
            if prev_risk.scalar_one_or_none():
                continue

            from app.services.risk_service import calculate_risk_dimensions
            scores = await calculate_risk_dimensions(db, vendor)
            overall, tier = calculate_weighted_score(scores)

            risk = RiskScore(
                vendor_id=vendor.vendor_id,
                security_score=scores["security"],
                data_access_score=scores["data_access"],
                compliance_score=scores["compliance"],
                financial_score=scores["financial"],
                contract_score=scores["contract"],
                overall_score=overall,
                risk_tier=tier,
            )
            db.add(risk)
            vendor.risk_tier = tier

            db.add(RiskHistory(
                vendor_id=vendor.vendor_id,
                overall_score=overall,
                risk_tier=tier,
            ))
        await db.flush()
        print("Seeded risk scores")

        # Run anomaly detection
        for vname, vendor in vendor_map.items():
            prev_anom = await db.execute(
                select(AnomalyEvent).where(AnomalyEvent.vendor_id == vendor.vendor_id).limit(1)
            )
            if prev_anom.scalar_one_or_none():
                continue
            await run_anomaly_detection(db, vendor, commit=False)
        await db.flush()
        print("Seeded anomaly events")

        # Compute evaluation
        prev_eval = await db.execute(select(EvaluationResult).limit(1))
        if not prev_eval.scalar_one_or_none():
            await compute_evaluation(db)
            await db.commit()
            print("Computed evaluation metrics")

        await db.commit()
        print("\n✅ Demo data seeded successfully!")
        print(f"   Vendors: {len(vendor_map)}")
        print("   Login: admin@sentinel.ai / admin123")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
