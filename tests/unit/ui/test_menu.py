"""
Unit tests for ui/menu.py
Tests menu functions including title card, main menu, instructions, and credits.
"""

import pytest
import json
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, mock_open, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Setup headless mode before importing pygame modules
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

from ui import menu


class TestLoadMenuContent:
    """Tests for load_menu_content function"""
    
    def test_load_menu_content_success(self):
        """Test loading menu content from JSON file"""
        mock_content = {
            'title_pygame': 'SHERIFF OF NOTTINGHAM',
            'how_to_play': {'header': 'HOW TO PLAY', 'sections': [], 'footer': ''},
            'credits': {'header': 'CREDITS', 'sections': [], 'footer': ''},
            'exit_message': 'Thanks for playing!'
        }
        
        with patch('builtins.open', mock_open(read_data=json.dumps(mock_content))):
            content = menu.load_menu_content()
            
        assert content['title_pygame'] == 'SHERIFF OF NOTTINGHAM'
        assert 'how_to_play' in content
        assert 'credits' in content
        assert 'exit_message' in content
    
    def test_load_menu_content_file_not_found(self):
        """Test fallback when menu content file is not found"""
        with patch('builtins.open', side_effect=FileNotFoundError):
            content = menu.load_menu_content()
            
        # Should return fallback content
        assert 'title_pygame' in content
        assert content['title_pygame'] == 'SHERIFF OF NOTTINGHAM'
        assert 'how_to_play' in content
        assert 'credits' in content
        assert 'exit_message' in content
    
    def test_load_menu_content_with_full_data(self):
        """Test loading menu content with full data structure"""
        mock_content = {
            'title_pygame': 'SHERIFF OF NOTTINGHAM',
            'how_to_play': {
                'header': 'HOW TO PLAY',
                'sections': [
                    {'title': 'Objective', 'content': 'Catch smugglers'},
                    {'title': 'Gameplay', 'content': 'Inspect bags'}
                ],
                'footer': 'Good luck!'
            },
            'credits': {
                'header': 'CREDITS',
                'title': 'Sheriff of Nottingham',
                'sections': [
                    {'title': 'Developer', 'content': 'Test Dev'}
                ],
                'version': 'v1.0',
                'footer': 'Thanks!'
            },
            'exit_message': 'Goodbye!'
        }
        
        with patch('builtins.open', mock_open(read_data=json.dumps(mock_content))):
            content = menu.load_menu_content()
            
        assert len(content['how_to_play']['sections']) == 2
        assert content['credits']['version'] == 'v1.0'
        assert content['exit_message'] == 'Goodbye!'


class TestShowTitleCard:
    """Tests for show_title_card function"""
    
    @patch('ui.menu.get_ui')
    @patch('ui.menu.load_menu_content')
    def test_show_title_card(self, mock_load_content, mock_get_ui):
        """Test displaying the title card"""
        mock_ui = Mock()
        mock_get_ui.return_value = mock_ui
        mock_load_content.return_value = {
            'title_pygame': 'SHERIFF OF NOTTINGHAM'
        }
        
        menu.show_title_card()
        
        mock_load_content.assert_called_once()
        mock_get_ui.assert_called_once()
        mock_ui.show_title_screen.assert_called_once_with('SHERIFF OF NOTTINGHAM')


class TestShowMainMenu:
    """Tests for show_main_menu function"""
    
    @patch('ui.menu.get_ui')
    def test_show_main_menu(self, mock_get_ui):
        """Test displaying the main menu"""
        mock_ui = Mock()
        mock_ui.show_choices.return_value = 'start'
        mock_get_ui.return_value = mock_ui
        
        result = menu.show_main_menu()
        
        mock_get_ui.assert_called_once()
        mock_ui.show_choices.assert_called_once()
        
        # Check that choices were passed correctly
        call_args = mock_ui.show_choices.call_args
        assert call_args[0][0] == ""  # Empty prompt
        choices = call_args[0][1]
        assert len(choices) == 4
        assert ('start', 'Start Game') in choices
        assert ('help', 'How to Play') in choices
        assert ('credits', 'Credits') in choices
        assert ('exit', 'Exit') in choices
        
        assert result == 'start'


class TestShowHowToPlay:
    """Tests for show_how_to_play function"""
    
    @patch('builtins.input')
    @patch('ui.menu.get_ui')
    @patch('ui.menu.load_menu_content')
    def test_show_how_to_play_basic(self, mock_load_content, mock_get_ui, mock_input):
        """Test displaying how to play instructions"""
        mock_load_content.return_value = {
            'how_to_play': {
                'header': 'HOW TO PLAY',
                'sections': [],
                'footer': 'Good luck!'
            }
        }
        
        mock_ui = Mock()
        mock_get_ui.return_value = mock_ui
        
        menu.show_how_to_play()
        
        mock_load_content.assert_called_once()
        mock_ui.clear_text.assert_called_once()
        mock_input.assert_called_once()
        
        # Check that display_text was called with header and footer
        display_calls = [call[0][0] for call in mock_ui.display_text.call_args_list]
        assert 'HOW TO PLAY' in display_calls
        assert 'Good luck!' in display_calls
    
    @patch('builtins.input')
    @patch('ui.menu.get_ui')
    @patch('ui.menu.load_menu_content')
    def test_show_how_to_play_with_sections(self, mock_load_content, mock_get_ui, mock_input):
        """Test displaying how to play with multiple sections"""
        mock_load_content.return_value = {
            'how_to_play': {
                'header': 'HOW TO PLAY',
                'sections': [
                    {'title': 'Objective', 'content': 'Catch smugglers'},
                    {'title': 'Gameplay', 'content': 'Inspect merchant bags'}
                ],
                'footer': 'Have fun!'
            }
        }
        
        mock_ui = Mock()
        mock_get_ui.return_value = mock_ui
        
        menu.show_how_to_play()
        
        # Check that display_text was called with all expected content
        display_calls = [call[0][0] for call in mock_ui.display_text.call_args_list]
        assert 'HOW TO PLAY' in display_calls
        assert 'Objective' in display_calls
        assert '   Catch smugglers' in display_calls
        assert 'Gameplay' in display_calls
        assert '   Inspect merchant bags' in display_calls
        assert 'Have fun!' in display_calls


class TestShowCredits:
    """Tests for show_credits function"""
    
    @patch('builtins.input')
    @patch('ui.menu.get_ui')
    @patch('ui.menu.load_menu_content')
    def test_show_credits_basic(self, mock_load_content, mock_get_ui, mock_input):
        """Test displaying credits"""
        mock_load_content.return_value = {
            'credits': {
                'header': 'CREDITS',
                'title': 'Game Title',
                'sections': [],
                'version': 'v1.0',
                'footer': 'Thanks!'
            }
        }
        
        mock_ui = Mock()
        mock_get_ui.return_value = mock_ui
        
        menu.show_credits()
        
        mock_load_content.assert_called_once()
        mock_ui.clear_text.assert_called_once()
        mock_input.assert_called_once()
        
        # Check that display_text was called with header and footer
        display_calls = [call[0][0] for call in mock_ui.display_text.call_args_list]
        assert 'CREDITS' in display_calls
        assert 'Thanks!' in display_calls
    
    @patch('builtins.input')
    @patch('ui.menu.get_ui')
    @patch('ui.menu.load_menu_content')
    def test_show_credits_with_sections(self, mock_load_content, mock_get_ui, mock_input):
        """Test displaying credits with multiple sections"""
        mock_load_content.return_value = {
            'credits': {
                'header': 'CREDITS',
                'title': 'Sheriff Game',
                'sections': [
                    {'title': 'Design', 'content': 'John Doe'},
                    {'title': 'Programming', 'content': 'Jane Smith'}
                ],
                'version': 'v2.0',
                'footer': 'Thank you!'
            }
        }
        
        mock_ui = Mock()
        mock_get_ui.return_value = mock_ui
        
        menu.show_credits()
        
        # Check that display_text was called with all expected content
        display_calls = [call[0][0] for call in mock_ui.display_text.call_args_list]
        assert 'CREDITS' in display_calls
        assert '    Sheriff Game' in display_calls
        assert '    Design' in display_calls
        assert '       John Doe' in display_calls
        assert '    Programming' in display_calls
        assert '       Jane Smith' in display_calls
        assert '    v2.0' in display_calls
        assert 'Thank you!' in display_calls


class TestRunMenu:
    """Tests for run_menu function"""
    
    @patch('ui.menu.show_main_menu')
    @patch('ui.menu.show_title_card')
    @patch('ui.menu.get_ui')
    def test_run_menu_start_game(self, mock_get_ui, mock_show_title, mock_show_menu):
        """Test run_menu when user chooses to start game"""
        mock_ui = Mock()
        mock_get_ui.return_value = mock_ui
        mock_show_menu.return_value = 'start'
        
        result = menu.run_menu()
        
        assert result is True
        mock_ui.clear_text.assert_called_once()
        mock_show_title.assert_called_once()
        mock_show_menu.assert_called_once()
    
    @patch('builtins.print')
    @patch('ui.menu.load_menu_content')
    @patch('ui.menu.show_main_menu')
    @patch('ui.menu.show_title_card')
    @patch('ui.menu.get_ui')
    def test_run_menu_exit(self, mock_get_ui, mock_show_title, mock_show_menu, 
                          mock_load_content, mock_print):
        """Test run_menu when user chooses to exit"""
        mock_ui = Mock()
        mock_get_ui.return_value = mock_ui
        mock_show_menu.return_value = 'exit'
        mock_load_content.return_value = {
            'exit_message': 'Thanks for playing!'
        }
        
        result = menu.run_menu()
        
        assert result is False
        mock_print.assert_called_once_with('Thanks for playing!')
    
    @patch('builtins.input')
    @patch('builtins.print')
    @patch('ui.menu.show_how_to_play')
    @patch('ui.menu.show_main_menu')
    @patch('ui.menu.show_title_card')
    @patch('ui.menu.get_ui')
    def test_run_menu_help_then_start(self, mock_get_ui, mock_show_title, 
                                      mock_show_menu, mock_show_help, 
                                      mock_print, mock_input):
        """Test run_menu when user views help then starts game"""
        mock_ui = Mock()
        mock_get_ui.return_value = mock_ui
        mock_show_menu.side_effect = ['help', 'start']
        
        result = menu.run_menu()
        
        assert result is True
        assert mock_show_menu.call_count == 2
        mock_show_help.assert_called_once()
    
    @patch('builtins.input')
    @patch('builtins.print')
    @patch('ui.menu.show_credits')
    @patch('ui.menu.show_main_menu')
    @patch('ui.menu.show_title_card')
    @patch('ui.menu.get_ui')
    def test_run_menu_credits_then_start(self, mock_get_ui, mock_show_title, 
                                         mock_show_menu, mock_show_credits,
                                         mock_print, mock_input):
        """Test run_menu when user views credits then starts game"""
        mock_ui = Mock()
        mock_get_ui.return_value = mock_ui
        mock_show_menu.side_effect = ['credits', 'start']
        
        result = menu.run_menu()
        
        assert result is True
        assert mock_show_menu.call_count == 2
        mock_show_credits.assert_called_once()
    
    @patch('builtins.input')
    @patch('builtins.print')
    @patch('ui.menu.show_credits')
    @patch('ui.menu.show_how_to_play')
    @patch('ui.menu.show_main_menu')
    @patch('ui.menu.show_title_card')
    @patch('ui.menu.get_ui')
    def test_run_menu_multiple_views(self, mock_get_ui, mock_show_title, 
                                     mock_show_menu, mock_show_help,
                                     mock_show_credits, mock_print, mock_input):
        """Test run_menu with multiple menu interactions"""
        mock_ui = Mock()
        mock_get_ui.return_value = mock_ui
        mock_show_menu.side_effect = ['help', 'credits', 'help', 'start']
        
        result = menu.run_menu()
        
        assert result is True
        assert mock_show_menu.call_count == 4
        assert mock_show_help.call_count == 2
        assert mock_show_credits.call_count == 1
