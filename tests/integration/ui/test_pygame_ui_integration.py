"""
Integration tests extracted from test_pygame_ui.py
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pygame
from ui.pygame_ui import VisualNovelUI, get_ui, close_ui


class TestVisualNovelUIIntegration:
    """Integration tests for VisualNovelUI"""
    
    def test_full_ui_workflow(self):
        """Test complete UI workflow"""
        pygame.init()
        
        ui = get_ui()
        
        # Load portrait
        ui.window.load_portrait = Mock(return_value=True)
        ui.load_portrait("alice")
        
        # Display text
        ui.text.display_text = Mock()
        ui.display_text("Hello", clear_previous=True, animate=False)
        
        # Update stats
        ui.stats_bar.update = Mock()
        ui.update_stats(merchant_count=1, total_merchants=10)
        
        # Render
        ui.stats_bar.render = Mock()
        ui.text.render = Mock()
        ui.price_menu.render = Mock()
        ui.render()
        
        # Verify all calls
        ui.window.load_portrait.assert_called_once()
        ui.text.display_text.assert_called_once()
        ui.stats_bar.update.assert_called_once()
        ui.stats_bar.render.assert_called_once()
        ui.text.render.assert_called_once()
        ui.price_menu.render.assert_called_once()
        
        close_ui()
        pygame.quit()
    
    def test_ui_component_coordination(self):
        """Test that UI components work together"""
        pygame.init()
        
        ui = VisualNovelUI()
        
        # Verify components are connected
        assert ui.text.window == ui.window
        assert ui.input.window == ui.window
        assert ui.input.text_display == ui.text
        assert ui.input.price_menu == ui.price_menu
        
        ui.close()
        pygame.quit()
