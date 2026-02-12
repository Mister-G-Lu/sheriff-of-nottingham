"""
Tests for Tiered Merchant Strategy System

Tests the consolidated risk score calculation and strategy weight selection
for Easy, Medium, and Hard tier merchants.
"""

import pytest

from ai_strategy.tiered_strategy import TieredMerchantStrategy
from core.systems.game_master_state import MerchantTier


class TestRiskScoreCalculation:
    """Test risk score calculation for different tiers."""

    def test_easy_tier_honest_merchant(self):
        """Test that very honest merchants have low risk scores (Easy tier)."""
        risk_score = TieredMerchantStrategy._calculate_risk_score(
            honesty=10,
            risk=0,
            greed=0,
            inspection_rate=0.5,
            catch_rate=0.5,
            tier=MerchantTier.EASY,
        )
        assert risk_score <= 0, "Honest Abe should have risk_score <= 0"

    def test_easy_tier_bold_merchant(self):
        """Test that bold merchants have high risk scores (Easy tier)."""
        risk_score = TieredMerchantStrategy._calculate_risk_score(
            honesty=1,
            risk=10,
            greed=10,
            inspection_rate=0.5,
            catch_rate=0.5,
            tier=MerchantTier.EASY,
        )
        assert risk_score >= 8, "Lying Larry should have risk_score >= 8"

    def test_medium_tier_honest_merchant(self):
        """Test that very honest merchants have low risk scores (Medium tier)."""
        risk_score = TieredMerchantStrategy._calculate_risk_score(
            honesty=10,
            risk=0,
            greed=0,
            inspection_rate=0.5,
            catch_rate=0.5,
            tier=MerchantTier.MEDIUM,
        )
        assert risk_score <= 0, "Honest merchant should have risk_score <= 0"

    def test_medium_tier_greedy_merchant(self):
        """Test that greed increases risk score (Medium tier)."""
        risk_score_low_greed = TieredMerchantStrategy._calculate_risk_score(
            honesty=5,
            risk=5,
            greed=0,
            inspection_rate=0.5,
            catch_rate=0.5,
            tier=MerchantTier.MEDIUM,
        )
        risk_score_high_greed = TieredMerchantStrategy._calculate_risk_score(
            honesty=5,
            risk=5,
            greed=10,
            inspection_rate=0.5,
            catch_rate=0.5,
            tier=MerchantTier.MEDIUM,
        )
        assert risk_score_high_greed > risk_score_low_greed, (
            "High greed should increase risk score"
        )

    def test_sheriff_aggression_reduces_risk(self):
        """Test that aggressive sheriffs reduce merchant risk-taking."""
        risk_score_lenient = TieredMerchantStrategy._calculate_risk_score(
            honesty=5,
            risk=5,
            greed=5,
            inspection_rate=0.2,
            catch_rate=0.2,
            tier=MerchantTier.MEDIUM,
        )
        risk_score_aggressive = TieredMerchantStrategy._calculate_risk_score(
            honesty=5,
            risk=5,
            greed=5,
            inspection_rate=0.8,
            catch_rate=0.8,
            tier=MerchantTier.MEDIUM,
        )
        assert risk_score_aggressive < risk_score_lenient, (
            "Aggressive sheriff should reduce risk score"
        )

    def test_hard_tier_pattern_exploitation(self):
        """Test that Hard tier exploits lenient sheriff patterns."""
        # Create history with mostly passes (lenient sheriff)
        lenient_history = [
            {"opened": False, "bribe_accepted": False, "caught_lie": False}
            for _ in range(5)
        ]

        risk_score_with_pattern = TieredMerchantStrategy._calculate_risk_score(
            honesty=5,
            risk=5,
            greed=5,
            inspection_rate=0.3,
            catch_rate=0.3,
            tier=MerchantTier.HARD,
            history=lenient_history,
        )

        risk_score_without_pattern = TieredMerchantStrategy._calculate_risk_score(
            honesty=5,
            risk=5,
            greed=5,
            inspection_rate=0.3,
            catch_rate=0.3,
            tier=MerchantTier.HARD,
            history=[],
        )

        assert risk_score_with_pattern > risk_score_without_pattern, (
            "Hard tier should exploit lenient patterns"
        )


class TestStrategyWeights:
    """Test strategy weight selection for different tiers."""

    def test_easy_tier_very_cautious_weights(self):
        """Test that very cautious merchants (risk_score=0) get mostly honest weights."""
        weights = TieredMerchantStrategy._get_strategy_weights(
            risk_score=0, tier=MerchantTier.EASY
        )
        assert weights[0] >= 0.90, "Very cautious should be 90%+ honest"
        assert weights[3] == 0.0, "Very cautious should have 0% contraband_low"
        assert weights[4] == 0.0, "Very cautious should have 0% contraband_high"

    def test_easy_tier_bold_weights(self):
        """Test that bold merchants (risk_score=10) get aggressive weights."""
        weights = TieredMerchantStrategy._get_strategy_weights(
            risk_score=10, tier=MerchantTier.EASY
        )
        assert weights[0] <= 0.10, "Very bold should be <=10% honest"
        assert weights[3] + weights[4] >= 0.50, "Very bold should be >=50% contraband"

    def test_medium_tier_more_aggressive_than_easy(self):
        """Test that Medium tier is more aggressive than Easy tier."""
        easy_weights = TieredMerchantStrategy._get_strategy_weights(
            risk_score=5, tier=MerchantTier.EASY
        )
        medium_weights = TieredMerchantStrategy._get_strategy_weights(
            risk_score=5, tier=MerchantTier.MEDIUM
        )

        # Medium should have less honesty, more contraband
        assert medium_weights[0] < easy_weights[0], (
            "Medium should be less honest than Easy"
        )
        assert (
            medium_weights[3] + medium_weights[4] > easy_weights[3] + easy_weights[4]
        ), "Medium should have more contraband than Easy"

    def test_hard_tier_most_aggressive(self):
        """Test that Hard tier is the most aggressive."""
        easy_weights = TieredMerchantStrategy._get_strategy_weights(
            risk_score=5, tier=MerchantTier.EASY
        )
        hard_weights = TieredMerchantStrategy._get_strategy_weights(
            risk_score=5, tier=MerchantTier.HARD
        )

        assert hard_weights[0] < easy_weights[0], "Hard should be less honest than Easy"
        assert hard_weights[3] + hard_weights[4] > easy_weights[3] + easy_weights[4], (
            "Hard should have more contraband than Easy"
        )

    def test_weights_sum_to_one(self):
        """Test that all weight arrays sum to 1.0."""
        for tier in [MerchantTier.EASY, MerchantTier.MEDIUM, MerchantTier.HARD]:
            for risk_score in [0, 2, 4, 6, 8, 10]:
                weights = TieredMerchantStrategy._get_strategy_weights(risk_score, tier)
                assert abs(sum(weights) - 1.0) < 0.01, (
                    f"Weights for tier={tier}, risk_score={risk_score} should sum to 1.0"
                )


class TestStrategySelection:
    """Test full strategy selection logic."""

    def test_honest_merchant_mostly_honest_strategy(self):
        """Test that honest merchants mostly select honest strategy."""
        personality = {"honesty_bias": 10, "risk_tolerance": 0, "greed": 0}
        sheriff_stats = {"inspection_rate": 0.5, "catch_rate": 0.5}

        # Run 100 times and count strategies
        strategies = []
        for _ in range(100):
            strategy = TieredMerchantStrategy._select_strategy_type(
                personality, MerchantTier.MEDIUM, sheriff_stats, []
            )
            strategies.append(strategy)

        honest_count = strategies.count("honest")
        assert honest_count >= 80, (
            f"Honest merchant should be honest 80%+ of the time, got {honest_count}%"
        )

    def test_bold_merchant_mostly_contraband_strategy(self):
        """Test that bold merchants mostly select contraband strategy."""
        personality = {"honesty_bias": 1, "risk_tolerance": 10, "greed": 10}
        sheriff_stats = {"inspection_rate": 0.3, "catch_rate": 0.3}

        # Run 200 times and count strategies (increased for better statistical reliability)
        strategies = []
        for _ in range(200):
            strategy = TieredMerchantStrategy._select_strategy_type(
                personality, MerchantTier.MEDIUM, sheriff_stats, []
            )
            strategies.append(strategy)

        contraband_count = sum(1 for s in strategies if "contraband" in s)
        contraband_percentage = (contraband_count / 200) * 100
        # Bold merchants should smuggle close to 50% of the time (allow 3% variance for randomness)
        assert contraband_count >= 94, (
            f"Bold merchant should smuggle ~50% of the time, got {contraband_percentage:.1f}%"
        )

        # Should smuggle more than an honest merchant
        honest_strategies = []
        honest_personality = {"honesty_bias": 10, "risk_tolerance": 0, "greed": 0}
        for _ in range(100):
            strategy = TieredMerchantStrategy._select_strategy_type(
                honest_personality, MerchantTier.MEDIUM, sheriff_stats, []
            )
            honest_strategies.append(strategy)

        honest_contraband_count = sum(1 for s in honest_strategies if "contraband" in s)
        assert contraband_count > honest_contraband_count * 3, (
            "Bold merchant should smuggle much more than honest merchant"
        )

    def test_hard_tier_reverse_psychology(self):
        """Test that Hard tier uses reverse psychology against effective sheriffs."""
        personality = {"honesty_bias": 5, "risk_tolerance": 5, "greed": 5}
        sheriff_stats = {"inspection_rate": 0.8, "catch_rate": 0.8}

        # Run 100 times and check for reverse psychology
        strategies = []
        for _ in range(100):
            strategy = TieredMerchantStrategy._select_strategy_type(
                personality, MerchantTier.HARD, sheriff_stats, []
            )
            strategies.append(strategy)

        honest_count = strategies.count("honest")
        # Should have some reverse psychology (25% chance), so expect 20-30% honest
        assert honest_count >= 15, (
            "Hard tier should use reverse psychology against effective sheriffs"
        )


class TestFullDeclarationFlow:
    """Test the full declaration flow."""

    def test_easy_tier_returns_valid_declaration(self):
        """Test that Easy tier returns a valid declaration."""
        personality = {"honesty_bias": 8, "risk_tolerance": 2, "greed": 3}

        declaration = TieredMerchantStrategy.choose_declaration(
            personality, MerchantTier.EASY
        )

        assert "declared_id" in declaration
        assert "count" in declaration
        assert "actual_ids" in declaration
        assert "lie" in declaration
        assert "bribe_amount" in declaration
        assert isinstance(declaration["lie"], bool)

    def test_medium_tier_returns_valid_declaration(self):
        """Test that Medium tier returns a valid declaration."""
        personality = {"honesty_bias": 5, "risk_tolerance": 5, "greed": 5}

        declaration = TieredMerchantStrategy.choose_declaration(
            personality, MerchantTier.MEDIUM
        )

        assert "declared_id" in declaration
        assert "count" in declaration
        assert "actual_ids" in declaration
        assert "lie" in declaration
        assert "bribe_amount" in declaration

    def test_hard_tier_returns_valid_declaration(self):
        """Test that Hard tier returns a valid declaration."""
        personality = {"honesty_bias": 3, "risk_tolerance": 7, "greed": 8}

        declaration = TieredMerchantStrategy.choose_declaration(
            personality, MerchantTier.HARD
        )

        assert "declared_id" in declaration
        assert "count" in declaration
        assert "actual_ids" in declaration
        assert "lie" in declaration
        assert "bribe_amount" in declaration


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
