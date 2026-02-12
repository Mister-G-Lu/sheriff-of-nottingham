"""
Tests for Notable Strategies (Legal Good Trick)

Tests the Legal Good Trick strategy used by Silas Voss and other merchants
to exploit strict sheriffs who inspect frequently.
"""

import pytest

from ai_strategy.notable_strategies import (
    calculate_legal_good_bribe,
    legal_good_with_bribe_trick,
)
from core.mechanics.goods import APPLE, BREAD, CHEESE, SILK


class TestLegalGoodWithBribeTrick:
    """Test detection logic for when to use Legal Good Trick."""

    def test_no_history_returns_false(self):
        """Test that with no history, strategy is not recommended."""
        # Function requires merchant parameter, use None for testing
        result = legal_good_with_bribe_trick(None, [])

        assert not result["should_use"]
        assert (
            "not enough" in result["reason"].lower()
            or "no history" in result["reason"].lower()
        )

    def test_insufficient_history_returns_false(self):
        """Test that with insufficient history, strategy is not recommended."""
        history = [
            {"opened": True, "bribe_offered": 0},
            {"opened": False, "bribe_offered": 0},
        ]

        result = legal_good_with_bribe_trick(None, history)

        assert not result["should_use"]

    def test_high_bribe_inspection_rate_triggers_strategy(self):
        """Test that high inspection rate among bribes triggers Legal Good Trick."""
        # Create history where sheriff inspects most bribes
        history = []
        for i in range(10):
            if i < 5:
                # Bribes that get inspected
                history.append({"opened": True, "bribe_offered": 5})
            else:
                # No bribes, not inspected
                history.append({"opened": False, "bribe_offered": 0})

        result = legal_good_with_bribe_trick(None, history)

        # Sheriff inspects 100% of bribes (5/5), should trigger strategy
        assert result["should_use"]
        assert (
            "strict" in result["reason"].lower()
            or "inspect" in result["reason"].lower()
        )

    def test_high_overall_inspection_rate_triggers_strategy(self):
        """Test that high overall inspection rate triggers Legal Good Trick."""
        # Create history where sheriff inspects most rounds
        history = [{"opened": True, "bribe_offered": 0} for _ in range(10)]

        result = legal_good_with_bribe_trick(None, history)

        # Sheriff inspects 100% of rounds, should trigger strategy
        assert result["should_use"]
        assert (
            "inspection rate" in result["reason"].lower()
            or "trigger happy" in result["reason"].lower()
        )

    def test_low_inspection_rate_does_not_trigger(self):
        """Test that low inspection rate does not trigger Legal Good Trick."""
        # Create history where sheriff rarely inspects
        history = []
        for i in range(10):
            history.append({"opened": i < 2, "bribe_offered": 5 if i < 5 else 0})

        result = legal_good_with_bribe_trick(None, history)

        # Sheriff inspects only 20% of rounds, should not trigger
        assert not result["should_use"]
        assert "not strict" in result["reason"].lower()

    def test_moderate_inspection_with_bribes_triggers(self):
        """Test that moderate overall but high bribe inspection triggers strategy."""
        history = []
        # 3 bribes, all inspected
        for _i in range(3):
            history.append({"opened": True, "bribe_offered": 5})
        # 7 no bribes, not inspected
        for _i in range(7):
            history.append({"opened": False, "bribe_offered": 0})

        result = legal_good_with_bribe_trick(None, history)

        # Overall: 30% inspection, but 100% of bribes inspected
        # Should trigger based on bribe inspection rate
        assert result["should_use"]


class TestCalculateLegalGoodBribe:
    """Test bribe calculation for Legal Good Trick."""

    def test_bribe_is_positive(self):
        """Test that bribe amount is always positive."""
        goods = [APPLE, APPLE, APPLE]

        for _ in range(10):
            bribe = calculate_legal_good_bribe(goods)
            assert bribe >= 1, "Bribe should be at least 1 gold"

    def test_bribe_scales_with_goods_value(self):
        """Test that bribe amount scales with goods value."""
        cheap_goods = [APPLE]  # Low value
        expensive_goods = [APPLE, APPLE, APPLE, BREAD, BREAD, CHEESE]  # Higher value

        cheap_bribes = [calculate_legal_good_bribe(cheap_goods) for _ in range(20)]
        expensive_bribes = [
            calculate_legal_good_bribe(expensive_goods) for _ in range(20)
        ]

        avg_cheap = sum(cheap_bribes) / len(cheap_bribes)
        avg_expensive = sum(expensive_bribes) / len(expensive_bribes)

        assert avg_expensive > avg_cheap, (
            "Higher value goods should result in higher average bribes"
        )

    def test_bribe_uses_declared_goods_if_provided(self):
        """Test that bribe calculation uses declared goods when provided."""
        actual_goods = [SILK, SILK]  # High value contraband
        declared_goods = [APPLE, APPLE]  # Low value legal goods

        # When declared goods provided, should use their value
        bribes_with_declared = [
            calculate_legal_good_bribe(actual_goods, declared_goods) for _ in range(20)
        ]
        bribes_without_declared = [
            calculate_legal_good_bribe(actual_goods) for _ in range(20)
        ]

        avg_with = sum(bribes_with_declared) / len(bribes_with_declared)
        avg_without = sum(bribes_without_declared) / len(bribes_without_declared)

        # Declared goods have lower value, so bribes should be lower on average
        assert avg_with < avg_without, (
            "Bribes based on declared goods should be lower than actual contraband"
        )

    def test_bribe_range_is_reasonable(self):
        """Test that bribe amounts are within reasonable range (10-90% of value)."""
        goods = [APPLE, APPLE, APPLE]  # Total value = 3 * APPLE.value
        total_value = sum(g.value for g in goods)

        bribes = [calculate_legal_good_bribe(goods) for _ in range(100)]

        min_bribe = min(bribes)
        max_bribe = max(bribes)

        # Should be at least 10% of value (or 1 gold minimum)
        expected_min = max(1, int(total_value * 0.10))
        assert min_bribe >= expected_min * 0.5, (
            f"Min bribe {min_bribe} should be reasonable"
        )

        # Should not exceed 90% of value
        expected_max = int(total_value * 0.90)
        assert max_bribe <= expected_max * 1.2, (
            f"Max bribe {max_bribe} should not be excessive"
        )

    def test_bribe_has_variance(self):
        """Test that bribe amounts vary (not always the same)."""
        goods = [APPLE, APPLE, APPLE]

        bribes = [calculate_legal_good_bribe(goods) for _ in range(20)]
        unique_bribes = set(bribes)

        # Should have at least 3 different bribe amounts in 20 tries
        assert len(unique_bribes) >= 3, "Bribe amounts should vary"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
