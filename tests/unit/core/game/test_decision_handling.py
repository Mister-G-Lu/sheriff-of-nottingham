"""
Unit tests for core/game/decision_handling.py
Tests player decision prompts and UI coordination
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

from core.game.decision_handling import prompt_inspection, update_stats_bar

class TestPromptInspection:
    """Tests for prompt_inspection function"""
    
    @patch('builtins.input', return_value='i')
    def test_prompt_inspection_inspect(self, mock_input):
        """Test choosing to inspect"""
        result = prompt_inspection()
        
        assert result is True
        mock_input.assert_called_once()
    
    @patch('builtins.input', return_value='inspect')
    def test_prompt_inspection_inspect_full_word(self, mock_input):
        """Test choosing to inspect with full word"""
        result = prompt_inspection()
        
        assert result is True
    
    @patch('builtins.input', return_value='p')
    def test_prompt_inspection_pass(self, mock_input):
        """Test choosing to pass"""
        result = prompt_inspection()
        
        assert result is False
    
    @patch('builtins.input', return_value='pass')
    def test_prompt_inspection_pass_full_word(self, mock_input):
        """Test choosing to pass with full word"""
        result = prompt_inspection()
        
        assert result is False
    
    @patch('builtins.input', side_effect=['invalid', 'i'])
    @patch('builtins.print')
    def test_prompt_inspection_invalid_then_valid(self, mock_print, mock_input):
        """Test invalid input then valid input"""
        result = prompt_inspection()
        
        assert result is True
        assert mock_input.call_count == 2
        # Should print error message
        assert mock_print.called
    
    @patch('builtins.input', side_effect=['', 'x', 'p'])
    @patch('builtins.print')
    def test_prompt_inspection_multiple_invalid(self, mock_print, mock_input):
        """Test multiple invalid inputs before valid"""
        result = prompt_inspection()
        
        assert result is False
        assert mock_input.call_count == 3
    
    @patch('builtins.input', return_value='I')
    def test_prompt_inspection_case_insensitive(self, mock_input):
        """Test that input is case insensitive"""
        result = prompt_inspection()
        
        assert result is True
    
    @patch('builtins.input', return_value='  i  ')
    def test_prompt_inspection_whitespace_stripped(self, mock_input):
        """Test that whitespace is stripped"""
        result = prompt_inspection()
        
        assert result is True
    
    @patch('builtins.input', return_value='i')
    def test_prompt_inspection_custom_prompt(self, mock_input):
        """Test with custom prompt message"""
        custom_prompt = "Custom prompt: "
        result = prompt_inspection(custom_prompt)
        
        assert result is True
        mock_input.assert_called_with(custom_prompt)

class TestUpdateStatsBar:
    """Tests for update_stats_bar function"""
    
    @patch('ui.pygame_ui.get_ui')
    def test_update_stats_bar_with_pygame(self, mock_get_ui):
        """Test updating stats bar when pygame UI is available"""
        mock_ui = Mock()
        mock_get_ui.return_value = mock_ui
        
        mock_sheriff = Mock()
        mock_stats = Mock()
        
        update_stats_bar(mock_sheriff, mock_stats, 5, 10)
        
        mock_get_ui.assert_called_once()
        mock_ui.update_stats.assert_called_once_with(mock_sheriff, mock_stats, 5, 10)
    
    @patch('ui.pygame_ui.get_ui', side_effect=ImportError)
    def test_update_stats_bar_without_pygame(self, mock_get_ui):
        """Test updating stats bar when pygame UI is not available (terminal mode)"""
        mock_sheriff = Mock()
        mock_stats = Mock()
        
        # Should not raise error
        update_stats_bar(mock_sheriff, mock_stats, 3, 8)
        
        mock_get_ui.assert_called_once()
    
    @patch('ui.pygame_ui.get_ui')
    def test_update_stats_bar_first_merchant(self, mock_get_ui):
        """Test updating stats bar for first merchant"""
        mock_ui = Mock()
        mock_get_ui.return_value = mock_ui
        
        mock_sheriff = Mock()
        mock_stats = Mock()
        
        update_stats_bar(mock_sheriff, mock_stats, 1, 10)
        
        mock_ui.update_stats.assert_called_once_with(mock_sheriff, mock_stats, 1, 10)
    
    @patch('ui.pygame_ui.get_ui')
    def test_update_stats_bar_last_merchant(self, mock_get_ui):
        """Test updating stats bar for last merchant"""
        mock_ui = Mock()
        mock_get_ui.return_value = mock_ui
        
        mock_sheriff = Mock()
        mock_stats = Mock()
        
        update_stats_bar(mock_sheriff, mock_stats, 10, 10)
        
        mock_ui.update_stats.assert_called_once_with(mock_sheriff, mock_stats, 10, 10)
    
    @patch('ui.pygame_ui.get_ui')
    def test_update_stats_bar_initial_state(self, mock_get_ui):
        """Test updating stats bar with initial state (0 merchants)"""
        mock_ui = Mock()
        mock_get_ui.return_value = mock_ui
        
        mock_sheriff = Mock()
        mock_stats = Mock()
        
        update_stats_bar(mock_sheriff, mock_stats, 0, 8)
        
        mock_ui.update_stats.assert_called_once_with(mock_sheriff, mock_stats, 0, 8)

