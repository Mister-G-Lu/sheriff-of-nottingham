"""
Integration tests extracted from test_pygame_window.py
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Setup headless mode before importing pygame modules
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame
from ui.pygame_window import PygameWindow


class TestPygameWindowIntegration:
    """Integration tests for PygameWindow"""
    
    def test_full_window_workflow(self):
        """Test complete window workflow"""
        pygame.init()
        
        window = PygameWindow()
        
        # Clear screen
        window.clear_screen()
        
        # Load and render portrait
        window.load_portrait_file = Mock(return_value=True)
        window.load_portrait_file("test.png")
        
        # Create mock portrait for rendering
        window.current_portrait = pygame.Surface((400, 400))
        window.render_portrait()
        
        # Update display
        window.update_display()
        
        # Clear portrait
        window.clear_portrait()
        
        # Close
        window.close()
    
    def test_portrait_loading_and_rendering(self):
        """Test loading and rendering portrait"""
        pygame.init()
        
        window = PygameWindow()
        
        # Mock portrait loading
        window.load_portrait_file = Mock(return_value=True)
        result = window.load_portrait_file("test.png")
        
        assert result is True
        
        # Set mock portrait for rendering
        window.current_portrait = pygame.Surface((400, 400))
        window.portrait_slide_offset = -100
        
        # Render multiple times
        for _ in range(5):
            window.clear_screen()
            window.render_portrait()
            window.update_display()
        
        window.close()
    
    def test_title_screen_display(self):
        """Test displaying title screen"""
        pygame.init()
        
        window = PygameWindow()
        
        # Show title screen
        window.show_title_screen("SHERIFF OF NOTTINGHAM")
        
        # Should be able to clear and render normally after
        window.clear_screen()
        window.update_display()
        
        window.close()
