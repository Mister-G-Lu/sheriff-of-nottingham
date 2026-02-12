"""
Unit tests for Monte Carlo Sheriff.
Tests probabilistic decision-making and expected value calculations.
"""

from unittest.mock import patch

import pytest

from core.mechanics.goods import APPLE
from core.players.monte_carlo_sheriff import (
    MonteCarloSheriff,
    create_monte_carlo_sheriff,
)


class TestMonteCarloSheriffInitialization:
    """Test sheriff initialization and simulation."""

    def test_creates_with_default_parameters(self):
        """Test creates sheriff with default parameters."""
        sheriff = MonteCarloSheriff()

        assert sheriff.simulation_count == 100
        assert sheriff.risk_tolerance == 0.5
        assert sheriff.bribe_weight == 1.2
        assert sheriff.honest_distribution is not None
        assert sheriff.smuggler_distribution is not None

    def test_creates_with_custom_parameters(self):
        """Test creates sheriff with custom parameters."""
        sheriff = create_monte_carlo_sheriff(
            simulation_count=50, risk_tolerance=0.3, bribe_weight=1.5
        )

        assert sheriff.simulation_count == 50
        assert sheriff.risk_tolerance == 0.3
        assert sheriff.bribe_weight == 1.5

    @patch("core.players.monte_carlo_sheriff.draw_hand")
    def test_runs_simulations_on_init(self, mock_draw_hand):
        """Test runs simulations during initialization."""
        # Mock draw_hand to return predictable cards
        mock_draw_hand.return_value = [APPLE, APPLE, APPLE, APPLE, APPLE, APPLE]

        MonteCarloSheriff(simulation_count=10)

        # Should have called draw_hand for each simulation (10 honest + 10 smuggle = 20)
        assert mock_draw_hand.call_count == 20

    def test_builds_probability_distributions(self):
        """Test builds probability distributions from simulations."""
        sheriff = MonteCarloSheriff(simulation_count=20)

        # Should have some probabilities
        assert len(sheriff.honest_distribution) > 0
        assert len(sheriff.smuggler_distribution) > 0

        # Probabilities should sum to ~1.0 for each distribution
        honest_sum = sum(sheriff.honest_distribution.values())
        smuggler_sum = sum(sheriff.smuggler_distribution.values())

        assert 0.9 <= honest_sum <= 1.1
        assert 0.9 <= smuggler_sum <= 1.1


class TestHonestyProbabilityCalculation:
    """Test Bayesian probability calculations."""

    def test_calculates_high_probability_for_common_honest_declaration(self):
        """Test assigns high probability to declarations common among honest merchants."""
        sheriff = MonteCarloSheriff(simulation_count=50)

        # Manually set distributions for testing
        sheriff.honest_distribution = {
            ("apple", 4): 0.3,  # Common in honest draws
            ("apple", 3): 0.2,
        }
        sheriff.smuggler_distribution = {
            ("apple", 4): 0.05,  # Rare in smuggler draws
            ("apple", 3): 0.03,
        }

        # No history (50/50 prior)
        p_honest = sheriff._calculate_honesty_probability("apple", 4, None)

        # Should be high (common in honest, rare in smuggle)
        assert p_honest > 0.7

    def test_calculates_low_probability_for_rare_honest_declaration(self):
        """Test assigns low probability to declarations rare among honest merchants."""
        sheriff = MonteCarloSheriff(simulation_count=50)

        # Manually set distributions
        sheriff.honest_distribution = {
            ("silk", 5): 0.02,  # Rare in honest draws
        }
        sheriff.smuggler_distribution = {
            ("silk", 5): 0.25,  # Common in smuggler draws
        }

        p_honest = sheriff._calculate_honesty_probability("silk", 5, None)

        # Should be low (rare in honest, common in smuggle)
        assert p_honest < 0.3

    def test_uses_merchant_history_as_prior(self):
        """Test incorporates merchant history into probability calculation."""
        sheriff = MonteCarloSheriff(simulation_count=50)

        sheriff.honest_distribution = {("apple", 4): 0.2}
        sheriff.smuggler_distribution = {("apple", 4): 0.2}

        # History showing merchant is usually honest
        honest_history = [
            {"opened": True, "caught": False},  # Honest
            {"opened": True, "caught": False},  # Honest
            {"opened": False},  # Assumed honest
        ]

        # History showing merchant is usually lying
        dishonest_history = [
            {"opened": True, "caught": True},  # Caught lying
            {"opened": True, "caught": True},  # Caught lying
        ]

        p_honest_good = sheriff._calculate_honesty_probability(
            "apple", 4, honest_history
        )
        p_honest_bad = sheriff._calculate_honesty_probability(
            "apple", 4, dishonest_history
        )

        # Good history should increase probability
        assert p_honest_good > p_honest_bad

    def test_handles_unknown_declaration(self):
        """Test handles declarations not in probability tables."""
        sheriff = MonteCarloSheriff(simulation_count=50)

        # Clear distributions
        sheriff.honest_distribution = {}
        sheriff.smuggler_distribution = {}

        p_honest = sheriff._calculate_honesty_probability("unknown", 99, None)

        # Should return 50/50 when no information
        assert p_honest == 0.5


class TestMerchantHonestyRate:
    """Test merchant history analysis."""

    def test_returns_default_with_no_history(self):
        """Test returns 0.5 prior with no history."""
        sheriff = MonteCarloSheriff(simulation_count=10)

        rate = sheriff._get_merchant_honesty_rate(None)
        assert rate == 0.5

        rate = sheriff._get_merchant_honesty_rate([])
        assert rate == 0.5

    def test_calculates_rate_from_inspections(self):
        """Test calculates honesty rate from inspection history."""
        sheriff = MonteCarloSheriff(simulation_count=10)

        history = [
            {"opened": True, "caught": False},  # Honest
            {"opened": True, "caught": False},  # Honest
            {"opened": True, "caught": True},  # Caught lying
            {"opened": False},  # Not opened (assume honest)
        ]

        rate = sheriff._get_merchant_honesty_rate(history)

        # 3 honest out of 4 = 0.75
        assert rate == 0.75

    def test_assumes_unopened_are_honest(self):
        """Test conservatively assumes unopened bags were honest."""
        sheriff = MonteCarloSheriff(simulation_count=10)

        history = [
            {"opened": False},
            {"opened": False},
            {"opened": False},
        ]

        rate = sheriff._get_merchant_honesty_rate(history)

        # All assumed honest
        assert rate == 1.0


class TestInspectionDecision:
    """Test inspection decision logic."""

    def test_inspects_when_high_probability_of_lie(self):
        """Test inspects when declaration is likely a lie."""
        sheriff = MonteCarloSheriff(simulation_count=10)

        # Set up distributions showing this is likely a lie
        sheriff.honest_distribution = {("silk", 6): 0.01}
        sheriff.smuggler_distribution = {("silk", 6): 0.5}

        declaration = {"good_id": "silk", "count": 6}

        should_inspect = sheriff.should_inspect(
            "TestMerchant", declaration, bribe_offered=0, merchant_history=None
        )

        assert should_inspect is True

    def test_accepts_bribe_when_likely_honest(self):
        """Test accepts bribe when declaration is likely honest."""
        sheriff = MonteCarloSheriff(simulation_count=10)

        # Set up distributions showing this is likely honest
        sheriff.honest_distribution = {("apple", 4): 0.4}
        sheriff.smuggler_distribution = {("apple", 4): 0.05}

        declaration = {"good_id": "apple", "count": 4}

        should_inspect = sheriff.should_inspect(
            "TestMerchant", declaration, bribe_offered=5, merchant_history=None
        )

        # Should not inspect (accept bribe)
        assert should_inspect is False

    def test_weighs_bribe_amount_in_decision(self):
        """Test considers bribe amount in decision."""
        sheriff = MonteCarloSheriff(simulation_count=10, bribe_weight=1.5)

        # Ambiguous declaration
        sheriff.honest_distribution = {("cheese", 4): 0.2}
        sheriff.smuggler_distribution = {("cheese", 4): 0.2}

        declaration = {"good_id": "cheese", "count": 4}

        # Small bribe - might inspect
        sheriff.should_inspect(
            "TestMerchant", declaration, bribe_offered=1, merchant_history=None
        )

        # Large bribe - should accept
        inspect_large = sheriff.should_inspect(
            "TestMerchant", declaration, bribe_offered=20, merchant_history=None
        )

        # Large bribe should be more likely to be accepted
        assert inspect_large is False

    def test_risk_tolerance_affects_decision(self):
        """Test risk tolerance parameter affects decisions."""
        # Aggressive sheriff (low risk tolerance)
        aggressive = MonteCarloSheriff(simulation_count=10, risk_tolerance=0.2)

        # Cautious sheriff (high risk tolerance)
        cautious = MonteCarloSheriff(simulation_count=10, risk_tolerance=0.8)

        # Set same distributions
        for sheriff in [aggressive, cautious]:
            sheriff.honest_distribution = {("apple", 4): 0.3}
            sheriff.smuggler_distribution = {("apple", 4): 0.15}

        declaration = {"good_id": "apple", "count": 4}

        aggressive_inspects = aggressive.should_inspect(
            "TestMerchant", declaration, 0, None
        )

        cautious_inspects = cautious.should_inspect(
            "TestMerchant", declaration, 0, None
        )

        # Aggressive sheriff more likely to inspect
        # (This test may be probabilistic depending on exact values)
        assert aggressive_inspects or not cautious_inspects


class TestExpectedValueCalculation:
    """Test expected value calculations."""

    def test_calculates_positive_ev_for_likely_lie(self):
        """Test calculates positive EV when likely catching a lie."""
        sheriff = MonteCarloSheriff(simulation_count=10)

        # 90% chance of lie
        ev = sheriff._calculate_inspection_ev("apple", 4, p_honest=0.1)

        # Should be positive (worth inspecting)
        assert ev > 0

    def test_calculates_negative_ev_for_likely_honest(self):
        """Test calculates negative EV when likely honest."""
        sheriff = MonteCarloSheriff(simulation_count=10)

        # 90% chance of honest
        ev = sheriff._calculate_inspection_ev("apple", 4, p_honest=0.9)

        # Should be negative (not worth inspecting)
        assert ev < 0

    def test_higher_value_declarations_have_higher_ev(self):
        """Test higher value goods have higher inspection EV."""
        sheriff = MonteCarloSheriff(simulation_count=10)

        # Same probability, different values
        ev_low = sheriff._calculate_inspection_ev("apple", 2, p_honest=0.3)
        ev_high = sheriff._calculate_inspection_ev("apple", 6, p_honest=0.3)

        # Higher count should have higher EV
        assert ev_high > ev_low


class TestBribeAcceptance:
    """Test bribe acceptance logic."""

    def test_accepts_bribe_when_shouldnt_inspect(self):
        """Test accepts bribe when inspection EV is negative."""
        sheriff = MonteCarloSheriff(simulation_count=10)

        sheriff.honest_distribution = {("apple", 4): 0.5}
        sheriff.smuggler_distribution = {("apple", 4): 0.05}

        declaration = {"good_id": "apple", "count": 4}

        should_accept = sheriff.should_accept_bribe(
            "TestMerchant", declaration, bribe_offered=5, merchant_history=None
        )

        assert should_accept is True

    def test_rejects_bribe_when_should_inspect(self):
        """Test rejects bribe when inspection EV is positive."""
        sheriff = MonteCarloSheriff(simulation_count=10)

        sheriff.honest_distribution = {("silk", 6): 0.01}
        sheriff.smuggler_distribution = {("silk", 6): 0.6}

        declaration = {"good_id": "silk", "count": 6}

        should_accept = sheriff.should_accept_bribe(
            "TestMerchant", declaration, bribe_offered=2, merchant_history=None
        )

        assert should_accept is False

    def test_returns_false_when_no_bribe_offered(self):
        """Test returns False when no bribe offered."""
        sheriff = MonteCarloSheriff(simulation_count=10)

        declaration = {"good_id": "apple", "count": 4}

        should_accept = sheriff.should_accept_bribe(
            "TestMerchant", declaration, bribe_offered=0, merchant_history=None
        )

        assert should_accept is False


class TestInspectionReasoning:
    """Test reasoning explanation generation."""

    def test_generates_readable_reasoning(self):
        """Test generates human-readable reasoning."""
        sheriff = MonteCarloSheriff(simulation_count=10)

        sheriff.honest_distribution = {("apple", 4): 0.3}
        sheriff.smuggler_distribution = {("apple", 4): 0.1}

        declaration = {"good_id": "apple", "count": 4}

        reasoning = sheriff.get_inspection_reasoning(
            "TestMerchant", declaration, bribe_offered=5, merchant_history=None
        )

        # Should contain key information
        assert "apple" in reasoning
        assert "P(Honest)" in reasoning
        assert "EV(Inspect)" in reasoning
        assert "EV(Accept)" in reasoning
        assert "Decision" in reasoning


class TestFactoryFunction:
    """Test factory function."""

    def test_creates_sheriff_with_parameters(self):
        """Test factory function creates sheriff correctly."""
        sheriff = create_monte_carlo_sheriff(
            simulation_count=25, risk_tolerance=0.7, bribe_weight=1.3
        )

        assert isinstance(sheriff, MonteCarloSheriff)
        assert sheriff.simulation_count == 25
        assert sheriff.risk_tolerance == 0.7
        assert sheriff.bribe_weight == 1.3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
