"""
Pytest configuration file for test setup
Handles path configuration and common fixtures
"""

import sys
import os
from pathlib import Path

# Setup headless mode for all pygame tests - MUST be before pygame imports
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

# Add project root to Python path
# This file is at: tests/conftest.py
# Project root is 1 level up
project_root = Path(__file__).resolve().parent.parent

# Insert at beginning of path if not already there
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Also ensure we can import from the installed package
import pytest

def pytest_configure(config):
    """Called after command line options have been parsed."""
    # Ensure project root is in path
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
