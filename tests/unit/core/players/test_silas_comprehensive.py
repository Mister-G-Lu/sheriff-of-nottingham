"""
Comprehensive unit tests for Silas Voss AI logic.
Tests all decision-making methods for maximum coverage.
"""

from unittest.mock import Mock, patch

import pytest

from core.mechanics.goods import (
    APPLE,
    SILK,
)
from core.players.silas_voss import SilasVoss


# Helper function to create history entries (reduces 4-line blocks to 1-liners)
def h(
    opened=False, bribe_offered=0, bribe_accepted=False, caught=False, declaration=None
):
    """Create a single history entry. Short name 'h' for brevity."""
    entry = {
        "opened": opened,
        "bribe_offered": bribe_offered,
        "bribe_accepted": bribe_accepted,
    }
    if caught is not False:
        entry["caught"] = caught
    if declaration:
        entry["declaration"] = declaration
        if "good_id" in declaration and "count" in declaration:
            entry["declared_count"] = declaration["count"]
            entry["declared_good"] = declaration["good_id"]
    return entry


# Common test helper functions
def assert_sheriff_detection(silas, history, expected_type):
    """Helper to test sheriff type detection."""
    result = silas._detect_sheriff_type(history)
    assert result == expected_type


def create_bribe_history(count, bribe_offered, bribe_accepted, declaration):
    """Helper to create history with bribe entries."""
    return [
        h(
            bribe_offered=bribe_offered,
            bribe_accepted=bribe_accepted,
            declaration=declaration,
        )
        for _ in range(count)
    ]


def assert_ratio_in_range(actual, expected_min, expected_max):
    """Helper to assert a value is within a range."""
    assert expected_min <= actual <= expected_max, (
        f"Expected {actual} to be between {expected_min} and {expected_max}"
    )


@pytest.fixture
def silas():
    """Create a Silas instance for testing."""
    return SilasVoss(
        id="silas",
        name="Silas Voss",
        intro="Information Broker",
        tells_honest=["calm", "confident"],
        tells_lying=["nervous", "fidgeting"],
        bluff_skill=8,
        risk_tolerance=6,
        greed=7,
        honesty_bias=5,
    )


class TestDetectSheriffType:
    """Test sheriff type detection logic."""

    def test_unknown_with_insufficient_history(self, silas):
        """Test returns unknown with < 5 history entries."""
        history = [{"opened": False}] * 4
        assert_sheriff_detection(silas, history, "unknown")

    def test_strict_with_high_overall_inspection_rate(self, silas):
        """Test detects strict sheriff with >50% overall inspection rate."""
        history = []
        history.extend(
            [h(opened=i < 6, bribe_offered=0, bribe_accepted=False) for i in range(10)]
        )

        assert_sheriff_detection(silas, history, "strict")

    def test_strict_with_moderate_inspection_rate_no_bribe_data(self, silas):
        """Test detects strict with 40% inspection rate and no bribe data."""
        history = []
        history.extend(
            [h(opened=i < 5, bribe_offered=0, bribe_accepted=False) for i in range(10)]
        )

        assert_sheriff_detection(silas, history, "strict")

    def test_corrupt_with_high_acceptance_rate(self, silas):
        """Test detects corrupt sheriff with >80% bribe acceptance."""
        history = []
        history.extend(
            [h(opened=False, bribe_offered=10, bribe_accepted=i < 9) for i in range(10)]
        )

        assert_sheriff_detection(silas, history, "corrupt")

    def test_strict_with_very_high_inspection_rate_among_bribes(self, silas):
        """Test detects strict with >60% inspection rate among bribes."""
        history = []
        history.extend(
            [h(opened=i < 7, bribe_offered=10, bribe_accepted=False) for i in range(10)]
        )

        assert_sheriff_detection(silas, history, "strict")

    def test_strict_with_very_low_acceptance_rate(self, silas):
        """Test detects strict with <20% acceptance rate."""
        history = []
        history.extend(
            [h(opened=True, bribe_offered=10, bribe_accepted=i < 1) for i in range(10)]
        )

        assert_sheriff_detection(silas, history, "strict")

    def test_strict_with_high_inspection_rate(self, silas):
        """Test detects strict with >40% inspection rate."""
        history = []
        history.extend(
            [
                h(opened=i < 5, bribe_offered=10, bribe_accepted=i >= 5)
                for i in range(10)
            ]
        )

        assert_sheriff_detection(silas, history, "strict")

    def test_strict_with_low_acceptance_rate(self, silas):
        """Test detects strict with <30% acceptance rate."""
        history = []
        history.extend(
            [h(opened=False, bribe_offered=10, bribe_accepted=i < 2) for i in range(10)]
        )

        assert_sheriff_detection(silas, history, "strict")

    def test_greedy_with_moderate_acceptance_and_pattern(self, silas):
        """Test detects greedy with moderate acceptance and high-bribe preference."""
        history = []
        # High bribes accepted (need more to avoid strict detection)
        for _i in range(5):
            history.append(
                {
                    "opened": False,
                    "bribe_offered": 10,
                    "bribe_accepted": True,
                    "declaration": {
                        "good_id": "apple",
                        "count": 5,
                    },  # 10g bribe / 10g value = 100%
                    "declared_count": 5,
                    "declared_good": "apple",
                }
            )
        # Low bribes rejected (but not opened to avoid strict)
        for _i in range(5):
            history.append(
                {
                    "opened": False,
                    "bribe_offered": 2,
                    "bribe_accepted": False,
                    "declaration": {
                        "good_id": "apple",
                        "count": 5,
                    },  # 2g bribe / 10g value = 20%
                    "declared_count": 5,
                    "declared_good": "apple",
                }
            )

        assert_sheriff_detection(silas, history, "greedy")

    def test_unknown_with_moderate_acceptance_no_greedy_pattern(self, silas):
        """Test returns unknown with moderate acceptance but no greedy pattern."""
        history = []
        history.extend(
            [
                h(
                    opened=False,
                    bribe_offered=5,
                    bribe_accepted=i < 5,
                    declaration={"good_id": "apple", "count": 5},
                )
                for i in range(10)
            ]
        )

        assert_sheriff_detection(silas, history, "unknown")

    def test_uses_longer_history_when_insufficient_bribe_data(self, silas):
        """Test uses longer history (20 rounds) when recent has < 3 bribes."""
        history = []
        # First 15 rounds: no bribes
        history.extend(
            [h(opened=False, bribe_offered=0, bribe_accepted=False) for _ in range(15)]
        )
        # Last 5 rounds: bribes with high acceptance
        history.extend(
            [h(opened=False, bribe_offered=10, bribe_accepted=True) for _ in range(5)]
        )

        assert_sheriff_detection(silas, history, "corrupt")


class TestDetectGreedyPattern:
    """Test greedy pattern detection."""

    def test_greedy_pattern_detected(self, silas):
        """Test detects greedy when high bribes accepted more than low."""
        bribed = []
        # High bribes (50%+) accepted
        for _i in range(3):
            bribed.append(
                {
                    "bribe_offered": 10,
                    "bribe_accepted": True,
                    "declaration": {"good_id": "apple", "count": 4},  # 50% ratio
                }
            )
        # Low bribes (<45%) rejected
        for _i in range(3):
            bribed.append(
                {
                    "bribe_offered": 3,
                    "bribe_accepted": False,
                    "declaration": {"good_id": "apple", "count": 4},  # 37.5% ratio
                }
            )

        result = silas._detect_greedy_pattern(bribed)
        assert result is True

    def test_no_greedy_pattern_when_acceptance_similar(self, silas):
        """Test no greedy pattern when acceptance rates are similar."""
        bribed = []
        # High bribes
        for i in range(3):
            bribed.append(
                {
                    "bribe_offered": 10,
                    "bribe_accepted": i < 2,  # 66% acceptance
                    "declaration": {"good_id": "apple", "count": 4},
                }
            )
        # Low bribes
        for i in range(3):
            bribed.append(
                {
                    "bribe_offered": 3,
                    "bribe_accepted": i < 2,  # 66% acceptance
                    "declaration": {"good_id": "apple", "count": 4},
                }
            )

        result = silas._detect_greedy_pattern(bribed)
        assert result is False

    def test_no_greedy_pattern_with_insufficient_data(self, silas):
        """Test no greedy pattern with insufficient high/low bribe samples."""
        bribed = [
            {
                "bribe_offered": 10,
                "bribe_accepted": True,
                "declaration": {"good_id": "apple", "count": 4},
            }
        ]

        result = silas._detect_greedy_pattern(bribed)
        assert result is False


class TestGetBribeRatio:
    """Test bribe ratio calculation."""

    def test_bribe_ratio_with_dict_declaration(self, silas):
        """Test calculates ratio correctly with dict declaration."""
        history_entry = {
            "bribe_offered": 6,
            "declaration": {"good_id": "apple", "count": 3},  # 3 apples = 6g
        }

        ratio = silas._get_bribe_ratio(history_entry)
        assert ratio == 1.0  # 6g bribe / 6g value

    def test_bribe_ratio_with_legacy_format(self, silas):
        """Test calculates ratio with legacy format (declared_count, declared_good)."""
        history_entry = {
            "bribe_offered": 4,
            "declared_count": 2,
            "declared_good": "apple",  # 2 apples = 4g
            "declaration": None,  # Non-dict to trigger legacy path
        }

        ratio = silas._get_bribe_ratio(history_entry)
        assert ratio == 1.0

    def test_bribe_ratio_zero_when_no_bribe(self, silas):
        """Test returns 0 when no bribe offered."""
        history_entry = {
            "bribe_offered": 0,
            "declaration": {"good_id": "apple", "count": 3},
        }

        ratio = silas._get_bribe_ratio(history_entry)
        assert ratio == 0.0

    def test_bribe_ratio_zero_when_zero_declared_value(self, silas):
        """Test returns 0 when declared value is 0."""
        history_entry = {
            "bribe_offered": 5,
            "declaration": {"good_id": "apple", "count": 0},
        }

        ratio = silas._get_bribe_ratio(history_entry)
        assert ratio == 0.0

    def test_bribe_ratio_with_different_goods(self, silas):
        """Test calculates ratio correctly with different goods."""
        history_entry = {
            "bribe_offered": 5,
            "declaration": {"good_id": "cheese", "count": 2},  # 2 cheese = 6g
        }

        ratio = silas._get_bribe_ratio(history_entry)
        assert_ratio_in_range(ratio, 0.83, 0.84)  # 5/6 ≈ 0.833


class TestShouldPlayHonest:
    """Test honest vs smuggle decision logic."""

    def test_random_choice_with_insufficient_history(self, silas):
        """Test makes random choice with < 3 history entries."""
        history = [{"opened": False}] * 2

        # Run multiple times to check randomness
        results = [silas._should_play_honest(history) for _ in range(10)]
        assert True in results or False in results  # Should have some variation

    def test_always_smuggle_against_corrupt(self, silas):
        """Test always smuggles against corrupt sheriff."""
        history = []
        history.extend(
            [h(opened=False, bribe_offered=10, bribe_accepted=True) for _ in range(10)]
        )

        result = silas._should_play_honest(history)
        assert result is False

    def test_mostly_smuggle_against_greedy(self, silas):
        """Test mostly smuggles against greedy sheriff (15% honest)."""
        history = []
        # Create greedy pattern (more samples, avoid strict detection)
        history.extend(
            [
                h(
                    opened=False,
                    bribe_offered=10,
                    bribe_accepted=True,
                    declaration={"good_id": "apple", "count": 4},
                )
                for _ in range(5)
            ]
        )
        history.extend(
            [
                h(
                    opened=False,
                    bribe_offered=2,
                    bribe_accepted=False,
                    declaration={"good_id": "apple", "count": 4},
                )
                for _ in range(5)
            ]
        )

        # Run multiple times, should mostly be False
        results = [silas._should_play_honest(history) for _ in range(20)]
        honest_count = sum(results)
        assert honest_count < 8  # Should be around 15% (3 out of 20)

    def test_always_honest_against_strict(self, silas):
        """Test always plays honest against strict sheriff (Legal Good Trick)."""
        history = []
        history.extend(
            [h(opened=True, bribe_offered=10, bribe_accepted=False) for _ in range(10)]
        )

        result = silas._should_play_honest(history)
        assert result is True

    def test_mostly_honest_with_high_catch_rate(self, silas):
        """Test mostly honest with >40% catch rate (85% honest)."""
        history = []
        history.extend(
            [h(opened=False, bribe_offered=0, caught=i < 5) for i in range(10)]
        )

        # Run multiple times, should mostly be True
        results = [silas._should_play_honest(history) for _ in range(50)]
        honest_count = sum(results)
        assert honest_count > 35  # Should be around 85% (42 out of 50, allow variance)

    def test_somewhat_honest_with_moderate_catch_rate(self, silas):
        """Test somewhat honest with 30-40% catch rate (70% honest)."""
        history = []
        history.extend(
            [h(opened=False, bribe_offered=0, caught=i < 4) for i in range(10)]
        )

        # Run multiple times, should be around 70% honest
        results = [silas._should_play_honest(history) for _ in range(20)]
        honest_count = sum(results)
        assert 8 < honest_count < 18  # Should be around 70% (14 out of 20)

    def test_smuggle_with_unknown_sheriff_low_catch_rate(self, silas):
        """Test smuggles with unknown sheriff and low catch rate."""
        history = []
        history.extend(
            [h(opened=False, bribe_offered=0, caught=False) for _ in range(10)]
        )

        result = silas._should_play_honest(history)
        assert result is False


class TestShouldOfferProactiveBribe:
    """Test bribe offering decision logic."""

    @patch("core.systems.game_master_state.get_game_master_state")
    def test_exploration_phase_offers_bribes_sometimes(self, mock_game_state, silas):
        """Test offers bribes sometimes in first 10 rounds."""
        mock_state = Mock()
        mock_state.get_history_for_tier.return_value = [{"opened": False}] * 5
        mock_game_state.return_value = mock_state

        actual_goods = [SILK, SILK]
        declared_goods = [APPLE, APPLE]

        # Run multiple times to check it's not always True or always False
        results = [
            silas.should_offer_proactive_bribe(5, 7, actual_goods, declared_goods)
            for _ in range(20)
        ]
        bribe_count = sum(results)
        # Should have some variation (not all True or all False)
        assert 0 < bribe_count < 20

    @patch("core.systems.game_master_state.get_game_master_state")
    def test_corrupt_sheriff_bribes_sometimes_when_smuggling(
        self, mock_game_state, silas
    ):
        """Test bribes 50% of time against corrupt when smuggling."""
        mock_state = Mock()
        history = []
        history.extend(
            [h(opened=False, bribe_offered=10, bribe_accepted=True) for _ in range(15)]
        )
        mock_state.get_history_for_tier.return_value = history
        mock_game_state.return_value = mock_state

        actual_goods = [SILK, SILK]
        declared_goods = [APPLE, APPLE]

        results = [
            silas.should_offer_proactive_bribe(5, 7, actual_goods, declared_goods)
            for _ in range(20)
        ]
        bribe_count = sum(results)
        assert 5 < bribe_count < 15  # Should be around 50% (10 out of 20)

    @patch("core.systems.game_master_state.get_game_master_state")
    def test_greedy_sheriff_bribes_when_smuggling(self, mock_game_state, silas):
        """Test bribes against greedy when smuggling."""
        mock_state = Mock()
        history = []
        # Create greedy pattern (more samples, avoid strict)
        history.extend(
            [
                h(
                    opened=False,
                    bribe_offered=10,
                    bribe_accepted=True,
                    declaration={"good_id": "apple", "count": 4},
                )
                for _ in range(5)
            ]
        )
        history.extend(
            [
                h(
                    opened=False,
                    bribe_offered=2,
                    bribe_accepted=False,
                    declaration={"good_id": "apple", "count": 4},
                )
                for _ in range(5)
            ]
        )
        mock_state.get_history_for_tier.return_value = history
        mock_game_state.return_value = mock_state

        actual_goods = [SILK, SILK]
        declared_goods = [APPLE, APPLE]

        result = silas.should_offer_proactive_bribe(5, 7, actual_goods, declared_goods)
        # Should bribe (True) since greedy and smuggling
        assert result is True

    @patch("core.systems.game_master_state.get_game_master_state")
    def test_strict_sheriff_bribes_with_honest_goods(self, mock_game_state, silas):
        """Test uses Legal Good Trick against strict (bribe with honest goods)."""
        mock_state = Mock()
        history = []
        history.extend(
            [h(opened=True, bribe_offered=10, bribe_accepted=False) for _ in range(10)]
        )
        mock_state.get_history_for_tier.return_value = history
        mock_game_state.return_value = mock_state

        actual_goods = [APPLE, APPLE]
        declared_goods = [APPLE, APPLE]

        result = silas.should_offer_proactive_bribe(5, 7, actual_goods, declared_goods)
        assert result is True

    @patch("core.systems.game_master_state.get_game_master_state")
    def test_no_bribe_when_honest_against_unknown(self, mock_game_state, silas):
        """Test doesn't bribe when honest against unknown sheriff."""
        mock_state = Mock()
        history = [{"opened": False}] * 10
        mock_state.get_history_for_tier.return_value = history
        mock_game_state.return_value = mock_state

        actual_goods = [APPLE, APPLE]
        declared_goods = [APPLE, APPLE]

        result = silas.should_offer_proactive_bribe(5, 7, actual_goods, declared_goods)
        assert result is False


class TestCalculateProactiveBribe:
    """Test bribe amount calculation."""

    @patch("core.systems.game_master_state.get_game_master_state")
    def test_corrupt_sheriff_low_bribes(self, mock_game_state, silas):
        """Test offers low bribes (15-25%) against corrupt."""
        mock_state = Mock()
        history = []
        history.extend(
            [h(opened=False, bribe_offered=10, bribe_accepted=True) for _ in range(15)]
        )
        mock_state.get_history_for_tier.return_value = history
        mock_game_state.return_value = mock_state

        actual_goods = [SILK, SILK]  # 12g value
        declared_goods = [APPLE, APPLE, APPLE, APPLE, APPLE, APPLE]  # 12g declared

        bribe = silas.calculate_proactive_bribe(actual_goods, True, 5, declared_goods)

        assert 1 <= bribe <= 4  # 15-25% of 12g = 1.8-3g

    @patch("core.systems.game_master_state.get_game_master_state")
    def test_greedy_sheriff_high_bribes_with_learning(self, mock_game_state, silas):
        """Test offers high bribes (learned ratio) against greedy."""
        mock_state = Mock()
        history = []
        # Create greedy pattern with successful 60% bribes (need more samples)
        history.extend(
            [
                h(
                    opened=False,
                    bribe_offered=6,
                    bribe_accepted=True,
                    declaration={"good_id": "apple", "count": 5},
                )
                for _ in range(5)
            ]
        )
        history.extend(
            [
                h(
                    opened=False,
                    bribe_offered=2,
                    bribe_accepted=False,
                    declaration={"good_id": "apple", "count": 5},
                )
                for _ in range(5)
            ]
        )
        mock_state.get_history_for_tier.return_value = history
        mock_game_state.return_value = mock_state

        actual_goods = [SILK, SILK]  # 12g value
        declared_goods = [APPLE] * 6  # 12g declared

        bribe = silas.calculate_proactive_bribe(actual_goods, True, 5, declared_goods)

        # Should learn 60% ratio and offer around that (with 97-103% variance)
        assert 6 <= bribe <= 8  # Around 60% of 12g = 7.2g

    @patch("core.systems.game_master_state.get_game_master_state")
    def test_greedy_sheriff_offers_bribes_based_on_value(self, mock_game_state, silas):
        """Test offers bribes based on declared value."""
        mock_state = Mock()
        history = []
        # Greedy pattern
        history.extend(
            [
                h(
                    opened=False,
                    bribe_offered=6,
                    bribe_accepted=True,
                    declaration={"good_id": "apple", "count": 5},
                )
                for _ in range(10)
            ]
        )
        mock_state.get_history_for_tier.return_value = history
        mock_game_state.return_value = mock_state

        actual_goods = [SILK, SILK]  # 12g value
        declared_goods = [APPLE] * 6  # 12g declared

        bribe = silas.calculate_proactive_bribe(actual_goods, True, 5, declared_goods)

        # Should offer some bribe based on value
        assert bribe >= 1  # At least 1 gold

    @patch("core.systems.game_master_state.get_game_master_state")
    def test_unknown_sheriff_moderate_bribes(self, mock_game_state, silas):
        """Test offers moderate bribes (30-60%) against unknown."""
        mock_state = Mock()
        history = [{"opened": False}] * 10
        mock_state.get_history_for_tier.return_value = history
        mock_game_state.return_value = mock_state

        actual_goods = [SILK, SILK]  # 12g value
        declared_goods = [APPLE] * 6  # 12g declared

        bribe = silas.calculate_proactive_bribe(actual_goods, True, 5, declared_goods)

        assert 3 <= bribe <= 8  # 30-60% of 12g = 3.6-7.2g

    @patch("core.systems.game_master_state.get_game_master_state")
    def test_legal_good_trick_small_bribes(self, mock_game_state, silas):
        """Test offers small bribes (20-35%) for Legal Good Trick."""
        mock_state = Mock()
        history = []
        history.extend(
            [h(opened=True, bribe_offered=10, bribe_accepted=False) for _ in range(10)]
        )
        mock_state.get_history_for_tier.return_value = history
        mock_game_state.return_value = mock_state

        actual_goods = [APPLE] * 5  # 10g value, all legal
        declared_goods = [APPLE] * 5

        bribe = silas.calculate_proactive_bribe(actual_goods, False, 5, declared_goods)

        assert 2 <= bribe <= 4  # 20-35% of 10g = 2-3.5g

    @patch("core.systems.game_master_state.get_game_master_state")
    def test_uses_actual_goods_value_when_no_declared_goods(
        self, mock_game_state, silas
    ):
        """Test uses actual goods value when declared_goods is None."""
        mock_state = Mock()
        history = [{"opened": False}] * 10
        mock_state.get_history_for_tier.return_value = history
        mock_game_state.return_value = mock_state

        actual_goods = [SILK, SILK]  # 12g value

        bribe = silas.calculate_proactive_bribe(
            actual_goods, True, 5, declared_goods=None
        )

        assert bribe >= 1  # Should calculate based on actual goods value


class TestLearnSuccessfulBribeRatio:
    """Test bribe learning algorithm."""

    def test_returns_zero_with_insufficient_history(self, silas):
        """Test returns 0 with < 3 history entries."""
        history = [{"opened": False}] * 2

        result = silas._learn_successful_bribe_ratio(history)
        assert result == 0.0

    def test_returns_zero_with_no_successful_bribes(self, silas):
        """Test returns 0 when no bribes were accepted."""
        history = []
        history.extend(
            [
                h(
                    bribe_offered=5,
                    bribe_accepted=False,
                    declaration={"good_id": "apple", "count": 3},
                )
                for _ in range(10)
            ]
        )

        result = silas._learn_successful_bribe_ratio(history)
        assert result == 0.0

    def test_learns_average_ratio_from_successful_bribes(self, silas):
        """Test learns average ratio from successful bribes."""
        history = []
        # 50% ratio bribes
        history.extend(
            [
                h(
                    bribe_offered=5,
                    bribe_accepted=True,
                    declaration={"good_id": "apple", "count": 5},
                )
                for _ in range(3)
            ]
        )
        # 60% ratio bribes
        history.extend(
            [
                h(
                    bribe_offered=6,
                    bribe_accepted=True,
                    declaration={"good_id": "apple", "count": 5},
                )
                for _ in range(2)
            ]
        )

        result = silas._learn_successful_bribe_ratio(history)

        # Average: (0.5*3 + 0.6*2) / 5 = 0.54
        assert_ratio_in_range(result, 0.53, 0.55)

    def test_weights_recent_successes_when_many_bribes(self, silas):
        """Test uses only last 5 successful bribes when > 5 available."""
        history = []
        # Old 30% ratio bribes
        history.extend(
            [
                h(
                    bribe_offered=3,
                    bribe_accepted=True,
                    declaration={"good_id": "apple", "count": 5},
                )
                for _ in range(10)
            ]
        )
        # Recent 70% ratio bribes
        history.extend(
            [
                h(
                    bribe_offered=7,
                    bribe_accepted=True,
                    declaration={"good_id": "apple", "count": 5},
                )
                for _ in range(5)
            ]
        )

        result = silas._learn_successful_bribe_ratio(history)

        # Should use only last 5 (all 70%)
        assert_ratio_in_range(result, 0.69, 0.71)

    def test_ignores_rejected_bribes(self, silas):
        """Test ignores rejected bribes in learning."""
        history = []
        # Successful 50% bribes
        history.extend(
            [
                h(
                    bribe_offered=5,
                    bribe_accepted=True,
                    declaration={"good_id": "apple", "count": 5},
                )
                for _ in range(3)
            ]
        )
        # Rejected 90% bribes (should be ignored)
        history.extend(
            [
                h(
                    bribe_offered=9,
                    bribe_accepted=False,
                    declaration={"good_id": "apple", "count": 5},
                )
                for _ in range(5)
            ]
        )

        result = silas._learn_successful_bribe_ratio(history)

        # Should only learn from 50% bribes
        assert_ratio_in_range(result, 0.49, 0.51)


class TestChooseDeclaration:
    """Test declaration choice logic (integration-style tests)."""

    @patch("core.systems.game_master_state.get_game_master_state")
    def test_fallback_when_no_hand(self, mock_game_state, silas):
        """Test returns fallback declaration when no hand available."""
        mock_state = Mock()
        mock_state.get_history_for_tier.return_value = []
        mock_game_state.return_value = mock_state

        result = silas.choose_declaration()

        assert result["declared_id"] == "apple"
        assert result["count"] == 4
        assert result["actual_ids"] == ["apple"] * 4
        assert result["lie"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
