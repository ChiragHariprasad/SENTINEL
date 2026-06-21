"""Unit-style tests for evaluation metrics computation."""

import pytest


class TestMetricsComputation:
    def test_precision_perfect(self):
        from app.services.evaluation_service import compute_metrics
        # tp=10, fp=0 → precision=1.0
        p, r, f1 = compute_metrics(10, 0, 0)
        assert p == 1.0
        assert r == 1.0
        assert f1 == 1.0

    def test_precision_half(self):
        from app.services.evaluation_service import compute_metrics
        p, r, f1 = compute_metrics(5, 5, 0)
        assert p == 0.5
        assert r == 1.0
        assert f1 == pytest.approx(0.6667, rel=1e-3)

    def test_recall_zero(self):
        from app.services.evaluation_service import compute_metrics
        p, r, f1 = compute_metrics(0, 0, 10)
        assert p == 0
        assert r == 0
        assert f1 == 0

    def test_no_predictions_or_ground_truth(self):
        from app.services.evaluation_service import compute_metrics
        p, r, f1 = compute_metrics(0, 0, 0)
        assert p == 0
        assert r == 0
        assert f1 == 0

    def test_typical_score(self):
        from app.services.evaluation_service import compute_metrics
        # tp=8, fp=2, fn=1
        p, r, f1 = compute_metrics(8, 2, 1)
        assert p == pytest.approx(0.8, rel=1e-3)
        assert r == pytest.approx(0.8889, rel=1e-3)
        assert f1 == pytest.approx(0.8421, rel=1e-3)
