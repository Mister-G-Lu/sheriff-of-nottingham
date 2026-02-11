"""
Integration tests extracted from test_intro.py
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import patch, mock_open

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from ui.intro import print_intro


class TestPrintIntroIntegration:
    """Integration tests for print_intro"""
    
    @patch('builtins.print')
    def test_full_intro_flow(self, mock_print):
        """Test complete intro flow from file load to display"""
        mock_intro_data = {
            "title": "Test Game",
            "intro": "Complete intro text"
        }
        
        with patch('builtins.open', mock_open()):
            with patch('json.load', return_value=mock_intro_data):
                print_intro()
                
                # Verify complete flow
                assert mock_print.called
                assert any("Test Game" in str(call) for call in mock_print.call_args_list)
                assert any("Complete intro text" in str(call) for call in mock_print.call_args_list)
    
    @patch('builtins.print')
    def test_fallback_intro_complete(self, mock_print):
        """Test complete fallback intro when file is missing"""
        with patch('builtins.open', side_effect=FileNotFoundError):
            print_intro()
            
            # Verify fallback text components
            assert any("Sheriff of Nottingham" in str(call) for call in mock_print.call_args_list)
            assert any("newly appointed inspector" in str(call) for call in mock_print.call_args_list)
            assert any("Nottingham's eastern gate" in str(call) for call in mock_print.call_args_list)
