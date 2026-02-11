"""
Unit tests for core/game_stats.py
Tests game statistics tracking.
"""

import unittest
from core.systems.game_stats import GameStats


class TestGameStatsInitialization(unittest.TestCase):
    """Test GameStats initialization."""
    
    def test_default_initialization(self):
        """Test stats initialize to zero."""
        stats = GameStats()
        
        self.assertEqual(stats.merchants_processed, 0)
        self.assertEqual(stats.total_inspections, 0)
        self.assertEqual(stats.smugglers_caught, 0)
        self.assertEqual(stats.honest_inspected, 0)
        self.assertEqual(stats.correct_inspections, 0)
        self.assertEqual(stats.missed_smugglers, 0)
        self.assertEqual(stats.bribes_accepted, 0)
        self.assertEqual(stats.gold_earned, 0)


class TestMerchantTracking(unittest.TestCase):
    """Test merchant processing tracking."""
    
    def test_record_merchant_processed(self):
        """Test recording processed merchants."""
        stats = GameStats()
        
        stats.merchants_processed += 1
        self.assertEqual(stats.merchants_processed, 1)
        
        stats.merchants_processed += 1
        self.assertEqual(stats.merchants_processed, 2)


class TestInspectionTracking(unittest.TestCase):
    """Test inspection tracking."""
    
    def test_record_inspection_smuggler_caught(self):
        """Test recording inspection that caught a smuggler."""
        stats = GameStats()
        
        stats.record_inspection(was_honest=False, caught_lie=True)
        
        self.assertEqual(stats.total_inspections, 1)
        self.assertEqual(stats.smugglers_caught, 1)
        self.assertEqual(stats.correct_inspections, 1)
        self.assertEqual(stats.honest_inspected, 0)
        self.assertEqual(stats.missed_smugglers, 0)
        
    def test_record_inspection_honest_merchant(self):
        """Test recording inspection of honest merchant."""
        stats = GameStats()
        
        stats.record_inspection(was_honest=True, caught_lie=False)
        
        self.assertEqual(stats.total_inspections, 1)
        self.assertEqual(stats.honest_inspected, 1)
        self.assertEqual(stats.smugglers_caught, 0)
        self.assertEqual(stats.correct_inspections, 0)
        
    def test_record_missed_smuggler(self):
        """Test recording missed smuggler (not inspected)."""
        stats = GameStats()
        
        stats.record_pass(was_honest=False)
        
        self.assertEqual(stats.missed_smugglers, 1)
        self.assertEqual(stats.total_inspections, 0)


class TestBribeTracking(unittest.TestCase):
    """Test bribe tracking."""
    
    def test_record_bribe(self):
        """Test recording bribe acceptance."""
        stats = GameStats()
        
        stats.record_bribe(15)
        
        self.assertEqual(stats.bribes_accepted, 1)
        self.assertEqual(stats.gold_earned, 15)
        
    def test_multiple_bribes(self):
        """Test recording multiple bribes."""
        stats = GameStats()
        
        stats.record_bribe(10)
        stats.record_bribe(20)
        stats.record_bribe(5)
        
        self.assertEqual(stats.bribes_accepted, 3)
        self.assertEqual(stats.gold_earned, 35)


class TestAccuracyCalculation(unittest.TestCase):
    """Test accuracy percentage calculation."""
    
    def test_accuracy_no_decisions(self):
        """Test accuracy when no decisions made."""
        stats = GameStats()
        
        accuracy = stats.accuracy_percentage()
        
        self.assertEqual(accuracy, 0.0)
        
    def test_accuracy_perfect(self):
        """Test 100% accuracy."""
        stats = GameStats()
        
        stats.record_inspection(was_honest=False, caught_lie=True)
        stats.record_inspection(was_honest=False, caught_lie=True)
        
        accuracy = stats.accuracy_percentage()
        
        self.assertEqual(accuracy, 100.0)
        
    def test_accuracy_mixed(self):
        """Test mixed accuracy."""
        stats = GameStats()
        
        stats.record_inspection(was_honest=False, caught_lie=True)  # Correct
        stats.record_inspection(was_honest=True, caught_lie=False)  # Incorrect (wasted inspection)
        stats.record_inspection(was_honest=False, caught_lie=True)  # Correct
        stats.record_pass(was_honest=False)  # Incorrect (missed smuggler)
        
        # 2 correct out of 4 decisions = 50%
        accuracy = stats.accuracy_percentage()
        
        self.assertEqual(accuracy, 50.0)
        
    def test_accuracy_all_wrong(self):
        """Test 0% accuracy."""
        stats = GameStats()
        
        stats.record_inspection(was_honest=True, caught_lie=False)  # Wrong
        stats.record_pass(was_honest=False)  # Wrong (missed smuggler)
        
        accuracy = stats.accuracy_percentage()
        
        self.assertEqual(accuracy, 0.0)


class TestComplexScenarios(unittest.TestCase):
    """Test complex game scenarios."""
    
    def test_full_game_scenario(self):
        """Test a complete game scenario."""
        stats = GameStats()
        
        # Merchant 1: Smuggler caught
        stats.merchants_processed += 1
        stats.record_inspection(was_honest=False, caught_lie=True)
        
        # Merchant 2: Honest, inspected (wasted)
        stats.merchants_processed += 1
        stats.record_inspection(was_honest=True, caught_lie=False)
        
        # Merchant 3: Smuggler, bribed
        stats.merchants_processed += 1
        stats.record_bribe(20)
        stats.record_pass(was_honest=False)
        
        # Merchant 4: Honest, passed
        stats.merchants_processed += 1
        stats.record_pass(was_honest=True)
        
        # Merchant 5: Smuggler caught
        stats.merchants_processed += 1
        stats.record_inspection(was_honest=False, caught_lie=True)
        
        # Verify totals
        self.assertEqual(stats.merchants_processed, 5)
        self.assertEqual(stats.total_inspections, 3)
        self.assertEqual(stats.smugglers_caught, 2)
        self.assertEqual(stats.honest_inspected, 1)
        self.assertEqual(stats.missed_smugglers, 1)
        self.assertEqual(stats.bribes_accepted, 1)
        self.assertEqual(stats.gold_earned, 20)
        self.assertEqual(stats.correct_inspections, 3)  # 2 caught + 1 trusted honest
        
        # Accuracy: 3 correct / 4 decisions (3 inspections + 1 missed) = 75%
        self.assertEqual(stats.accuracy_percentage(), 75.0)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases."""
    
    def test_zero_gold_bribe(self):
        """Test recording a bribe with 0 gold."""
        stats = GameStats()
        
        stats.record_bribe(0)
        
        self.assertEqual(stats.bribes_accepted, 1)
        self.assertEqual(stats.gold_earned, 0)
        
    def test_large_numbers(self):
        """Test with large numbers."""
        stats = GameStats()
        
        for _ in range(100):
            stats.merchants_processed += 1
            stats.record_inspection(was_honest=False, caught_lie=True)
            
        self.assertEqual(stats.merchants_processed, 100)
        self.assertEqual(stats.total_inspections, 100)
        self.assertEqual(stats.accuracy_percentage(), 100.0)


if __name__ == '__main__':
    unittest.main()
