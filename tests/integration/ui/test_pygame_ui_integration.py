"""
Integration tests extracted from test_pygame_ui.py
"""

# Must be first import - sets up test environment
from unittest.mock import Mock

import pygame

import tests.test_setup  # noqa: F401
from ui.pygame_ui import VisualNovelUI, close_ui, get_ui


class TestVisualNovelUIIntegration:
    """Integration tests for VisualNovelUI"""

    def test_full_ui_workflow(self):
        """Test complete UI workflow"""
        pygame.init()

        ui = get_ui()

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
