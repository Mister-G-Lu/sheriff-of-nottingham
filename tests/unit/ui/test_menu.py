"""
Unit tests for ui/menu.py
Tests menu functions including title card, main menu, instructions, and credits.
"""

# Must be first import - sets up headless pygame environment
import json
from unittest.mock import Mock, mock_open, patch

import tests.test_setup  # noqa: F401
from ui import menu


class TestLoadMenuContent:
    """Tests for load_menu_content function"""

    def test_load_menu_content_success(self):
        """Test loading menu content from JSON file"""
        mock_content = {
            "title_pygame": "SHERIFF OF NOTTINGHAM",
            "how_to_play": {"header": "HOW TO PLAY", "sections": [], "footer": ""},
            "credits": {"header": "CREDITS", "sections": [], "footer": ""},
            "exit_message": "Thanks for playing!",
        }

        with patch("builtins.open", mock_open(read_data=json.dumps(mock_content))):
            content = menu.load_menu_content()

        assert content["title_pygame"] == "SHERIFF OF NOTTINGHAM"
        assert "how_to_play" in content
        assert "credits" in content
        assert "exit_message" in content

    def test_load_menu_content_file_not_found(self):
        """Test fallback when menu content file is not found"""
        with patch("builtins.open", side_effect=FileNotFoundError):
            content = menu.load_menu_content()

        # Should return fallback content
        assert "title_pygame" in content
        assert content["title_pygame"] == "SHERIFF OF NOTTINGHAM"
        assert "how_to_play" in content
        assert "credits" in content
        assert "exit_message" in content

    def test_load_menu_content_with_full_data(self):
        """Test loading menu content with full data structure"""
        mock_content = {
            "title_pygame": "SHERIFF OF NOTTINGHAM",
            "how_to_play": {
                "header": "HOW TO PLAY",
                "sections": [
                    {"title": "Objective", "content": "Catch smugglers"},
                    {"title": "Gameplay", "content": "Inspect bags"},
                ],
                "footer": "Good luck!",
            },
            "credits": {
                "header": "CREDITS",
                "title": "Sheriff of Nottingham",
                "sections": [{"title": "Developer", "content": "Test Dev"}],
                "version": "v1.0",
                "footer": "Thanks!",
            },
            "exit_message": "Goodbye!",
        }

        with patch("builtins.open", mock_open(read_data=json.dumps(mock_content))):
            content = menu.load_menu_content()

        assert len(content["how_to_play"]["sections"]) == 2
        assert content["credits"]["version"] == "v1.0"
        assert content["exit_message"] == "Goodbye!"


class TestShowTitleCard:
    """Tests for show_title_card function"""

    @patch("ui.menu.get_ui")
    @patch("ui.menu.load_menu_content")
    def test_show_title_card(self, mock_load_content, mock_get_ui):
        """Test displaying the title card"""
        mock_ui = Mock()
        mock_get_ui.return_value = mock_ui
        mock_load_content.return_value = {"title_pygame": "SHERIFF OF NOTTINGHAM"}

        menu.show_title_card()

        mock_load_content.assert_called_once()
        mock_get_ui.assert_called_once()
        mock_ui.show_title_screen.assert_called_once_with("SHERIFF OF NOTTINGHAM")


class TestShowMainMenu:
    """Tests for show_main_menu function"""

    @patch("ui.menu.get_ui")
    def test_show_main_menu(self, mock_get_ui):
        """Test show_main_menu displays correct choices."""
        mock_ui = Mock()
        mock_ui.show_choices.return_value = "start"
        mock_get_ui.return_value = mock_ui

        result = menu.show_main_menu()

        mock_get_ui.assert_called_once()
        mock_ui.show_choices.assert_called_once()

        # Should show 5 choices (added tutorial)
        args = mock_ui.show_choices.call_args[0]
        assert (
            len(args[1]) == 5
        )  # 5 menu options (start, tutorial, help, credits, exit)
        assert args[0] == ""  # Empty prompt
        choices = args[1]
        assert ("start", "Start Game") in choices
        assert ("tutorial", "Tutorial") in choices
        assert ("help", "How to Play") in choices
        assert ("credits", "Credits") in choices
        assert ("exit", "Exit") in choices

        assert result == "start"


class TestShowHowToPlay:
    """Tests for show_how_to_play function"""

    @patch("builtins.input")
    @patch("ui.menu.get_ui")
    @patch("ui.menu.load_menu_content")
    def test_show_how_to_play_basic(self, mock_load_content, mock_get_ui, mock_input):
        """Test displaying how to play instructions as static text"""
        mock_load_content.return_value = {
            "how_to_play": {
                "header": "HOW TO PLAY",
                "sections": [],
                "footer": "Good luck!",
            }
        }

        mock_ui = Mock()
        mock_get_ui.return_value = mock_ui

        menu.show_how_to_play()

        mock_load_content.assert_called_once()
        mock_input.assert_called_once()

        # Check that display_static_text was called with all content
        mock_ui.text.display_static_text.assert_called_once()
        static_text_lines = mock_ui.text.display_static_text.call_args[0][0]
        assert "HOW TO PLAY" in static_text_lines
        assert "Good luck!" in static_text_lines

    @patch("builtins.input")
    @patch("ui.menu.get_ui")
    @patch("ui.menu.load_menu_content")
    def test_show_how_to_play_with_sections(
        self, mock_load_content, mock_get_ui, mock_input
    ):
        """Test displaying how to play with multiple sections as static text"""
        mock_load_content.return_value = {
            "how_to_play": {
                "header": "HOW TO PLAY",
                "sections": [
                    {"title": "Objective", "content": "Catch smugglers"},
                    {"title": "Gameplay", "content": "Inspect merchant bags"},
                ],
                "footer": "Have fun!",
            }
        }

        mock_ui = Mock()
        mock_get_ui.return_value = mock_ui

        menu.show_how_to_play()

        # Check that display_static_text was called with all expected content
        mock_ui.text.display_static_text.assert_called_once()
        static_text_lines = mock_ui.text.display_static_text.call_args[0][0]
        assert "HOW TO PLAY" in static_text_lines
        assert "Objective" in static_text_lines
        assert "   Catch smugglers" in static_text_lines
        assert "Gameplay" in static_text_lines
        assert "   Inspect merchant bags" in static_text_lines
        assert "Have fun!" in static_text_lines


class TestShowCredits:
    """Tests for show_credits function"""

    @patch("builtins.input")
    @patch("ui.menu.get_ui")
    @patch("ui.menu.load_menu_content")
    def test_show_credits_basic(self, mock_load_content, mock_get_ui, mock_input):
        """Test displaying credits as static text"""
        mock_load_content.return_value = {
            "credits": {
                "header": "CREDITS",
                "title": "Game Title",
                "sections": [],
                "version": "v1.0",
                "footer": "Thanks!",
            }
        }

        mock_ui = Mock()
        mock_get_ui.return_value = mock_ui

        menu.show_credits()

        mock_load_content.assert_called_once()
        mock_input.assert_called_once()

        # Check that display_static_text was called with all content
        mock_ui.text.display_static_text.assert_called_once()
        static_text_lines = mock_ui.text.display_static_text.call_args[0][0]
        assert "CREDITS" in static_text_lines
        assert "Thanks!" in static_text_lines

    @patch("builtins.input")
    @patch("ui.menu.get_ui")
    @patch("ui.menu.load_menu_content")
    def test_show_credits_with_sections(
        self, mock_load_content, mock_get_ui, mock_input
    ):
        """Test displaying credits with multiple sections as static text"""
        mock_load_content.return_value = {
            "credits": {
                "header": "CREDITS",
                "title": "Game Title",
                "sections": [
                    {"title": "Developer", "content": "John Doe"},
                    {"title": "Artist", "content": "Jane Smith"},
                ],
                "version": "v1.0",
                "footer": "Thanks!",
            }
        }

        mock_ui = Mock()
        mock_get_ui.return_value = mock_ui

        menu.show_credits()

        # Check that display_static_text was called with all expected content
        mock_ui.text.display_static_text.assert_called_once()
        static_text_lines = mock_ui.text.display_static_text.call_args[0][0]
        assert "CREDITS" in static_text_lines
        assert "    Developer" in static_text_lines
        assert "       John Doe" in static_text_lines
        assert "    Artist" in static_text_lines
        assert "       Jane Smith" in static_text_lines
        assert "Thanks!" in static_text_lines


class TestRunMenu:
    """Tests for run_menu function"""

    @patch("ui.menu.show_main_menu")
    @patch("ui.menu.show_title_card")
    @patch("ui.menu.get_ui")
    def test_run_menu_start_game(self, mock_get_ui, mock_show_title, mock_show_menu):
        """Test run_menu when user chooses to start game"""
        mock_ui = Mock()
        mock_get_ui.return_value = mock_ui
        mock_show_menu.return_value = "start"

        result = menu.run_menu()

        assert result is True
        mock_ui.clear_text.assert_called_once()
        mock_show_title.assert_called_once()
        mock_show_menu.assert_called_once()

    @patch("builtins.print")
    @patch("ui.menu.load_menu_content")
    @patch("ui.menu.show_main_menu")
    @patch("ui.menu.show_title_card")
    @patch("ui.menu.get_ui")
    def test_run_menu_exit(
        self,
        mock_get_ui,
        mock_show_title,
        mock_show_menu,
        mock_load_content,
        mock_print,
    ):
        """Test run_menu when user chooses to exit"""
        mock_ui = Mock()
        mock_get_ui.return_value = mock_ui
        mock_show_menu.return_value = "exit"
        mock_load_content.return_value = {"exit_message": "Thanks for playing!"}

        result = menu.run_menu()

        assert result is False
        mock_print.assert_called_once_with("Thanks for playing!")

    @patch("builtins.input")
    @patch("builtins.print")
    @patch("ui.menu.show_how_to_play")
    @patch("ui.menu.show_main_menu")
    @patch("ui.menu.show_title_card")
    @patch("ui.menu.get_ui")
    def test_run_menu_help_then_start(
        self,
        mock_get_ui,
        mock_show_title,
        mock_show_menu,
        mock_show_help,
        mock_print,
        mock_input,
    ):
        """Test run_menu when user views help then starts game"""
        mock_ui = Mock()
        mock_get_ui.return_value = mock_ui
        mock_show_menu.side_effect = ["help", "start"]

        result = menu.run_menu()

        assert result is True
        assert mock_show_menu.call_count == 2
        mock_show_help.assert_called_once()

    @patch("builtins.input")
    @patch("builtins.print")
    @patch("ui.menu.show_credits")
    @patch("ui.menu.show_main_menu")
    @patch("ui.menu.show_title_card")
    @patch("ui.menu.get_ui")
    def test_run_menu_credits_then_start(
        self,
        mock_get_ui,
        mock_show_title,
        mock_show_menu,
        mock_show_credits,
        mock_print,
        mock_input,
    ):
        """Test run_menu when user views credits then starts game"""
        mock_ui = Mock()
        mock_get_ui.return_value = mock_ui
        mock_show_menu.side_effect = ["credits", "start"]

        result = menu.run_menu()

        assert result is True
        assert mock_show_menu.call_count == 2
        mock_show_credits.assert_called_once()

    @patch("builtins.input")
    @patch("builtins.print")
    @patch("ui.menu.show_credits")
    @patch("ui.menu.show_how_to_play")
    @patch("ui.menu.show_main_menu")
    @patch("ui.menu.show_title_card")
    @patch("ui.menu.get_ui")
    def test_run_menu_multiple_views(
        self,
        mock_get_ui,
        mock_show_title,
        mock_show_menu,
        mock_show_help,
        mock_show_credits,
        mock_print,
        mock_input,
    ):
        """Test run_menu with multiple menu interactions"""
        mock_ui = Mock()
        mock_get_ui.return_value = mock_ui
        mock_show_menu.side_effect = ["help", "credits", "help", "start"]

        result = menu.run_menu()

        assert result is True
        assert mock_show_menu.call_count == 4
        assert mock_show_help.call_count == 2
        assert mock_show_credits.call_count == 1
