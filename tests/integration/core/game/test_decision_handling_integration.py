"""
Integration tests extracted from test_decision_handling.py
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from core.game.decision_handling import update_stats_bar, prompt_inspection


class TestDecisionHandlingIntegration:
    """Integration tests for decision_handling module"""
    
    @patch('builtins.input', return_value='i')
    @patch('ui.pygame_ui.get_ui')
    def test_full_decision_flow(self, mock_get_ui, mock_input):
        """Test complete decision flow with stats update"""
        mock_ui = Mock()
        mock_get_ui.return_value = mock_ui
        
        mock_sheriff = Mock()
        mock_stats = Mock()
        
        # Update stats before decision
        update_stats_bar(mock_sheriff, mock_stats, 1, 5)
        
        # Get player decision
        should_inspect = prompt_inspection()
        
        # Update stats after decision
        update_stats_bar(mock_sheriff, mock_stats, 2, 5)
        
        assert should_inspect is True
        assert mock_ui.update_stats.call_count == 2
    
    @patch('builtins.input', side_effect=['invalid', 'p'])
    @patch('ui.pygame_ui.get_ui', side_effect=ImportError)
    @patch('builtins.print')
    def test_terminal_mode_with_retry(self, mock_print, mock_get_ui, mock_input):
        """Test decision handling in terminal mode with input retry"""
        mock_sheriff = Mock()
        mock_stats = Mock()
        
        # Stats update should not fail in terminal mode
        update_stats_bar(mock_sheriff, mock_stats, 1, 3)
        
        # Prompt should handle invalid input
        should_inspect = prompt_inspection()
        
        assert should_inspect is False
        assert mock_input.call_count == 2
