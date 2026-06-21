"""Unit tests for anomaly detection rules."""

import pytest
from app.ai.rules import ANOMALY_RULES, evaluate_rule


class FakeVendor:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class TestRuleDefinitions:
    def test_all_rules_have_required_fields(self):
        for rule in ANOMALY_RULES:
            assert "name" in rule
            assert "severity" in rule
            assert "description" in rule
            assert "check" in rule
            assert "explanation" in rule
            assert callable(rule["check"])
            assert callable(rule["explanation"])

    def test_seven_rules_exist(self):
        assert len(ANOMALY_RULES) == 7

    def test_critical_and_high_severity_rules_present(self):
        names = {r["name"]: r["severity"] for r in ANOMALY_RULES}
        assert names["BREACHED_VENDOR_HIGH_ACCESS"] == "CRITICAL"
        for high_rule in ["VENDOR_UNDER_INVESTIGATION", "HIGH_RISK_SCORE", "EXPIRED_CERTIFICATION", "RECENTLY_BREACHED_VENDOR"]:
            assert names[high_rule] == "HIGH"


class TestEvaluateRule:
    def test_breached_vendor_high_access_triggers(self):
        rule = [r for r in ANOMALY_RULES if r["name"] == "BREACHED_VENDOR_HIGH_ACCESS"][0]
        vendor = FakeVendor(vendor_name="TestCorp")
        ctx = {
            "recent_breach": True,
            "has_data_access": {"PII": True},
        }
        result = evaluate_rule(rule, vendor, ctx)
        assert result is not None
        assert result["label"] == "BREACHED_VENDOR_HIGH_ACCESS"
        assert result["severity"] == "CRITICAL"

    def test_breached_no_sensitive_access_no_match(self):
        rule = [r for r in ANOMALY_RULES if r["name"] == "BREACHED_VENDOR_HIGH_ACCESS"][0]
        vendor = FakeVendor(vendor_name="TestCorp")
        ctx = {"recent_breach": True, "has_data_access": {"LOW_SENSITIVITY": True}}
        assert evaluate_rule(rule, vendor, ctx) is None

    def test_high_risk_score_triggers(self):
        rule = [r for r in ANOMALY_RULES if r["name"] == "HIGH_RISK_SCORE"][0]
        vendor = FakeVendor(vendor_name="RiskCorp")
        ctx = {"risk_score": 85, "recent_breach": False}
        result = evaluate_rule(rule, vendor, ctx)
        assert result is not None
        assert result["label"] == "HIGH_RISK_SCORE"

    def test_high_risk_below_threshold_no_match(self):
        rule = [r for r in ANOMALY_RULES if r["name"] == "HIGH_RISK_SCORE"][0]
        ctx = {"risk_score": 50}
        assert evaluate_rule(rule, FakeVendor(), ctx) is None

    def test_expired_cert_triggers(self):
        rule = [r for r in ANOMALY_RULES if r["name"] == "EXPIRED_CERTIFICATION"][0]
        ctx = {"has_expired_cert": True, "expired_certs": ["SOC2"]}
        result = evaluate_rule(rule, FakeVendor(vendor_name="CertCorp"), ctx)
        assert result is not None
        assert "SOC2" in result["explanation"]

    def test_contract_expired_with_access(self):
        rule = [r for r in ANOMALY_RULES if r["name"] == "CONTRACT_EXPIRED_ACTIVE_ACCESS"][0]
        ctx = {"contract_expired": True, "has_active_access": True}
        result = evaluate_rule(rule, FakeVendor(vendor_name="ExpiredCorp"), ctx)
        assert result is not None
        assert result["severity"] == "MEDIUM"

    def test_contract_expired_no_access_no_match(self):
        rule = [r for r in ANOMALY_RULES if r["name"] == "CONTRACT_EXPIRED_ACTIVE_ACCESS"][0]
        ctx = {"contract_expired": True, "has_active_access": False}
        assert evaluate_rule(rule, FakeVendor(), ctx) is None

    def test_elevated_risk_triggers(self):
        rule = [r for r in ANOMALY_RULES if r["name"] == "ELEVATED_RISK_VENDOR"][0]
        ctx = {"risk_score": 70}
        result = evaluate_rule(rule, FakeVendor(vendor_name="ElevatedCorp"), ctx)
        assert result is not None
        assert result["severity"] == "MEDIUM"

    def test_elevated_risk_below_range_no_match(self):
        rule = [r for r in ANOMALY_RULES if r["name"] == "ELEVATED_RISK_VENDOR"][0]
        assert evaluate_rule(rule, FakeVendor(), {"risk_score": 40}) is None
        assert evaluate_rule(rule, FakeVendor(), {"risk_score": 85}) is None

    def test_exception_returns_none(self):
        rule = [r for r in ANOMALY_RULES if r["name"] == "HIGH_RISK_SCORE"][0]
        result = evaluate_rule(rule, FakeVendor(), {})  # missing risk_score key will fail
        assert result is None

    def test_vendor_under_investigation(self):
        rule = [r for r in ANOMALY_RULES if r["name"] == "VENDOR_UNDER_INVESTIGATION"][0]
        assert evaluate_rule(rule, FakeVendor(vendor_name="V"), {"under_investigation": True}) is not None
        assert evaluate_rule(rule, FakeVendor(vendor_name="V"), {"under_investigation": False}) is None

    def test_recently_breached(self):
        rule = [r for r in ANOMALY_RULES if r["name"] == "RECENTLY_BREACHED_VENDOR"][0]
        assert evaluate_rule(rule, FakeVendor(vendor_name="Breached"), {"recent_breach": True}) is not None
        assert evaluate_rule(rule, FakeVendor(), {"recent_breach": False}) is None
