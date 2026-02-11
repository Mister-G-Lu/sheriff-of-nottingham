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

# Suppress pygame welcome message (must be before pygame import)
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"

import sys
import builtins

# Initialize Pygame UI
from ui.pygame_ui import get_ui, close_ui

# Redirect print and input to use Pygame UI globally
_original_print = builtins.print
_original_input = builtins.input

def pygame_print(*args, sep=' ', end='\n', **kwargs):
    """Pygame version of print()"""
    text = sep.join(str(arg) for arg in args)
    if text or end != '\n':
        text += end
    ui = get_ui()
    ui.display_text(text.rstrip('\n'), clear_previous=False)

def pygame_input(prompt: str = "") -> str:
    """Pygame version of input()"""
    if prompt:
        ui = get_ui()
        ui.display_text(prompt, clear_previous=False)
    ui = get_ui()
    return ui.get_input()

# Replace built-in print and input globally
builtins.print = pygame_print
builtins.input = pygame_input

# Import game components after print redirection is set up
from ui.menu import run_menu
from core.game.game_manager import run_game


if __name__ == "__main__":
    # Suppress Python warnings for clean output
    import warnings
    warnings.filterwarnings('ignore')
    
    try:
        # Initialize Pygame UI
        ui = get_ui()
        
        # Clear screen and show menu
        ui.clear_text()
        
        # Show menu first
        should_start = run_menu()
        
        if should_start:
            # Clear screen before starting game
            ui.clear_text()
            # Start the game
            run_game()
        
        # Keep window open after game ends
        ui.display_text("\n[Game ended. Close the window to exit.]", clear_previous=False)
        
        # Wait for window close
        import pygame
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            ui.clock.tick(60)
    
    except Exception as e:
        _original_print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        close_ui()
