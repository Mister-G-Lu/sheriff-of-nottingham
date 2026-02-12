"""
Unit tests for core/end_game.py
Tests victory conditions, defeat states, and lore loading.
"""

import unittest
from unittest.mock import Mock, patch

from core.game.end_game import (
    EndGameState,
    _create_result,
    _load_lore,
    determine_end_game_state,
)


class TestEndGameStates(unittest.TestCase):
    """Test end game state determination."""

    def setUp(self):
        """Set up test fixtures."""
        self.sheriff = Mock()
        self.stats = Mock()

    def test_legendary_sheriff_victory(self):
        """Test legendary sheriff victory path (high rep + gold + catches)."""
        self.sheriff.reputation = 8
        self.stats.gold_earned = 60
        self.stats.bribes_accepted = 2
        self.stats.smugglers_caught = 5

        result = determine_end_game_state(self.sheriff, self.stats)

        self.assertEqual(result.state, EndGameState.LEGENDARY_SHERIFF)
        self.assertIn("LEGENDARY", result.title)
        self.assertIsInstance(result.flavor_text, list)

    def test_honorable_sheriff_victory(self):
        """Test honorable sheriff victory path (high rep + no bribes)."""
        self.sheriff.reputation = 9
        self.stats.gold_earned = 10
        self.stats.bribes_accepted = 0
        self.stats.smugglers_caught = 3

        result = determine_end_game_state(self.sheriff, self.stats)

        self.assertEqual(result.state, EndGameState.HONORABLE_SHERIFF)
        self.assertIn("HONORABLE", result.title)

    def test_corrupt_baron_victory(self):
        """Test corrupt baron victory path (low rep + high bribes + gold)."""
        self.sheriff.reputation = 2
        self.stats.gold_earned = 75
        self.stats.bribes_accepted = 8
        self.stats.smugglers_caught = 1

        result = determine_end_game_state(self.sheriff, self.stats)

        self.assertEqual(result.state, EndGameState.CORRUPT_BARON)
        self.assertIn("CORRUPT", result.title)

    def test_excellent_rating(self):
        """Test excellent performance rating."""
        self.sheriff.reputation = 7
        self.stats.gold_earned = 20
        self.stats.bribes_accepted = 1
        self.stats.smugglers_caught = 2

        result = determine_end_game_state(self.sheriff, self.stats)

        self.assertEqual(result.state, EndGameState.EXCELLENT)

    def test_good_rating(self):
        """Test good performance rating."""
        self.sheriff.reputation = 5
        self.stats.gold_earned = 15
        self.stats.bribes_accepted = 2
        self.stats.smugglers_caught = 1

        result = determine_end_game_state(self.sheriff, self.stats)

        self.assertEqual(result.state, EndGameState.GOOD)

    def test_mediocre_rating(self):
        """Test mediocre performance rating."""
        self.sheriff.reputation = 3
        self.stats.gold_earned = 5
        self.stats.bribes_accepted = 3
        self.stats.smugglers_caught = 0

        result = determine_end_game_state(self.sheriff, self.stats)

        self.assertEqual(result.state, EndGameState.MEDIOCRE)

    def test_poor_rating(self):
        """Test poor performance rating."""
        self.sheriff.reputation = 1
        self.stats.gold_earned = 2
        self.stats.bribes_accepted = 5
        self.stats.smugglers_caught = 0

        result = determine_end_game_state(self.sheriff, self.stats)

        self.assertEqual(result.state, EndGameState.POOR)

    def test_fired_game_over(self):
        """Test fired/game over state (reputation 0)."""
        self.sheriff.reputation = 0
        self.stats.gold_earned = 0
        self.stats.bribes_accepted = 10
        self.stats.smugglers_caught = 0

        result = determine_end_game_state(self.sheriff, self.stats)

        self.assertEqual(result.state, EndGameState.FIRED)
        self.assertIn("FIRED", result.title)


class TestLoreLoading(unittest.TestCase):
    """Test lore loading from JSON."""

    def test_load_lore_success(self):
        """Test successful lore loading."""
        lore = _load_lore()

        # Should return a dict (even if empty due to missing file in test)
        self.assertIsInstance(lore, dict)

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_load_lore_file_not_found(self, mock_open):
        """Test lore loading when file doesn't exist."""
        lore = _load_lore()

        # Should return empty dict on error
        self.assertEqual(lore, {})

    def test_create_result_helper(self):
        """Test _create_result helper function."""
        lore = {
            "test_state": {
                "title": "Test Title",
                "rating": "★★★★★",
                "paragraphs": ["Line 1", "Line 2"],
            }
        }

        result = _create_result(
            lore,
            "test_state",
            EndGameState.EXCELLENT,
            "Default Title",
            "★★★☆☆",
            ["Default text"],
        )

        self.assertEqual(result.state, EndGameState.EXCELLENT)
        self.assertEqual(result.title, "Test Title")
        self.assertEqual(result.rating, "★★★★★")
        self.assertEqual(result.flavor_text, ["Line 1", "Line 2"])

    def test_create_result_with_defaults(self):
        """Test _create_result uses defaults when lore key missing."""
        lore = {}

        result = _create_result(
            lore,
            "missing_key",
            EndGameState.GOOD,
            "Default Title",
            "★★★☆☆",
            ["Default text"],
        )

        self.assertEqual(result.title, "Default Title")
        self.assertEqual(result.rating, "★★★☆☆")
        self.assertEqual(result.flavor_text, ["Default text"])


class TestVictoryConditionEdgeCases(unittest.TestCase):
    """Test edge cases in victory condition logic."""

    def setUp(self):
        self.sheriff = Mock()
        self.stats = Mock()

    def test_legendary_requires_all_three_conditions(self):
        """Legendary requires high rep AND gold AND catches."""
        # Missing gold
        self.sheriff.reputation = 8
        self.stats.gold_earned = 30  # Too low
        self.stats.bribes_accepted = 0
        self.stats.smugglers_caught = 5

        result = determine_end_game_state(self.sheriff, self.stats)
        self.assertEqual(
            result.state, EndGameState.HONORABLE_SHERIFF
        )  # Falls through to honorable

    def test_honorable_requires_zero_bribes(self):
        """Honorable requires exactly 0 bribes."""
        self.sheriff.reputation = 8
        self.stats.gold_earned = 10
        self.stats.bribes_accepted = 1  # Even 1 bribe disqualifies
        self.stats.smugglers_caught = 2

        result = determine_end_game_state(self.sheriff, self.stats)
        self.assertEqual(
            result.state, EndGameState.EXCELLENT
        )  # Falls through to excellent

    def test_boundary_reputation_values(self):
        """Test reputation boundary values."""
        self.stats.gold_earned = 10
        self.stats.bribes_accepted = 1
        self.stats.smugglers_caught = 1

        # Test rep = 7 (excellent)
        self.sheriff.reputation = 7
        result = determine_end_game_state(self.sheriff, self.stats)
        self.assertEqual(result.state, EndGameState.EXCELLENT)

        # Test rep = 6 (good)
        self.sheriff.reputation = 6
        result = determine_end_game_state(self.sheriff, self.stats)
        self.assertEqual(result.state, EndGameState.GOOD)

        # Test rep = 4 (good)
        self.sheriff.reputation = 4
        result = determine_end_game_state(self.sheriff, self.stats)
        self.assertEqual(result.state, EndGameState.GOOD)

        # Test rep = 3 (mediocre)
        self.sheriff.reputation = 3
        result = determine_end_game_state(self.sheriff, self.stats)
        self.assertEqual(result.state, EndGameState.MEDIOCRE)


if __name__ == "__main__":
    unittest.main()
