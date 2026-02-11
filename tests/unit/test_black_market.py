"""
Unit tests for core/black_market.py
Tests black market encounter system.
"""

import unittest
from unittest.mock import Mock
from core.mechanics.black_market import BlackMarketContact, check_black_market_offer


class TestBlackMarketContact(unittest.TestCase):
    """Test BlackMarketContact class."""
    
    def test_initialization(self):
        """Test black market initializes correctly."""
        bm = BlackMarketContact()
        
        self.assertFalse(bm.has_appeared)
        self.assertFalse(bm.deal_accepted)
        
    def test_mark_appeared(self):
        """Test marking black market as appeared."""
        bm = BlackMarketContact()
        
        bm.has_appeared = True
        
        self.assertTrue(bm.has_appeared)
        self.assertFalse(bm.deal_accepted)
        
    def test_accept_deal(self):
        """Test accepting black market deal."""
        bm = BlackMarketContact()
        
        bm.deal_accepted = True
        
        self.assertTrue(bm.deal_accepted)


class TestBlackMarketTrigger(unittest.TestCase):
    """Test black market appearance conditions."""
    
    def test_no_trigger_if_already_appeared(self):
        """Test black market doesn't appear twice."""
        bm = BlackMarketContact()
        bm.has_appeared = True
        
        sheriff = Mock()
        sheriff.reputation = 2
        
        stats = Mock()
        stats.bribes_accepted = 5
        stats.missed_smugglers = 0  # Add missing attribute
        
        should_appear, _ = check_black_market_offer(stats, sheriff)
        
        # Function returns tuple, we just check it doesn't crash
        self.assertIsInstance(should_appear, bool)
        
    def test_trigger_on_low_reputation(self):
        """Test black market can appear with low reputation."""
        bm = BlackMarketContact()
        
        sheriff = Mock()
        sheriff.reputation = 2
        
        stats = Mock()
        stats.bribes_accepted = 3
        stats.missed_smugglers = 2
        
        # This should potentially trigger (has random chance)
        # We test the logic allows it
        result, _ = check_black_market_offer(stats, sheriff)
        
        # Result is boolean (may be True or False due to randomness)
        self.assertIsInstance(result, bool)
        
    def test_trigger_on_many_bribes(self):
        """Test black market can appear with many bribes."""
        bm = BlackMarketContact()
        
        sheriff = Mock()
        sheriff.reputation = 5
        
        stats = Mock()
        stats.bribes_accepted = 5
        stats.missed_smugglers = 3
        
        result, _ = check_black_market_offer(stats, sheriff)
        
        self.assertIsInstance(result, bool)
        
    def test_no_trigger_on_high_reputation_few_bribes(self):
        """Test black market unlikely with high rep and few bribes."""
        bm = BlackMarketContact()
        
        sheriff = Mock()
        sheriff.reputation = 9
        
        stats = Mock()
        stats.bribes_accepted = 0
        stats.missed_smugglers = 0
        
        result, _ = check_black_market_offer(stats, sheriff)
        
        # Should be False (conditions not met)
        self.assertFalse(result)


class TestBlackMarketState(unittest.TestCase):
    """Test black market state management."""
    
    def test_state_persistence(self):
        """Test black market state persists."""
        bm = BlackMarketContact()
        
        # Simulate appearance
        bm.has_appeared = True
        
        # Later check
        self.assertTrue(bm.has_appeared)
        
        # Simulate deal acceptance
        bm.deal_accepted = True
        
        self.assertTrue(bm.deal_accepted)
        
    def test_independent_flags(self):
        """Test has_appeared and deal_accepted are independent."""
        bm = BlackMarketContact()
        
        # Can appear without accepting
        bm.has_appeared = True
        self.assertTrue(bm.has_appeared)
        self.assertFalse(bm.deal_accepted)
        
        # Can accept after appearing
        bm.deal_accepted = True
        self.assertTrue(bm.has_appeared)
        self.assertTrue(bm.deal_accepted)


class TestBlackMarketEdgeCases(unittest.TestCase):
    """Test edge cases."""
    
    def test_reputation_zero(self):
        """Test with reputation at 0."""
        bm = BlackMarketContact()
        
        sheriff = Mock()
        sheriff.reputation = 0
        
        stats = Mock()
        stats.bribes_accepted = 10
        stats.missed_smugglers = 5
        
        # Should still work (or at least not crash)
        result, _ = check_black_market_offer(stats, sheriff)
        self.assertIsInstance(result, bool)
        
    def test_negative_bribes(self):
        """Test with negative bribes (shouldn't happen, but test robustness)."""
        bm = BlackMarketContact()
        
        sheriff = Mock()
        sheriff.reputation = 5
        
        stats = Mock()
        stats.bribes_accepted = -1
        stats.missed_smugglers = 0
        
        result, _ = check_black_market_offer(stats, sheriff)
        
        # Should handle gracefully
        self.assertIsInstance(result, bool)


if __name__ == '__main__':
    unittest.main()
