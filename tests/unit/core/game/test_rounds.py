"""
Unit tests for core/game/rounds.py
Tests inspection resolution, lie detection, and contraband tracking.
"""

# Must be first import - sets up test environment
import unittest
from unittest.mock import Mock

import tests.test_setup  # noqa: F401
from core.game.rounds import (
    Declaration,
    RoundState,
    merchant_arrival,
    resolve_inspection,
)
from core.mechanics.goods import APPLE, CHEESE, PEPPER, SILK, Good
from core.players.merchants import Merchant

# Import test helpers
from tests.test_helpers import create_test_merchant, create_test_sheriff


class TestResolveInspection(unittest.TestCase):
    """Test inspection resolution logic."""

    def test_honest_declaration_no_inspection(self):
        """Test that honest declarations don't trigger inspection."""
        sheriff = create_test_sheriff(perception=5)
        merchant = create_test_merchant()
        decl = Declaration(good_id="apple", count=2)
        actual = [APPLE, APPLE]

        opens, caught = resolve_inspection(sheriff, merchant, decl, actual)

        self.assertFalse(opens)
        self.assertFalse(caught)

    def test_wrong_count_triggers_inspection(self):
        """Test that wrong count triggers inspection attempt."""
        sheriff = create_test_sheriff(perception=10)
        merchant = create_test_merchant(bluff_skill=1)
        decl = Declaration(good_id="apple", count=2)
        actual = [APPLE]  # Only 1, not 2

        # Mock rolls to ensure sheriff wins
        with unittest.mock.patch("core.game.rounds.random.randint", return_value=10):
            with unittest.mock.patch.object(merchant, "roll_bluff", return_value=1):
                opens, caught = resolve_inspection(sheriff, merchant, decl, actual)

        self.assertTrue(opens)
        self.assertTrue(caught)

    def test_wrong_good_type_triggers_inspection(self):
        """Test that wrong good type triggers inspection attempt."""
        sheriff = create_test_sheriff(perception=10)
        merchant = create_test_merchant(bluff_skill=1)
        decl = Declaration(good_id="apple", count=1)
        actual = [SILK]  # Declared apple, but has silk

        with unittest.mock.patch("core.game.rounds.random.randint", return_value=10):
            with unittest.mock.patch.object(merchant, "roll_bluff", return_value=1):
                opens, caught = resolve_inspection(sheriff, merchant, decl, actual)

        self.assertTrue(opens)
        self.assertTrue(caught)

    def test_merchant_bluff_succeeds(self):
        """Test merchant successfully bluffing past sheriff."""
        sheriff = create_test_sheriff(perception=1)
        merchant = create_test_merchant(bluff_skill=10)
        decl = Declaration(good_id="apple", count=1)
        actual = [SILK]

        # Force sheriff to roll low
        with unittest.mock.patch("core.game.rounds.random.randint", return_value=1):
            with unittest.mock.patch.object(merchant, "roll_bluff", return_value=20):
                opens, caught = resolve_inspection(sheriff, merchant, decl, actual)

        self.assertFalse(opens)
        self.assertFalse(caught)

    def test_sheriff_perception_bonus(self):
        """Test that sheriff's perception adds to roll."""
        sheriff = create_test_sheriff(perception=8)
        merchant = create_test_merchant(bluff_skill=5)
        decl = Declaration(good_id="apple", count=1)
        actual = [SILK]

        # Sheriff rolls 5 + 8 perception = 13, merchant rolls 10
        with unittest.mock.patch("core.game.rounds.random.randint", return_value=5):
            with unittest.mock.patch.object(merchant, "roll_bluff", return_value=10):
                opens, caught = resolve_inspection(sheriff, merchant, decl, actual)

        self.assertTrue(opens)  # 13 >= 10
        self.assertTrue(caught)


class TestContrabandTracking(unittest.TestCase):
    """Test contraband tracking in RoundState."""

    def test_contraband_recorded_when_bluff_succeeds(self):
        """Test that contraband is recorded when merchant bluffs successfully."""
        sheriff = create_test_sheriff(perception=1)
        merchant = create_test_merchant(bluff_skill=10)
        decl = Declaration(good_id="apple", count=1)
        actual = [SILK]  # Contraband

        round_state = RoundState(merchant=merchant, bag_actual=actual, declaration=decl)

        with unittest.mock.patch("core.game.rounds.random.randint", return_value=1):
            with unittest.mock.patch.object(merchant, "roll_bluff", return_value=20):
                opens, caught = resolve_inspection(
                    sheriff, merchant, decl, actual, round_state
                )

        self.assertFalse(opens)
        self.assertFalse(caught)
        self.assertEqual(round_state.contraband_passed_count, 1)
        self.assertEqual(round_state.contraband_passed_value, SILK.value)

    def test_multiple_contraband_items_tracked(self):
        """Test tracking multiple contraband items."""
        sheriff = create_test_sheriff(perception=1)
        merchant = create_test_merchant(bluff_skill=10)
        decl = Declaration(good_id="apple", count=3)
        from core.mechanics.goods import GoodKind

        actual = [
            SILK,
            PEPPER,
            Good(id="crossbow", name="Crossbow", kind=GoodKind.CONTRABAND, value=12),
        ]

        round_state = RoundState(merchant=merchant, bag_actual=actual, declaration=decl)

        with unittest.mock.patch("core.game.rounds.random.randint", return_value=1):
            with unittest.mock.patch.object(merchant, "roll_bluff", return_value=20):
                resolve_inspection(sheriff, merchant, decl, actual, round_state)

        self.assertEqual(round_state.contraband_passed_count, 3)
        expected_value = SILK.value + PEPPER.value + 12
        self.assertEqual(round_state.contraband_passed_value, expected_value)

    def test_mixed_legal_contraband_only_tracks_contraband(self):
        """Test that only contraband is tracked, not legal goods."""
        sheriff = create_test_sheriff(perception=1)
        merchant = create_test_merchant(bluff_skill=10)
        decl = Declaration(good_id="apple", count=3)
        actual = [APPLE, SILK, CHEESE]  # Legal, contraband, legal

        round_state = RoundState(merchant=merchant, bag_actual=actual, declaration=decl)

        with unittest.mock.patch("core.game.rounds.random.randint", return_value=1):
            with unittest.mock.patch.object(merchant, "roll_bluff", return_value=20):
                resolve_inspection(sheriff, merchant, decl, actual, round_state)

        # Only SILK is contraband
        self.assertEqual(round_state.contraband_passed_count, 1)
        self.assertEqual(round_state.contraband_passed_value, SILK.value)

    def test_no_contraband_tracking_when_caught(self):
        """Test that contraband is not tracked when sheriff catches the lie."""
        sheriff = create_test_sheriff(perception=10)
        merchant = create_test_merchant(bluff_skill=1)
        decl = Declaration(good_id="apple", count=1)
        actual = [SILK]

        round_state = RoundState(merchant=merchant, bag_actual=actual, declaration=decl)

        with unittest.mock.patch("core.game.rounds.random.randint", return_value=10):
            with unittest.mock.patch.object(merchant, "roll_bluff", return_value=1):
                opens, caught = resolve_inspection(
                    sheriff, merchant, decl, actual, round_state
                )

        self.assertTrue(opens)
        self.assertTrue(caught)
        # Contraband should NOT be tracked when caught
        self.assertEqual(round_state.contraband_passed_count, 0)
        self.assertEqual(round_state.contraband_passed_value, 0)

    def test_no_contraband_tracking_without_round_state(self):
        """Test that function works without RoundState parameter."""
        sheriff = create_test_sheriff(perception=1)
        merchant = create_test_merchant(bluff_skill=10)
        decl = Declaration(good_id="apple", count=1)
        actual = [SILK]

        with unittest.mock.patch("core.game.rounds.random.randint", return_value=1):
            with unittest.mock.patch.object(merchant, "roll_bluff", return_value=20):
                # Should not crash without round_state
                opens, caught = resolve_inspection(
                    sheriff, merchant, decl, actual, round_state=None
                )

        self.assertFalse(opens)
        self.assertFalse(caught)

    def test_merchant_record_round_result_called(self):
        """Test that merchant.record_round_result is called when contraband slips through."""
        sheriff = create_test_sheriff(perception=1)
        merchant = Mock(spec=Merchant)
        merchant.roll_bluff = Mock(return_value=20)
        merchant.record_round_result = Mock()

        decl = Declaration(good_id="apple", count=1)
        actual = [SILK]
        round_state = RoundState(merchant=merchant, bag_actual=actual, declaration=decl)

        with unittest.mock.patch("core.game.rounds.random.randint", return_value=1):
            resolve_inspection(sheriff, merchant, decl, actual, round_state)

        # Verify merchant was notified
        merchant.record_round_result.assert_called_once_with(round_state)

    def test_merchant_record_round_result_exception_handled(self):
        """Test that exceptions from merchant.record_round_result are handled gracefully."""
        sheriff = create_test_sheriff(perception=1)
        merchant = Mock(spec=Merchant)
        merchant.roll_bluff = Mock(return_value=20)
        merchant.record_round_result = Mock(
            side_effect=AttributeError("Not implemented")
        )

        decl = Declaration(good_id="apple", count=1)
        actual = [SILK]
        round_state = RoundState(merchant=merchant, bag_actual=actual, declaration=decl)

        with unittest.mock.patch("core.game.rounds.random.randint", return_value=1):
            # Should not crash even if merchant doesn't implement the method
            opens, caught = resolve_inspection(
                sheriff, merchant, decl, actual, round_state
            )

        self.assertFalse(opens)
        self.assertFalse(caught)


class TestRoundStateDataclass(unittest.TestCase):
    """Test RoundState dataclass."""

    def test_round_state_initialization(self):
        """Test RoundState can be initialized with defaults."""
        merchant = create_test_merchant()
        rs = RoundState(merchant=merchant)

        self.assertEqual(rs.merchant, merchant)
        self.assertIsNone(rs.declaration)
        self.assertEqual(rs.bribe, "")
        self.assertEqual(rs.bag_actual, [])
        self.assertFalse(rs.sheriff_opens)
        self.assertFalse(rs.sheriff_caught_lie)
        self.assertEqual(rs.contraband_passed_count, 0)
        self.assertEqual(rs.contraband_passed_value, 0)

    def test_round_state_with_all_fields(self):
        """Test RoundState with all fields set."""
        merchant = create_test_merchant()
        decl = Declaration(good_id="apple", count=2)
        goods = [APPLE, APPLE]

        rs = RoundState(
            merchant=merchant,
            declaration=decl,
            bribe="10 gold",
            bag_actual=goods,
            sheriff_opens=True,
            sheriff_caught_lie=True,
            contraband_passed_count=2,
            contraband_passed_value=14,
        )

        self.assertEqual(rs.merchant, merchant)
        self.assertEqual(rs.declaration, decl)
        self.assertEqual(rs.bribe, "10 gold")
        self.assertEqual(rs.bag_actual, goods)
        self.assertTrue(rs.sheriff_opens)
        self.assertTrue(rs.sheriff_caught_lie)
        self.assertEqual(rs.contraband_passed_count, 2)
        self.assertEqual(rs.contraband_passed_value, 14)


class TestDeclarationDataclass(unittest.TestCase):
    """Test Declaration dataclass."""

    def test_declaration_initialization(self):
        """Test Declaration initialization."""
        decl = Declaration(good_id="apple", count=5)

        self.assertEqual(decl.good_id, "apple")
        self.assertEqual(decl.count, 5)


class TestMerchantArrival(unittest.TestCase):
    """Test merchant_arrival UI hook."""

    def test_merchant_arrival_is_noop(self):
        """Test that merchant_arrival is a no-op function."""
        merchant = create_test_merchant()

        # Should not crash and return None
        result = merchant_arrival(merchant)

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
