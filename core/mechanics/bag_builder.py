"""
Bag Builder - Handles bag and declaration creation logic
Extracted from game_manager.py for better testability and organization
"""

import random

from core.game.rounds import Declaration
from core.mechanics.deck import draw_hand
from core.mechanics.goods import GOOD_BY_ID
from core.players.merchants import Merchant


def build_bag_and_declaration(merchant: Merchant, history: list = None):
    """Create a bag (true contents) and what the merchant declares using merchant's strategy.

    Args:
        merchant: The merchant making the declaration
        history: Optional history of previous encounters for strategic merchants

    Returns:
        tuple: (declaration, actual_goods, is_honest)
    """
    # Draw a hand for the merchant (simulate card drawing)
    # This is critical for merchants like Silas who analyze their hand to make decisions
    merchant.hand = draw_hand()

    # Use merchant's strategic decision-making
    decision = merchant.choose_declaration(history)

    declared_id = decision["declared_id"]
    declared_count = decision["count"]
    actual_ids = decision["actual_ids"]
    is_honest = not decision["lie"]

    # Convert IDs to Good objects
    actual_goods = [GOOD_BY_ID[good_id] for good_id in actual_ids]

    declaration = Declaration(good_id=declared_id, count=declared_count)
    return declaration, actual_goods, is_honest


def choose_tell(merchant: Merchant, is_honest: bool) -> str:
    """Pick a random tell line depending on whether the merchant is honest this round."""
    pool = merchant.tells_honest if is_honest else merchant.tells_lying
    return random.choice(pool) if pool else ""
