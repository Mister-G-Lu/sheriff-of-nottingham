"""
Centralized Constants for Sheriff of Nottingham
All game constants organized by category for easy reference and modification
"""

# ============================================================================
# GAME RULES & MECHANICS
# ============================================================================

# Starting resources
STARTING_GOLD = 50
STARTING_REPUTATION = 5  # Sheriff starts with neutral reputation (scale 0-10)
STARTING_PERCEPTION = 1  # Sheriff's starting perception stat
STARTING_AUTHORITY = 1   # Sheriff's starting authority stat
STARTING_EXPERIENCE = 0  # Sheriff starts with no experience

# Bag and inventory limits
HAND_SIZE_LIMIT = 7  # Maximum cards a merchant has available to choose from
BAG_SIZE_LIMIT = 5   # Maximum items a merchant can carry/smuggle in their bag

# Penalty rules
CONFISCATION_PENALTY_RATE = 0.5  # Merchants pay 50% of confiscated goods' value

# Reputation bounds
MIN_REPUTATION = 0
MAX_REPUTATION = 10

# Sheriff stats bounds
MIN_STAT = 0
MAX_STAT = 10


# ============================================================================
# UI - COLORS
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
# UI - SCREEN DIMENSIONS
# ============================================================================

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800


# ============================================================================
# UI - LAYOUT - PORTRAITS
# ============================================================================

# Gameplay portraits (centered horizontally)
PORTRAIT_WIDTH = 400
PORTRAIT_HEIGHT = 400
PORTRAIT_Y = 60  # Moved down to make room for stats bar

# Title screen portraits
TITLE_PORTRAIT_WIDTH = 500
TITLE_PORTRAIT_HEIGHT = 700
TITLE_PORTRAIT_Y = 50


# ============================================================================
# UI - LAYOUT - TEXT BOX
# ============================================================================

TEXT_BOX_X = 50
TEXT_BOX_Y = 500
TEXT_BOX_WIDTH = SCREEN_WIDTH - 100
TEXT_BOX_HEIGHT = 250


# ============================================================================
# UI - LAYOUT - STATS BAR
# ============================================================================

STATS_BAR_HEIGHT = 40
STATS_BAR_PADDING = 10
STATS_BAR_MARGIN = 5


# ============================================================================
# UI - FONTS
# ============================================================================

FONT_SIZE_SMALL = 16
FONT_SIZE_NORMAL = 20
FONT_SIZE_LARGE = 28
FONT_SIZE_TITLE = 56


# ============================================================================
# UI - ANIMATION
# ============================================================================

PORTRAIT_SLIDE_SPEED = 30  # Pixels per frame for portrait slide-in effect
PORTRAIT_INITIAL_OFFSET = -400  # Starting position off-screen (left)


# ============================================================================
# GOODS - VALUES
# ============================================================================

# Legal goods values
APPLE_VALUE = 2
CHEESE_VALUE = 3
BREAD_VALUE = 3
CHICKEN_VALUE = 4

# Contraband values
SILK_VALUE = 8
PEPPER_VALUE = 8
MEAD_VALUE = 10
CROSSBOW_VALUE = 15
