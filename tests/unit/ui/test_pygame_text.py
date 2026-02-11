"""
Unit tests for ui/pygame_text.py
Tests the PygameText class for text display, wrapping, and scrolling.
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Setup headless mode before importing pygame modules
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame
from ui.pygame_text import PygameText

class TestPygameTextInit:
    """Tests for PygameText initialization"""
    
    def test_init(self):
        """Test initialization stores window and sets default state"""
        mock_window = Mock()
        text_display = PygameText(mock_window)
        
        assert text_display.window == mock_window
        assert text_display.text_lines == []
        assert text_display.text_scroll_offset == 0
        assert text_display.text_speed_wpm == 500
        assert text_display.text_display_complete is True

class TestPygameTextWrapText:
    """Tests for PygameText.wrap_text method"""
    
    @pytest.mark.parametrize("text,width,expected_lines", [
        ("Short text", 500, 1),  # Fits on one line
        ("This is a very long text that should wrap to multiple lines when displayed", 200, ">1"),  # Wraps
        ("", 500, 1),  # Empty string
        ("Supercalifragilisticexpialidocious", 100, 1),  # Single long word
    ])
    def test_wrap_text(self, text, width, expected_lines):
        """Test text wrapping with various inputs"""
        pygame.init()
        mock_window = Mock()
        font = pygame.font.Font(None, 24)
        text_display = PygameText(mock_window)
        
        result = text_display.wrap_text(text, width, font)
        
        if expected_lines == ">1":
            assert len(result) > 1
            for line in result:
                assert len(line) < len(text)
        else:
            assert len(result) == expected_lines
        
        pygame.quit()

class TestPygameTextDisplayText:
    """Tests for PygameText.display_text method"""
    
    @pytest.mark.parametrize("clear_previous,initial_lines,expected_old_line_present", [
        (True, ["Old line 1", "Old line 2"], False),  # Clear previous
        (False, ["Old line"], True),  # Append mode
    ])
    def test_display_text_clear_and_append_behavior(self, clear_previous, initial_lines, expected_old_line_present):
        """Test display_text clears or appends based on clear_previous parameter"""
        pygame.init()
        mock_window = Mock()
        mock_window.font_normal = pygame.font.Font(None, 24)
        
        text_display = PygameText(mock_window)
        text_display.render = Mock()
        text_display.text_lines = initial_lines.copy()
        
        text_display.display_text("New text", clear_previous=clear_previous, animate=False)
        
        # Check if old lines are present based on clear_previous
        old_line_present = any(line in text_display.text_lines for line in initial_lines)
        assert old_line_present == expected_old_line_present
        text_display.render.assert_called_once()
        
        pygame.quit()
    
    def test_display_text_handles_newlines_and_scrolling(self):
        """Test displaying text with newlines and auto-scrolling when full"""
        pygame.init()
        mock_window = Mock()
        mock_window.font_normal = pygame.font.Font(None, 24)
        
        text_display = PygameText(mock_window)
        text_display.render = Mock()
        
        # Test newlines
        text_display.display_text("Line 1\nLine 2\nLine 3", clear_previous=True, animate=False)
        assert len(text_display.text_lines) >= 3
        
        # Test auto-scrolling with many lines
        long_text = "\n".join([f"Line {i}" for i in range(100)])
        text_display.display_text(long_text, clear_previous=True, animate=False)
        assert text_display.text_scroll_offset > 0
        
        pygame.quit()

class TestPygameTextDisplayTextAnimated:
    """Tests for PygameText._display_text_animated method"""
    
    @patch('time.time')
    @patch('time.sleep')
    @patch('pygame.event.get')
    def test_display_text_animated_can_be_skipped(self, mock_event_get, mock_sleep, mock_time):
        """Test that animated text can be skipped"""
        pygame.init()
        mock_window = Mock()
        mock_window.clock = pygame.time.Clock()
        mock_window.font_normal = pygame.font.Font(None, 24)
        mock_window.screen = pygame.display.set_mode((1200, 800))
        
        text_display = PygameText(mock_window)
        text_display.render = Mock()
        
        # Mock time to increment on each call to simulate time passing
        time_counter = [0.0]
        def increment_time():
            time_counter[0] += 0.1
            return time_counter[0]
        mock_time.side_effect = increment_time
        
        # Simulate skip event (mouse click)
        skip_event = Mock(type=pygame.MOUSEBUTTONDOWN)
        # Use a generator to provide empty lists until the skip event
        call_count = [0]
        def event_generator():
            call_count[0] += 1
            if call_count[0] <= 8:  # Allow initial pause and first line to start
                return []
            return [skip_event]
        mock_event_get.side_effect = event_generator
        
        text_display._display_text_animated(["Line 1", "Line 2"])
        
        # Should have added all lines (skip completes current line and adds remaining)
        assert len(text_display.text_lines) >= 2
        assert "Line 1" in " ".join(text_display.text_lines)
        assert "Line 2" in " ".join(text_display.text_lines)
        assert text_display.text_display_complete is True
        
        pygame.quit()
    
    @patch('time.time')
    @patch('time.sleep')
    @patch('pygame.event.get')
    def test_display_text_animated_with_zero_wpm(self, mock_event_get, mock_sleep, mock_time):
        """Test animated display with zero WPM (instant)"""
        pygame.init()
        mock_window = Mock()
        mock_window.clock = pygame.time.Clock()
        mock_window.font_normal = pygame.font.Font(None, 24)
        mock_window.screen = pygame.display.set_mode((1200, 800))
        
        text_display = PygameText(mock_window)
        text_display.text_speed_wpm = 0  # Instant display
        text_display.render = Mock()
        
        # Mock time to increment on each call to simulate time passing
        time_counter = [0.0]
        def increment_time():
            time_counter[0] += 0.1
            return time_counter[0]
        mock_time.side_effect = increment_time
        mock_event_get.return_value = []
        
        text_display._display_text_animated(["Line 1"])
        
        # Should complete immediately
        assert text_display.text_display_complete is True
        
        pygame.quit()

class TestPygameTextHandleScroll:
    """Tests for PygameText._handle_scroll method"""
    
    @pytest.mark.parametrize("initial_offset,scroll_amount,expected_comparison", [
        (10, -1, ">"),  # Scroll down increases offset
        (10, 1, "<"),   # Scroll up decreases offset
        (0, 5, "=="),   # Bounded at top
    ])
    def test_handle_scroll(self, initial_offset, scroll_amount, expected_comparison):
        """Test scrolling behavior and bounds"""
        pygame.init()
        mock_window = Mock()
        mock_window.font_normal = pygame.font.Font(None, 24)
        
        text_display = PygameText(mock_window)
        text_display.render = Mock()
        text_display.text_lines = [f"Line {i}" for i in range(100)]
        text_display.text_scroll_offset = initial_offset
        
        text_display._handle_scroll(scroll_amount)
        
        if expected_comparison == ">":
            assert text_display.text_scroll_offset > initial_offset
        elif expected_comparison == "<":
            assert text_display.text_scroll_offset < initial_offset
        elif expected_comparison == "==":
            assert text_display.text_scroll_offset == initial_offset
        
        pygame.quit()

class TestPygameTextRender:
    """Tests for PygameText.render method"""
    
    def test_render_clears_and_draws(self):
        """Test that render clears screen and draws text"""
        pygame.init()
        mock_window = Mock()
        mock_window.screen = pygame.display.set_mode((1200, 800))
        mock_window.font_normal = pygame.font.Font(None, 24)
        mock_window.font_small = pygame.font.Font(None, 18)
        mock_window.clear_screen = Mock()
        mock_window.render_portrait = Mock()
        mock_window.update_display = Mock()
        
        text_display = PygameText(mock_window)
        text_display.text_lines = ["Line 1", "Line 2"]
        
        text_display.render()
        
        mock_window.clear_screen.assert_called_once()
        mock_window.render_portrait.assert_called_once()
        mock_window.update_display.assert_called_once()
        
        pygame.quit()
    
    def test_render_with_scrolling(self):
        """Test rendering with scroll offset"""
        pygame.init()
        mock_window = Mock()
        mock_window.screen = pygame.display.set_mode((1200, 800))
        mock_window.font_normal = pygame.font.Font(None, 24)
        mock_window.font_small = pygame.font.Font(None, 18)
        mock_window.clear_screen = Mock()
        mock_window.render_portrait = Mock()
        mock_window.update_display = Mock()
        
        text_display = PygameText(mock_window)
        text_display.text_lines = [f"Line {i}" for i in range(100)]
        text_display.text_scroll_offset = 10
        
        text_display.render()
        
        # Should render without errors
        mock_window.update_display.assert_called_once()
        
        pygame.quit()
    
    def test_render_shows_scroll_indicator(self):
        """Test that render shows scroll indicator when needed"""
        pygame.init()
        mock_window = Mock()
        mock_window.screen = pygame.display.set_mode((1200, 800))
        mock_window.font_normal = pygame.font.Font(None, 24)
        mock_window.font_small = pygame.font.Font(None, 18)
        mock_window.clear_screen = Mock()
        mock_window.render_portrait = Mock()
        mock_window.update_display = Mock()
        
        text_display = PygameText(mock_window)
        text_display.text_lines = [f"Line {i}" for i in range(100)]
        
        text_display.render()
        
        # Should render without errors (scroll indicator should appear)
        mock_window.update_display.assert_called_once()
        
        pygame.quit()
    
    def test_render_shows_skip_indicator_during_animation(self):
        """Test that render shows skip indicator during animation"""
        pygame.init()
        mock_window = Mock()
        mock_window.screen = pygame.display.set_mode((1200, 800))
        mock_window.font_normal = pygame.font.Font(None, 24)
        mock_window.font_small = pygame.font.Font(None, 18)
        mock_window.clear_screen = Mock()
        mock_window.render_portrait = Mock()
        mock_window.update_display = Mock()
        
        text_display = PygameText(mock_window)
        text_display.text_lines = ["Line 1"]
        text_display.text_display_complete = False  # Animation in progress
        
        text_display.render()
        
        # Should render without errors (skip indicator should appear)
        mock_window.update_display.assert_called_once()
        
        pygame.quit()

class TestPygameTextClearText:
    """Tests for PygameText.clear_text method"""
    
    def test_clear_text_removes_all_lines(self):
        """Test that clear_text removes all text lines"""
        pygame.init()
        mock_window = Mock()
        mock_window.screen = pygame.display.set_mode((1200, 800))
        mock_window.font_normal = pygame.font.Font(None, 24)
        mock_window.font_small = pygame.font.Font(None, 18)
        mock_window.clear_screen = Mock()
        mock_window.render_portrait = Mock()
        mock_window.update_display = Mock()
        
        text_display = PygameText(mock_window)
        text_display.text_lines = ["Line 1", "Line 2", "Line 3"]
        text_display.text_scroll_offset = 5
        
        text_display.clear_text()
        
        assert text_display.text_lines == []
        assert text_display.text_scroll_offset == 0
        
        pygame.quit()
    
    def test_clear_text_calls_render(self):
        """Test that clear_text calls render"""
        pygame.init()
        mock_window = Mock()
        mock_window.screen = pygame.display.set_mode((1200, 800))
        mock_window.font_normal = pygame.font.Font(None, 24)
        mock_window.font_small = pygame.font.Font(None, 18)
        mock_window.clear_screen = Mock()
        mock_window.render_portrait = Mock()
        mock_window.update_display = Mock()
        
        text_display = PygameText(mock_window)
        text_display.text_lines = ["Line 1"]
        
        text_display.clear_text()
        
        mock_window.update_display.assert_called_once()
        
        pygame.quit()

