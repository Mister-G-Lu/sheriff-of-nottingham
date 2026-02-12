"""
Integration tests extracted from test_pygame_input.py
"""

# Must be first import - sets up test environment
from unittest.mock import Mock, patch

import pygame

import tests.test_setup  # noqa: F401
from ui.pygame_input import PygameInput


class TestPygameInputIntegration:
    """Integration tests for PygameInput"""

    @patch("pygame.event.get")
    def test_full_input_flow(self, mock_event_get):
        """Test complete input flow from prompt to submission"""
        pygame.init()
        mock_window = Mock()
        mock_window.clock = pygame.time.Clock()
        mock_window.font_normal = pygame.font.Font(None, 24)
        mock_window.screen = pygame.display.set_mode((1200, 800))

        mock_text_display = Mock()
        mock_text_display.text_lines = []
        mock_text_display.text_scroll_offset = 0

        input_handler = PygameInput(mock_window, mock_text_display)

        # Simulate typing "hello" and submitting
        events = [
            Mock(type=pygame.KEYDOWN, key=pygame.K_h, unicode="h"),
            Mock(type=pygame.KEYDOWN, key=pygame.K_e, unicode="e"),
            Mock(type=pygame.KEYDOWN, key=pygame.K_l, unicode="l"),
            Mock(type=pygame.KEYDOWN, key=pygame.K_l, unicode="l"),
            Mock(type=pygame.KEYDOWN, key=pygame.K_o, unicode="o"),
            Mock(type=pygame.KEYDOWN, key=pygame.K_RETURN, unicode="\r"),
        ]

        mock_event_get.side_effect = [[e] for e in events]

        result = input_handler.get_input("Say hello:")

        assert result == "hello"
        assert input_handler.input_submitted is True
        assert input_handler.waiting_for_input is False

        pygame.quit()

    @patch("pygame.event.get")
    def test_scrolling_during_input(self, mock_event_get):
        """Test that scrolling works during text input"""
        pygame.init()
        mock_window = Mock()
        mock_window.clock = pygame.time.Clock()
        mock_window.font_normal = pygame.font.Font(None, 24)
        mock_window.screen = pygame.display.set_mode((1200, 800))

        mock_text_display = Mock()
        mock_text_display.text_lines = ["Line " + str(i) for i in range(50)]
        mock_text_display.text_scroll_offset = 0
        mock_text_display._handle_scroll = Mock()

        input_handler = PygameInput(mock_window, mock_text_display)

        # Simulate scroll event then enter
        scroll_event = Mock(type=pygame.MOUSEWHEEL, y=3)
        enter_event = Mock(type=pygame.KEYDOWN, key=pygame.K_RETURN, unicode="\r")

        mock_event_get.side_effect = [
            [scroll_event],
            [enter_event],
        ]

        input_handler.get_input("Scroll test:")

        # Verify scroll was handled
        mock_text_display._handle_scroll.assert_called_once_with(3)

        pygame.quit()
