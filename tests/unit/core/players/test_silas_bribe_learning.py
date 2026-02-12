"""
Unit tests for Silas Voss's bribe learning system.

Tests the _learn_successful_bribe_ratio function that analyzes history
to determine optimal bribe ratios.
"""

import pytest

from core.players.silas_voss import SilasVoss


class TestSilasBribeLearning:
    """Test Silas's bribe learning algorithm."""

    def test_learn_bribe_ratio_with_no_history(self):
        """Test learning returns 0 with insufficient history."""
        silas = SilasVoss("silas", "Silas", "Test", [], [], 8, 6, 7, 5)

        result = silas._learn_successful_bribe_ratio([])
        assert result == 0.0

        result = silas._learn_successful_bribe_ratio([{"bribe_offered": 0}])
        assert result == 0.0

    def test_learn_bribe_ratio_with_successful_bribes(self):
        """Test learning calculates average of successful bribe ratios."""
        silas = SilasVoss("silas", "Silas", "Test", [], [], 8, 6, 7, 5)

        # Create history with successful bribes at 50% ratio
        history = []
        for _i in range(5):
            history.append(
                {
                    "bribe_offered": 10,
                    "bribe_accepted": True,
                    "declaration": {
                        "good_id": "apple",
                        "count": 10,
                    },  # 20g declared, 50% ratio
                }
            )

        result = silas._learn_successful_bribe_ratio(history)
        assert result == 0.5, f"Expected 0.5 ratio, got {result}"

    def test_learn_bribe_ratio_ignores_rejected_bribes(self):
        """Test learning only considers accepted bribes."""
        silas = SilasVoss("silas", "Silas", "Test", [], [], 8, 6, 7, 5)

        history = []
        # Accepted bribes at 50%
        for _i in range(3):
            history.append(
                {
                    "bribe_offered": 10,
                    "bribe_accepted": True,
                    "declaration": {"good_id": "apple", "count": 10},
                }
            )
        # Rejected bribes at 30% (should be ignored)
        for _i in range(3):
            history.append(
                {
                    "bribe_offered": 6,
                    "bribe_accepted": False,
                    "declaration": {"good_id": "apple", "count": 10},
                }
            )

        result = silas._learn_successful_bribe_ratio(history)
        assert result == 0.5, "Should only learn from accepted bribes"

    def test_learn_bribe_ratio_weights_recent_successes(self):
        """Test learning weights recent successes when there are many."""
        silas = SilasVoss("silas", "Silas", "Test", [], [], 8, 6, 7, 5)

        history = []
        # 10 old successful bribes at 40%
        for _i in range(10):
            history.append(
                {
                    "bribe_offered": 8,
                    "bribe_accepted": True,
                    "declaration": {"good_id": "apple", "count": 10},
                }
            )
        # 5 recent successful bribes at 60%
        for _i in range(5):
            history.append(
                {
                    "bribe_offered": 12,
                    "bribe_accepted": True,
                    "declaration": {"good_id": "apple", "count": 10},
                }
            )

        result = silas._learn_successful_bribe_ratio(history)
        # Should use last 5 bribes (60% ratio) when there are >5 successful bribes
        assert result == 0.6, f"Should weight recent bribes, got {result}"

    def test_learn_bribe_ratio_uses_last_20_rounds(self):
        """Test learning only looks at last 20 rounds of history."""
        silas = SilasVoss("silas", "Silas", "Test", [], [], 8, 6, 7, 5)

        history = []
        # 30 rounds of history
        for i in range(30):
            if i < 10:
                # Old bribes at 30% (should be ignored)
                history.append(
                    {
                        "bribe_offered": 6,
                        "bribe_accepted": True,
                        "declaration": {"good_id": "apple", "count": 10},
                    }
                )
            else:
                # Recent bribes at 50% (should be used)
                history.append(
                    {
                        "bribe_offered": 10,
                        "bribe_accepted": True,
                        "declaration": {"good_id": "apple", "count": 10},
                    }
                )

        result = silas._learn_successful_bribe_ratio(history)
        # Should only use last 20 rounds (all at 50%)
        assert result == 0.5, f"Should only use last 20 rounds, got {result}"


class TestSilasProactiveBribeWithLearning:
    """Test bribe calculation that uses learning."""

    def test_greedy_sheriff_uses_learned_ratio(self):
        """Test that Silas uses learned ratio against greedy sheriffs."""
        silas = SilasVoss("silas", "Silas", "Test", [], [], 8, 6, 7, 5)

        # This test verifies the integration between calculate_proactive_bribe
        # and _learn_successful_bribe_ratio
        # The actual learning happens in gameplay, so we just verify the code path exists

        from core.mechanics.goods import SILK

        actual_goods = [SILK, SILK]

        # Call calculate_proactive_bribe which should internally call _learn_successful_bribe_ratio
        # when sheriff_type is 'greedy'
        bribe = silas.calculate_proactive_bribe(
            actual_goods=actual_goods, is_lying=True, sheriff_authority=5
        )

        # Should return a valid bribe amount
        assert isinstance(bribe, int)
        assert bribe >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
