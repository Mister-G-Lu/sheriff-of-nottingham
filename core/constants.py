"""
Game Logic Constants for Sheriff of Nottingham

This module contains constants for game rules, mechanics, and logic ONLY.
For UI-related constants, see ui/ui_constants.py

All game constants organized by category for easy reference and modification
"""

# ============================================================================
# GAME RULES & MECHANICS
# ============================================================================

# Starting resources
STARTING_GOLD = 50
STARTING_REPUTATION = 5  # Sheriff starts with neutral reputation (scale 0-10)
STARTING_PERCEPTION = 1  # Sheriff's starting perception stat
STARTING_AUTHORITY = 1  # Sheriff's starting authority stat
STARTING_EXPERIENCE = 0  # Sheriff starts with no experience

# Bag and inventory limits
HAND_SIZE_LIMIT = 7  # Maximum cards a merchant has available to choose from
BAG_SIZE_LIMIT = 5  # Maximum items a merchant can carry/smuggle in their bag

# Penalty rules
CONFISCATION_PENALTY_RATE = 0.5  # Merchants pay 50% of confiscated goods' value

# Reputation bounds
MIN_REPUTATION = 0
MAX_REPUTATION = 10

# Sheriff stats bounds
MIN_STAT = 0
MAX_STAT = 10


# ============================================================================
# PROBABILITIES
# ============================================================================

# Bribe probability thresholds
BRIBE_PROB_LOW = 0.2  # 20% base chance for low-risk bribes
BRIBE_PROB_MODERATE = 0.3  # 30% chance for moderate bribes
BRIBE_PROB_HIGH = 0.5  # 50% chance for high-risk bribes
BRIBE_PROB_MAX = 0.7  # 70% maximum bribe probability

# Merchant attribute scales
MERCHANT_ATTRIBUTE_MIN = 0  # Minimum value for merchant attributes
MERCHANT_ATTRIBUTE_MAX = 10  # Maximum value for merchant attributes (risk, greed, etc.)


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
PEPPER_VALUE = 10
MEAD_VALUE = 12
CROSSBOW_VALUE = 15
