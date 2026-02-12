"""
Pytest configuration file for test setup
Handles path configuration and common fixtures
"""

# Must be first import - sets up test environment
import os
import sys
import warnings
from pathlib import Path

import tests.test_setup  # noqa: F401

# Setup headless mode for all pygame tests - MUST be before pygame imports
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

# Suppress pygame's pkg_resources deprecation warning
# This is a known issue in pygame that uses the deprecated pkg_resources API
# The pygame team is working on migrating to importlib.resources
# See: https://github.com/pygame/pygame/issues/3307
warnings.filterwarnings("ignore", category=UserWarning, module="pygame.pkgdata")

# Add project root to Python path
# This file is at: tests/conftest.py
# Project root is 1 level up
project_root = Path(__file__).resolve().parent.parent

# Insert at beginning of path if not already there
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Also ensure we can import from the installed package


def pytest_configure(config):
    """Called after command line options have been parsed."""
    # Ensure project root is in path
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
