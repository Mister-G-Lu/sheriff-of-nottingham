"""
UI Constants - All UI-related constants for the Pygame interface

This module contains constants for:
- Screen dimensions
- Colors
- Text display settings
- Button and menu dimensions
- Animation settings
"""

# ============================================================================
# COLORS
# ============================================================================

# Basic colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (200, 200, 200)

# Themed colors
GREEN = (0, 255, 0)
DARK_GREEN = (0, 180, 0)
RED = (255, 0, 0)
DARK_RED = (180, 0, 0)
GOLD = (255, 215, 0)


# ============================================================================
# SCREEN DIMENSIONS
# ============================================================================

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800


# ============================================================================
# TEXT BOX LAYOUT
# ============================================================================

# Text box position and size
TEXT_BOX_X = 50
TEXT_BOX_Y = 250
TEXT_BOX_WIDTH = 700
TEXT_BOX_HEIGHT = 500


# ============================================================================
# PORTRAIT DISPLAY
# ============================================================================

# Portrait dimensions and position
PORTRAIT_WIDTH = 400
PORTRAIT_HEIGHT = 600
PORTRAIT_X = 750
PORTRAIT_Y = 150


# ============================================================================
# FONT SIZES
# ============================================================================

FONT_SIZE_SMALL = 20
FONT_SIZE_NORMAL = 28
FONT_SIZE_LARGE = 36
FONT_SIZE_TITLE = 48


# ============================================================================
# TEXT DISPLAY
# ============================================================================

# Text rendering
TEXT_SPEED_WPM = 500  # Words per minute for typewriter effect
TEXT_BOX_PADDING = 40  # Top/bottom padding in pixels
TEXT_BOX_VERTICAL_PADDING = 20  # Vertical padding inside text box
LINE_SPACING = 5  # Pixels between lines of text
SCROLL_INDICATOR_WIDTH = 250  # Width of scroll indicator in pixels

# Text wrapping
TEXT_WRAP_MARGIN = 40  # Margin for text wrapping (pixels from edge)


# ============================================================================
# PRICE MENU
# ============================================================================

# Button dimensions
PRICE_BUTTON_WIDTH = 120  # Width of "Show Prices" button
PRICE_BUTTON_HEIGHT = 40  # Height of "Show Prices" button
PRICE_BUTTON_Y_OFFSET = 50  # Y position below stats bar
PRICE_BUTTON_MARGIN = 20  # Margin from screen edge

# Menu panel dimensions
PRICE_MENU_WIDTH = 350  # Width of price menu panel
PRICE_MENU_HEIGHT = 500  # Height of price menu panel
PRICE_MENU_Y_OFFSET = 100  # Y position of menu panel


# ============================================================================
# ANIMATION
# ============================================================================

PORTRAIT_SLIDE_SPEED = 30  # Pixels per frame for portrait slide-in effect
PORTRAIT_INITIAL_OFFSET = -400  # Starting position off-screen (left)
