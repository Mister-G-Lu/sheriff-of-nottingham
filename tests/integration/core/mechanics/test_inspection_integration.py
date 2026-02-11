"""
Integration tests extracted from test_inspection.py
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from core.mechanics.inspection import handle_inspection, handle_pass_without_inspection
from core.mechanics.goods import APPLE, SILK, CHEESE
from core.players.merchants import Merchant
from core.players.sheriff import Sheriff


class TestInspectionIntegration:
    """Integration tests for inspection module"""
    
    @patch('core.mechanics.inspection.calculate_confiscation_penalty')
    @patch('core.mechanics.inspection.separate_declared_and_undeclared')
    @patch('random.randint')
    def test_full_inspection_flow_caught(self, mock_randint, mock_separate, mock_penalty):
        """Test complete inspection flow where lie is caught"""
        merchant = Mock()
        merchant.gold = 50
        merchant.roll_bluff.return_value = 10
        
        mock_cheese = Mock(id='cheese', value=8)
        mock_silk = Mock(id='silk', value=20)
        mock_pepper = Mock(id='pepper', value=15)
        actual_goods = [mock_cheese, mock_silk, mock_pepper]
        declaration = {'good_id': 'cheese', 'count': 3}
        sheriff = Mock(perception=7)
        
        # Sheriff catches the lie
        mock_randint.return_value = 8  # 8 + 7 = 15 > 10
        mock_separate.return_value = ([mock_cheese], [mock_silk, mock_pepper])
        mock_penalty.return_value = 17  # 50% of 35
        
        result = handle_inspection(merchant, actual_goods, declaration, sheriff)
        
        assert result['was_honest'] is False
        assert result['caught_lie'] is True
        assert len(result['goods_passed']) == 1  # Only cheese passes
        assert len(result['goods_confiscated']) == 2  # Silk and pepper confiscated
        assert result['penalty_paid'] == 17
        assert merchant.gold == 33
    
    def test_comparison_inspect_vs_pass(self):
        """Test comparing inspection vs passing for same scenario"""
        merchant1 = Mock(gold=100, roll_bluff=Mock(return_value=15))
        merchant2 = Mock(gold=100)
        
        mock_apple = Mock(id='apple', value=5)
        mock_silk = Mock(id='silk', value=20)
        actual_goods1 = [mock_apple, mock_silk]
        actual_goods2 = [mock_apple, mock_silk]
        declaration = {'good_id': 'apple', 'count': 2}
        sheriff = Mock(perception=5)
        
        # Pass without inspection
        result_pass = handle_pass_without_inspection(merchant2, actual_goods2, declaration)
        
        # Inspect (with bluff succeeding)
        with patch('random.randint', return_value=5):
            with patch('core.mechanics.inspection.separate_declared_and_undeclared', return_value=([mock_apple], [mock_silk])):
                result_inspect = handle_inspection(merchant1, actual_goods1, declaration, sheriff)
        
        # Both should let goods pass (bluff succeeded)
        assert result_pass['goods_passed'] == actual_goods2
        assert result_inspect['goods_passed'] == actual_goods1
        assert result_pass['was_honest'] == result_inspect['was_honest']
