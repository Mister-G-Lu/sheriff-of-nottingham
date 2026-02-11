"""
Unit tests for ui/pygame_window.py
Tests the PygameWindow class for window management and rendering.
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
from ui.pygame_window import PygameWindow

class TestPygameWindowInit:
    """Tests for PygameWindow initialization"""
    
    def test_init(self):
        """Test initialization creates window and sets all properties"""
        pygame.init()
        window = PygameWindow()
        
        # Window components
        assert window.screen is not None
        assert window.clock is not None
        assert window.font_normal is not None
        assert window.font_large is not None
        assert window.font_small is not None
        
        # Caption
        caption = pygame.display.get_caption()[0]
        assert caption == "Sheriff of Nottingham"
        
        # Portrait state
        assert window.current_portrait is None
        assert window.portrait_slide_offset == -400
        assert window.portrait_slide_speed == 30
        
        # Project root
        assert window.project_root is not None
        assert isinstance(window.project_root, Path)
        
        window.close()
        pygame.quit()

class TestPygameWindowLoadPortraitFile:
    """Tests for load_portrait_file method"""
    
    @patch('pygame.image.load')
    @patch('pygame.transform.scale')
    def test_load_portrait_file_success(self, mock_scale, mock_load):
        """Test loading portrait file successfully"""
        pygame.init()
        window = PygameWindow()
        
        mock_surface = Mock()
        mock_surface.convert_alpha = Mock(return_value=mock_surface)
        mock_load.return_value = mock_surface
        mock_scale.return_value = mock_surface
        
        result = window.load_portrait_file("test.png")
        
        assert result is True
        assert window.current_portrait == mock_surface
        assert window.portrait_slide_offset == -400
        
        window.close()
        pygame.quit()
    
    def test_load_portrait_file_not_found(self):
        """Test loading portrait file that doesn't exist"""
        pygame.init()
        window = PygameWindow()
        
        result = window.load_portrait_file("nonexistent.png")
        
        assert result is False
        assert window.current_portrait is None
        
        window.close()
        pygame.quit()
    
    @patch('pygame.image.load', side_effect=pygame.error("Test error"))
    def test_load_portrait_file_pygame_error(self, mock_load):
        """Test handling pygame error when loading portrait"""
        pygame.init()
        window = PygameWindow()
        
        result = window.load_portrait_file("error.png")
        
        assert result is False
        assert window.current_portrait is None
        
        window.close()
        pygame.quit()

class TestPygameWindowLoadPortrait:
    """Tests for load_portrait method (legacy)"""
    
    @pytest.mark.parametrize("character,expected_file", [
        ("alice", "baker.png"),
        ("baker", "baker.png"),
        ("benedict", "trader.png"),
        ("cedric", "blacksmith.png"),
        ("silas", "broker.png"),
        ("sheriff", "sheriff.png"),
        ("ALICE", "baker.png"),  # Case insensitive
    ])
    def test_load_portrait_character_mapping(self, character, expected_file):
        """Test loading portraits for various characters"""
        pygame.init()
        window = PygameWindow()
        window.load_portrait_file = Mock(return_value=True)
        
        result = window.load_portrait(character)
        
        assert result is True
        window.load_portrait_file.assert_called_once_with(expected_file)
        
        window.close()
        pygame.quit()
    
    def test_load_portrait_unknown_character(self):
        """Test loading portrait for unknown character"""
        pygame.init()
        window = PygameWindow()
        
        result = window.load_portrait("unknown_character")
        
        assert result is False
        assert window.current_portrait is None
        
        window.close()
        pygame.quit()

class TestPygameWindowClearPortrait:
    """Tests for clear_portrait method"""
    
    @pytest.mark.parametrize("has_portrait", [True, False])
    def test_clear_portrait(self, has_portrait):
        """Test clearing portrait with and without existing portrait"""
        pygame.init()
        window = PygameWindow()
        
        if has_portrait:
            window.current_portrait = Mock()
            window.portrait_slide_offset = 0
        
        window.clear_portrait()
        
        assert window.current_portrait is None
        assert window.portrait_slide_offset == -400
        
        window.close()
        pygame.quit()

class TestPygameWindowShowTitleScreen:
    """Tests for show_title_screen method"""
    
    @patch('pygame.image.load')
    def test_show_title_screen_with_portrait(self, mock_load):
        """Test showing title screen with sheriff portrait"""
        pygame.init()
        
        # Create a proper pygame Surface for the mock to return
        mock_surface = pygame.Surface((100, 100))
        mock_load.return_value = mock_surface
        
        window = PygameWindow()
        
        # Should not raise errors
        window.show_title_screen("SHERIFF OF NOTTINGHAM")
        
        window.close()
        pygame.quit()
    
    def test_show_title_screen_without_portrait(self):
        """Test showing title screen when portrait file is missing"""
        pygame.init()
        window = PygameWindow()
        
        # Should not raise errors even if portrait is missing
        window.show_title_screen("SHERIFF OF NOTTINGHAM")
        
        window.close()
        pygame.quit()
    
    def test_show_title_screen_multiline(self):
        """Test showing title screen with multiline text"""
        pygame.init()
        window = PygameWindow()
        
        # Should not raise errors
        window.show_title_screen("SHERIFF OF\nNOTTINGHAM")
        
        window.close()
        pygame.quit()
    
    def test_show_title_screen_empty_lines(self):
        """Test showing title screen with empty lines"""
        pygame.init()
        window = PygameWindow()
        
        # Should not raise errors
        window.show_title_screen("SHERIFF OF\n\nNOTTINGHAM")
        
        window.close()
        pygame.quit()

class TestPygameWindowRenderPortrait:
    """Tests for render_portrait method"""
    
    def test_render_portrait_with_portrait(self):
        """Test rendering portrait when one is loaded"""
        pygame.init()
        window = PygameWindow()
        
        # Create a mock portrait
        mock_portrait = pygame.Surface((400, 400))
        window.current_portrait = mock_portrait
        window.portrait_slide_offset = 0
        
        # Should not raise errors
        window.render_portrait()
        
        window.close()
        pygame.quit()
    
    def test_render_portrait_without_portrait(self):
        """Test rendering portrait when none is loaded"""
        pygame.init()
        window = PygameWindow()
        
        window.current_portrait = None
        
        # Should not raise errors
        window.render_portrait()
        
        window.close()
        pygame.quit()
    
    def test_render_portrait_slide_in_effect(self):
        """Test portrait slide-in animation"""
        pygame.init()
        window = PygameWindow()
        
        mock_portrait = pygame.Surface((400, 400))
        window.current_portrait = mock_portrait
        window.portrait_slide_offset = -100
        
        initial_offset = window.portrait_slide_offset
        
        # Render multiple times to simulate animation
        for _ in range(5):
            window.render_portrait()
        
        # Offset should have moved toward 0
        assert window.portrait_slide_offset > initial_offset
        
        window.close()
        pygame.quit()
    
    def test_render_portrait_slide_complete(self):
        """Test portrait slide-in completes at 0"""
        pygame.init()
        window = PygameWindow()
        
        mock_portrait = pygame.Surface((400, 400))
        window.current_portrait = mock_portrait
        window.portrait_slide_offset = -10
        
        # Render enough times to complete slide
        for _ in range(10):
            window.render_portrait()
        
        # Should stop at 0
        assert window.portrait_slide_offset == 0
        
        window.close()
        pygame.quit()

class TestPygameWindowClearScreen:
    """Tests for clear_screen method"""
    
    def test_clear_screen(self):
        """Test clearing screen"""
        pygame.init()
        window = PygameWindow()
        
        # Should not raise errors
        window.clear_screen()
        
        window.close()
        pygame.quit()
    
    def test_clear_screen_with_background(self):
        """Test clearing screen with background"""
        pygame.init()
        window = PygameWindow()
        
        # Set a background
        window.marketplace_background = pygame.Surface((1200, 800))
        
        # Should not raise errors
        window.clear_screen()
        
        window.close()
        pygame.quit()

class TestPygameWindowUpdateDisplay:
    """Tests for update_display method"""
    
    def test_update_display(self):
        """Test updating display"""
        pygame.init()
        window = PygameWindow()
        
        # Should not raise errors
        window.update_display()
        
        window.close()
        pygame.quit()

class TestPygameWindowHandleEvents:
    """Tests for handle_events method"""
    
    @patch('pygame.event.get')
    def test_handle_events_no_events(self, mock_get):
        """Test handling events when there are none"""
        pygame.init()
        window = PygameWindow()
        
        mock_get.return_value = []
        
        # Should not raise errors
        window.handle_events()
        
        window.close()
        pygame.quit()
    
    @patch('pygame.event.get')
    @patch('sys.exit')
    def test_handle_events_quit(self, mock_exit, mock_get):
        """Test handling quit event"""
        pygame.init()
        window = PygameWindow()
        
        quit_event = Mock()
        quit_event.type = pygame.QUIT
        mock_get.return_value = [quit_event]
        
        # Should call sys.exit
        window.handle_events()
        
        mock_exit.assert_called_once()
        
        window.close()

class TestPygameWindowClose:
    """Tests for close method"""
    
    def test_close(self):
        """Test closing window"""
        pygame.init()
        window = PygameWindow()
        
        # Should not raise errors
        window.close()
        
        # pygame.quit() is called in close, so we don't call it again

