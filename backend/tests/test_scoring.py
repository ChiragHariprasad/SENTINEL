"""Unit tests for risk scoring engine."""

from app.ai.scoring import calculate_weighted_score


class TestWeightedScoring:
    def test_all_scores_zero_returns_green(self):
        scores = {"security": 0, "data_access": 0, "compliance": 0, "financial": 0, "contract": 0}
        overall, tier = calculate_weighted_score(scores)
        assert overall == 0
        assert tier == "GREEN"

    def test_max_scores_returns_red(self):
        scores = {"security": 100, "data_access": 100, "compliance": 100, "financial": 100, "contract": 100}
        overall, tier = calculate_weighted_score(scores)
        assert overall == 100
        assert tier == "RED"

    def test_tier_boundaries(self):
        # RED: 71-100 (all max)
        scores = {"security": 100, "data_access": 100, "compliance": 100, "financial": 100, "contract": 100}
        overall, tier = calculate_weighted_score(scores)
        assert tier == "RED"
        assert overall == 100

        # YELLOW: 41-70
        scores = {"security": 60, "data_access": 60, "compliance": 60, "financial": 60, "contract": 60}
        overall, tier = calculate_weighted_score(scores)
        assert tier == "YELLOW"

        # GREEN: 0-40
        scores = {"security": 10, "data_access": 10, "compliance": 10, "financial": 10, "contract": 10}
        overall, tier = calculate_weighted_score(scores)
        assert tier == "GREEN"

    def test_weight_distribution(self):
        """security (35%) has highest weight, contract (10%) lowest."""
        high_security = {"security": 100, "data_access": 0, "compliance": 0, "financial": 0, "contract": 0}
        high_contract = {"security": 0, "data_access": 0, "compliance": 0, "financial": 0, "contract": 100}
        sec_overall, _ = calculate_weighted_score(high_security)
        con_overall, _ = calculate_weighted_score(high_contract)
        assert sec_overall > con_overall
        assert sec_overall == 35.0
        assert con_overall == 10.0

    def test_overall_capped_at_100(self):
        scores = {"security": 200, "data_access": 200, "compliance": 200, "financial": 200, "contract": 200}
        overall, tier = calculate_weighted_score(scores)
        assert overall == 100
        assert tier == "RED"

    def test_partial_scores(self):
        scores = {"security": 50, "data_access": 0, "compliance": 0, "financial": 0, "contract": 0}
        overall, tier = calculate_weighted_score(scores)
        assert overall == 17.5  # 50 * 0.35

    def test_missing_dimension_defaults_to_zero(self):
        scores = {"security": 100}  # missing others
        overall, tier = calculate_weighted_score(scores)
        assert overall == 35.0  # only security contributed
