"""
Integration test for Silas Voss's greedy sheriff detection.

This test verifies that Silas's greedy detection logic is actually called
during gameplay and correctly identifies greedy sheriffs.
"""

import pytest

from core.players.silas_voss import SilasVoss


class TestSilasGreedyDetectionIntegration:
    """Integration tests for Silas's greedy sheriff detection."""

    def test_detect_greedy_pattern_with_clear_preference(self):
        """Test that greedy pattern is detected when high bribes are clearly preferred."""
        silas = SilasVoss(
            id="silas",
            name="Silas",
            intro="Test",
            tells_honest=[],
            tells_lying=[],
            bluff_skill=8,
            risk_tolerance=6,
            greed=7,
            honesty_bias=5,
        )

        # Create history where high bribes (>=45% ratio) are accepted, low bribes rejected
        bribed_history = []

        # High bribes (50% ratio) - all accepted
        # Apple value is 2, so 10 apples = 20g declared value
        for _i in range(5):
            bribed_history.append(
                {
                    "bribe_offered": 10,  # 10/20 = 50% ratio
                    "bribe_accepted": True,
                    "declaration": {
                        "good_id": "apple",
                        "count": 10,
                    },  # 10 * 2g = 20g declared value
                    "actual_goods": ["silk", "silk"],
                }
            )

        # Low bribes (30% ratio) - all rejected
        for _i in range(5):
            bribed_history.append(
                {
                    "bribe_offered": 6,  # 6/20 = 30% ratio
                    "bribe_accepted": False,
                    "declaration": {
                        "good_id": "apple",
                        "count": 10,
                    },  # 10 * 2g = 20g declared value
                    "actual_goods": ["silk", "silk"],
                }
            )

        # Test the extracted function
        result = silas._detect_greedy_pattern(bribed_history)

        assert result, "Should detect greedy pattern when high bribes accepted more"

    def test_detect_greedy_pattern_no_clear_preference(self):
        """Test that greedy pattern is NOT detected when no clear preference."""
        silas = SilasVoss(
            id="silas",
            name="Silas",
            intro="Test",
            tells_honest=[],
            tells_lying=[],
            bluff_skill=8,
            risk_tolerance=6,
            greed=7,
            honesty_bias=5,
        )

        # Create history where acceptance rate is similar for high and low bribes
        bribed_history = []

        # High bribes - 50% accepted
        for i in range(4):
            bribed_history.append(
                {
                    "bribe_offered": 10,
                    "bribe_accepted": i < 2,  # 2 out of 4 accepted
                    "declaration": {"good_id": "apple", "count": 10},  # 20g declared
                    "actual_goods": ["silk", "silk"],
                }
            )

        # Low bribes - 50% accepted (no significant difference)
        for i in range(4):
            bribed_history.append(
                {
                    "bribe_offered": 6,
                    "bribe_accepted": i < 2,  # 2 out of 4 accepted
                    "declaration": {"good_id": "apple", "count": 10},  # 20g declared
                    "actual_goods": ["silk", "silk"],
                }
            )

        result = silas._detect_greedy_pattern(bribed_history)

        assert not result, "Should NOT detect greedy when acceptance rates are similar"

    def test_detect_greedy_pattern_insufficient_data(self):
        """Test that greedy pattern requires sufficient data."""
        silas = SilasVoss(
            id="silas",
            name="Silas",
            intro="Test",
            tells_honest=[],
            tells_lying=[],
            bluff_skill=8,
            risk_tolerance=6,
            greed=7,
            honesty_bias=5,
        )

        # Only 1 high bribe and 1 low bribe (insufficient)
        bribed_history = [
            {
                "bribe_offered": 10,
                "bribe_accepted": True,
                "declaration": {"good_id": "apple", "count": 10},  # 20g declared
                "actual_goods": ["silk", "silk"],
            },
            {
                "bribe_offered": 6,
                "bribe_accepted": False,
                "declaration": {"good_id": "apple", "count": 10},  # 20g declared
                "actual_goods": ["silk", "silk"],
            },
        ]

        result = silas._detect_greedy_pattern(bribed_history)

        assert not result, "Should require at least 2 high and 2 low bribes"

    def test_full_detection_identifies_greedy(self):
        """Integration test: Full detection flow identifies greedy sheriff."""
        silas = SilasVoss(
            id="silas",
            name="Silas",
            intro="Test",
            tells_honest=[],
            tells_lying=[],
            bluff_skill=8,
            risk_tolerance=6,
            greed=7,
            honesty_bias=5,
        )

        # Create full history with greedy pattern
        history = []

        # High bribes - mostly accepted (50% ratio = 10/20)
        for _ in range(5):
            history.append(
                {
                    "bribe_offered": 10,  # 50% ratio
                    "bribe_accepted": True,
                    "opened": False,
                    "declaration": {
                        "good_id": "apple",
                        "count": 10,
                    },  # 10 * 2g = 20g declared value
                    "actual_goods": ["silk", "silk"],
                }
            )

        # Low bribes - mostly rejected but some accepted (30% ratio = 6/20)
        for i in range(5):
            history.append(
                {
                    "bribe_offered": 6,  # 30% ratio
                    "bribe_accepted": i < 2,  # 40% acceptance
                    "opened": i >= 2,  # Inspect when rejecting bribe
                    "declaration": {
                        "good_id": "apple",
                        "count": 10,
                    },  # 10 * 2g = 20g declared value
                    "actual_goods": ["silk", "silk"],
                }
            )

        # Test full detection
        sheriff_type = silas._detect_sheriff_type(history)

        assert sheriff_type == "greedy", (
            f"Should detect greedy sheriff, got: {sheriff_type}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
