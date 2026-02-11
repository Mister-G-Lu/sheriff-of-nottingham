"""
Unit tests for ui/pygame_ui.py
Tests the VisualNovelUI class that coordinates all UI components.
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Setup headless mode before importing pygame modules
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame
from ui.pygame_ui import VisualNovelUI, get_ui, close_ui

class TestVisualNovelUIInit:
    """Tests for VisualNovelUI initialization"""
    
    def test_init_creates_all_components(self):
        """Test that initialization creates all UI components"""
        pygame.init()
        
        ui = VisualNovelUI()
        
        assert ui.window is not None
        assert ui.text is not None
        assert ui.price_menu is not None
        assert ui.input is not None
        assert ui.stats_bar is not None
        
        ui.close()
        pygame.quit()
    
    def test_init_exposes_window_attributes(self):
        """Test that initialization exposes window attributes for backward compatibility"""
        pygame.init()
        
        ui = VisualNovelUI()
        
        assert ui.screen is not None
        assert ui.clock is not None
        assert ui.font_normal is not None
        assert ui.font_large is not None
        assert ui.font_small is not None
        
        ui.close()
        pygame.quit()

class TestVisualNovelUIWindowMethods:
    """Tests for window-related methods"""
    
    def test_load_portrait_file(self):
        """Test loading portrait by filename"""
        pygame.init()
        ui = VisualNovelUI()
        
        # Mock the window's load_portrait_file method
        ui.window.load_portrait_file = Mock(return_value=True)
        
        result = ui.load_portrait_file("test.png")
        
        assert result is True
        ui.window.load_portrait_file.assert_called_once_with("test.png")
        
        ui.close()
        pygame.quit()
    
    def test_load_portrait(self):
        """Test loading portrait by character name"""
        pygame.init()
        ui = VisualNovelUI()
        
        ui.window.load_portrait = Mock(return_value=True)
        
        result = ui.load_portrait("alice")
        
        assert result is True
        ui.window.load_portrait.assert_called_once_with("alice")
        
        ui.close()
        pygame.quit()
    
    def test_clear_portrait(self):
        """Test clearing portrait"""
        pygame.init()
        ui = VisualNovelUI()
        
        ui.window.clear_portrait = Mock()
        
        ui.clear_portrait()
        
        ui.window.clear_portrait.assert_called_once()
        
        ui.close()
        pygame.quit()
    
    def test_show_title_screen(self):
        """Test showing title screen"""
        pygame.init()
        ui = VisualNovelUI()
        
        ui.window.show_title_screen = Mock()
        
        ui.show_title_screen("Test Title")
        
        ui.window.show_title_screen.assert_called_once_with("Test Title")
        
        ui.close()
        pygame.quit()

class TestVisualNovelUITextMethods:
    """Tests for text-related methods"""
    
    def test_display_text(self):
        """Test displaying text"""
        pygame.init()
        ui = VisualNovelUI()
        
        ui.text.display_text = Mock()
        
        ui.display_text("Hello World", clear_previous=True, animate=False)
        
        ui.text.display_text.assert_called_once_with("Hello World", True, False)
        
        ui.close()
        pygame.quit()
    
    def test_clear_text(self):
        """Test clearing text"""
        pygame.init()
        ui = VisualNovelUI()
        
        ui.text.clear_text = Mock()
        
        ui.clear_text()
        
        ui.text.clear_text.assert_called_once()
        
        ui.close()
        pygame.quit()

class TestVisualNovelUIStatsBar:
    """Tests for stats bar methods"""
    
    def test_update_stats(self):
        """Test updating stats bar"""
        pygame.init()
        ui = VisualNovelUI()
        
        ui.stats_bar.update = Mock()
        
        mock_sheriff = Mock()
        mock_stats = Mock()
        
        ui.update_stats(sheriff=mock_sheriff, stats=mock_stats, merchant_count=5, total_merchants=10)
        
        ui.stats_bar.update.assert_called_once_with(mock_sheriff, mock_stats, 5, 10)
        
        ui.close()
        pygame.quit()

class TestVisualNovelUIRender:
    """Tests for render method"""
    
    def test_render_calls_all_components(self):
        """Test that render calls all component render methods"""
        pygame.init()
        ui = VisualNovelUI()
        
        ui.stats_bar.render = Mock()
        ui.text.render = Mock()
        ui.price_menu.render = Mock()
        
        ui.render()
        
        ui.stats_bar.render.assert_called_once()
        ui.text.render.assert_called_once()
        ui.price_menu.render.assert_called_once()
        
        ui.close()
        pygame.quit()

class TestVisualNovelUIInputMethods:
    """Tests for input-related methods"""
    
    def test_get_input(self):
        """Test getting text input"""
        pygame.init()
        ui = VisualNovelUI()
        
        ui.input.get_input = Mock(return_value="test input")
        
        result = ui.get_input("Enter something:")
        
        assert result == "test input"
        ui.input.get_input.assert_called_once_with("Enter something:")
        
        ui.close()
        pygame.quit()
    
    def test_show_choices(self):
        """Test showing choices"""
        pygame.init()
        ui = VisualNovelUI()
        
        ui.input.show_choices = Mock(return_value="option1")
        
        choices = [("option1", "Option 1"), ("option2", "Option 2")]
        result = ui.show_choices("Choose:", choices)
        
        assert result == "option1"
        ui.input.show_choices.assert_called_once_with("Choose:", choices)
        
        ui.close()
        pygame.quit()
    
    def test_wait_for_continue(self):
        """Test waiting for continue"""
        pygame.init()
        ui = VisualNovelUI()
        
        ui.input.wait_for_continue = Mock()
        
        ui.wait_for_continue()
        
        ui.input.wait_for_continue.assert_called_once()
        
        ui.close()
        pygame.quit()

class TestVisualNovelUIEventHandling:
    """Tests for event handling methods"""
    
    def test_handle_events(self):
        """Test handling pygame events"""
        pygame.init()
        ui = VisualNovelUI()
        
        ui.window.handle_events = Mock()
        
        ui.handle_events()
        
        ui.window.handle_events.assert_called_once()
        
        ui.close()
        pygame.quit()
    
    def test_handle_click(self):
        """Test handling mouse clicks"""
        pygame.init()
        ui = VisualNovelUI()
        
        ui.price_menu.handle_click = Mock(return_value=True)
        
        result = ui.handle_click((100, 100))
        
        assert result is True
        ui.price_menu.handle_click.assert_called_once_with((100, 100))
        
        ui.close()
        pygame.quit()

class TestVisualNovelUIClose:
    """Tests for close method"""
    
    def test_close(self):
        """Test closing UI"""
        pygame.init()
        ui = VisualNovelUI()
        
        ui.window.close = Mock()
        
        ui.close()
        
        ui.window.close.assert_called_once()
        
        pygame.quit()

class TestGetUI:
    """Tests for get_ui global function"""
    
    def test_get_ui_creates_instance(self):
        """Test that get_ui creates a UI instance"""
        pygame.init()
        
        # Clear any existing instance
        close_ui()
        
        ui = get_ui()
        
        assert ui is not None
        assert isinstance(ui, VisualNovelUI)
        
        close_ui()
        pygame.quit()
    
    def test_get_ui_returns_same_instance(self):
        """Test that get_ui returns the same instance"""
        pygame.init()
        
        close_ui()
        
        ui1 = get_ui()
        ui2 = get_ui()
        
        assert ui1 is ui2
        
        close_ui()
        pygame.quit()
    
    def test_get_ui_after_close(self):
        """Test that get_ui creates new instance after close"""
        pygame.init()
        
        close_ui()
        
        ui1 = get_ui()
        close_ui()
        ui2 = get_ui()
        
        assert ui1 is not ui2
        
        close_ui()
        pygame.quit()

class TestCloseUI:
    """Tests for close_ui global function"""
    
    def test_close_ui_closes_instance(self):
        """Test that close_ui closes the UI instance"""
        pygame.init()
        
        ui = get_ui()
        ui.close = Mock()
        
        close_ui()
        
        ui.close.assert_called_once()
        
        pygame.quit()
    
    def test_close_ui_clears_instance(self):
        """Test that close_ui clears the global instance"""
        pygame.init()
        
        get_ui()
        close_ui()
        
        # Getting UI again should create new instance
        ui = get_ui()
        assert ui is not None
        
        close_ui()
        pygame.quit()
    
    def test_close_ui_when_no_instance(self):
        """Test that close_ui handles no instance gracefully"""
        pygame.init()
        
        close_ui()
        close_ui()  # Should not raise error
        
        pygame.quit()

