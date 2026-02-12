"""
Tests for Contraband Set Bonus System

Tests the bonus multipliers for smuggling multiple of the same contraband type.
"""

import pytest

from core.mechanics.contraband_bonus import (
    CONTRABAND_BONUS_MULTIPLIERS,
    calculate_contraband_bonus,
    get_best_contraband_for_set,
    should_redraw_for_contraband_set,
)
from core.mechanics.goods import APPLE, CHEESE, CROSSBOW, MEAD, PEPPER, SILK


class TestContrabandBonusCalculation:
    """Test contraband set bonus calculations."""

    def test_no_bonus_for_single_contraband(self):
        """Test that 1 contraband gets no bonus (1x multiplier)."""
        goods = [SILK]

        result = calculate_contraband_bonus(goods)

        base_value = SILK.value
        expected_multiplier = CONTRABAND_BONUS_MULTIPLIERS.get(1, 1.0)
        expected_bonus_value = int(base_value * expected_multiplier)

        assert result["base_value"] == base_value
        assert result["bonus_value"] == expected_bonus_value
        assert result["bonus_amount"] == expected_bonus_value - base_value
        assert result["sets"]["silk"]["multiplier"] == expected_multiplier

    def test_two_same_contraband_gets_bonus(self):
        """Test that 2 of same contraband gets bonus."""
        goods = [SILK, SILK]

        result = calculate_contraband_bonus(goods)

        base_value = SILK.value * 2
        expected_multiplier = CONTRABAND_BONUS_MULTIPLIERS.get(2, 1.0)
        expected_bonus_value = int(base_value * expected_multiplier)

        assert result["base_value"] == base_value
        assert result["bonus_value"] == expected_bonus_value
        assert result["bonus_amount"] == expected_bonus_value - base_value
        assert result["sets"]["silk"]["multiplier"] == expected_multiplier

    def test_three_same_contraband_gets_bonus(self):
        """Test that 3 of same contraband gets bonus."""
        goods = [MEAD, MEAD, MEAD]

        result = calculate_contraband_bonus(goods)

        base_value = MEAD.value * 3
        expected_multiplier = CONTRABAND_BONUS_MULTIPLIERS.get(3, 1.0)
        expected_bonus_value = int(base_value * expected_multiplier)

        assert result["base_value"] == base_value
        assert result["bonus_value"] == expected_bonus_value
        assert result["bonus_amount"] == expected_bonus_value - base_value
        assert result["sets"]["mead"]["multiplier"] == expected_multiplier

    def test_four_same_contraband_gets_bonus(self):
        """Test that 4 of same contraband gets bonus."""
        goods = [PEPPER, PEPPER, PEPPER, PEPPER]

        result = calculate_contraband_bonus(goods)

        base_value = PEPPER.value * 4
        expected_multiplier = CONTRABAND_BONUS_MULTIPLIERS.get(4, 1.0)
        expected_bonus_value = int(base_value * expected_multiplier)

        assert result["base_value"] == base_value
        assert result["bonus_value"] == expected_bonus_value
        assert result["bonus_amount"] == expected_bonus_value - base_value
        assert result["sets"]["pepper"]["multiplier"] == expected_multiplier

    def test_five_same_contraband_gets_bonus(self):
        """Test that 5 of same contraband gets bonus."""
        goods = [CROSSBOW, CROSSBOW, CROSSBOW, CROSSBOW, CROSSBOW]

        result = calculate_contraband_bonus(goods)

        base_value = CROSSBOW.value * 5
        expected_multiplier = CONTRABAND_BONUS_MULTIPLIERS.get(5, 1.0)
        expected_bonus_value = int(base_value * expected_multiplier)

        assert result["base_value"] == base_value
        assert result["bonus_value"] == expected_bonus_value
        assert result["bonus_amount"] == expected_bonus_value - base_value
        assert result["sets"]["crossbow"]["multiplier"] == expected_multiplier

    def test_mixed_contraband_no_bonus(self):
        """Test that mixed contraband types don't get set bonuses."""
        goods = [SILK, PEPPER, MEAD]

        result = calculate_contraband_bonus(goods)

        # Each gets 1x multiplier since they're all different
        base_value = SILK.value + PEPPER.value + MEAD.value
        expected_multiplier = CONTRABAND_BONUS_MULTIPLIERS.get(1, 1.0)
        # Each contraband is counted separately with 1x multiplier
        expected_bonus_value = int(
            SILK.value * expected_multiplier
            + PEPPER.value * expected_multiplier
            + MEAD.value * expected_multiplier
        )

        assert result["base_value"] == base_value
        assert result["bonus_value"] == expected_bonus_value
        assert result["bonus_amount"] == 0  # No bonus for mixed types

    def test_legal_goods_with_contraband_bonus(self):
        """Test that legal goods are counted but don't get bonuses."""
        goods = [APPLE, CHEESE, SILK, SILK]  # 2 legal + 2 silk

        result = calculate_contraband_bonus(goods)

        assert result["legal_value"] == 5  # 2 + 3
        assert result["contraband_base_value"] == 16  # 8 + 8
        assert result["contraband_bonus_value"] == 24  # 16 * 1.5
        assert result["base_value"] == 21  # 5 + 16
        assert result["bonus_value"] == 29  # 5 + 24
        assert result["bonus_amount"] == 8


class TestBestContrabandForSet:
    """Test logic for determining best contraband to collect."""

    def test_most_common_contraband_is_best(self):
        """Test that most common contraband is prioritized."""
        goods = [SILK, SILK, PEPPER]

        best_id, count, potential = get_best_contraband_for_set(goods)

        assert best_id == "silk"
        assert count == 2
        # 3 silk would be 24g * 2.0 = 48g

    def test_highest_value_breaks_ties(self):
        """Test that highest value contraband breaks ties."""
        goods = [SILK, CROSSBOW]  # Both have count 1, Crossbow is more valuable

        best_id, count, potential = get_best_contraband_for_set(goods)

        assert best_id == "crossbow"  # Higher value
        assert count == 1

    def test_empty_contraband_list(self):
        """Test handling of empty contraband list."""
        goods = []

        best_id, count, potential = get_best_contraband_for_set(goods)

        assert best_id is None
        assert count == 0


class TestShouldRedrawForContrabandSet:
    """Test logic for deciding to redraw for contraband sets."""

    def test_greedy_merchant_redraws_with_one_contraband(self):
        """Test that very greedy merchants redraw when they have 1 contraband."""
        hand = [SILK, APPLE, CHEESE, APPLE, CHEESE, APPLE, CHEESE]

        # Very greedy (greed=9) and bold (risk=8)
        should_redraw, num, target = should_redraw_for_contraband_set(
            hand, risk_tolerance=8, greed=9
        )

        assert should_redraw
        assert num > 0  # Should redraw some cards
        assert target == "silk"

    def test_not_greedy_enough_no_redraw(self):
        """Test that non-greedy merchants don't redraw for sets."""
        hand = [SILK, APPLE, CHEESE, APPLE, CHEESE, APPLE, CHEESE]

        # Not greedy enough (greed=5)
        should_redraw, num, target = should_redraw_for_contraband_set(
            hand, risk_tolerance=8, greed=5
        )

        assert not should_redraw
        assert num == 0

    def test_two_contraband_triggers_redraw(self):
        """Test that 2 of same contraband triggers redraw for greedy merchants."""
        hand = [MEAD, MEAD, APPLE, CHEESE, APPLE, CHEESE, APPLE]

        # Greedy (greed=7) and risky (risk=6)
        should_redraw, num, target = should_redraw_for_contraband_set(
            hand, risk_tolerance=6, greed=7
        )

        assert should_redraw
        assert target == "mead"

    def test_no_contraband_no_redraw(self):
        """Test that no contraband means no set redraw."""
        hand = [APPLE, CHEESE, APPLE, CHEESE, APPLE, CHEESE, APPLE]

        should_redraw, num, target = should_redraw_for_contraband_set(
            hand, risk_tolerance=10, greed=10
        )

        assert not should_redraw


class TestContrabandBonusEconomics:
    """Test the economic impact of contraband bonuses."""

    def test_five_crossbow_jackpot(self):
        """Test that 5 crossbows gives jackpot payout."""
        goods = [CROSSBOW] * 5

        result = calculate_contraband_bonus(goods)

        base_value = CROSSBOW.value * 5
        expected_multiplier = CONTRABAND_BONUS_MULTIPLIERS.get(5, 1.0)
        expected_bonus_value = int(base_value * expected_multiplier)

        assert result["bonus_value"] == expected_bonus_value
        assert result["bonus_amount"] == expected_bonus_value - base_value

    def test_specialization_vs_diversification(self):
        """Test that specializing in one contraband is more profitable."""
        # Specialized: 3 of same type
        specialized = [MEAD, MEAD, MEAD]
        specialized_result = calculate_contraband_bonus(specialized)

        # Diversified: 3 different types
        diversified = [SILK, PEPPER, MEAD]
        diversified_result = calculate_contraband_bonus(diversified)

        # Calculate expected values
        specialized_base = MEAD.value * 3
        specialized_multiplier = CONTRABAND_BONUS_MULTIPLIERS.get(3, 1.0)
        specialized_expected = int(specialized_base * specialized_multiplier)

        SILK.value + PEPPER.value + MEAD.value
        diversified_multiplier = CONTRABAND_BONUS_MULTIPLIERS.get(1, 1.0)
        diversified_expected = int(
            SILK.value * diversified_multiplier
            + PEPPER.value * diversified_multiplier
            + MEAD.value * diversified_multiplier
        )

        # Specialized should be more profitable due to set bonus
        assert specialized_result["bonus_value"] > diversified_result["bonus_value"]
        assert specialized_result["bonus_value"] == specialized_expected
        assert diversified_result["bonus_value"] == diversified_expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
