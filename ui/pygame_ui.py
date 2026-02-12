"""
Pygame Visual Novel UI for Sheriff of Nottingham
Main interface that coordinates window, text, and input components
"""

from typing import Optional

from ui.price_menu import PriceMenu
from ui.pygame_input import PygameInput
from ui.pygame_text import PygameText
from ui.pygame_window import PygameWindow
from ui.stats_bar import StatsBar


class VisualNovelUI:
    """Main Pygame UI class that coordinates all components"""

    def __init__(self):
        # Initialize components
        self.window = PygameWindow()
        self.text = PygameText(self.window)
        self.price_menu = PriceMenu(
            self.window.screen, self.window.font_normal, self.window.font_small
        )
        self.input = PygameInput(self.window, self.text, self.price_menu)
        self.stats_bar = StatsBar(self.window.screen, self.window.font_small)

        # Expose commonly used attributes for backward compatibility
        self.screen = self.window.screen
        self.clock = self.window.clock
        self.font_normal = self.window.font_normal
        self.font_large = self.window.font_large
        self.font_small = self.window.font_small

    # Window methods
    def load_portrait_file(self, portrait_filename: str) -> bool:
        """Load a portrait PNG directly by filename"""
        return self.window.load_portrait_file(portrait_filename)

    def clear_portrait(self):
        """Clear the current portrait"""
        self.window.clear_portrait()

    def show_title_screen(self, title_text: str):
        """Display title screen"""
        self.window.show_title_screen(title_text)

    # Text methods
    def display_text(
        self, text: str, clear_previous: bool = True, animate: bool = True
    ):
        """Display text with optional typewriter effect"""
        self.text.display_text(text, clear_previous, animate)

    def clear_text(self):
        """Clear all text"""
        self.text.clear_text()

    def update_stats(
        self,
        sheriff=None,
        stats=None,
        merchant_count: int = 0,
        total_merchants: int = 0,
    ):
        """Update the stats bar with current game state"""
        self.stats_bar.update(sheriff, stats, merchant_count, total_merchants)

    def render(self):
        """Render the current state"""
        self.stats_bar.render()  # Render stats bar first (at top)
        self.text.render()
        self.price_menu.render()

    # Input methods
    def get_input(self, prompt: str = "") -> str:
        """Get text input from user"""
        return self.input.get_input(prompt)

    def show_choices(self, prompt: str, choices: list[tuple[str, str]]) -> str:
        """Show choice buttons and return selected choice"""
        return self.input.show_choices(prompt, choices)

    def wait_for_continue(self):
        """Wait for user to continue"""
        self.input.wait_for_continue()

    # Event handling
    def handle_events(self):
        """Handle pygame events"""
        self.window.handle_events()

    def handle_click(self, pos):
        """Handle mouse click events"""
        return self.price_menu.handle_click(pos)

    def close(self):
        """Close the pygame window"""
        self.window.close()


# Global UI instance
_ui_instance: Optional[VisualNovelUI] = None


def get_ui() -> VisualNovelUI:
    """Get or create the global UI instance"""
    global _ui_instance
    if _ui_instance is None:
        _ui_instance = VisualNovelUI()
    return _ui_instance


def close_ui():
    """Close the UI"""
    global _ui_instance
    if _ui_instance:
        _ui_instance.close()
        _ui_instance = None
