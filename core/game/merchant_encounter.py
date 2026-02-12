"""
Merchant Encounter - Handles negotiation and merchant interaction logic
Extracted from game_manager.py for better testability and organization
"""

from core.mechanics.goods import Good
from core.mechanics.negotiation import initiate_threat, sheriff_respond_to_bribe
from core.players.merchants import Merchant
from core.players.sheriff import Sheriff
from core.systems.game_master_state import get_game_master_state
from core.systems.game_stats import GameStats
from ui.narration import (
    prompt_negotiation_response,
    show_bribe_accepted,
    show_bribe_offer,
    show_bribe_rejected,
    show_merchant_gives_up,
    show_merchant_refuses,
    show_threat,
)


def run_negotiation(
    sheriff: Sheriff,
    merchant: Merchant,
    actual_goods: list[Good],
    stats: GameStats = None,
) -> bool:
    """Run the negotiation phase. Returns True if sheriff should inspect, False if bribed.

    Args:
        sheriff: Sheriff object with authority and reputation
        merchant: Merchant object being negotiated with
        actual_goods: List of goods in the merchant's bag
        stats: Optional GameStats object for tracking

    Returns:
        bool: True if sheriff should inspect, False if bribe was accepted
    """
    # Get game state for recording events
    get_game_master_state()

    show_threat(merchant)

    # Calculate contraband value for merchant's decision-making
    contraband_value = sum(g.value for g in actual_goods if not g.is_legal())

    # Merchant decides whether to offer bribe or refuse
    outcome = initiate_threat(merchant, contraband_value, sheriff.authority)

    if outcome == "refuse":
        show_merchant_refuses(merchant)
        return True  # Inspect

    # Merchant offers a bribe
    bribe_amount = outcome  # initiate_threat returns bribe amount
    round_number = 1
    show_bribe_offer(merchant, bribe_amount, round_number)

    # Negotiation loop
    while True:
        # Sheriff responds to bribe
        choice, demand_amount = prompt_negotiation_response(bribe_amount)

        if choice == "accept":
            # Sheriff accepts the bribe
            sheriff_respond_to_bribe(sheriff, merchant, bribe_amount, stats)
            show_bribe_accepted(merchant, bribe_amount)
            return False  # Don't inspect

        elif choice == "reject":
            # Sheriff rejects the bribe
            show_bribe_rejected(merchant)
            return True  # Inspect

        elif choice == "counter":
            # Sheriff demands more gold
            round_number += 1

            # Merchant decides whether to accept the counter-demand
            accepts = merchant.should_accept_counter(
                sheriff_demand=demand_amount,
                original_offer=bribe_amount,
                goods_value=contraband_value,
            )

            if accepts:
                # Merchant accepts the counter-offer
                sheriff_respond_to_bribe(sheriff, merchant, demand_amount, stats)
                show_bribe_accepted(merchant, demand_amount)
                return False  # Don't inspect
            else:
                # Merchant refuses and gives up
                show_merchant_gives_up(merchant)
                return True  # Inspect
