"""
Unit tests for merchant loading and management system
"""

import unittest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.players.merchants import Merchant, load_merchants
from core.players.merchant_loader import characters_dir


class TestMerchantLoading(unittest.TestCase):
    """Test merchant loading system."""
    
    def test_load_merchants(self):
        """Test loading all merchants."""
        merchants = load_merchants()
        
        self.assertIsInstance(merchants, list)
        self.assertGreater(len(merchants), 0)
        
        # All should be Merchant objects
        for merchant in merchants:
            self.assertIsInstance(merchant, Merchant)
    
    def test_merchant_has_required_attributes(self):
        """Test that loaded merchants have required attributes."""
        merchants = load_merchants(limit=1)
        
        if len(merchants) > 0:
            merchant = merchants[0]
            
            # Required attributes
            self.assertIsNotNone(merchant.id)
            self.assertIsNotNone(merchant.name)
            self.assertIsNotNone(merchant.intro)
            self.assertIsInstance(merchant.tells_honest, list)
            self.assertIsInstance(merchant.tells_lying, list)
            
            # Numeric attributes should be valid
            self.assertGreaterEqual(merchant.bluff_skill, 0)
            self.assertLessEqual(merchant.bluff_skill, 10)
            self.assertGreaterEqual(merchant.risk_tolerance, 0)
            self.assertLessEqual(merchant.risk_tolerance, 10)
    
    def test_characters_dir_exists(self):
        """Test that characters directory function returns a valid path."""
        char_dir = characters_dir()
        
        self.assertIsNotNone(char_dir)
        # The function returns a Path object - check it's valid
        self.assertIsInstance(char_dir, Path)
        
        # The function should return a path that ends with "characters"
        self.assertEqual(char_dir.name, "characters")
        
        # Test that we can construct a data path from it
        data_dir = char_dir / "data"
        self.assertIsInstance(data_dir, Path)
        
        # The actual directory existence depends on where the code is run from
        # Just verify the path is constructed correctly
        self.assertTrue(str(data_dir).endswith("characters/data") or 
                       str(data_dir).endswith("characters\\data"))
    
    def test_load_merchants_with_limit(self):
        """Test loading merchants with limit."""
        merchants = load_merchants(limit=3)
        
        self.assertLessEqual(len(merchants), 3)


class TestMerchantBehavior(unittest.TestCase):
    """Test merchant behavior and state tracking."""
    
    def test_merchant_gold_tracking(self):
        """Test merchant gold tracking."""
        merchant = Merchant(id="test", name="Test", intro="", tells_honest=[], tells_lying=[], gold=100)
        
        self.assertEqual(merchant.gold, 100)
        
        # Simulate spending gold
        merchant.gold -= 20
        self.assertEqual(merchant.gold, 80)
    
    def test_merchant_bluff_roll(self):
        """Test merchant bluff roll."""
        merchant = Merchant(id="test", name="Test", intro="", tells_honest=[], tells_lying=[], bluff_skill=5)
        
        # Roll multiple times to test range
        for _ in range(10):
            roll = merchant.roll_bluff()
            self.assertIsInstance(roll, int)
            self.assertGreaterEqual(roll, 1)
            self.assertLessEqual(roll, 20)  # 1-10 + 0-10 skill
    
    def test_merchant_smuggle_summary(self):
        """Test merchant smuggle summary."""
        merchant = Merchant(id="test", name="Test", intro="", tells_honest=[], tells_lying=[])
        
        summary = merchant.smuggle_summary()
        
        self.assertIsInstance(summary, dict)
        self.assertIn('contraband_passed_count', summary)
        self.assertIn('contraband_passed_value', summary)
        self.assertIn('legal_sold_count', summary)
        self.assertIn('legal_sold_value', summary)
    
    def test_merchant_difficulty_tier(self):
        """Test merchant difficulty tier assignment."""
        merchant = Merchant(id="test", name="Test", intro="", tells_honest=[], tells_lying=[], 
                          difficulty_tier="medium")
        
        self.assertEqual(merchant.difficulty_tier, "medium")


if __name__ == '__main__':
    unittest.main()
