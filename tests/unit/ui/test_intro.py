"""
Unit tests for ui/intro.py
Tests the game intro display functionality.
"""

import pytest
import json
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, mock_open, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Setup headless mode before importing pygame modules
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

from ui.intro import print_intro

class TestPrintIntro:
    """Tests for print_intro function"""
    
    @patch('builtins.print')
    @patch('builtins.open', new_callable=mock_open)
    def test_print_intro_with_json_file(self, mock_file, mock_print):
        """Test printing intro when JSON file exists"""
        mock_intro_data = {
            "title": "Sheriff of Nottingham",
            "intro": "Welcome to the game! You are the sheriff."
        }
        
        mock_file.return_value.read.return_value = json.dumps(mock_intro_data)
        mock_file.return_value.__enter__ = Mock(return_value=mock_file.return_value)
        mock_file.return_value.__exit__ = Mock(return_value=False)
        
        # Mock json.load to return our data
        with patch('json.load', return_value=mock_intro_data):
            print_intro()
            
            # Verify title was printed
            assert any("Sheriff of Nottingham" in str(call) for call in mock_print.call_args_list)
            
            # Verify intro text was printed
            assert any("Welcome to the game" in str(call) for call in mock_print.call_args_list)
    
    @patch('builtins.print')
    def test_print_intro_file_not_found(self, mock_print):
        """Test printing intro when JSON file is not found"""
        with patch('builtins.open', side_effect=FileNotFoundError):
            print_intro()
            
            # Should print fallback intro
            assert any("Sheriff of Nottingham" in str(call) for call in mock_print.call_args_list)
            assert any("newly appointed inspector" in str(call) for call in mock_print.call_args_list)
    
    @patch('builtins.print')
    def test_print_intro_json_decode_error(self, mock_print):
        """Test printing intro when JSON is malformed"""
        with patch('builtins.open', mock_open(read_data="invalid json")):
            with patch('json.load', side_effect=json.JSONDecodeError("msg", "doc", 0)):
                print_intro()
                
                # Should print fallback intro
                assert any("Sheriff of Nottingham" in str(call) for call in mock_print.call_args_list)
    
    @patch('builtins.print')
    def test_print_intro_without_pygame(self, mock_print):
        """Test printing intro in terminal mode (no pygame)"""
        mock_intro_data = {
            "title": "Test Title",
            "intro": "Test intro text"
        }
        
        with patch('builtins.open', mock_open()):
            with patch('json.load', return_value=mock_intro_data):
                print_intro()
                
                # Should print without error
                assert mock_print.called
    
    @patch('builtins.print')
    def test_print_intro_with_custom_title(self, mock_print):
        """Test printing intro with custom title"""
        mock_intro_data = {
            "title": "Custom Game Title",
            "intro": "Custom intro text"
        }
        
        with patch('builtins.open', mock_open()):
            with patch('json.load', return_value=mock_intro_data):
                print_intro()
                
                # Verify custom title was printed
                assert any("Custom Game Title" in str(call) for call in mock_print.call_args_list)
                assert any("Custom intro text" in str(call) for call in mock_print.call_args_list)
    
    @patch('builtins.print')
    def test_print_intro_empty_intro_text(self, mock_print):
        """Test printing intro with empty intro text"""
        mock_intro_data = {
            "title": "Sheriff of Nottingham",
            "intro": ""
        }
        
        with patch('builtins.open', mock_open()):
            with patch('json.load', return_value=mock_intro_data):
                print_intro()
                
                # Should still print title
                assert any("Sheriff of Nottingham" in str(call) for call in mock_print.call_args_list)
    
    @patch('builtins.print')
    def test_print_intro_missing_fields(self, mock_print):
        """Test printing intro when JSON is missing expected fields"""
        mock_intro_data = {}  # Empty dict
        
        with patch('builtins.open', mock_open()):
            with patch('json.load', return_value=mock_intro_data):
                print_intro()
                
                # Should use default values
                assert any("Sheriff of Nottingham" in str(call) for call in mock_print.call_args_list)
    
    @patch('builtins.print')
    def test_print_intro_with_multiline_text(self, mock_print):
        """Test printing intro with multiline intro text"""
        mock_intro_data = {
            "title": "Sheriff of Nottingham",
            "intro": "Line 1\nLine 2\nLine 3"
        }
        
        with patch('builtins.open', mock_open()):
            with patch('json.load', return_value=mock_intro_data):
                print_intro()
                
                # Verify multiline text was printed
                assert any("Line 1" in str(call) for call in mock_print.call_args_list)

