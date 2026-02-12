"""
Unit tests for AI strategy modules
"""

# Must be first import - sets up test environment
import tests.test_setup  # noqa: F401
from ai_strategy.bribe_strategy import calculate_scaled_bribe, should_offer_bribe
from core.systems.game_master_state import MerchantTier


class TestBribeStrategy:
    """Test bribe calculation and strategy."""

    def test_calculate_scaled_bribe_with_contraband(self):
        """Test bribe calculation when carrying contraband."""
        personality = {"greed": 6, "risk_tolerance": 7, "honesty_bias": 5}
        sheriff_stats = {"inspection_rate": 0.5, "bribe_acceptance_rate": 0.4}

        bribe = calculate_scaled_bribe(
            declared_good_id="apple",
            declared_count=5,
            actual_good_ids=["silk", "silk", "pepper"],  # Contraband
            is_lying=True,
            personality=personality,
            sheriff_stats=sheriff_stats,
            tier=MerchantTier.MEDIUM,
        )

        # Should return a bribe amount (could be 0 if decides not to bribe)
        assert isinstance(bribe, int)
        assert bribe >= 0

    def test_calculate_scaled_bribe_honest(self):
        """Test bribe calculation when honest (should usually be 0)."""
        personality = {"greed": 3, "risk_tolerance": 2, "honesty_bias": 8}
        sheriff_stats = {"inspection_rate": 0.3, "bribe_acceptance_rate": 0.2}

        bribe = calculate_scaled_bribe(
            declared_good_id="apple",
            declared_count=5,
            actual_good_ids=["apple"] * 5,  # Honest
            is_lying=False,
            personality=personality,
            sheriff_stats=sheriff_stats,
            tier=MerchantTier.EASY,
        )

        # Honest merchants usually don't bribe (unless advanced bluff for HARD tier)
        assert isinstance(bribe, int)
        assert bribe >= 0

    def test_should_offer_bribe_high_risk(self):
        """Test bribe decision with high-risk contraband."""
        personality = {"greed": 8, "risk_tolerance": 7, "honesty_bias": 3}

        result = should_offer_bribe(
            is_lying=True,
            contraband_value=30,
            inspection_rate=0.7,  # High inspection rate
            bribe_acceptance_rate=0.5,
            personality=personality,
            tier=MerchantTier.HARD,
        )

        assert isinstance(result, bool)

    def test_should_offer_bribe_low_risk(self):
        """Test bribe decision with low-risk scenario."""
        personality = {"greed": 3, "risk_tolerance": 2, "honesty_bias": 8}

        result = should_offer_bribe(
            is_lying=True,
            contraband_value=5,
            inspection_rate=0.2,  # Low inspection rate
            bribe_acceptance_rate=0.1,  # Low acceptance rate
            personality=personality,
            tier=MerchantTier.EASY,
        )

        assert isinstance(result, bool)
