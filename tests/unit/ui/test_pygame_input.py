"""
Unit tests for ui/pygame_input.py
Tests the PygameInput class for handling user input and choice buttons.
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Setup headless mode before importing pygame modules
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame
from ui.pygame_input import PygameInput

class TestPygameInputInit:
    """Tests for PygameInput initialization"""
    
    def test_init_stores_dependencies(self):
        """Test that initialization stores window and text_display"""
        mock_window = Mock()
        mock_text_display = Mock()
        
        input_handler = PygameInput(mock_window, mock_text_display)
        
        assert input_handler.window == mock_window
        assert input_handler.text_display == mock_text_display
        assert input_handler.price_menu is None
        
    def test_init_with_price_menu(self):
        """Test initialization with price menu"""
        mock_window = Mock()
        mock_text_display = Mock()
        mock_price_menu = Mock()
        
        input_handler = PygameInput(mock_window, mock_text_display, mock_price_menu)
        
        assert input_handler.price_menu == mock_price_menu
    
    def test_init_default_state(self):
        """Test that initialization sets default state"""
        mock_window = Mock()
        mock_text_display = Mock()
        
        input_handler = PygameInput(mock_window, mock_text_display)
        
        assert input_handler.input_prompt is None
        assert input_handler.user_input == ""
        assert input_handler.waiting_for_input is False
        assert input_handler.input_submitted is False
        assert input_handler.choice_buttons == []

class TestPygameInputGetInput:
    """Tests for PygameInput.get_input method"""
    
    @patch('pygame.event.get')
    def test_get_input_with_text_entry(self, mock_event_get):
        """Test getting text input from user"""
        pygame.init()
        mock_window = Mock()
        mock_window.clock = pygame.time.Clock()
        mock_window.font_normal = pygame.font.Font(None, 24)
        mock_window.screen = pygame.display.set_mode((1200, 800))
        
        mock_text_display = Mock()
        mock_text_display.text_lines = []
        mock_text_display.text_scroll_offset = 0
        
        input_handler = PygameInput(mock_window, mock_text_display)
        
        # Simulate typing "test" and pressing enter
        events = [
            Mock(type=pygame.KEYDOWN, key=pygame.K_t, unicode='t'),
            Mock(type=pygame.KEYDOWN, key=pygame.K_e, unicode='e'),
            Mock(type=pygame.KEYDOWN, key=pygame.K_s, unicode='s'),
            Mock(type=pygame.KEYDOWN, key=pygame.K_t, unicode='t'),
            Mock(type=pygame.KEYDOWN, key=pygame.K_RETURN, unicode='\r'),
        ]
        
        mock_event_get.side_effect = [[e] for e in events]
        
        result = input_handler.get_input("Enter text:")
        
        assert result == "test"
        assert input_handler.waiting_for_input is False
        
        pygame.quit()
    
    @patch('pygame.event.get')
    def test_get_input_with_backspace(self, mock_event_get):
        """Test backspace functionality in text input"""
        pygame.init()
        mock_window = Mock()
        mock_window.clock = pygame.time.Clock()
        mock_window.font_normal = pygame.font.Font(None, 24)
        mock_window.screen = pygame.display.set_mode((1200, 800))
        
        mock_text_display = Mock()
        mock_text_display.text_lines = []
        mock_text_display.text_scroll_offset = 0
        
        input_handler = PygameInput(mock_window, mock_text_display)
        
        # Type "test", backspace twice, then enter
        events = [
            Mock(type=pygame.KEYDOWN, key=pygame.K_t, unicode='t'),
            Mock(type=pygame.KEYDOWN, key=pygame.K_e, unicode='e'),
            Mock(type=pygame.KEYDOWN, key=pygame.K_s, unicode='s'),
            Mock(type=pygame.KEYDOWN, key=pygame.K_t, unicode='t'),
            Mock(type=pygame.KEYDOWN, key=pygame.K_BACKSPACE, unicode='\b'),
            Mock(type=pygame.KEYDOWN, key=pygame.K_BACKSPACE, unicode='\b'),
            Mock(type=pygame.KEYDOWN, key=pygame.K_RETURN, unicode='\r'),
        ]
        
        mock_event_get.side_effect = [[e] for e in events]
        
        result = input_handler.get_input("Enter text:")
        
        assert result == "te"
        
        pygame.quit()
    
    @patch('pygame.event.get')
    def test_get_input_strips_whitespace(self, mock_event_get):
        """Test that get_input strips leading/trailing whitespace"""
        pygame.init()
        mock_window = Mock()
        mock_window.clock = pygame.time.Clock()
        mock_window.font_normal = pygame.font.Font(None, 24)
        mock_window.screen = pygame.display.set_mode((1200, 800))
        
        mock_text_display = Mock()
        mock_text_display.text_lines = []
        mock_text_display.text_scroll_offset = 0
        
        input_handler = PygameInput(mock_window, mock_text_display)
        
        # Type spaces, text, spaces, then enter
        events = [
            Mock(type=pygame.KEYDOWN, key=pygame.K_SPACE, unicode=' '),
            Mock(type=pygame.KEYDOWN, key=pygame.K_t, unicode='t'),
            Mock(type=pygame.KEYDOWN, key=pygame.K_e, unicode='e'),
            Mock(type=pygame.KEYDOWN, key=pygame.K_SPACE, unicode=' '),
            Mock(type=pygame.KEYDOWN, key=pygame.K_RETURN, unicode='\r'),
        ]
        
        mock_event_get.side_effect = [[e] for e in events]
        
        result = input_handler.get_input("Enter text:")
        
        assert result == "te"
        
        pygame.quit()

class TestPygameInputShowChoices:
    """Tests for PygameInput.show_choices method"""
    
    @patch('pygame.event.get')
    def test_show_choices_creates_buttons(self, mock_event_get):
        """Test that show_choices creates button rectangles"""
        pygame.init()
        mock_window = Mock()
        mock_window.clock = pygame.time.Clock()
        mock_window.font_normal = pygame.font.Font(None, 24)
        mock_window.screen = pygame.display.set_mode((1200, 800))
        
        mock_text_display = Mock()
        
        input_handler = PygameInput(mock_window, mock_text_display)
        
        choices = [
            ('option1', 'Option 1'),
            ('option2', 'Option 2'),
        ]
        
        # Simulate clicking the first button
        first_button_click = Mock(type=pygame.MOUSEBUTTONDOWN, button=1)
        # Use a generator to provide empty lists until the click event
        call_count = [0]
        def event_generator():
            call_count[0] += 1
            if call_count[0] <= 1:
                return []
            return [first_button_click]
        mock_event_get.side_effect = event_generator
        
        # Mock mouse position to be on first button
        # Button positions: start_x = (1200 - 460) // 2 = 370, start_y = 720
        # First button: x=370, y=720, width=220, height=50
        with patch('pygame.mouse.get_pos', return_value=(480, 745)):
            result = input_handler.show_choices("Choose:", choices)
        
        # After selection, buttons should be cleared
        assert len(input_handler.choice_buttons) == 0
        
        pygame.quit()
    
    @patch('pygame.event.get')
    def test_show_choices_returns_selected_key(self, mock_event_get):
        """Test that show_choices returns the selected choice key"""
        pygame.init()
        mock_window = Mock()
        mock_window.clock = pygame.time.Clock()
        mock_window.font_normal = pygame.font.Font(None, 24)
        mock_window.screen = pygame.display.set_mode((1200, 800))
        
        mock_text_display = Mock()
        
        input_handler = PygameInput(mock_window, mock_text_display)
        
        choices = [
            ('yes', 'Yes'),
            ('no', 'No'),
        ]
        
        # Create button rectangles manually for testing
        button1_rect = pygame.Rect(400, 750, 220, 50)
        button2_rect = pygame.Rect(640, 750, 220, 50)
        
        # Simulate clicking the first button
        click_event = Mock(type=pygame.MOUSEBUTTONDOWN, button=1)
        # Use a generator to provide empty lists until the click event
        call_count = [0]
        def event_generator():
            call_count[0] += 1
            if call_count[0] <= 1:
                return []
            return [click_event]
        mock_event_get.side_effect = event_generator
        
        # Mock mouse position to be on first button
        # Button positions: start_x = (1200 - 460) // 2 = 370, start_y = 720
        # First button: x=370, y=720, width=220, height=50
        with patch('pygame.mouse.get_pos', return_value=(480, 745)):
            result = input_handler.show_choices("", choices)
        
        # Result should be the key of the first clicked choice
        assert result == 'yes'
        
        pygame.quit()
    
    @patch('pygame.event.get')
    def test_show_choices_with_prompt(self, mock_event_get):
        """Test show_choices displays prompt text"""
        pygame.init()
        mock_window = Mock()
        mock_window.clock = pygame.time.Clock()
        mock_window.font_normal = pygame.font.Font(None, 24)
        mock_window.screen = pygame.display.set_mode((1200, 800))
        
        mock_text_display = Mock()
        
        input_handler = PygameInput(mock_window, mock_text_display)
        
        choices = [('option1', 'Option 1')]
        
        click_event = Mock(type=pygame.MOUSEBUTTONDOWN, button=1)
        # Use a generator to provide empty lists until the click event
        call_count = [0]
        def event_generator():
            call_count[0] += 1
            if call_count[0] <= 1:
                return []
            return [click_event]
        mock_event_get.side_effect = event_generator
        
        # Button positions: start_x = (1200 - 220) // 2 = 490, start_y = 720
        # Button: x=490, y=720, width=220, height=50
        with patch('pygame.mouse.get_pos', return_value=(600, 745)):
            input_handler.show_choices("Select an option:", choices)
        
        # Verify prompt was displayed
        mock_text_display.display_text.assert_called()
        
        pygame.quit()

class TestPygameInputWaitForContinue:
    """Tests for PygameInput.wait_for_continue method"""
    
    @patch('pygame.event.get')
    def test_wait_for_continue_with_keypress(self, mock_event_get):
        """Test wait_for_continue exits on key press"""
        pygame.init()
        mock_window = Mock()
        mock_window.clock = pygame.time.Clock()
        
        mock_text_display = Mock()
        
        input_handler = PygameInput(mock_window, mock_text_display)
        
        # Simulate a key press
        key_event = Mock(type=pygame.KEYDOWN, key=pygame.K_SPACE)
        mock_event_get.side_effect = [
            [],  # First iteration
            [key_event],  # Key press
        ]
        
        input_handler.wait_for_continue()
        
        # Should have displayed continue prompt
        assert mock_text_display.display_text.call_count >= 2
        
        pygame.quit()
    
    @patch('pygame.event.get')
    def test_wait_for_continue_with_mouse_click(self, mock_event_get):
        """Test wait_for_continue exits on mouse click"""
        pygame.init()
        mock_window = Mock()
        mock_window.clock = pygame.time.Clock()
        mock_window.update_display = Mock()
        
        mock_text_display = Mock()
        mock_text_display.render = Mock()
        
        input_handler = PygameInput(mock_window, mock_text_display)
        
        # Simulate a mouse click
        click_event = Mock(type=pygame.MOUSEBUTTONDOWN, button=1)
        mock_event_get.side_effect = [
            [],  # First iteration
            [click_event],  # Mouse click
        ]
        
        with patch('pygame.mouse.get_pos', return_value=(100, 100)):
            input_handler.wait_for_continue()
        
        # Should have cleared text after continuing
        mock_text_display.clear_text.assert_called_once()
        
        pygame.quit()
    
    @patch('pygame.event.get')
    def test_wait_for_continue_with_price_menu(self, mock_event_get):
        """Test wait_for_continue handles price menu clicks"""
        pygame.init()
        mock_window = Mock()
        mock_window.clock = pygame.time.Clock()
        mock_window.update_display = Mock()
        
        mock_text_display = Mock()
        mock_text_display.render = Mock()
        
        mock_price_menu = Mock()
        mock_price_menu.handle_click = Mock(side_effect=[True, False])
        mock_price_menu.render = Mock()
        
        input_handler = PygameInput(mock_window, mock_text_display, mock_price_menu)
        
        # Simulate clicking price menu, then clicking elsewhere
        click1 = Mock(type=pygame.MOUSEBUTTONDOWN, button=1)
        click2 = Mock(type=pygame.MOUSEBUTTONDOWN, button=1)
        mock_event_get.side_effect = [
            [],
            [click1],  # Click on price menu
            [click2],  # Click elsewhere to continue
        ]
        
        with patch('pygame.mouse.get_pos', return_value=(100, 100)):
            input_handler.wait_for_continue()
        
        assert mock_price_menu.handle_click.call_count == 2
        
        pygame.quit()

class TestPygameInputRenderMethods:
    """Tests for PygameInput render methods"""
    
    def test_render_with_input(self):
        """Test _render_with_input method"""
        pygame.init()
        mock_window = Mock()
        mock_window.font_normal = pygame.font.Font(None, 24)
        mock_window.screen = pygame.display.set_mode((1200, 800))
        mock_window.update_display = Mock()
        
        mock_text_display = Mock()
        mock_text_display.text_lines = ["Line 1", "Line 2"]
        mock_text_display.text_scroll_offset = 0
        mock_text_display.render = Mock()
        
        input_handler = PygameInput(mock_window, mock_text_display)
        input_handler.waiting_for_input = True
        input_handler.input_prompt = "Enter something:"
        input_handler.user_input = "test"
        
        # Should not raise errors
        input_handler._render_with_input()
        
        mock_text_display.render.assert_called_once()
        mock_window.update_display.assert_called_once()
        
        pygame.quit()
    
    def test_render_with_buttons(self):
        """Test _render_with_buttons method"""
        pygame.init()
        mock_window = Mock()
        mock_window.font_normal = pygame.font.Font(None, 24)
        mock_window.screen = pygame.display.set_mode((1200, 800))
        mock_window.update_display = Mock()
        
        mock_text_display = Mock()
        mock_text_display.text_lines = []
        mock_text_display.render = Mock()
        
        input_handler = PygameInput(mock_window, mock_text_display)
        
        # Create some choice buttons
        button1 = pygame.Rect(100, 100, 200, 50)
        button2 = pygame.Rect(320, 100, 200, 50)
        input_handler.choice_buttons = [
            ("Option 1", button1),
            ("Option 2", button2),
        ]
        
        with patch('pygame.mouse.get_pos', return_value=(150, 125)):
            input_handler._render_with_buttons()
        
        mock_window.update_display.assert_called_once()
        
        pygame.quit()
    
    def test_render_with_buttons_preserves_title_screen(self):
        """Test _render_with_buttons preserves title screen when no text"""
        pygame.init()
        mock_window = Mock()
        mock_window.font_normal = pygame.font.Font(None, 24)
        mock_window.screen = pygame.display.set_mode((1200, 800))
        mock_window.update_display = Mock()
        
        mock_text_display = Mock()
        mock_text_display.text_lines = []  # Empty text lines
        mock_text_display.render = Mock()
        
        input_handler = PygameInput(mock_window, mock_text_display)
        input_handler.choice_buttons = []
        
        with patch('pygame.mouse.get_pos', return_value=(0, 0)):
            input_handler._render_with_buttons()
        
        # Should not call render when text_lines is empty
        mock_text_display.render.assert_not_called()
        
        pygame.quit()

