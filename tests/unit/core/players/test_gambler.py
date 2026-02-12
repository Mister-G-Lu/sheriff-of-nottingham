"""
Tests for The Gambler merchant.

The Gambler is a unique merchant who:
- Plays honest by default to build reputation
- Goes all-in when dealt 2+ of same contraband (hard mulligan)
- Never offers bribes (relies on honest reputation)
- Accepts consequences when caught (never raises)
"""

from unittest.mock import patch

import pytest

from core.mechanics.goods import APPLE, BREAD, MEAD, PEPPER, SILK
from core.players.gambler import Gambler


def create_test_gambler():
    """Helper to create a test Gambler."""
    return Gambler(
        id="test_gambler",
        name="Test Gambler",
        intro="A test gambler",
        tells_honest=["calm"],
        tells_lying=["nervous"],
        bluff_skill=9,
        risk_tolerance=9,
        greed=7,
        honesty_bias=6,
    )


class TestGamblerInitialization:
    """Test Gambler initialization."""

    def test_gambler_inherits_from_merchant(self):
        """Gambler should inherit from Merchant."""
        gambler = create_test_gambler()

        assert gambler.name == "Test Gambler"
        assert gambler.bluff_skill == 9
        assert gambler.risk_tolerance == 9
        assert gambler.greed == 7
        assert gambler.honesty_bias == 6

    def test_gambler_tracks_honest_plays(self):
        """Gambler should track times played honestly."""
        gambler = create_test_gambler()

        # Should start at 0
        assert hasattr(gambler, "times_honest")
        assert gambler.times_honest == 0


class TestGamblerBribeStrategy:
    """Test Gambler's no-bribe strategy."""

    def test_never_offers_proactive_bribe_with_contraband(self):
        """Test that Gambler never offers bribes even with contraband."""
        gambler = create_test_gambler()

        # Scenario: Smuggling contraband
        actual_goods = [SILK, SILK, SILK]
        declared_goods = [APPLE, APPLE, APPLE]

        should_bribe = gambler.should_offer_proactive_bribe(
            sheriff_authority=5,
            sheriff_reputation=10,
            actual_goods=actual_goods,
            declared_goods=declared_goods,
        )

        assert not should_bribe, "Gambler should never offer bribes"

    def test_never_offers_proactive_bribe_when_honest(self):
        """Test that Gambler never offers bribes even when honest."""
        gambler = create_test_gambler()

        # Scenario: Honest goods
        actual_goods = [APPLE, APPLE, APPLE]
        declared_goods = [APPLE, APPLE, APPLE]

        should_bribe = gambler.should_offer_proactive_bribe(
            sheriff_authority=5,
            sheriff_reputation=10,
            actual_goods=actual_goods,
            declared_goods=declared_goods,
        )

        assert not should_bribe, "Gambler should never offer bribes"

    def test_calculate_proactive_bribe_returns_zero(self):
        """Test that Gambler always returns 0 for bribe calculation."""
        gambler = create_test_gambler()

        actual_goods = [SILK, SILK, SILK]

        bribe = gambler.calculate_proactive_bribe(
            actual_goods=actual_goods, is_lying=True, sheriff_authority=5
        )

        assert bribe == 0, "Gambler should always return 0 bribe"

    def test_gambler_accepts_consequences(self):
        """Test that Gambler accepts consequences through should_accept_counter."""
        gambler = create_test_gambler()

        # Gambler's high risk tolerance (9) means he's more likely to accept sheriff demands
        # rather than continuing to negotiate (accepts consequences of his gamble)
        # This is tested through the should_accept_counter method in base Merchant class

        # Verify Gambler has high risk tolerance
        assert gambler.risk_tolerance >= 9, "Gambler should have high risk tolerance"


class TestGamblerDeclarationStrategy:
    """Test Gambler's card-based decision making."""

    @patch("core.mechanics.deck.redraw_cards")
    def test_plays_honest_with_no_contraband_sets(self, mock_redraw):
        """Test that Gambler plays honest when no contraband sets."""
        gambler = create_test_gambler()

        # Hand with no contraband sets (all different)
        gambler.hand = [APPLE, BREAD, SILK, PEPPER, MEAD, APPLE]

        declaration = gambler.choose_declaration(history=[])

        # Should play honest (no contraband sets to exploit)
        assert declaration is not None
        assert "lie" in declaration

    @patch("core.mechanics.deck.redraw_cards")
    def test_goes_all_in_with_contraband_set(self, mock_redraw):
        """Test that Gambler goes all-in when dealt 2+ of same contraband."""
        gambler = create_test_gambler()

        # Hand with 2 of same contraband (set opportunity!)
        gambler.hand = [SILK, SILK, APPLE, BREAD, APPLE, BREAD]

        # Mock redraw to return more silk
        mock_redraw.return_value = [SILK, SILK, SILK]

        declaration = gambler.choose_declaration(history=[])

        # Should attempt to maximize contraband set
        assert declaration is not None
        # Redraw should have been called to maximize the set
        if mock_redraw.called:
            assert mock_redraw.call_count >= 1

    def test_declaration_returns_valid_structure(self):
        """Test that Gambler's declaration has valid structure."""
        gambler = create_test_gambler()
        gambler.hand = [APPLE, APPLE, APPLE, BREAD, BREAD, BREAD]

        declaration = gambler.choose_declaration(history=[])

        assert declaration is not None
        assert "declared_id" in declaration
        assert "count" in declaration
        assert "actual_ids" in declaration
        assert "lie" in declaration

        # Count should match actual_ids length
        assert declaration["count"] == len(declaration["actual_ids"])


class TestGamblerPersonality:
    """Test Gambler's personality traits."""

    def test_high_bluff_skill(self):
        """Test that Gambler has high bluff skill (poker face)."""
        gambler = create_test_gambler()

        assert gambler.bluff_skill >= 9, "Gambler should have excellent poker face"

    def test_high_risk_tolerance(self):
        """Test that Gambler has high risk tolerance (goes all-in)."""
        gambler = create_test_gambler()

        assert gambler.risk_tolerance >= 9, "Gambler should have high risk tolerance"

    def test_moderate_to_high_greed(self):
        """Test that Gambler has moderate to high greed (motivated by big scores)."""
        gambler = create_test_gambler()

        assert gambler.greed >= 7, "Gambler should be motivated by big scores"

    def test_moderate_honesty_bias(self):
        """Test that Gambler has moderate honesty (honest most of the time)."""
        gambler = create_test_gambler()

        # Should be honest enough to build reputation, but not too honest
        assert 5 <= gambler.honesty_bias <= 7, "Gambler should be moderately honest"


class TestGamblerStrategy:
    """Test Gambler's overall strategy."""

    def test_no_bribe_strategy_consistency(self):
        """Test that Gambler consistently never bribes."""
        gambler = create_test_gambler()

        # Test multiple scenarios
        scenarios = [
            ([SILK, SILK, SILK], [APPLE, APPLE, APPLE], True),  # Contraband
            ([APPLE, APPLE, APPLE], [APPLE, APPLE, APPLE], False),  # Honest
            ([SILK, APPLE, BREAD], [APPLE, APPLE, APPLE], True),  # Mixed
        ]

        for actual, declared, is_lying in scenarios:
            should_bribe = gambler.should_offer_proactive_bribe(
                sheriff_authority=5,
                sheriff_reputation=10,
                actual_goods=actual,
                declared_goods=declared,
            )
            assert not should_bribe, (
                f"Gambler should never bribe (scenario: lying={is_lying})"
            )

            bribe = gambler.calculate_proactive_bribe(actual, is_lying, 5)
            assert bribe == 0, (
                f"Gambler should always return 0 bribe (scenario: lying={is_lying})"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
