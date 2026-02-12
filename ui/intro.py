"""
Game Intro Display
Handles loading and displaying the game introduction
"""

import json
from pathlib import Path


def print_intro() -> None:
    """Load and display game intro from JSON file."""
    # Load intro from JSON
    intro_path = Path(__file__).parent.parent / "data" / "game_intro.json"
    try:
        with open(intro_path, encoding="utf-8") as f:
            intro_data = json.load(f)

        title = intro_data.get("title", "Sheriff of Nottingham")
        intro_text = intro_data.get("intro", "")

        print(f"=== {title} ===")
        print("")
        print(intro_text)
        print("")

    except (FileNotFoundError, json.JSONDecodeError):
        # Fallback to hardcoded intro if file not found
        print("=== Sheriff of Nottingham ===")
        print("")
        print("You are the newly appointed inspector at Nottingham's eastern gate.")
        print("")

    # Wait for user to click to proceed (Pygame mode)
    try:
        from ui.pygame_ui import get_ui

        ui = get_ui()
        ui.wait_for_continue()
    except Exception:
        # Terminal mode or UI not initialized - no wait needed
        # This is expected behavior, not an error
        pass
