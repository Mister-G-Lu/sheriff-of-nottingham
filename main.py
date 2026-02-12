"""
Sheriff of Nottingham — Interactive Inspector Game

DEVELOPER NOTE:
===============
This file should remain MINIMAL - only initialization and entry point.
All game logic has been extracted to:
    - core/game_manager.py - Main game loop and merchant encounters
    - ui/menu.py - Menu system
    - ui/pygame_ui.py - UI components

Keep this file focused on:
1. Environment setup (pygame suppression, print redirection)
2. UI initialization
3. Menu and game flow coordination
4. Error handling and cleanup

DO NOT add game logic here - put it in the appropriate manager file!
"""

# Environment setup (must be first - sets up pygame environment)
# Standard library imports
import builtins
import logging
import os
import warnings

import setup_env  # noqa: F401 - imported for side effects

# Suppress pygame welcome message (MUST be before importing pygame)
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

# Local imports - core
from core.game.game_manager import run_game
from core.utils.error_logger import (
    cleanup_old_logs,
    install_exception_handler,
    log_game_event,
    setup_error_logging,
)

# Local imports - UI (imports pygame, so must be after os.environ)
from ui.menu import run_menu
from ui.output import game_input, game_print
from ui.pygame_ui import close_ui, get_ui

# Initialize logging system
main_log, error_log = setup_error_logging()
install_exception_handler()
cleanup_old_logs(keep_count=10)  # Keep last 10 log files

# TEMPORARY: Monkey patch for backward compatibility
# TODO: Gradually replace print() with game_print() and input() with game_input()
# throughout the codebase, then remove this monkey patching
_original_print = builtins.print
_original_input = builtins.input
builtins.print = game_print
builtins.input = game_input

if __name__ == "__main__":
    # Suppress Python warnings for clean output
    import warnings

    warnings.filterwarnings("ignore")

    try:
        log_game_event("startup", "Initializing game")

        # Initialize Pygame UI
        ui = get_ui()
        log_game_event("startup", "UI initialized")

        # Clear screen and show menu
        ui.clear_text()

        # Show menu first
        should_start = run_menu()

        if should_start:
            log_game_event("game_start", "Starting new game")
            # Clear screen before starting game
            ui.clear_text()
            # Start the game
            run_game()
            log_game_event("game_end", "Game completed normally")
        else:
            log_game_event("menu", "User exited from menu")

        # Keep window open after game ends
        ui.display_text(
            "\n[Game ended. Close the window to exit.]", clear_previous=False
        )

        # Wait for window close
        import pygame

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            ui.clock.tick(60)

        log_game_event("shutdown", "Game closed normally")

    except Exception as e:
        logging.error("Fatal error in main game loop", exc_info=e)
        _original_print(f"\nFATAL ERROR: {e}")
        _original_print(f"Check logs directory for details: {main_log}")
        import traceback

        traceback.print_exc()
    finally:
        log_game_event("cleanup", "Cleaning up resources")
        close_ui()
        logging.info("=" * 70)
        logging.info("Sheriff of Nottingham - Session Ended")
        logging.info("=" * 70)
