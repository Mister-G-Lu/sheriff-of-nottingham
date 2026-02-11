"""
Unit tests for core/game/game_rules.py
Tests game constants and rule functions
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock

# Setup headless mode
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from core.constants import BAG_SIZE_LIMIT, STARTING_GOLD, STARTING_REPUTATION
from core.game.game_rules import (
    calculate_confiscation_penalty, separate_declared_and_undeclared
)

class TestGameConstants:
    """Tests for game constants"""
    
    def test_bag_size_limit_exists(self):
        """Test that BAG_SIZE_LIMIT is defined"""
        assert BAG_SIZE_LIMIT is not None
        assert isinstance(BAG_SIZE_LIMIT, int)
        assert BAG_SIZE_LIMIT > 0
    
    def test_starting_gold_exists(self):
        """Test that STARTING_GOLD is defined"""
        assert STARTING_GOLD is not None
        assert isinstance(STARTING_GOLD, int)
        assert STARTING_GOLD >= 0
    
    def test_starting_reputation_exists(self):
        """Test that STARTING_REPUTATION is defined"""
        assert STARTING_REPUTATION is not None
        assert isinstance(STARTING_REPUTATION, int)
        assert STARTING_REPUTATION > 0

class TestCalculateConfiscationPenalty:
    """Tests for calculate_confiscation_penalty function"""
    
    def test_penalty_single_item(self):
        """Test penalty calculation for single item"""
        mock_good = Mock()
        mock_good.value = 10
        
        penalty = calculate_confiscation_penalty([mock_good])
        
        assert penalty == 5  # 50% of 10
    
    def test_penalty_multiple_items(self):
        """Test penalty calculation for multiple items"""
        mock_good1 = Mock()
        mock_good1.value = 10
        mock_good2 = Mock()
        mock_good2.value = 20
        
        penalty = calculate_confiscation_penalty([mock_good1, mock_good2])
        
        assert penalty == 15  # 50% of 30
    
    def test_penalty_empty_list(self):
        """Test penalty calculation for empty list"""
        penalty = calculate_confiscation_penalty([])
        
        assert penalty == 0
    
    def test_penalty_odd_value(self):
        """Test penalty calculation with odd total value"""
        mock_good = Mock()
        mock_good.value = 15
        
        penalty = calculate_confiscation_penalty([mock_good])
        
        assert penalty == 7  # 50% of 15, rounded down
    
    def test_penalty_high_value_items(self):
        """Test penalty calculation for high value items"""
        goods = [Mock(value=50), Mock(value=30), Mock(value=20)]
        
        penalty = calculate_confiscation_penalty(goods)
        
        assert penalty == 50  # 50% of 100

class TestSeparateDeclaredAndUndeclared:
    """Tests for separate_declared_and_undeclared function"""
    
    def test_separate_all_declared(self):
        """Test when all goods match declaration"""
        mock_apple1 = Mock()
        mock_apple1.id = 'apple'
        mock_apple2 = Mock()
        mock_apple2.id = 'apple'
        
        actual_goods = [mock_apple1, mock_apple2]
        declaration = {'good_id': 'apple', 'count': 2}
        
        declared, undeclared = separate_declared_and_undeclared(actual_goods, declaration)
        
        assert len(declared) == 2
        assert len(undeclared) == 0
    
    def test_separate_all_undeclared(self):
        """Test when no goods match declaration"""
        mock_silk = Mock()
        mock_silk.id = 'silk'
        mock_pepper = Mock()
        mock_pepper.id = 'pepper'
        
        actual_goods = [mock_silk, mock_pepper]
        declaration = {'good_id': 'apple', 'count': 2}
        
        declared, undeclared = separate_declared_and_undeclared(actual_goods, declaration)
        
        assert len(declared) == 0
        assert len(undeclared) == 2
    
    def test_separate_mixed_goods(self):
        """Test when some goods match declaration"""
        mock_apple1 = Mock()
        mock_apple1.id = 'apple'
        mock_apple2 = Mock()
        mock_apple2.id = 'apple'
        mock_silk = Mock()
        mock_silk.id = 'silk'
        
        actual_goods = [mock_apple1, mock_apple2, mock_silk]
        declaration = {'good_id': 'apple', 'count': 2}
        
        declared, undeclared = separate_declared_and_undeclared(actual_goods, declaration)
        
        assert len(declared) == 2
        assert len(undeclared) == 1
        assert all(g.id == 'apple' for g in declared)
        assert undeclared[0].id == 'silk'
    
    def test_separate_partial_declaration(self):
        """Test when declared count is less than actual matching goods"""
        apples = [Mock(id='apple') for _ in range(3)]
        
        actual_goods = apples
        declaration = {'good_id': 'apple', 'count': 2}
        
        declared, undeclared = separate_declared_and_undeclared(actual_goods, declaration)
        
        assert len(declared) == 2
        assert len(undeclared) == 1
    
    def test_separate_over_declaration(self):
        """Test when declared count is more than actual matching goods"""
        mock_apple = Mock()
        mock_apple.id = 'apple'
        mock_cheese = Mock()
        mock_cheese.id = 'cheese'
        
        actual_goods = [mock_apple, mock_cheese]
        declaration = {'good_id': 'apple', 'count': 3}
        
        declared, undeclared = separate_declared_and_undeclared(actual_goods, declaration)
        
        assert len(declared) == 1  # Only 1 apple available
        assert len(undeclared) == 1  # Cheese is undeclared
    
    def test_separate_empty_bag(self):
        """Test with empty bag"""
        actual_goods = []
        declaration = {'good_id': 'apple', 'count': 2}
        
        declared, undeclared = separate_declared_and_undeclared(actual_goods, declaration)
        
        assert len(declared) == 0
        assert len(undeclared) == 0

