"""
Integration tests extracted from test_intro.py
"""

# Must be first import - sets up test environment
from unittest.mock import mock_open, patch

import tests.test_setup  # noqa: F401
from ui.intro import print_intro


class TestPrintIntroIntegration:
    """Integration tests for print_intro"""

    @patch("ui.pygame_ui.get_ui")
    @patch("builtins.print")
    def test_full_intro_flow(self, mock_print, mock_get_ui):
        """Test complete intro flow from file load to display"""
        # Mock the UI wait_for_continue to avoid blocking
        mock_ui = mock_get_ui.return_value
        mock_ui.wait_for_continue.return_value = None

        mock_intro_data = {"title": "Test Game", "intro": "Complete intro text"}

        with patch("builtins.open", mock_open()):
            with patch("json.load", return_value=mock_intro_data):
                print_intro()

                # Verify complete flow
                assert mock_print.called
                assert any(
                    "Test Game" in str(call) for call in mock_print.call_args_list
                )
                assert any(
                    "Complete intro text" in str(call)
                    for call in mock_print.call_args_list
                )

    @patch("ui.pygame_ui.get_ui")
    @patch("builtins.print")
    def test_fallback_intro_complete(self, mock_print, mock_get_ui):
        """Test complete fallback intro when file is missing"""
        # Mock the UI wait_for_continue to avoid blocking
        mock_ui = mock_get_ui.return_value
        mock_ui.wait_for_continue.return_value = None

        with patch("builtins.open", side_effect=FileNotFoundError):
            print_intro()

            # Verify fallback text components
            assert any(
                "Sheriff of Nottingham" in str(call)
                for call in mock_print.call_args_list
            )
            assert any(
                "newly appointed inspector" in str(call)
                for call in mock_print.call_args_list
            )
            assert any(
                "Nottingham's eastern gate" in str(call)
                for call in mock_print.call_args_list
            )
