"""
UI Output Module - Clean alternative to monkey patching built-ins

This module provides game_print() and game_input() functions that work with
the Pygame UI, without modifying built-in print() and input().

Usage:
    from ui.output import game_print, game_input

    game_print("Hello, Sheriff!")
    name = game_input("What is your name? ")
"""


def game_print(*args, sep: str = " ", end: str = "\n", **kwargs) -> None:
    """Display text in the game UI.

    This is a drop-in replacement for print() that works with the Pygame UI.
    Falls back to standard print() if UI is not available.

    Args:
        *args: Values to print
        sep: Separator between values (default: ' ')
        end: String appended after the last value (default: '\n')
        **kwargs: Additional keyword arguments (for compatibility)
    """
    text = sep.join(str(arg) for arg in args)
    if text or end != "\n":
        text += end

    try:
        from ui.pygame_ui import get_ui

        ui = get_ui()
        ui.display_text(text.rstrip("\n"), clear_previous=False)
    except Exception:
        # Fallback to standard print if UI not available
        print(text, end="")


def game_input(prompt: str = "") -> str:
    """Get input from the user via the game UI.

    This is a drop-in replacement for input() that works with the Pygame UI.
    Falls back to standard input() if UI is not available.

    Args:
        prompt: Prompt to display to the user

    Returns:
        str: User's input
    """
    if prompt:
        game_print(prompt, end="")

    try:
        from ui.pygame_ui import get_ui

        ui = get_ui()
        return ui.get_input()
    except Exception:
        # Fallback to standard input if UI not available
        return input()


# For backward compatibility with code that uses print/input directly
# These can be imported and used explicitly instead of monkey patching
__all__ = ["game_print", "game_input"]
