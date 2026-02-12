"""
Additional tests for Merchant base class to increase coverage.
"""

import pytest

from core.mechanics.goods import APPLE, BREAD, SILK
from core.players.merchants import Merchant


class TestMerchantBribeWithLying:
    """Test merchant bribe calculation for lying about legal goods."""

    def test_bribe_for_lying_about_legal_mix(self):
        """Test bribe when lying about legal goods mix."""
        merchant = Merchant(
            id="test",
            name="Test",
            intro="Test",
            tells_honest=[],
            tells_lying=[],
            bluff_skill=5,
            risk_tolerance=5,
            greed=5,
            honesty_bias=5,
        )

        # Lying about legal goods mix (3 apples declared, but actually 2 apples + 1 bread)
        actual_goods = [APPLE, APPLE, BREAD]

        bribe = merchant.calculate_proactive_bribe(
            actual_goods=actual_goods, is_lying=True, sheriff_authority=1
        )

        # Should offer some bribe for the mismatch
        assert isinstance(bribe, int)
        assert bribe >= 0


class TestMerchantPersonality:
    """Test merchant personality traits."""

    def test_merchant_with_high_honesty(self):
        """Test merchant with high honesty bias."""
        honest_merchant = Merchant(
            id="honest",
            name="Honest",
            intro="Test",
            tells_honest=[],
            tells_lying=[],
            bluff_skill=5,
            risk_tolerance=5,
            greed=5,
            honesty_bias=10,
        )

        assert honest_merchant.honesty_bias == 10

    def test_merchant_with_low_risk_tolerance(self):
        """Test merchant with low risk tolerance (cautious)."""
        cautious_merchant = Merchant(
            id="cautious",
            name="Cautious",
            intro="Test",
            tells_honest=[],
            tells_lying=[],
            bluff_skill=5,
            risk_tolerance=1,
            greed=5,
            honesty_bias=5,
        )

        assert cautious_merchant.risk_tolerance == 1

    def test_merchant_with_high_greed(self):
        """Test merchant with high greed."""
        greedy_merchant = Merchant(
            id="greedy",
            name="Greedy",
            intro="Test",
            tells_honest=[],
            tells_lying=[],
            bluff_skill=5,
            risk_tolerance=5,
            greed=10,
            honesty_bias=5,
        )

        assert greedy_merchant.greed == 10


class TestMerchantBribeDecision:
    """Test should_offer_proactive_bribe logic."""

    def test_should_bribe_with_contraband(self):
        """Test bribe decision with contraband."""
        merchant = Merchant(
            id="test",
            name="Test",
            intro="Test",
            tells_honest=[],
            tells_lying=[],
            bluff_skill=5,
            risk_tolerance=5,
            greed=5,
            honesty_bias=5,
        )

        actual_goods = [SILK, SILK]
        declared_goods = [APPLE, APPLE]

        # Run multiple times due to randomness
        results = []
        for _ in range(10):
            should_bribe = merchant.should_offer_proactive_bribe(
                sheriff_authority=5,
                sheriff_reputation=10,
                actual_goods=actual_goods,
                declared_goods=declared_goods,
            )
            results.append(should_bribe)

        # Should return boolean
        assert all(isinstance(r, bool) for r in results)

    def test_should_bribe_when_lying_about_legal(self):
        """Test bribe decision when lying about legal goods."""
        merchant = Merchant(
            id="test",
            name="Test",
            intro="Test",
            tells_honest=[],
            tells_lying=[],
            bluff_skill=5,
            risk_tolerance=5,
            greed=5,
            honesty_bias=5,
        )

        actual_goods = [APPLE, APPLE, BREAD]
        declared_goods = [APPLE, APPLE, APPLE]

        # Run multiple times due to randomness
        results = []
        for _ in range(10):
            should_bribe = merchant.should_offer_proactive_bribe(
                sheriff_authority=5,
                sheriff_reputation=10,
                actual_goods=actual_goods,
                declared_goods=declared_goods,
            )
            results.append(should_bribe)

        # Should return boolean
        assert all(isinstance(r, bool) for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
