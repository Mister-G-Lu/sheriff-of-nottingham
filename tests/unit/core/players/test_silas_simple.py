"""
Simple tests for Silas Voss's core functionality.
"""

import pytest

from core.mechanics.goods import SILK
from core.players.silas_voss import SilasVoss


class TestSilasBasics:
    """Test Silas's basic functionality."""

    def test_silas_initialization(self):
        """Test that Silas initializes correctly."""
        silas = SilasVoss(
            id="silas",
            name="Silas Voss",
            intro="Information Broker",
            tells_honest=["calm"],
            tells_lying=["nervous"],
            bluff_skill=8,
            risk_tolerance=6,
            greed=7,
            honesty_bias=5,
        )

        assert silas.name == "Silas Voss"
        assert silas.bluff_skill == 8
        assert silas.risk_tolerance == 6

    def test_detect_sheriff_with_no_history(self):
        """Test detection returns unknown with no history."""
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

        result = silas._detect_sheriff_type([])
        assert result == "unknown"

    def test_detect_sheriff_with_insufficient_history(self):
        """Test detection returns unknown with insufficient history."""
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

        history = [{"opened": False, "bribe_offered": 0}] * 3
        result = silas._detect_sheriff_type(history)
        assert result == "unknown"

    def test_detect_strict_sheriff(self):
        """Test detection of strict sheriff (high inspection rate)."""
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

        # Sheriff inspects 80% of rounds
        history = []
        for i in range(10):
            history.append(
                {
                    "opened": i < 8,  # 8 out of 10 inspected
                    "bribe_offered": 0,
                    "bribe_accepted": False,
                }
            )

        result = silas._detect_sheriff_type(history)
        assert result == "strict"

    def test_detect_corrupt_sheriff(self):
        """Test detection of corrupt sheriff (accepts most bribes)."""
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

        # Sheriff accepts 90% of bribes
        history = []
        for i in range(10):
            history.append(
                {
                    "opened": False,
                    "bribe_offered": 5,
                    "bribe_accepted": i < 9,  # 9 out of 10 accepted
                }
            )

        result = silas._detect_sheriff_type(history)
        assert result == "corrupt"

    def test_get_bribe_ratio(self):
        """Test bribe ratio calculation."""
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

        # Test with contraband value
        history_entry = {
            "bribe_offered": 5,
            "declared_good": "apple",
            "declared_count": 3,
            "actual_goods": ["silk", "silk"],  # Contraband
        }

        ratio = silas._get_bribe_ratio(history_entry)
        assert isinstance(ratio, float)
        assert 0 <= ratio <= 1.0


class TestSilasBribeStrategy:
    """Test Silas's bribe calculation."""

    def test_calculate_proactive_bribe_returns_int(self):
        """Test that bribe calculation returns an integer."""
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

        actual_goods = [SILK, SILK]
        bribe = silas.calculate_proactive_bribe(
            actual_goods=actual_goods, is_lying=True, sheriff_authority=5
        )

        assert isinstance(bribe, int)
        assert bribe >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
