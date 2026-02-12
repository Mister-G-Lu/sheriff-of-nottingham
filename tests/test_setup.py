"""
Test Setup Module

This module must be imported at the very top of test files that use pygame.
It sets up the headless environment before pygame is imported.

Usage:
    import tests.test_setup  # Must be first import
    from ui.menu import run_menu  # Now safe to import pygame modules
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup headless mode for pygame (must be before pygame import)
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
