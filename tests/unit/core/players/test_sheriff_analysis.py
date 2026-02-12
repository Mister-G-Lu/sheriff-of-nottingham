"""
Unit tests for core/sheriff_analysis.py
Tests sheriff behavior analysis utilities.
"""

import unittest

from core.players.sheriff_analysis import analyze_sheriff_detailed, calculate_catch_rate


class TestCatchRateCalculation(unittest.TestCase):
    """Test simple catch rate calculation."""

    def test_empty_history(self):
        """Test with no history returns default 0.5."""
        result = calculate_catch_rate([])
        self.assertEqual(result, 0.5)

    def test_all_lies_caught(self):
        """Test 100% catch rate."""
        history = [
            {
                "declaration": {"good_id": "apple", "count": 2},
                "actual_ids": ["silk", "silk"],
                "caught_lie": True,
                "opened": True,
            },
            {
                "declaration": {"good_id": "cheese", "count": 1},
                "actual_ids": ["pepper"],
                "caught_lie": True,
                "opened": True,
            },
        ]

        result = calculate_catch_rate(history)
        self.assertEqual(result, 1.0)

    def test_no_lies_caught(self):
        """Test 0% catch rate."""
        history = [
            {
                "declaration": {"good_id": "apple", "count": 2},
                "actual_ids": ["silk", "silk"],
                "caught_lie": False,
                "opened": False,
            },
            {
                "declaration": {"good_id": "cheese", "count": 1},
                "actual_ids": ["pepper"],
                "caught_lie": False,
                "opened": False,
            },
        ]

        result = calculate_catch_rate(history)
        self.assertEqual(result, 0.0)

    def test_partial_catch_rate(self):
        """Test 50% catch rate."""
        history = [
            {
                "declaration": {"good_id": "apple", "count": 2},
                "actual_ids": ["silk", "silk"],
                "caught_lie": True,
                "opened": True,
            },
            {
                "declaration": {"good_id": "cheese", "count": 1},
                "actual_ids": ["pepper"],
                "caught_lie": False,
                "opened": False,
            },
        ]

        result = calculate_catch_rate(history)
        self.assertEqual(result, 0.5)

    def test_honest_merchants_ignored(self):
        """Test that honest merchants don't affect catch rate."""
        history = [
            {
                "declaration": {"good_id": "apple", "count": 2},
                "actual_ids": ["apple", "apple"],
                "caught_lie": False,
                "opened": False,
            },
            {
                "declaration": {"good_id": "cheese", "count": 1},
                "actual_ids": ["pepper"],
                "caught_lie": True,
                "opened": True,
            },
        ]

        result = calculate_catch_rate(history)
        self.assertEqual(result, 1.0)  # 1 lie, 1 caught = 100%

    def test_no_lies_in_history(self):
        """Test when all merchants were honest."""
        history = [
            {
                "declaration": {"good_id": "apple", "count": 2},
                "actual_ids": ["apple", "apple"],
                "caught_lie": False,
                "opened": False,
            }
        ]

        result = calculate_catch_rate(history)
        self.assertEqual(result, 0.5)  # Default when no lies


class TestDetailedAnalysis(unittest.TestCase):
    """Test detailed sheriff behavior analysis."""

    def test_empty_history_defaults(self):
        """Test empty history returns default values."""
        result = analyze_sheriff_detailed([])

        self.assertEqual(result["inspection_rate"], 0.5)
        self.assertEqual(result["catch_rate"], 0.5)
        self.assertEqual(result["total_rounds"], 0)
        self.assertEqual(result["lies_caught"], 0)
        self.assertEqual(result["lies_successful"], 0)
        self.assertEqual(result["truths_inspected"], 0)

    def test_all_metrics_calculated(self):
        """Test all metrics are calculated correctly."""
        history = [
            # Honest merchant, inspected
            {
                "declaration": {"good_id": "apple", "count": 2},
                "actual_ids": ["apple", "apple"],
                "caught_lie": False,
                "opened": True,
            },
            # Liar, caught
            {
                "declaration": {"good_id": "cheese", "count": 1},
                "actual_ids": ["silk"],
                "caught_lie": True,
                "opened": True,
            },
            # Liar, not caught
            {
                "declaration": {"good_id": "bread", "count": 2},
                "actual_ids": ["pepper", "pepper"],
                "caught_lie": False,
                "opened": False,
            },
            # Honest merchant, not inspected
            {
                "declaration": {"good_id": "chicken", "count": 1},
                "actual_ids": ["chicken"],
                "caught_lie": False,
                "opened": False,
            },
        ]

        result = analyze_sheriff_detailed(history)

        self.assertEqual(result["total_rounds"], 4)
        self.assertEqual(result["lies_caught"], 1)
        self.assertEqual(result["lies_successful"], 1)
        self.assertEqual(result["truths_inspected"], 1)
        self.assertEqual(result["inspection_rate"], 0.5)  # 2 inspections / 4 rounds
        self.assertEqual(result["catch_rate"], 0.5)  # 1 caught / 2 lies

    def test_inspection_rate_calculation(self):
        """Test inspection rate is calculated correctly."""
        history = [
            {
                "declaration": {"good_id": "apple", "count": 1},
                "actual_ids": ["apple"],
                "caught_lie": False,
                "opened": True,
            },
            {
                "declaration": {"good_id": "cheese", "count": 1},
                "actual_ids": ["cheese"],
                "caught_lie": False,
                "opened": False,
            },
            {
                "declaration": {"good_id": "bread", "count": 1},
                "actual_ids": ["bread"],
                "caught_lie": False,
                "opened": False,
            },
            {
                "declaration": {"good_id": "chicken", "count": 1},
                "actual_ids": ["chicken"],
                "caught_lie": False,
                "opened": False,
            },
        ]

        result = analyze_sheriff_detailed(history)

        # 1 inspection out of 4 rounds = 25%
        self.assertEqual(result["inspection_rate"], 0.25)

    def test_aggressive_sheriff(self):
        """Test analysis of aggressive sheriff (inspects everyone)."""
        history = [
            {
                "declaration": {"good_id": "apple", "count": 1},
                "actual_ids": ["silk"],
                "caught_lie": True,
                "opened": True,
            },
            {
                "declaration": {"good_id": "cheese", "count": 1},
                "actual_ids": ["cheese"],
                "caught_lie": False,
                "opened": True,
            },
            {
                "declaration": {"good_id": "bread", "count": 1},
                "actual_ids": ["pepper"],
                "caught_lie": True,
                "opened": True,
            },
        ]

        result = analyze_sheriff_detailed(history)

        self.assertEqual(result["inspection_rate"], 1.0)  # Inspected all
        self.assertEqual(result["catch_rate"], 1.0)  # Caught all liars

    def test_lenient_sheriff(self):
        """Test analysis of lenient sheriff (never inspects)."""
        history = [
            {
                "declaration": {"good_id": "apple", "count": 1},
                "actual_ids": ["silk"],
                "caught_lie": False,
                "opened": False,
            },
            {
                "declaration": {"good_id": "cheese", "count": 1},
                "actual_ids": ["pepper"],
                "caught_lie": False,
                "opened": False,
            },
        ]

        result = analyze_sheriff_detailed(history)

        self.assertEqual(result["inspection_rate"], 0.0)  # Never inspected
        self.assertEqual(result["catch_rate"], 0.0)  # Caught no one


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""

    def test_mismatched_count_is_lie(self):
        """Test that mismatched count is detected as a lie."""
        history = [
            {
                "declaration": {"good_id": "apple", "count": 3},
                "actual_ids": ["apple", "apple"],  # Only 2, not 3
                "caught_lie": True,
                "opened": True,
            }
        ]

        result = calculate_catch_rate(history)
        self.assertEqual(result, 1.0)

    def test_mixed_goods_is_lie(self):
        """Test that mixed goods (even if legal) is a lie."""
        history = [
            {
                "declaration": {"good_id": "apple", "count": 2},
                "actual_ids": ["apple", "cheese"],  # Mixed legal goods
                "caught_lie": True,
                "opened": True,
            }
        ]

        result = calculate_catch_rate(history)
        self.assertEqual(result, 1.0)


if __name__ == "__main__":
    unittest.main()
