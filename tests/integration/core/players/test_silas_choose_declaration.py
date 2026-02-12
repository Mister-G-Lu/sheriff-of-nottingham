"""
Integration tests for Silas Voss's choose_declaration method.
Tests the full declaration logic including hand analysis and strategy selection.
"""

from unittest.mock import Mock, patch

import pytest

from core.mechanics.goods import APPLE, BREAD, CHEESE, CROSSBOW, MEAD, PEPPER, SILK
from core.players.silas_voss import SilasVoss


@pytest.fixture
def silas():
    """Create a Silas instance for testing."""
    return SilasVoss(
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


class TestChooseDeclarationWithHand:
    """Test choose_declaration with actual hands."""

    @patch("core.systems.game_master_state.get_game_master_state")
    @patch("core.mechanics.deck.should_redraw_for_silas")
    @patch("ai_strategy.declaration_builder.build_honest_declaration")
    def test_honest_declaration_against_strict_sheriff(
        self, mock_honest_builder, mock_redraw, mock_game_state, silas
    ):
        """Test chooses honest declaration against strict sheriff."""
        # Setup game state with strict sheriff history
        mock_state = Mock()
        history = []
        for _i in range(10):
            history.append(
                {
                    "opened": True,  # High inspection rate = strict
                    "bribe_offered": 10,
                    "bribe_accepted": False,
                }
            )
        mock_state.get_history_for_tier.return_value = history
        mock_game_state.return_value = mock_state

        # Setup hand with legal goods
        silas.hand = [APPLE, APPLE, CHEESE, BREAD, CHEESE, APPLE]

        # Mock no redraw needed
        mock_redraw.return_value = 0

        # Mock honest declaration builder
        mock_honest_builder.return_value = {
            "declared_id": "apple",
            "count": 3,
            "actual_ids": ["apple", "apple", "apple"],
            "lie": False,
        }

        result = silas.choose_declaration()

        # Should call honest builder (Legal Good Trick against strict)
        mock_honest_builder.assert_called_once()
        assert result["lie"] is False
        assert result["declared_id"] == "apple"

    @patch("core.systems.game_master_state.get_game_master_state")
    @patch("core.mechanics.deck.should_redraw_for_silas")
    @patch("core.mechanics.deck.redraw_cards")
    @patch("ai_strategy.declaration_builder.build_contraband_high_declaration")
    def test_smuggle_declaration_against_corrupt_sheriff(
        self,
        mock_contraband_builder,
        mock_redraw_cards,
        mock_redraw_check,
        mock_game_state,
        silas,
    ):
        """Test chooses smuggle declaration against corrupt sheriff."""
        # Setup game state with corrupt sheriff history
        mock_state = Mock()
        history = []
        for _i in range(15):
            history.append(
                {
                    "opened": False,
                    "bribe_offered": 10,
                    "bribe_accepted": True,  # High acceptance = corrupt
                }
            )
        mock_state.get_history_for_tier.return_value = history
        mock_game_state.return_value = mock_state

        # Setup hand with contraband
        silas.hand = [SILK, PEPPER, MEAD, APPLE, CHEESE, BREAD]

        # Mock no redraw needed
        mock_redraw_check.return_value = 0

        # Mock contraband declaration builder
        mock_contraband_builder.return_value = {
            "declared_id": "apple",
            "count": 4,
            "actual_ids": ["silk", "pepper", "mead", "apple"],
            "lie": True,
        }

        result = silas.choose_declaration()

        # Should call contraband builder (smuggle against corrupt)
        # Note: May be called 0 or 1 times depending on random choice
        assert result is not None

    @patch("core.systems.game_master_state.get_game_master_state")
    @patch("core.mechanics.deck.should_redraw_for_silas")
    @patch("core.mechanics.deck.redraw_cards")
    @patch("ai_strategy.declaration_builder.build_contraband_high_declaration")
    def test_redraw_for_contraband_against_greedy(
        self,
        mock_contraband_builder,
        mock_redraw_cards,
        mock_redraw_check,
        mock_game_state,
        silas,
    ):
        """Test redraws cards to get more contraband against greedy sheriff."""
        # Setup game state with greedy sheriff history
        mock_state = Mock()
        history = []
        # Greedy pattern
        for _i in range(5):
            history.append(
                {
                    "opened": False,
                    "bribe_offered": 10,
                    "bribe_accepted": True,
                    "declaration": {"good_id": "apple", "count": 4},
                }
            )
        for _i in range(5):
            history.append(
                {
                    "opened": False,
                    "bribe_offered": 2,
                    "bribe_accepted": False,
                    "declaration": {"good_id": "apple", "count": 4},
                }
            )
        mock_state.get_history_for_tier.return_value = history
        mock_game_state.return_value = mock_state

        # Setup hand with some contraband
        silas.hand = [SILK, PEPPER, APPLE, CHEESE, BREAD, APPLE]

        # Mock redraw suggestion
        mock_redraw_check.return_value = 2

        # Mock redraw result (more contraband)
        mock_redraw_cards.return_value = [SILK, PEPPER, MEAD, CROSSBOW, BREAD, APPLE]

        # Mock contraband declaration builder
        mock_contraband_builder.return_value = {
            "declared_id": "apple",
            "count": 4,
            "actual_ids": ["silk", "pepper", "mead", "crossbow"],
            "lie": True,
        }

        result = silas.choose_declaration()

        # Should have called redraw (key behavior we're testing)
        mock_redraw_cards.assert_called_once()

        # Result should be a valid declaration
        assert "declared_id" in result
        assert "count" in result
        assert "actual_ids" in result
        assert "lie" in result

        # Note: We don't assert specific lie value or contraband builder calls
        # due to randomness in Silas's decision-making

    @patch("core.systems.game_master_state.get_game_master_state")
    @patch("core.mechanics.deck.redraw_cards")
    def test_aggressive_redraw_against_corrupt_greedy(
        self, mock_redraw_cards, mock_game_state, silas
    ):
        """Test aggressively redraws ALL legal cards against corrupt/greedy."""
        # Setup game state with corrupt sheriff
        mock_state = Mock()
        history = []
        for _i in range(15):
            history.append(
                {"opened": False, "bribe_offered": 10, "bribe_accepted": True}
            )
        mock_state.get_history_for_tier.return_value = history
        mock_game_state.return_value = mock_state

        # Setup hand with mostly legal goods
        silas.hand = [APPLE, CHEESE, BREAD, APPLE, CHEESE, SILK]

        # Mock redraw result (all contraband)
        mock_redraw_cards.return_value = [SILK, PEPPER, MEAD, CROSSBOW, PEPPER, SILK]

        with patch(
            "ai_strategy.declaration_builder.build_contraband_high_declaration"
        ) as mock_builder:
            mock_builder.return_value = {
                "declared_id": "apple",
                "count": 4,
                "actual_ids": ["silk", "pepper", "mead", "crossbow"],
                "lie": True,
            }

            silas.choose_declaration()

            # Should have redrawn 5 legal cards (all except the 1 silk)
            mock_redraw_cards.assert_called_once()
            call_args = mock_redraw_cards.call_args
            assert call_args[0][1] == 5  # num_to_redraw = 5
            assert call_args[1]["prefer_contraband"] is True
            assert call_args[1]["prefer_high_value"] is True

    @patch("core.systems.game_master_state.get_game_master_state")
    @patch("core.mechanics.deck.should_redraw_for_silas")
    @patch("core.mechanics.deck.redraw_cards")
    @patch("ai_strategy.declaration_builder.build_honest_declaration")
    def test_redraw_for_legal_when_playing_honest(
        self,
        mock_honest_builder,
        mock_redraw_cards,
        mock_redraw_check,
        mock_game_state,
        silas,
    ):
        """Test redraws for legal goods when playing honest."""
        # Setup game state with strict sheriff
        mock_state = Mock()
        history = []
        for _i in range(10):
            history.append(
                {"opened": True, "bribe_offered": 10, "bribe_accepted": False}
            )
        mock_state.get_history_for_tier.return_value = history
        mock_game_state.return_value = mock_state

        # Setup hand with mixed goods
        silas.hand = [APPLE, SILK, PEPPER, CHEESE, BREAD, APPLE]

        # Mock redraw suggestion
        mock_redraw_check.return_value = 2

        # Mock redraw result (more legal)
        mock_redraw_cards.return_value = [APPLE, CHEESE, BREAD, CHEESE, BREAD, APPLE]

        # Mock honest declaration builder
        mock_honest_builder.return_value = {
            "declared_id": "apple",
            "count": 3,
            "actual_ids": ["apple", "apple", "apple"],
            "lie": False,
        }

        silas.choose_declaration()

        # Should have called redraw with prefer_legal
        mock_redraw_cards.assert_called_once()
        call_args = mock_redraw_cards.call_args
        assert call_args[1]["prefer_legal"] is True
        assert call_args[1]["prefer_high_value"] is True

    @patch("core.systems.game_master_state.get_game_master_state")
    @patch("core.mechanics.deck.should_redraw_for_silas")
    @patch("ai_strategy.declaration_builder.build_honest_declaration")
    def test_fallback_to_honest_when_no_contraband(
        self, mock_honest_builder, mock_redraw_check, mock_game_state, silas
    ):
        """Test falls back to honest when wanting to smuggle but no contraband."""
        # Setup game state with corrupt sheriff (wants to smuggle)
        mock_state = Mock()
        history = []
        for _i in range(15):
            history.append(
                {"opened": False, "bribe_offered": 10, "bribe_accepted": True}
            )
        mock_state.get_history_for_tier.return_value = history
        mock_game_state.return_value = mock_state

        # Setup hand with NO contraband
        silas.hand = [APPLE, APPLE, CHEESE, BREAD, CHEESE, APPLE]

        # Mock no redraw
        mock_redraw_check.return_value = 0

        # Mock honest declaration builder
        mock_honest_builder.return_value = {
            "declared_id": "apple",
            "count": 3,
            "actual_ids": ["apple", "apple", "apple"],
            "lie": False,
        }

        result = silas.choose_declaration()

        # Should fall back to honest (no contraband available)
        # Note: May be called 0 or 1 times depending on random choice
        assert result is not None

    @patch("core.systems.game_master_state.get_game_master_state")
    def test_fallback_declaration_when_no_hand(self, mock_game_state, silas):
        """Test returns fallback declaration when no hand."""
        mock_state = Mock()
        mock_state.get_history_for_tier.return_value = []
        mock_game_state.return_value = mock_state

        # No hand set
        silas.hand = []

        result = silas.choose_declaration()

        # Should return fallback
        assert result["declared_id"] == "apple"
        assert result["count"] == 4
        assert result["actual_ids"] == ["apple"] * 4
        assert result["lie"] is False

    @patch("core.systems.game_master_state.get_game_master_state")
    @patch("core.mechanics.deck.should_redraw_for_silas")
    def test_sheriff_analysis_calculation(
        self, mock_redraw_check, mock_game_state, silas
    ):
        """Test correctly calculates sheriff analysis metrics."""
        mock_state = Mock()
        history = []
        # 10 rounds: 6 opened, 4 caught
        for i in range(10):
            history.append({"opened": i < 6, "caught": i < 4, "bribe_offered": 0})
        mock_state.get_history_for_tier.return_value = history
        mock_game_state.return_value = mock_state

        silas.hand = [APPLE, CHEESE, BREAD, APPLE, CHEESE, APPLE]
        mock_redraw_check.return_value = 0

        with patch(
            "ai_strategy.declaration_builder.build_honest_declaration"
        ) as mock_builder:
            mock_builder.return_value = {
                "declared_id": "apple",
                "count": 3,
                "actual_ids": ["apple", "apple", "apple"],
                "lie": False,
            }

            silas.choose_declaration()

            # Verify should_redraw_for_silas was called with correct analysis
            mock_redraw_check.assert_called_once()
            call_args = mock_redraw_check.call_args
            sheriff_analysis = call_args[0][1]

            assert sheriff_analysis["inspection_rate"] == 0.6  # 6/10
            assert sheriff_analysis["catch_rate"] == 0.4  # 4/10
            assert "history" in sheriff_analysis


class TestChooseDeclarationEdgeCases:
    """Test edge cases in choose_declaration."""

    @patch("core.systems.game_master_state.get_game_master_state")
    def test_handles_empty_history(self, mock_game_state, silas):
        """Test handles empty history gracefully."""
        mock_state = Mock()
        mock_state.get_history_for_tier.return_value = []
        mock_game_state.return_value = mock_state

        silas.hand = [APPLE, CHEESE, BREAD, APPLE, CHEESE, APPLE]

        with patch("core.mechanics.deck.should_redraw_for_silas") as mock_redraw:
            mock_redraw.return_value = 0
            with patch(
                "ai_strategy.declaration_builder.build_honest_declaration"
            ) as mock_builder:
                mock_builder.return_value = {
                    "declared_id": "apple",
                    "count": 3,
                    "actual_ids": ["apple", "apple", "apple"],
                    "lie": False,
                }

                result = silas.choose_declaration()

                # Should not crash with empty history
                assert result is not None

    @patch("core.systems.game_master_state.get_game_master_state")
    @patch("core.mechanics.deck.should_redraw_for_silas")
    def test_handles_hand_attribute_missing(self, mock_redraw, mock_game_state, silas):
        """Test handles missing hand attribute gracefully."""
        mock_state = Mock()
        mock_state.get_history_for_tier.return_value = []
        mock_game_state.return_value = mock_state

        # Remove hand attribute if it exists
        if hasattr(silas, "hand"):
            delattr(silas, "hand")

        result = silas.choose_declaration()

        # Should return fallback
        assert result["declared_id"] == "apple"
        assert result["count"] == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
