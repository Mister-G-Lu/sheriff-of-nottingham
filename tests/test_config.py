"""
Test Configuration

Provides utilities for running tests in headless mode to avoid
pygame windows flashing on screen during test execution.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def setup_headless_mode():
    """
    Configure pygame to run in headless mode for testing.
    
    This prevents pygame windows from appearing during tests,
    which can be distracting when running test suites.
    
    Call this at the start of test files that use pygame.
    """
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    os.environ['SDL_AUDIODRIVER'] = 'dummy'


def teardown_headless_mode():
    """Clean up headless mode environment variables."""
    os.environ.pop('SDL_VIDEODRIVER', None)
    os.environ.pop('SDL_AUDIODRIVER', None)


def create_headless_window():
    """
    Create a pygame window in headless mode.
    
    Returns:
        PygameWindow instance configured for headless operation
    """
    from ui.pygame_window import PygameWindow
    return PygameWindow(headless=True)
