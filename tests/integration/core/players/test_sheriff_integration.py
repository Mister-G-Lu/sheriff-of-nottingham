"""
Integration tests extracted from test_sheriff.py
"""

import pytest
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from core.players.sheriff import Sheriff


class TestSheriffIntegration:
    """Integration tests for Sheriff"""
    
    def test_sheriff_game_scenario(self):
        """Test Sheriff in a game-like scenario"""
        sheriff = Sheriff(reputation=5, authority=1, perception=5)
        
        # Reputation decreases from accepting bribes
        sheriff.reputation -= 1
        assert sheriff.reputation == 4
        
        # Reputation increases from catching smugglers
        sheriff.reputation += 2
        assert sheriff.reputation == 6
        
        # Authority might increase over time
        sheriff.authority += 1
        assert sheriff.authority == 2
    
    def test_multiple_sheriffs(self):
        """Test creating multiple Sheriff instances"""
        sheriff1 = Sheriff(reputation=5)
        sheriff2 = Sheriff(reputation=8)
        
        assert sheriff1.reputation == 5
        assert sheriff2.reputation == 8
        
        # They should be independent
        sheriff1.reputation = 3
        assert sheriff2.reputation == 8
