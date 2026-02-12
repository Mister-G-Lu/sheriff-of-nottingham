"""
Decision Handling - Handles player decision prompts and input
Extracted from game_manager.py for better testability and organization
"""


def prompt_inspection(
    decision_prompt: str = "Inspect the bag or let them pass? [i/p]: ",
) -> bool:
    """Ask the player whether to inspect (True) or pass (False).

    Args:
        decision_prompt: The prompt to display to the user

    Returns:
        bool: True if player chooses to inspect, False if they choose to pass
    """
    while True:
        choice = input(decision_prompt).strip().lower()
        if choice in {"i", "inspect"}:
            return True
        if choice in {"p", "pass"}:
            return False
        print("Please answer with 'i' to inspect or 'p' to pass.")


def update_stats_bar(sheriff, stats, merchant_idx, total_merchants):
    """Helper to update the stats bar UI (if available).

    Args:
        sheriff: Sheriff object with reputation and stats
        stats: GameStats object
        merchant_idx: Current merchant index (1-based)
        total_merchants: Total number of merchants
    """
    try:
        from ui.pygame_ui import get_ui

        ui = get_ui()
        ui.update_stats(sheriff, stats, merchant_idx, total_merchants)
    except ImportError:
        pass  # Terminal mode, no UI
