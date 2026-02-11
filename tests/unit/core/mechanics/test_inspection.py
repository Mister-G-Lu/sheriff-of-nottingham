"""
Unit tests for core/mechanics/inspection.py
Tests inspection logic with proper Sheriff of Nottingham rules
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch

# Setup headless mode
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from core.mechanics.inspection import handle_inspection, handle_pass_without_inspection

class TestHandleInspection:
    """Tests for handle_inspection function"""
    
    @patch('core.mechanics.inspection.separate_declared_and_undeclared')
    def test_inspection_honest_merchant(self, mock_separate):
        """Test inspecting honest merchant"""
        merchant = Mock()
        merchant.gold = 100
        
        mock_apple = Mock(id='apple', value=5)
        actual_goods = [mock_apple, mock_apple]
        declaration = {'good_id': 'apple', 'count': 2}
        sheriff = Mock(perception=5)
        
        # All goods match declaration
        mock_separate.return_value = (actual_goods, [])
        
        result = handle_inspection(merchant, actual_goods, declaration, sheriff)
        
        assert result['was_honest'] is True
        assert result['caught_lie'] is False
        assert result['goods_passed'] == actual_goods
        assert result['goods_confiscated'] == []
        assert result['penalty_paid'] == 0
    
    @patch('core.mechanics.inspection.calculate_confiscation_penalty')
    @patch('core.mechanics.inspection.separate_declared_and_undeclared')
    @patch('random.randint')
    def test_inspection_caught_lying(self, mock_randint, mock_separate, mock_penalty):
        """Test catching lying merchant"""
        merchant = Mock()
        merchant.gold = 100
        merchant.roll_bluff.return_value = 8
        
        mock_apple = Mock(id='apple', value=5)
        mock_silk = Mock(id='silk', value=20)
        actual_goods = [mock_apple, mock_silk]
        declaration = {'good_id': 'apple', 'count': 2}
        sheriff = Mock(perception=5)
        
        # Sheriff roll beats merchant bluff
        mock_randint.return_value = 10  # Sheriff rolls 10 + 5 perception = 15 > 8
        mock_separate.return_value = ([mock_apple], [mock_silk])
        mock_penalty.return_value = 10
        
        result = handle_inspection(merchant, actual_goods, declaration, sheriff)
        
        assert result['was_honest'] is False
        assert result['caught_lie'] is True
        assert len(result['goods_passed']) == 1
        assert len(result['goods_confiscated']) == 1
        assert result['penalty_paid'] == 10
        assert merchant.gold == 90
    
    @patch('core.mechanics.inspection.separate_declared_and_undeclared')
    @patch('random.randint')
    def test_inspection_bluff_succeeds(self, mock_randint, mock_separate):
        """Test when merchant's bluff succeeds"""
        merchant = Mock()
        merchant.gold = 100
        merchant.roll_bluff.return_value = 15
        
        mock_apple = Mock(id='apple', value=5)
        mock_silk = Mock(id='silk', value=20)
        actual_goods = [mock_apple, mock_silk]
        declaration = {'good_id': 'apple', 'count': 2}
        sheriff = Mock(perception=5)
        
        # Merchant bluff beats sheriff roll
        mock_randint.return_value = 5  # Sheriff rolls 5 + 5 = 10 < 15
        mock_separate.return_value = ([mock_apple], [mock_silk])
        
        result = handle_inspection(merchant, actual_goods, declaration, sheriff)
        
        assert result['was_honest'] is False
        assert result['caught_lie'] is False
        assert result['goods_passed'] == actual_goods  # All goods pass!
        assert result['goods_confiscated'] == []
        assert result['penalty_paid'] == 0
    
    @patch('core.mechanics.inspection.calculate_confiscation_penalty')
    @patch('core.mechanics.inspection.separate_declared_and_undeclared')
    @patch('random.randint')
    def test_inspection_insufficient_gold_for_penalty(self, mock_randint, mock_separate, mock_penalty):
        """Test when merchant doesn't have enough gold for penalty"""
        merchant = Mock()
        merchant.gold = 5  # Only 5 gold
        merchant.roll_bluff.return_value = 5
        
        mock_silk = Mock(id='silk', value=20)
        actual_goods = [mock_silk]
        declaration = {'good_id': 'apple', 'count': 1}
        sheriff = Mock(perception=5)
        
        mock_randint.return_value = 10
        mock_separate.return_value = ([], [mock_silk])
        mock_penalty.return_value = 10  # Penalty is 10 but merchant only has 5
        
        result = handle_inspection(merchant, actual_goods, declaration, sheriff)
        
        assert result['penalty_paid'] == 5  # Only pays what they have
        assert merchant.gold == 0
        assert result['sheriff_gold_gained'] == 5

class TestHandlePassWithoutInspection:
    """Tests for handle_pass_without_inspection function"""
    
    def test_pass_honest_merchant(self):
        """Test passing honest merchant without inspection"""
        merchant = Mock()
        
        mock_apple = Mock(id='apple', value=5)
        actual_goods = [mock_apple, mock_apple]
        declaration = {'good_id': 'apple', 'count': 2}
        
        result = handle_pass_without_inspection(merchant, actual_goods, declaration)
        
        assert result['was_honest'] is True
        assert result['caught_lie'] is False
        assert result['goods_passed'] == actual_goods
        assert result['goods_confiscated'] == []
        assert result['penalty_paid'] == 0
    
    def test_pass_lying_merchant(self):
        """Test passing lying merchant without inspection"""
        merchant = Mock()
        
        mock_apple = Mock(id='apple', value=5)
        mock_silk = Mock(id='silk', value=20)
        actual_goods = [mock_apple, mock_silk]
        declaration = {'good_id': 'apple', 'count': 2}
        
        result = handle_pass_without_inspection(merchant, actual_goods, declaration)
        
        assert result['was_honest'] is False
        assert result['caught_lie'] is False  # Can't catch if not inspecting
        assert result['goods_passed'] == actual_goods  # All goods pass
        assert result['goods_confiscated'] == []
        assert result['penalty_paid'] == 0
    
    def test_pass_all_contraband(self):
        """Test passing merchant with all contraband"""
        merchant = Mock()
        
        mock_silk = Mock(id='silk', value=20)
        mock_pepper = Mock(id='pepper', value=15)
        actual_goods = [mock_silk, mock_pepper]
        declaration = {'good_id': 'apple', 'count': 2}
        
        result = handle_pass_without_inspection(merchant, actual_goods, declaration)
        
        assert result['was_honest'] is False
        assert result['goods_passed'] == actual_goods
        assert result['goods_confiscated'] == []
    
    def test_pass_empty_bag(self):
        """Test passing with empty bag"""
        merchant = Mock()
        
        actual_goods = []
        declaration = {'good_id': 'apple', 'count': 0}
        
        result = handle_pass_without_inspection(merchant, actual_goods, declaration)
        
        assert result['was_honest'] is True
        assert result['goods_passed'] == []

