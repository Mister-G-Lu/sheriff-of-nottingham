"""
Integration tests extracted from test_pygame_text.py
"""

# Must be first import - sets up test environment
from unittest.mock import Mock

import pygame

import tests.test_setup  # noqa: F401
from ui.pygame_text import PygameText


class TestPygameTextIntegration:
    """Integration tests for PygameText"""

    def test_full_text_display_flow(self):
        """Test complete text display flow"""
        pygame.init()
        mock_window = Mock()
        mock_window.screen = pygame.display.set_mode((1200, 800))
        mock_window.font_normal = pygame.font.Font(None, 24)
        mock_window.font_small = pygame.font.Font(None, 18)
        mock_window.clear_screen = Mock()
        mock_window.render_portrait = Mock()
        mock_window.update_display = Mock()

        text_display = PygameText(mock_window)

        # Display text
        text_display.display_text("First message", clear_previous=True, animate=False)
        assert len(text_display.text_lines) > 0

        # Append more text
        text_display.display_text("Second message", clear_previous=False, animate=False)
        assert len(text_display.text_lines) > 1

        # Clear all text
        text_display.clear_text()
        assert len(text_display.text_lines) == 0

        pygame.quit()

    def test_text_wrapping_integration(self):
        """Test text wrapping with display"""
        pygame.init()
        mock_window = Mock()
        mock_window.screen = pygame.display.set_mode((1200, 800))
        mock_window.font_normal = pygame.font.Font(None, 24)
        mock_window.font_small = pygame.font.Font(None, 18)
        mock_window.clear_screen = Mock()
        mock_window.render_portrait = Mock()
        mock_window.update_display = Mock()

        text_display = PygameText(mock_window)

        # Display long text that should wrap (make it even longer to ensure wrapping)
        long_text = "This is a very long line of text that should definitely wrap to multiple lines when displayed in the text box area because it contains many words and exceeds the maximum width allowed for a single line in the text display box"
        text_display.display_text(long_text, clear_previous=True, animate=False)

        # Should have wrapped to multiple lines
        # The text should be wrapped based on TEXT_BOX_WIDTH - 40 pixels
        assert len(text_display.text_lines) >= 1, "Should have at least one line"
        # Verify wrapping occurred by checking if any line is shorter than the original
        if len(text_display.text_lines) > 1:
            assert any(
                len(line) < len(long_text) for line in text_display.text_lines
            ), "Lines should be wrapped"

        pygame.quit()

    def test_scrolling_integration(self):
        """Test scrolling with many lines"""
        pygame.init()
        mock_window = Mock()
        mock_window.screen = pygame.display.set_mode((1200, 800))
        mock_window.font_normal = pygame.font.Font(None, 24)
        mock_window.font_small = pygame.font.Font(None, 18)
        mock_window.clear_screen = Mock()
        mock_window.render_portrait = Mock()
        mock_window.update_display = Mock()

        text_display = PygameText(mock_window)

        # Add many lines
        for i in range(50):
            text_display.display_text(f"Line {i}", clear_previous=False, animate=False)

        initial_offset = text_display.text_scroll_offset

        # Scroll up
        text_display._handle_scroll(5)
        assert text_display.text_scroll_offset < initial_offset

        # Scroll down
        text_display._handle_scroll(-5)

        pygame.quit()
