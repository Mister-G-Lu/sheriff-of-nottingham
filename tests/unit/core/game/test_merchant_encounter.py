"""
Unit tests for core/game/merchant_encounter.py
Tests negotiation flow logic with mocked UI functions.
"""

import unittest
from unittest.mock import Mock, patch

from core.game.merchant_encounter import run_negotiation
from core.mechanics.goods import APPLE, SILK, Good
from core.players.merchants import Merchant
from core.players.sheriff import Sheriff
from core.systems.game_stats import GameStats


class TestNegotiationFlow(unittest.TestCase):
    """Test negotiation flow with various outcomes."""

    def setUp(self):
        """Set up test fixtures."""
        self.sheriff = Sheriff(perception=5, authority=5, reputation=10)
        self.merchant = Mock(spec=Merchant)
        self.merchant.name = "Test Merchant"
        self.merchant.gold = 50
        self.stats = GameStats()
        self.actual_goods = [APPLE, SILK]  # Mixed legal/contraband

    @patch("core.game.merchant_encounter.show_threat")
    @patch("core.game.merchant_encounter.show_merchant_refuses")
    @patch("core.game.merchant_encounter.initiate_threat")
    def test_merchant_refuses_bribe_leads_to_inspection(
        self, mock_initiate, mock_refuses, mock_threat
    ):
        """Test that merchant refusing to bribe leads to inspection."""
        # Merchant refuses to offer bribe
        mock_initiate.return_value = "refuse"

        result = run_negotiation(
            self.sheriff, self.merchant, self.actual_goods, self.stats
        )

        # Should return True (inspect)
        self.assertTrue(result)

        # Verify UI calls
        mock_threat.assert_called_once_with(self.merchant)
        mock_refuses.assert_called_once_with(self.merchant)

    @patch("core.game.merchant_encounter.show_threat")
    @patch("core.game.merchant_encounter.show_bribe_offer")
    @patch("core.game.merchant_encounter.show_bribe_accepted")
    @patch("core.game.merchant_encounter.prompt_negotiation_response")
    @patch("core.game.merchant_encounter.initiate_threat")
    @patch("core.game.merchant_encounter.sheriff_respond_to_bribe")
    def test_sheriff_accepts_bribe_first_offer(
        self,
        mock_sheriff_respond,
        mock_initiate,
        mock_prompt,
        mock_accepted,
        mock_offer,
        mock_threat,
    ):
        """Test sheriff accepting bribe on first offer."""
        # Merchant offers 10 gold
        mock_initiate.return_value = 10
        # Sheriff accepts immediately
        mock_prompt.return_value = ("accept", 0)

        result = run_negotiation(
            self.sheriff, self.merchant, self.actual_goods, self.stats
        )

        # Should return False (don't inspect)
        self.assertFalse(result)

        # Verify bribe was processed
        mock_sheriff_respond.assert_called_once_with(
            self.sheriff, self.merchant, 10, self.stats
        )

        # Verify UI calls
        mock_threat.assert_called_once()
        mock_offer.assert_called_once_with(self.merchant, 10, 1)
        mock_accepted.assert_called_once_with(self.merchant, 10)

    @patch("core.game.merchant_encounter.show_threat")
    @patch("core.game.merchant_encounter.show_bribe_offer")
    @patch("core.game.merchant_encounter.show_bribe_rejected")
    @patch("core.game.merchant_encounter.prompt_negotiation_response")
    @patch("core.game.merchant_encounter.initiate_threat")
    def test_sheriff_rejects_bribe_leads_to_inspection(
        self, mock_initiate, mock_prompt, mock_rejected, mock_offer, mock_threat
    ):
        """Test sheriff rejecting bribe leads to inspection."""
        # Merchant offers 10 gold
        mock_initiate.return_value = 10
        # Sheriff rejects
        mock_prompt.return_value = ("reject", 0)

        result = run_negotiation(
            self.sheriff, self.merchant, self.actual_goods, self.stats
        )

        # Should return True (inspect)
        self.assertTrue(result)

        # Verify UI calls
        mock_rejected.assert_called_once_with(self.merchant)

    @patch("core.game.merchant_encounter.show_threat")
    @patch("core.game.merchant_encounter.show_bribe_offer")
    @patch("core.game.merchant_encounter.show_merchant_gives_up")
    @patch("core.game.merchant_encounter.prompt_negotiation_response")
    @patch("core.game.merchant_encounter.initiate_threat")
    @patch("core.game.merchant_encounter.sheriff_respond_to_bribe")
    def test_merchant_gives_up_after_counter(
        self,
        mock_sheriff_respond,
        mock_initiate,
        mock_prompt,
        mock_gives_up,
        mock_offer,
        mock_threat,
    ):
        """Test merchant giving up after sheriff counter-offer."""
        # Merchant offers 10 gold
        mock_initiate.return_value = 10
        # Sheriff counters with 20 gold demand
        mock_prompt.return_value = ("counter", 20)
        # Merchant refuses counter (via should_accept_counter method)
        self.merchant.should_accept_counter.return_value = False

        result = run_negotiation(
            self.sheriff, self.merchant, self.actual_goods, self.stats
        )

        # Should return True (inspect)
        self.assertTrue(result)

        # Verify merchant was asked to respond to counter
        self.merchant.should_accept_counter.assert_called_once()

        # Verify UI calls
        mock_gives_up.assert_called_once_with(self.merchant)

    @patch("core.game.merchant_encounter.show_threat")
    @patch("core.game.merchant_encounter.show_bribe_offer")
    @patch("core.game.merchant_encounter.show_bribe_accepted")
    @patch("core.game.merchant_encounter.prompt_negotiation_response")
    @patch("core.game.merchant_encounter.initiate_threat")
    @patch("core.game.merchant_encounter.sheriff_respond_to_bribe")
    def test_merchant_accepts_counter_offer(
        self,
        mock_sheriff_respond,
        mock_initiate,
        mock_prompt,
        mock_accepted,
        mock_offer,
        mock_threat,
    ):
        """Test merchant accepting sheriff's counter-offer."""
        # Merchant offers 10 gold
        mock_initiate.return_value = 10
        # Sheriff counters with 15 gold demand
        mock_prompt.return_value = ("counter", 15)
        # Merchant accepts counter (via should_accept_counter method)
        self.merchant.should_accept_counter.return_value = True

        result = run_negotiation(
            self.sheriff, self.merchant, self.actual_goods, self.stats
        )

        # Should return False (don't inspect)
        self.assertFalse(result)

        # Verify bribe was processed with counter amount
        mock_sheriff_respond.assert_called_once_with(
            self.sheriff, self.merchant, 15, self.stats
        )

        # Verify UI calls
        mock_accepted.assert_called_once_with(self.merchant, 15)

    # NOTE: Multi-round negotiation test removed as implementation was simplified
    # The new implementation uses merchant.should_accept_counter() which returns boolean
    # instead of supporting multi-round counter-counter offers


class TestContrabandValueCalculation(unittest.TestCase):
    """Test that contraband value is calculated correctly for merchant decisions."""

    @patch("core.game.merchant_encounter.show_threat")
    @patch("core.game.merchant_encounter.show_merchant_refuses")
    @patch("core.game.merchant_encounter.initiate_threat")
    def test_contraband_value_passed_to_initiate_threat(
        self, mock_initiate, mock_refuses, mock_threat
    ):
        """Test that contraband value is correctly calculated and passed."""
        sheriff = Sheriff(perception=5, authority=5, reputation=10)
        merchant = Mock(spec=Merchant)
        merchant.name = "Test Merchant"

        # Create goods with known contraband value
        from core.mechanics.goods import GoodKind

        legal_good = Good(id="apple", name="Apple", kind=GoodKind.LEGAL, value=2)
        contraband1 = Good(id="silk", name="Silk", kind=GoodKind.CONTRABAND, value=6)
        contraband2 = Good(
            id="pepper", name="Pepper", kind=GoodKind.CONTRABAND, value=8
        )
        actual_goods = [legal_good, contraband1, contraband2]

        mock_initiate.return_value = "refuse"

        run_negotiation(sheriff, merchant, actual_goods)

        # Verify initiate_threat was called with correct contraband value (6 + 8 = 14)
        mock_initiate.assert_called_once_with(merchant, 14, sheriff.authority)


class TestNegotiationWithoutStats(unittest.TestCase):
    """Test negotiation works without GameStats object."""

    @patch("core.game.merchant_encounter.show_threat")
    @patch("core.game.merchant_encounter.show_bribe_offer")
    @patch("core.game.merchant_encounter.show_bribe_accepted")
    @patch("core.game.merchant_encounter.prompt_negotiation_response")
    @patch("core.game.merchant_encounter.initiate_threat")
    @patch("core.game.merchant_encounter.sheriff_respond_to_bribe")
    def test_negotiation_without_stats_object(
        self,
        mock_sheriff_respond,
        mock_initiate,
        mock_prompt,
        mock_accepted,
        mock_offer,
        mock_threat,
    ):
        """Test that negotiation works when stats=None."""
        sheriff = Sheriff(perception=5, authority=5, reputation=10)
        merchant = Mock(spec=Merchant)
        merchant.name = "Test Merchant"
        actual_goods = [APPLE]

        mock_initiate.return_value = 10
        mock_prompt.return_value = ("accept", 0)

        # Call without stats parameter
        result = run_negotiation(sheriff, merchant, actual_goods, stats=None)

        # Should still work
        self.assertFalse(result)

        # Verify stats=None was passed through
        mock_sheriff_respond.assert_called_once_with(sheriff, merchant, 10, None)


if __name__ == "__main__":
    unittest.main()
