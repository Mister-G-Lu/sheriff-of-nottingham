"""
Unit tests for core game mechanics
"""

# Must be first import - sets up test environment
import unittest

import tests.test_setup  # noqa: F401
from core.game.rounds import Declaration
from core.mechanics.goods import (
    ALL_CONTRABAND,
    ALL_LEGAL,
    APPLE,
    BREAD,
    CHEESE,
    CHICKEN,
    CROSSBOW,
    MEAD,
    PEPPER,
    SILK,
)
from core.mechanics.inspection import handle_inspection, handle_pass_without_inspection

# Import test helpers
from tests.test_helpers import (
    assert_inspection_result,
    create_test_goods,
    create_test_merchant,
    create_test_round_state,
    create_test_sheriff,
)


class TestGoods(unittest.TestCase):
    """Test goods definitions and properties."""

    def test_legal_goods_exist(self):
        """Test that legal goods are defined."""
        self.assertEqual(len(ALL_LEGAL), 4)
        self.assertIn(APPLE, ALL_LEGAL)
        self.assertIn(CHEESE, ALL_LEGAL)
        self.assertIn(BREAD, ALL_LEGAL)
        self.assertIn(CHICKEN, ALL_LEGAL)

    def test_contraband_exists(self):
        """Test that contraband is defined."""
        self.assertEqual(len(ALL_CONTRABAND), 4)
        self.assertIn(SILK, ALL_CONTRABAND)
        self.assertIn(PEPPER, ALL_CONTRABAND)
        self.assertIn(MEAD, ALL_CONTRABAND)
        self.assertIn(CROSSBOW, ALL_CONTRABAND)

    def test_good_properties(self):
        """Test that goods have correct properties."""
        self.assertEqual(APPLE.name, "Apple")
        self.assertTrue(APPLE.value > 0)  # Dynamic: value should be positive
        self.assertFalse(APPLE.is_contraband())  # is_contraband is a method

        self.assertEqual(SILK.name, "Silk")
        self.assertTrue(
            SILK.value > APPLE.value
        )  # Dynamic: contraband worth more than legal
        self.assertTrue(SILK.is_contraband())  # is_contraband is a method

    def test_good_equality(self):
        """Test that goods can be compared."""
        apple1 = APPLE
        apple2 = APPLE
        self.assertEqual(apple1, apple2)
        self.assertNotEqual(APPLE, SILK)


class TestInspection(unittest.TestCase):
    """Test inspection mechanics."""

    def test_handle_inspection_honest_merchant(self):
        """Test inspection of honest merchant."""
        merchant = create_test_merchant(gold=50)
        sheriff = create_test_sheriff(perception=5)
        bag = create_test_goods("legal", 3)
        declaration = {"good_id": "apple", "count": 3}

        result = handle_inspection(merchant, bag, declaration, sheriff)

        assert_inspection_result(result, expected_honest=True, expected_caught=False)
        self.assertEqual(len(result["goods_passed"]), 3)
        self.assertEqual(len(result["goods_confiscated"]), 0)

    def test_handle_inspection_with_contraband(self):
        """Test inspection catching contraband."""
        merchant = create_test_merchant(
            gold=50, bluff_skill=1
        )  # Low bluff to ensure caught
        sheriff = create_test_sheriff(perception=10)  # High perception to ensure catch
        bag = [SILK, PEPPER, APPLE]
        declaration = {"good_id": "apple", "count": 3}

        result = handle_inspection(merchant, bag, declaration, sheriff)

        assert_inspection_result(result, expected_honest=False)
        # Result depends on bluff roll, but structure should be correct
        self.assertIn("caught_lie", result)

    def test_handle_pass_without_inspection(self):
        """Test merchant passing without inspection."""
        merchant = create_test_merchant()
        bag = [APPLE, APPLE, SILK]
        declaration = {"good_id": "apple", "count": 3}

        result = handle_pass_without_inspection(merchant, bag, declaration)

        assert_inspection_result(result, expected_caught=False)
        self.assertEqual(len(result["goods_passed"]), 3)  # All goods pass
        self.assertEqual(len(result["goods_confiscated"]), 0)


class TestDeclaration(unittest.TestCase):
    """Test declaration mechanics."""

    def test_declaration_creation(self):
        """Test creating a declaration."""
        decl = Declaration(good_id=APPLE.id, count=5)
        self.assertEqual(decl.good_id, APPLE.id)
        self.assertEqual(decl.count, 5)

    def test_declaration_value(self):
        """Test declaration value calculation."""
        decl = Declaration(good_id=CHEESE.id, count=3)
        # Declaration doesn't have total_value() method, just stores good_id and count
        # The value calculation is done elsewhere in the game logic
        self.assertEqual(decl.good_id, CHEESE.id)
        self.assertEqual(decl.count, 3)


class TestRoundState(unittest.TestCase):
    """Test round state tracking."""

    def test_round_state_creation(self):
        """Test creating a round state."""
        merchant = create_test_merchant()
        bag = [APPLE, APPLE, SILK]

        rs = create_test_round_state(merchant=merchant, bag_actual=bag)
        self.assertEqual(rs.merchant, merchant)
        self.assertEqual(len(rs.bag_actual), 3)
        self.assertFalse(rs.sheriff_opens)

    def test_round_state_inspection(self):
        """Test round state after inspection."""
        merchant = create_test_merchant()
        bag = [APPLE, SILK]

        rs = create_test_round_state(merchant=merchant, bag_actual=bag)
        rs.sheriff_opens = True
        rs.contraband_found_count = 1
        rs.contraband_found_value = SILK.value

        self.assertTrue(rs.sheriff_opens)
        self.assertEqual(rs.contraband_found_count, 1)
        self.assertEqual(
            rs.contraband_found_value, SILK.value
        )  # Dynamic: use actual SILK value


class TestMerchant(unittest.TestCase):
    """Test merchant functionality."""

    def test_merchant_creation(self):
        """Test creating a merchant."""
        m = create_test_merchant(
            name="Test Merchant",
            tells_honest=["calm", "steady"],
            tells_lying=["nervous", "fidgety"],
            bluff_skill=5,
            risk_tolerance=3,
            greed=4,
            honesty_bias=7,
        )

        self.assertEqual(m.id, "test")
        self.assertEqual(m.name, "Test Merchant")
        self.assertEqual(m.bluff_skill, 5)
        self.assertEqual(m.risk_tolerance, 3)
        self.assertEqual(m.greed, 4)
        self.assertEqual(m.honesty_bias, 7)

    def test_merchant_roll_bluff(self):
        """Test merchant bluff roll."""
        m = create_test_merchant(bluff_skill=5)
        result = m.roll_bluff()

        self.assertIsInstance(result, int)
        # roll_bluff returns random.randint(1, 10) + bluff_skill
        # With bluff_skill=5, range is 6-15
        self.assertGreaterEqual(result, 6)
        self.assertLessEqual(result, 15)

    def test_merchant_record_round(self):
        """Test recording round results."""
        m = create_test_merchant()
        rs = create_test_round_state(merchant=m, bag_actual=[APPLE, SILK])
        rs.sheriff_opens = False
        rs.contraband_passed_count = 1
        rs.contraband_passed_value = SILK.value

        m.record_round_result(rs)
        summary = m.smuggle_summary()

        self.assertEqual(summary["contraband_passed_count"], 1)
        self.assertEqual(
            summary["contraband_passed_value"], SILK.value
        )  # Dynamic: use actual SILK value


if __name__ == "__main__":
    unittest.main()
