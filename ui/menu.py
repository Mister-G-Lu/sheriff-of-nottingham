"""
Game menu and intro screen with ASCII art and image display.

DEVELOPER NOTE:
===============
DO NOT add large blocks of hardcoded text to this file!
All menu content (instructions, credits, ASCII art, etc.) should be stored in:
    data/menu_content.json

This keeps the code clean and makes content easy to edit without touching Python code.
To add or modify menu content:
1. Edit data/menu_content.json
2. Use load_menu_content() to load the content
3. Display it using the appropriate function

Keep this file focused on menu logic and display functions, not content storage.
"""

import json
from pathlib import Path

from ui.pygame_ui import get_ui


def load_menu_content():
    """Load all menu content from JSON file."""
    menu_file = Path(__file__).parent.parent / "data" / "menu_content.json"
    try:
        with open(menu_file, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback if file not found
        return {
            "title_pygame": "SHERIFF OF NOTTINGHAM",
            "how_to_play": {"header": "HOW TO PLAY", "sections": [], "footer": ""},
            "credits": {"header": "CREDITS", "sections": [], "footer": ""},
            "exit_message": "Thanks for playing!",
        }


def show_title_card():
    """Display the game title card."""
    content = load_menu_content()
    ui = get_ui()
    # Show split screen: title on left, sheriff portrait on right
    ui.show_title_screen(content["title_pygame"])


def show_main_menu():
    """Display the main menu and get player choice."""
    ui = get_ui()
    choices = [
        ("start", "Start Game"),
        ("tutorial", "Tutorial"),
        ("help", "How to Play"),
        ("credits", "Credits"),
        ("exit", "Exit"),
    ]
    return ui.show_choices("", choices)


def show_how_to_play():
    """Display how to play instructions as static scrollable text."""
    content = load_menu_content()
    how_to_play = content["how_to_play"]
    ui = get_ui()

    # Hide price menu button and expand text zone for "How to Play"
    ui.price_menu.visible = False
    ui.text.set_fullscreen_mode(True)

    # Build all text content at once (no typewriter effect)
    all_text = []
    all_text.append(how_to_play["header"])
    all_text.append("")  # Empty line

    # Add each section
    for section in how_to_play["sections"]:
        all_text.append(section["title"])
        # Split multi-line content
        for line in section["content"].split("\n"):
            all_text.append(f"   {line}")
        all_text.append("")  # Empty line between sections

    # Add footer
    all_text.append(how_to_play["footer"])
    all_text.append("")
    all_text.append(
        "[Use mouse wheel or arrow keys to scroll. Press Enter or click to exit.]"
    )

    # Display all text at once as static content
    ui.text.display_static_text(all_text)

    # Wait for user to exit
    input()

    # Restore normal mode
    ui.price_menu.visible = True
    ui.text.set_fullscreen_mode(False)
    ui.clear_text()


def show_credits():
    """Display game credits as static scrollable text."""
    content = load_menu_content()
    credits_data = content["credits"]
    ui = get_ui()

    # Hide price menu button and expand text zone for Credits
    ui.price_menu.visible = False
    ui.text.set_fullscreen_mode(True)

    # Build all text content at once (no typewriter effect)
    all_text = []
    all_text.append(credits_data["header"])
    all_text.append("")  # Empty line

    # Add title
    for line in credits_data["title"].split("\n"):
        all_text.append(f"    {line}")
    all_text.append("")  # Empty line

    # Add each section
    for section in credits_data["sections"]:
        all_text.append(f"    {section['title']}")
        # Split multi-line content
        for line in section["content"].split("\n"):
            all_text.append(f"       {line}")
        all_text.append("")  # Empty line between sections

    # Add version and footer
    all_text.append(f"    {credits_data['version']}")
    all_text.append("")
    all_text.append(credits_data["footer"])
    all_text.append("")
    all_text.append(
        "[Use mouse wheel or arrow keys to scroll. Press Enter or click to exit.]"
    )

    # Display all text at once as static content
    ui.text.display_static_text(all_text)

    # Wait for user to exit
    input()

    # Restore normal mode
    ui.price_menu.visible = True
    ui.text.set_fullscreen_mode(False)
    ui.clear_text()


def run_menu():
    """Run the main menu loop."""
    ui = get_ui()

    while True:
        # Clear screen
        ui.clear_text()

        # Show title card
        show_title_card()

        # Show menu and get choice
        choice = show_main_menu()

        if choice == "start":
            # Ask if they want tutorial (screen already cleared by menu loop)
            tutorial_choice = ui.show_choices(
                "Would you like to play the tutorial first?",
                [("yes", "Yes, show me the tutorial"), ("no", "No, skip to main game")],
            )

            if tutorial_choice == "yes":
                from core.game.tutorial import run_interactive_tutorial

                ui.clear_text()
                start_game = run_interactive_tutorial()
                if start_game:
                    return True  # Start the game after tutorial
                # Otherwise loop back to menu
            else:
                return True  # Start the game directly

        elif choice == "tutorial":
            # Run tutorial from menu
            from core.game.tutorial import run_interactive_tutorial

            ui.clear_text()
            start_game = run_interactive_tutorial()
            if start_game:
                return True  # Start the game after tutorial
            # Otherwise loop back to menu

        elif choice == "help":
            show_how_to_play()
        elif choice == "credits":
            show_credits()
        elif choice == "exit":
            content = load_menu_content()
            print(content["exit_message"])
            return False  # Exit the game
