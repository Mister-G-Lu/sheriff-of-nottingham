"""
Unit tests for game state management
"""

import unittest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.systems.game_master_state import GameMasterState, MerchantTier
from core.systems.game_stats import GameStats
from core.players.merchants import Merchant


class TestGameMasterState(unittest.TestCase):
    """Test game master state tracking."""
    
    def test_initialization(self):
        """Test game master state initialization."""
        gms = GameMasterState()
        
        # New API uses 'events' instead of 'history'
        self.assertEqual(len(gms.events), 0)
        self.assertEqual(gms.current_round, 0)
    
    def test_record_inspection(self):
        """Test recording inspection events."""
        gms = GameMasterState()
        
        # New API uses record_event with different parameters
        gms.record_event(
            merchant_name="test_merchant",
            declared_good="apple",
            declared_count=5,
            actual_goods=["apple", "silk"],
            was_opened=True,
            caught_lie=True,
            bribe_offered=10
        )
        
        self.assertEqual(len(gms.events), 1)
        self.assertEqual(gms.current_round, 1)
        
        # Check event entry
        event = gms.events[0]
        self.assertEqual(event.merchant_name, "test_merchant")
        self.assertTrue(event.was_opened)
        self.assertTrue(event.caught_lie)
        self.assertEqual(event.bribe_offered, 10)
    
    def test_get_recent_history(self):
        """Test getting recent history."""
        gms = GameMasterState()
        
        # Add multiple events
        for i in range(5):
            gms.record_event(
                merchant_name=f"merchant_{i}",
                declared_good="apple",
                declared_count=5,
                actual_goods=["apple"],
                was_opened=True,
                caught_lie=True,
                bribe_offered=i * 5
            )
        
        # Get history for medium tier (last 4 events)
        recent = gms.get_history_for_tier(MerchantTier.MEDIUM)
        
        self.assertLessEqual(len(recent), 4)
        # Verify we got recent events
        self.assertGreater(len(recent), 0)
    
    def test_get_merchant_history(self):
        """Test getting history for specific merchant."""
        gms = GameMasterState()
        
        # Add events for different merchants
        gms.record_event("merchant_a", "apple", 5, ["apple"], True, True, 10)
        gms.record_event("merchant_b", "apple", 5, ["apple"], False, False, 0)
        gms.record_event("merchant_a", "apple", 5, ["silk"], True, False, 15)
        
        # Get all history and filter for merchant_a
        all_history = gms.get_history_for_tier(MerchantTier.HARD)
        history = [e for e in all_history if e['merchant_name'] == "merchant_a"]
        
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]['merchant_name'], "merchant_a")
        self.assertEqual(history[1]['merchant_name'], "merchant_a")


class TestGameStats(unittest.TestCase):
    """Test game statistics tracking."""
    
    def test_initialization(self):
        """Test game stats initialization."""
        stats = GameStats()
        
        # New API uses different attribute names
        self.assertEqual(stats.merchants_processed, 0)
        self.assertEqual(stats.gold_earned, 0)
        self.assertEqual(stats.bribes_accepted, 0)
    
    def test_record_round(self):
        """Test recording round statistics."""
        stats = GameStats()
        
        # New API uses different methods
        stats.record_bribe(25)
        stats.record_inspection(was_honest=False, caught_lie=True)
        
        self.assertEqual(stats.bribes_accepted, 1)
        self.assertEqual(stats.gold_earned, 25)
        self.assertEqual(stats.smugglers_caught, 1)
    
    def test_get_summary(self):
        """Test getting statistics summary."""
        stats = GameStats()
        
        stats.record_bribe(10)
        stats.record_bribe(15)
        stats.record_inspection(was_honest=False, caught_lie=True)
        stats.record_pass(was_honest=True)
        
        # Verify stats are tracked correctly
        self.assertEqual(stats.bribes_accepted, 2)
        self.assertEqual(stats.gold_earned, 25)
        self.assertEqual(stats.smugglers_caught, 1)


class TestMerchantTier(unittest.TestCase):
    """Test merchant tier enum."""
    
    def test_tier_values(self):
        """Test that tier enum has expected values."""
        self.assertIsNotNone(MerchantTier.EASY)
        self.assertIsNotNone(MerchantTier.MEDIUM)
        self.assertIsNotNone(MerchantTier.HARD)
    
    def test_tier_comparison(self):
        """Test tier comparison."""
        self.assertNotEqual(MerchantTier.EASY, MerchantTier.HARD)
        self.assertEqual(MerchantTier.MEDIUM, MerchantTier.MEDIUM)


if __name__ == '__main__':
    unittest.main()
