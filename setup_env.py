"""
Environment Setup - Run before main

This module sets up environment variables that must be configured
before importing pygame or other modules.

Import this at the very top of main.py to avoid E402 linting errors.
"""

import os

# Suppress pygame welcome message
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
