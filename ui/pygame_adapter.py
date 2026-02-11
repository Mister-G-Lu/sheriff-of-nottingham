"""
Adapter to make Pygame UI work with existing game code
Provides print() and input() replacements that use the Pygame UI
"""

from ui.pygame_ui import get_ui
from typing import Optional


class PygameOutput:
    """Replacement for stdout that uses Pygame UI"""
    
    def write(self, text: str):
        if text and text.strip():  # Only display non-empty text
            ui = get_ui()
            ui.display_text(text.rstrip('\n'), clear_previous=False)
    
    def flush(self):
        pass


class PygameInput:
    """Replacement for stdin that uses Pygame UI"""
    
    def readline(self) -> str:
        ui = get_ui()
        return ui.get_input() + '\n'


def pygame_print(*args, sep=' ', end='\n', **kwargs):
    """Pygame version of print()"""
    text = sep.join(str(arg) for arg in args) + end
    ui = get_ui()
    ui.display_text(text.rstrip('\n'), clear_previous=False)


def pygame_input(prompt: str = "") -> str:
    """Pygame version of input()"""
    if prompt:
        ui = get_ui()
        ui.display_text(prompt, clear_previous=False)
    ui = get_ui()
    return ui.get_input()


def clear_screen():
    """Clear the pygame screen"""
    ui = get_ui()
    ui.clear_text()


def wait_for_continue():
    """Wait for user to continue"""
    ui = get_ui()
    ui.wait_for_continue()


def show_portrait(character_name: str):
    """Show a character portrait"""
    ui = get_ui()
    ui.load_portrait(character_name)


def clear_portrait():
    """Clear the current portrait"""
    ui = get_ui()
    ui.clear_portrait()
