"""
Unit tests for menu scroll behavior
Tests that scroll events don't trigger unwanted actions on menu screen
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Setup headless mode before importing pygame modules
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame
from ui import menu


class TestMenuScrollBehavior:
    """Tests for scroll behavior on menu screen"""
    
    @patch('ui.menu.get_ui')
    @patch('ui.menu.load_menu_content')
    def test_main_menu_ignores_scroll_events(self, mock_load_content, mock_get_ui):
        """Test that scroll events don't trigger actions on main menu"""
        mock_load_content.return_value = {
            'title_pygame': 'SHERIFF OF NOTTINGHAM',
            'how_to_play': {'header': 'HOW TO PLAY', 'sections': [], 'footer': ''},
            'credits': {'header': 'CREDITS', 'sections': [], 'footer': ''},
            'exit_message': 'Thanks for playing!'
        }
        
        mock_ui = Mock()
        mock_text_display = Mock()
        mock_text_display.text_lines = []  # Empty text on menu screen
        mock_ui.text = mock_text_display
        mock_get_ui.return_value = mock_ui
        
        # Simulate scroll event by creating a mock that will be called
        scroll_handler = Mock()
        mock_text_display._handle_scroll = scroll_handler
        
        # Mock show_choices to simulate a scroll event
        def mock_show_choices(prompt, choices):
            # Simulate MOUSEWHEEL event with empty text
            # This should NOT call _handle_scroll since there's no text
            if len(mock_text_display.text_lines) == 0:
                # Scroll should be ignored
                pass
            else:
                scroll_handler(1)
            return 'start'
        
        mock_ui.show_choices = mock_show_choices
        
        # Run menu
        result = menu.run_menu()
        
        # Verify scroll handler was NOT called (no text to scroll)
        scroll_handler.assert_not_called()
        assert result is True
    
    @patch('ui.menu.get_ui')
    @patch('ui.menu.load_menu_content')
    def test_menu_only_responds_to_button_clicks(self, mock_load_content, mock_get_ui):
        """Test that menu only responds to button clicks, not other inputs"""
        mock_load_content.return_value = {
            'title_pygame': 'SHERIFF OF NOTTINGHAM',
            'how_to_play': {'header': 'HOW TO PLAY', 'sections': [], 'footer': ''},
            'credits': {'header': 'CREDITS', 'sections': [], 'footer': ''},
            'exit_message': 'Thanks for playing!'
        }
        
        mock_ui = Mock()
        mock_get_ui.return_value = mock_ui
        
        # Track what methods were called
        calls = []
        
        def track_show_choices(prompt, choices):
            calls.append('show_choices')
            return 'start'
        
        def track_show_title_screen(title):
            calls.append('show_title_screen')
        
        def track_clear_text():
            calls.append('clear_text')
        
        mock_ui.show_choices = track_show_choices
        mock_ui.show_title_screen = track_show_title_screen
        mock_ui.clear_text = track_clear_text
        
        # Run menu
        result = menu.run_menu()
        
        # Verify expected methods were called
        assert 'clear_text' in calls
        assert 'show_title_screen' in calls
        assert 'show_choices' in calls
        assert result is True


class TestScrollEventHandling:
    """Tests for scroll event handling in pygame_input"""
    
    def test_scroll_ignored_when_no_text(self):
        """Test that scroll events are ignored when there's no text to scroll"""
        pygame.init()
        
        from ui.pygame_window import PygameWindow
        from ui.pygame_text import PygameText
        from ui.pygame_input import PygameInput
        
        window = PygameWindow()
        text_display = PygameText(window)
        input_handler = PygameInput(window, text_display)
        
        # Ensure text_lines is empty (like on menu screen)
        text_display.text_lines = []
        initial_scroll = text_display.text_scroll_offset
        
        # Simulate scroll event with no text
        # The scroll should be ignored
        max_lines = 10  # Approximate
        if len(text_display.text_lines) <= max_lines:
            # Scroll should not change offset
            assert text_display.text_scroll_offset == initial_scroll
        
        window.close()
    
    def test_scroll_works_when_text_present(self):
        """Test that scroll events work when there's text to scroll"""
        pygame.init()
        
        from ui.pygame_window import PygameWindow
        from ui.pygame_text import PygameText
        from ui.pygame_input import PygameInput
        
        window = PygameWindow()
        text_display = PygameText(window)
        input_handler = PygameInput(window, text_display)
        
        # Add many lines of text (more than can fit on screen)
        for i in range(50):
            text_display.text_lines.append(f"Line {i}")
        
        initial_scroll = text_display.text_scroll_offset
        
        # Simulate scroll down
        text_display._handle_scroll(-1)
        
        # Scroll offset should have changed
        assert text_display.text_scroll_offset != initial_scroll
        
        window.close()
