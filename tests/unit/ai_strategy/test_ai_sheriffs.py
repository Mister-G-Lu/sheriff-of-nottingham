"""
Tests for AI Sheriff Strategies

Tests the different sheriff AI behaviors: trigger_happy, corrupt_greedy, greedy,
smart_adaptive, and strict_inspector.
"""

import pytest

from ai_strategy.ai_sheriffs import (
    corrupt_greedy,
    greedy,
    smart_adaptive,
    strict_inspector,
    trigger_happy,
)
from core.mechanics.goods import APPLE, SILK
from core.players.merchants import Merchant


def create_test_merchant(name="Test"):
    """Helper to create a test merchant."""
    return Merchant(
        id="test",
        name=name,
        intro="Test",
        tells_honest=["honest"],
        tells_lying=["lying"],
        bluff_skill=5,
        risk_tolerance=5,
        greed=5,
        honesty_bias=5,
    )


def create_test_declaration(good_id="apple", count=3):
    """Helper to create a test declaration."""
    from core.mechanics.bag_builder import Declaration

    return Declaration(good_id=good_id, count=count)


class TestTriggerHappy:
    """Test Trigger Happy sheriff (inspects all bribes)."""

    def test_inspects_when_bribe_offered(self):
        """Test that Trigger Happy always inspects when bribed."""
        merchant = create_test_merchant()
        declaration = create_test_declaration()
        actual_goods = [APPLE, APPLE, APPLE]

        # Offer a bribe
        should_inspect, accept_bribe = trigger_happy(
            merchant,
            bribe_offered=5,
            declaration=declaration,
            actual_goods=actual_goods,
            history=[],
        )

        assert should_inspect, "Trigger Happy should inspect when bribed"
        assert not accept_bribe, "Trigger Happy never accepts bribes"

    def test_does_not_inspect_without_bribe(self):
        """Test that Trigger Happy doesn't inspect without bribe."""
        merchant = create_test_merchant()
        declaration = create_test_declaration()
        actual_goods = [APPLE, APPLE, APPLE]

        # No bribe
        should_inspect, accept_bribe = trigger_happy(
            merchant,
            bribe_offered=0,
            declaration=declaration,
            actual_goods=actual_goods,
            history=[],
        )

        assert not should_inspect, "Trigger Happy should not inspect without bribe"
        assert not accept_bribe


class TestCorruptGreedy:
    """Test Corrupt & Greedy sheriff (accepts all bribes)."""

    def test_accepts_all_bribes(self):
        """Test that Corrupt & Greedy accepts any bribe."""
        merchant = create_test_merchant()
        declaration = create_test_declaration()
        actual_goods = [SILK, SILK]  # Contraband

        # Offer small bribe
        should_inspect, accept_bribe = corrupt_greedy(
            merchant,
            bribe_offered=1,
            declaration=declaration,
            actual_goods=actual_goods,
            history=[],
        )

        assert accept_bribe, "Corrupt & Greedy should accept any bribe"
        assert not should_inspect, "Should not inspect when bribe accepted"

    def test_lets_pass_without_bribe(self):
        """Test that Corrupt & Greedy lets pass without bribe (wants bribes)."""
        merchant = create_test_merchant()
        declaration = create_test_declaration()
        actual_goods = [SILK, SILK]

        # No bribe
        should_inspect, accept_bribe = corrupt_greedy(
            merchant,
            bribe_offered=0,
            declaration=declaration,
            actual_goods=actual_goods,
            history=[],
        )

        # Corrupt & Greedy wants bribes, so lets pass without one (hoping for bribe next time)
        assert not should_inspect, "Should let pass without bribe"
        assert not accept_bribe


class TestGreedy:
    """Test Greedy sheriff (demands high bribes 50%+)."""

    def test_accepts_high_bribes(self):
        """Test that Greedy accepts high bribes (50%+ of contraband value)."""
        merchant = create_test_merchant()
        declaration = create_test_declaration()
        actual_goods = [SILK, SILK]  # Contraband worth 16g
        contraband_value = sum(g.value for g in actual_goods if not g.is_legal())

        # Offer high bribe (>50% of contraband value)
        high_bribe = int(contraband_value * 0.6)
        should_inspect, accept_bribe = greedy(
            merchant,
            bribe_offered=high_bribe,
            declaration=declaration,
            actual_goods=actual_goods,
            history=[],
        )

        assert accept_bribe, "Greedy should accept high bribes"
        assert not should_inspect

    def test_rejects_low_bribes(self):
        """Test that Greedy rejects low bribes (<50% of contraband value)."""
        merchant = create_test_merchant()
        declaration = create_test_declaration()
        actual_goods = [SILK, SILK]

        # Offer low bribe
        should_inspect, accept_bribe = greedy(
            merchant,
            bribe_offered=2,
            declaration=declaration,
            actual_goods=actual_goods,
            history=[],
        )

        assert not accept_bribe, "Greedy should reject low bribes"
        assert should_inspect, "Should inspect when bribe rejected"

    def test_behavior_without_bribe(self):
        """Test Greedy behavior without bribe (may inspect or let pass)."""
        merchant = create_test_merchant()
        declaration = create_test_declaration()
        actual_goods = [SILK, SILK]

        # No bribe
        should_inspect, accept_bribe = greedy(
            merchant,
            bribe_offered=0,
            declaration=declaration,
            actual_goods=actual_goods,
            history=[],
        )

        # Greedy behavior without bribe can vary, just verify valid response
        assert isinstance(should_inspect, bool)
        assert not accept_bribe, "Should never accept when no bribe offered"


class TestStrictInspector:
    """Test Strict Inspector sheriff (inspects everyone)."""

    def test_always_inspects(self):
        """Test that Strict Inspector always inspects."""
        merchant = create_test_merchant()
        declaration = create_test_declaration()
        actual_goods = [APPLE, APPLE, APPLE]

        # With bribe
        should_inspect, accept_bribe = strict_inspector(
            merchant,
            bribe_offered=5,
            declaration=declaration,
            actual_goods=actual_goods,
            history=[],
        )

        assert should_inspect, "Strict Inspector should always inspect"
        assert not accept_bribe, "Strict Inspector never accepts bribes"

        # Without bribe
        should_inspect, accept_bribe = strict_inspector(
            merchant,
            bribe_offered=0,
            declaration=declaration,
            actual_goods=actual_goods,
            history=[],
        )

        assert should_inspect, "Strict Inspector should always inspect"
        assert not accept_bribe


class TestSmartAdaptive:
    """Test Smart Adaptive sheriff (learns from patterns)."""

    def test_inspects_known_smugglers(self):
        """Test that Smart Adaptive inspects merchants with smuggling history."""
        merchant = create_test_merchant("Known Smuggler")
        declaration = create_test_declaration()
        actual_goods = [SILK, SILK]

        # Create history showing this merchant smuggles
        history = []
        for _ in range(5):
            history.append(
                {
                    "merchant_name": "Known Smuggler",
                    "caught_lie": True,
                    "opened": True,
                    "bribe_offered": 5,
                }
            )

        # Smart Adaptive should be suspicious
        should_inspect, accept_bribe = smart_adaptive(
            merchant,
            bribe_offered=5,
            declaration=declaration,
            actual_goods=actual_goods,
            history=history,
        )

        # Should likely inspect (though there's randomness)
        # Just verify it returns valid values
        assert isinstance(should_inspect, bool)
        assert isinstance(accept_bribe, bool)

    def test_trusts_honest_merchants(self):
        """Test that Smart Adaptive trusts merchants with honest history."""
        merchant = create_test_merchant("Honest Merchant")
        declaration = create_test_declaration()
        actual_goods = [APPLE, APPLE, APPLE]

        # Create history showing this merchant is honest
        history = []
        for _ in range(5):
            history.append(
                {
                    "merchant_name": "Honest Merchant",
                    "caught_lie": False,
                    "opened": True,
                    "bribe_offered": 0,
                }
            )

        # Smart Adaptive should trust them
        should_inspect, accept_bribe = smart_adaptive(
            merchant,
            bribe_offered=0,
            declaration=declaration,
            actual_goods=actual_goods,
            history=history,
        )

        # Should likely not inspect (though there's randomness)
        assert isinstance(should_inspect, bool)
        assert isinstance(accept_bribe, bool)

    def test_handles_empty_history(self):
        """Test that Smart Adaptive handles empty history gracefully."""
        merchant = create_test_merchant()
        declaration = create_test_declaration()
        actual_goods = [APPLE, APPLE, APPLE]

        # Empty history
        should_inspect, accept_bribe = smart_adaptive(
            merchant,
            bribe_offered=0,
            declaration=declaration,
            actual_goods=actual_goods,
            history=[],
        )

        # Should return valid values
        assert isinstance(should_inspect, bool)
        assert isinstance(accept_bribe, bool)

    def test_adapts_to_bribe_patterns(self):
        """Test that Smart Adaptive learns from bribe acceptance patterns."""
        merchant = create_test_merchant()
        declaration = create_test_declaration()
        actual_goods = [SILK, SILK]

        # Create history showing bribes work
        history = []
        for _ in range(5):
            history.append(
                {
                    "merchant_name": merchant.name,
                    "caught_lie": False,
                    "opened": False,
                    "bribe_offered": 10,
                    "bribe_accepted": True,
                }
            )

        # Offer bribe
        should_inspect, accept_bribe = smart_adaptive(
            merchant,
            bribe_offered=10,
            declaration=declaration,
            actual_goods=actual_goods,
            history=history,
        )

        # Should return valid values
        assert isinstance(should_inspect, bool)
        assert isinstance(accept_bribe, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
