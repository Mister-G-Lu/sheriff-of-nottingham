"""
Unit tests for ui/narration.py
Tests narration display functions.
"""

import unittest
from unittest.mock import Mock
from core.players.merchants import Merchant
from core.game.rounds import Declaration
from ui.narration import narrate_arrival, show_declaration


class TestNarration(unittest.TestCase):
    """Test narration functions."""
    
    def test_narrate_arrival(self):
        """Test merchant arrival narration."""
        merchant = Mock()
        merchant.name = "Test Merchant"
        merchant.intro = "A test merchant."
        merchant.lore = None
        
        # Should not crash
        narrate_arrival(merchant)
        
    def test_show_declaration(self):
        """Test declaration display."""
        merchant = Mock()
        merchant.name = "Test Merchant"
        
        declaration = Declaration(good_id="apple", count=3)
        
        # Should not crash
        show_declaration(merchant, declaration)


if __name__ == '__main__':
    unittest.main()