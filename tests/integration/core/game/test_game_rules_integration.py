"""
Integration tests extracted from test_game_rules.py
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from core.game.game_rules import separate_declared_and_undeclared, calculate_confiscation_penalty
from core.mechanics.goods import APPLE, SILK, CHEESE, PEPPER, MEAD


class TestGameRulesIntegration:
    """Integration tests for game rules"""
    
    def test_full_inspection_scenario(self):
        """Test complete inspection scenario with rules"""
        # Merchant declares 2 apples but has 1 apple + 1 silk
        mock_apple = Mock(id='apple', value=5)
        mock_silk = Mock(id='silk', value=20)
        
        actual_goods = [mock_apple, mock_silk]
        declaration = {'good_id': 'apple', 'count': 2}
        
        # Separate goods
        declared, undeclared = separate_declared_and_undeclared(actual_goods, declaration)
        
        # Calculate penalty
        penalty = calculate_confiscation_penalty(undeclared)
        
        assert len(declared) == 1  # 1 apple
        assert len(undeclared) == 1  # 1 silk
        assert penalty == 10  # 50% of 20
    
    def test_honest_merchant_scenario(self):
        """Test scenario with honest merchant"""
        apples = [Mock(id='apple', value=5) for _ in range(3)]
        
        actual_goods = apples
        declaration = {'good_id': 'apple', 'count': 3}
        
        declared, undeclared = separate_declared_and_undeclared(actual_goods, declaration)
        penalty = calculate_confiscation_penalty(undeclared)
        
        assert len(declared) == 3
        assert len(undeclared) == 0
        assert penalty == 0
    
    def test_full_contraband_scenario(self):
        """Test scenario with all contraband"""
        contraband = [
            Mock(id='silk', value=20),
            Mock(id='pepper', value=15),
            Mock(id='mead', value=10)
        ]
        
        actual_goods = contraband
        declaration = {'good_id': 'apple', 'count': 3}
        
        declared, undeclared = separate_declared_and_undeclared(actual_goods, declaration)
        penalty = calculate_confiscation_penalty(undeclared)
        
        assert len(declared) == 0
        assert len(undeclared) == 3
        assert penalty == 22  # 50% of 45 (rounded down)
