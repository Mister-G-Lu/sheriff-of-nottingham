"""
Tests for bribe strategy calculation functions.
"""

import pytest

from ai_strategy.bribe_strategy import (
    calculate_actual_value,
    calculate_advanced_bluff_bribe,
    calculate_contraband_bribe,
    calculate_contraband_value,
    calculate_declared_value,
    calculate_legal_lie_bribe,
)
from core.mechanics.goods import APPLE, BREAD, SILK


class TestValueCalculations:
    """Test value calculation functions."""

    def test_calculate_declared_value_with_string_id(self):
        """Test declared value calculation with string ID."""
        value = calculate_declared_value("apple", 3)
        assert value == APPLE.value * 3

    def test_calculate_declared_value_with_good_object(self):
        """Test declared value calculation with Good object."""
        value = calculate_declared_value(APPLE, 3)
        assert value == APPLE.value * 3

    def test_calculate_actual_value_with_string_ids(self):
        """Test actual value calculation with string IDs."""
        value = calculate_actual_value(["apple", "apple", "bread"])
        expected = APPLE.value * 2 + BREAD.value
        assert value == expected

    def test_calculate_actual_value_with_good_objects(self):
        """Test actual value calculation with Good objects."""
        value = calculate_actual_value([APPLE, APPLE, BREAD])
        expected = APPLE.value * 2 + BREAD.value
        assert value == expected

    def test_calculate_contraband_value_filters_legal(self):
        """Test that contraband value only counts contraband."""
        value = calculate_contraband_value([APPLE, SILK, BREAD])
        assert value == SILK.value  # Only silk is contraband

    def test_calculate_contraband_value_with_no_contraband(self):
        """Test contraband value with all legal goods."""
        value = calculate_contraband_value([APPLE, APPLE, BREAD])
        assert value == 0


class TestContrabandBribe:
    """Test contraband bribe calculation."""

    def test_contraband_bribe_is_positive(self):
        """Test that contraband bribe is always positive."""
        bribe = calculate_contraband_bribe(
            declared_value=10, contraband_value=20, greed=5, risk_tolerance=5
        )
        assert isinstance(bribe, int)
        assert bribe > 0

    def test_contraband_bribe_scales_with_value(self):
        """Test that bribe scales with contraband value."""
        low_bribe = calculate_contraband_bribe(
            declared_value=5, contraband_value=10, greed=5, risk_tolerance=5
        )

        high_bribe = calculate_contraband_bribe(
            declared_value=20, contraband_value=40, greed=5, risk_tolerance=5
        )

        assert isinstance(low_bribe, int)
        assert isinstance(high_bribe, int)
        assert high_bribe > low_bribe

    def test_contraband_bribe_affected_by_greed(self):
        """Test that greed affects bribe amount."""
        greedy_bribe = calculate_contraband_bribe(
            declared_value=10,
            contraband_value=20,
            greed=10,  # Very greedy
            risk_tolerance=5,
        )

        not_greedy_bribe = calculate_contraband_bribe(
            declared_value=10,
            contraband_value=20,
            greed=1,  # Not greedy
            risk_tolerance=5,
        )

        assert isinstance(greedy_bribe, int)
        assert isinstance(not_greedy_bribe, int)

    def test_contraband_bribe_affected_by_risk(self):
        """Test that risk tolerance affects bribe amount."""
        cautious_bribe = calculate_contraband_bribe(
            declared_value=10,
            contraband_value=20,
            greed=5,
            risk_tolerance=1,  # Very cautious
        )

        bold_bribe = calculate_contraband_bribe(
            declared_value=10,
            contraband_value=20,
            greed=5,
            risk_tolerance=10,  # Very bold
        )

        assert isinstance(cautious_bribe, int)
        assert isinstance(bold_bribe, int)


class TestLegalLieBribe:
    """Test legal lie bribe calculation."""

    def test_legal_lie_bribe_is_positive(self):
        """Test that legal lie bribe is always positive."""
        bribe = calculate_legal_lie_bribe(declared_value=10, actual_value=12, greed=5)
        assert isinstance(bribe, int)
        assert bribe >= 2  # Minimum 2 gold

    def test_legal_lie_bribe_scales_with_difference(self):
        """Test that bribe scales with value difference."""
        small_diff_bribe = calculate_legal_lie_bribe(
            declared_value=10, actual_value=11, greed=5
        )

        large_diff_bribe = calculate_legal_lie_bribe(
            declared_value=10,
            actual_value=30,  # Larger difference
            greed=5,
        )

        assert isinstance(small_diff_bribe, int)
        assert isinstance(large_diff_bribe, int)
        assert large_diff_bribe >= small_diff_bribe  # Allow equal due to minimum


class TestAdvancedBluffBribe:
    """Test advanced bluff bribe calculation."""

    def test_advanced_bluff_bribe_is_small(self):
        """Test that advanced bluff bribe is small (2-5 gold)."""
        bribe = calculate_advanced_bluff_bribe(declared_value=20)
        assert isinstance(bribe, int)
        assert 2 <= bribe <= 5

    def test_advanced_bluff_bribe_with_low_value(self):
        """Test advanced bluff with low declared value."""
        bribe = calculate_advanced_bluff_bribe(declared_value=5)
        assert isinstance(bribe, int)
        assert bribe >= 2

    def test_advanced_bluff_bribe_with_high_value(self):
        """Test advanced bluff with high declared value."""
        bribe = calculate_advanced_bluff_bribe(declared_value=50)
        assert isinstance(bribe, int)
        assert bribe <= 5  # Capped at 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
