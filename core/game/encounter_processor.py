"""
Encounter Processor - Handles individual merchant encounters
Extracted from game_manager.py for better separation of concerns
"""

from core.game.decision_handling import update_stats_bar
from core.game.inspection_display import show_tell
from core.game.merchant_encounter import run_negotiation
from core.mechanics.bag_builder import build_bag_and_declaration, choose_tell
from core.mechanics.goods import GOOD_BY_ID
from core.systems.reputation import update_sheriff_reputation
from ui.narration import (
    narrate_arrival,
    prompt_initial_decision,
    show_declaration,
    show_proactive_bribe,
)


def setup_merchant_encounter(merchant, sheriff, encounter_history):
    """
    Setup a merchant encounter: arrival, bag building, declaration.

    Returns:
        tuple: (declaration, actual_goods, is_honest, tell)
    """
    # Merchant arrives
    narrate_arrival(merchant)

    # Build bag and declaration using merchant's strategy
    declaration, actual_goods, is_honest = build_bag_and_declaration(
        merchant, encounter_history
    )

    # Show tell
    tell = choose_tell(merchant, is_honest)
    if tell:
        show_tell(tell)
        print()

    show_declaration(merchant, declaration)

    return declaration, actual_goods, is_honest, tell


def handle_proactive_bribe_offer(
    merchant, sheriff, actual_goods, declaration, is_honest
):
    """
    Check if merchant offers proactive bribe and handle the offer.

    Returns:
        tuple: (offers_proactive, proactive_bribe_amount)
    """
    declared_goods = [GOOD_BY_ID[declaration.good_id]] * declaration.count

    offers_proactive = merchant.should_offer_proactive_bribe(
        sheriff.authority, sheriff.reputation, actual_goods, declared_goods
    )

    proactive_bribe_amount = 0
    if offers_proactive:
        proactive_bribe_amount = merchant.calculate_proactive_bribe(
            actual_goods, not is_honest, sheriff.authority, declared_goods
        )
        show_proactive_bribe(merchant, proactive_bribe_amount, not is_honest)

    return offers_proactive, proactive_bribe_amount


def execute_player_decision(
    decision,
    merchant,
    sheriff,
    stats,
    actual_goods,
    declaration,
    proactive_bribe_amount,
    process_proactive_bribe_fn,
    process_pass_fn,
    process_inspection_fn,
    idx,
    total_merchants,
):
    """
    Execute the player's decision and return encounter results.

    Args:
        decision: Player's choice ('accept', 'pass', 'inspect', 'threaten')
        merchant: Merchant instance
        sheriff: Sheriff instance
        stats: GameStats instance
        actual_goods: List of actual goods in bag
        declaration: Declaration object
        proactive_bribe_amount: Amount of proactive bribe offered
        process_proactive_bribe_fn: Function to process proactive bribe
        process_pass_fn: Function to process passing without inspection
        process_inspection_fn: Function to process inspection
        idx: Current merchant index
        total_merchants: Total number of merchants

    Returns:
        tuple: (was_opened, was_honest, caught_lie, bribe_info)
    """
    was_opened = False
    caught_lie = False
    bribe_info = {"amount": 0, "accepted": False, "proactive": False}

    if decision == "accept":
        # Accept proactive bribe
        process_proactive_bribe_fn(
            merchant, proactive_bribe_amount, sheriff, stats, idx, total_merchants
        )
        was_honest, caught_lie = process_pass_fn(
            merchant, actual_goods, declaration, stats
        )
        bribe_info = {
            "amount": proactive_bribe_amount,
            "accepted": True,
            "proactive": True,
        }

    elif decision == "pass":
        # Let them pass without inspection
        was_honest, caught_lie = process_pass_fn(
            merchant, actual_goods, declaration, stats
        )
        update_sheriff_reputation(sheriff, False, was_honest, stats, actual_goods)

    elif decision == "inspect":
        # Inspect immediately (no negotiation)
        was_honest, caught_lie = process_inspection_fn(
            merchant, actual_goods, declaration, sheriff, stats
        )
        was_opened = True

    elif decision == "threaten":
        # Threaten inspection (may trigger negotiation)
        should_inspect = run_negotiation(sheriff, merchant, actual_goods, stats)

        if should_inspect:
            # Inspect the bag
            was_honest, caught_lie = process_inspection_fn(
                merchant, actual_goods, declaration, sheriff, stats
            )
            was_opened = True
        else:
            # Bribe accepted during negotiation
            was_honest, caught_lie = process_pass_fn(
                merchant, actual_goods, declaration, stats
            )

    return was_opened, was_honest, caught_lie, bribe_info


def process_single_merchant(
    merchant,
    sheriff,
    stats,
    encounter_history,
    idx,
    total_merchants,
    process_proactive_bribe_fn,
    process_pass_fn,
    process_inspection_fn,
):
    """
    Process a complete merchant encounter from arrival to completion.

    Args:
        merchant: Merchant instance
        sheriff: Sheriff instance
        stats: GameStats instance
        encounter_history: List of previous encounters
        idx: Current merchant index (1-based)
        total_merchants: Total number of merchants
        process_proactive_bribe_fn: Function to process proactive bribe
        process_pass_fn: Function to process passing without inspection
        process_inspection_fn: Function to process inspection

    Returns:
        dict: Encounter result with keys: declaration, actual_goods, was_opened, was_honest, caught_lie, bribe_info
    """
    # Update stats bar
    update_stats_bar(sheriff, stats, idx, total_merchants)

    # Setup encounter
    declaration, actual_goods, is_honest, tell = setup_merchant_encounter(
        merchant, sheriff, encounter_history
    )

    # Handle proactive bribe offer
    offers_proactive, proactive_bribe_amount = handle_proactive_bribe_offer(
        merchant, sheriff, actual_goods, declaration, is_honest
    )

    # Get player decision
    decision = prompt_initial_decision(offers_proactive, proactive_bribe_amount)

    # Execute decision
    was_opened, was_honest, caught_lie, bribe_info = execute_player_decision(
        decision,
        merchant,
        sheriff,
        stats,
        actual_goods,
        declaration,
        proactive_bribe_amount,
        process_proactive_bribe_fn,
        process_pass_fn,
        process_inspection_fn,
        idx,
        total_merchants,
    )

    return {
        "declaration": declaration,
        "actual_goods": actual_goods,
        "was_opened": was_opened,
        "was_honest": was_honest,
        "caught_lie": caught_lie,
        "bribe_info": bribe_info,
    }
