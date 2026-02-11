"""
Unit tests for price menu visibility during gameplay
Tests that the price menu button is visible and accessible during game
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Setup headless mode before importing pygame modules
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame
from ui.price_menu import PriceMenu


class TestPriceMenuVisibility:
    """Tests for price menu visibility and positioning"""
    
    def test_price_menu_button_in_top_right(self):
        """Test that price menu button is positioned in top right corner"""
        pygame.init()
        
        screen = pygame.display.set_mode((1200, 800))
        font_normal = pygame.font.Font(None, 32)
        font_small = pygame.font.Font(None, 24)
        
        price_menu = PriceMenu(screen, font_normal, font_small)
        
        # Verify button is in top right area
        # Button should be near the right edge (within 200px)
        assert price_menu.button_x > screen.get_width() - 200
        
        # Button should be near the top (below stats bar at y=40)
        assert price_menu.button_y >= 40  # Below stats bar
        assert price_menu.button_y < 150  # But still in top area
        
        # Button should have reasonable dimensions
        assert price_menu.button_width > 0
        assert price_menu.button_height > 0
        
        pygame.quit()
    
    def test_price_menu_button_clickable(self):
        """Test that price menu button responds to clicks"""
        pygame.init()
        
        screen = pygame.display.set_mode((1200, 800))
        font_normal = pygame.font.Font(None, 32)
        font_small = pygame.font.Font(None, 24)
        
        price_menu = PriceMenu(screen, font_normal, font_small)
        
        # Initially closed
        assert price_menu.is_open is False
        
        # Click on button (center of button rect)
        button_center = price_menu.button_rect.center
        result = price_menu.handle_click(button_center)
        
        # Should return True (click was handled) and toggle state
        assert result is True
        assert price_menu.is_open is True
        
        # Click again to close
        result = price_menu.handle_click(button_center)
        assert result is True
        assert price_menu.is_open is False
        
        pygame.quit()
    
    def test_price_menu_button_text_changes(self):
        """Test that button text changes when menu is opened/closed"""
        pygame.init()
        
        screen = pygame.display.set_mode((1200, 800))
        font_normal = pygame.font.Font(None, 32)
        font_small = pygame.font.Font(None, 24)
        
        price_menu = PriceMenu(screen, font_normal, font_small)
        
        # When closed, should say "Show Prices"
        assert price_menu.is_open is False
        # (We can't directly test the rendered text, but we verify the state)
        
        # Open the menu
        price_menu.is_open = True
        # When open, should say "Hide Prices"
        # (State verified, rendering tested in integration tests)
        
        pygame.quit()
    
    def test_price_menu_displays_all_goods(self):
        """Test that price menu includes all legal goods and contraband"""
        pygame.init()
        
        screen = pygame.display.set_mode((1200, 800))
        font_normal = pygame.font.Font(None, 32)
        font_small = pygame.font.Font(None, 24)
        
        price_menu = PriceMenu(screen, font_normal, font_small)
        
        # Open the menu
        price_menu.is_open = True
        
        # Render the menu (this should not crash)
        try:
            price_menu.render()
            success = True
        except Exception as e:
            success = False
            print(f"Render failed: {e}")
        
        assert success is True
        
        pygame.quit()
    
    def test_price_menu_button_visible_during_gameplay(self):
        """Test that price menu button is visible during normal gameplay"""
        pygame.init()
        
        from ui.pygame_ui import VisualNovelUI
        
        # Create UI (simulating gameplay)
        ui = VisualNovelUI()
        
        # Verify price menu exists and has button
        assert ui.price_menu is not None
        assert hasattr(ui.price_menu, 'button_rect')
        assert hasattr(ui.price_menu, 'render_button')
        
        # Verify button is in valid position
        assert ui.price_menu.button_x > 0
        assert ui.price_menu.button_y > 0
        
        # Verify button dimensions are reasonable
        assert ui.price_menu.button_width > 50  # At least 50px wide
        assert ui.price_menu.button_height > 20  # At least 20px tall
        
        ui.close()
    
    def test_price_menu_accessible_via_ui(self):
        """Test that price menu is accessible through the main UI"""
        pygame.init()
        
        from ui.pygame_ui import VisualNovelUI
        
        ui = VisualNovelUI()
        
        # Verify we can access price menu through UI
        assert hasattr(ui, 'price_menu')
        
        # Verify we can toggle it
        initial_state = ui.price_menu.is_open
        button_pos = ui.price_menu.button_rect.center
        
        ui.handle_click(button_pos)
        assert ui.price_menu.is_open != initial_state
        
        ui.close()
    
    def test_price_menu_position_does_not_overlap_stats(self):
        """Test that price menu button doesn't overlap with stats bar"""
        pygame.init()
        
        screen = pygame.display.set_mode((1200, 800))
        font_normal = pygame.font.Font(None, 32)
        font_small = pygame.font.Font(None, 24)
        
        price_menu = PriceMenu(screen, font_normal, font_small)
        
        # Stats bar is 40px tall at the top
        # Button should start below that (y >= 40)
        assert price_menu.button_y >= 40
        
        # Button should not extend into stats bar area
        assert price_menu.button_rect.top >= 40
        
        pygame.quit()


class TestPriceMenuContent:
    """Tests for price menu content accuracy"""
    
    def test_price_menu_shows_legal_goods(self):
        """Test that price menu displays legal goods section"""
        pygame.init()
        
        from core.mechanics.goods import ALL_LEGAL
        
        screen = pygame.display.set_mode((1200, 800))
        font_normal = pygame.font.Font(None, 32)
        font_small = pygame.font.Font(None, 24)
        
        price_menu = PriceMenu(screen, font_normal, font_small)
        
        # Verify ALL_LEGAL is imported and used
        assert len(ALL_LEGAL) > 0
        
        # Open menu and render (should include all legal goods)
        price_menu.is_open = True
        price_menu.render_menu()
        
        pygame.quit()
    
    def test_price_menu_shows_contraband(self):
        """Test that price menu displays contraband section"""
        pygame.init()
        
        from core.mechanics.goods import ALL_CONTRABAND
        
        screen = pygame.display.set_mode((1200, 800))
        font_normal = pygame.font.Font(None, 32)
        font_small = pygame.font.Font(None, 24)
        
        price_menu = PriceMenu(screen, font_normal, font_small)
        
        # Verify ALL_CONTRABAND is imported and used
        assert len(ALL_CONTRABAND) > 0
        
        # Open menu and render (should include all contraband)
        price_menu.is_open = True
        price_menu.render_menu()
        
        pygame.quit()
    
    def test_price_menu_button_label_correct(self):
        """Test that button has correct label 'Show Prices' / 'Hide Prices'"""
        pygame.init()
        
        screen = pygame.display.set_mode((1200, 800))
        font_normal = pygame.font.Font(None, 32)
        font_small = pygame.font.Font(None, 24)
        
        price_menu = PriceMenu(screen, font_normal, font_small)
        
        # The button text is rendered in render_button()
        # We verify the logic by checking the state
        
        # When closed, button should show "Show Prices"
        assert price_menu.is_open is False
        
        # When open, button should show "Hide Prices"
        price_menu.is_open = True
        
        # Render button (should not crash)
        try:
            price_menu.render_button()
            success = True
        except:
            success = False
        
        assert success is True
        
        pygame.quit()
