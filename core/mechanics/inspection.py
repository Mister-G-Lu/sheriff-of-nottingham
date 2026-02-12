"""
Inspection Logic
Handles bag inspection with proper Sheriff of Nottingham rules
"""

import random

from core.game.game_rules import (
    calculate_confiscation_penalty,
    separate_declared_and_undeclared,
)
from core.mechanics.goods import Good


def handle_inspection(
    merchant, actual_goods: list[Good], declaration: dict, sheriff
) -> dict:
    """
    Handle bag inspection with proper Sheriff of Nottingham rules.

    Rules:
    1. If merchant told the TRUTH:
       - All goods pass through (even though inspected)
       - Merchant keeps everything
       - Sheriff loses reputation for wrongly inspecting honest merchant

    2. If merchant LIED and got CAUGHT:
       - Separate declared (truthful) goods from undeclared goods
       - ALL undeclared goods are CONFISCATED (legal AND contraband)
       - Merchant pays Sheriff HALF the value of confiscated goods
       - Only truthfully declared goods pass through
       - Sheriff gains reputation

    Args:
        merchant: Merchant object with gold
        actual_goods: List of Good objects in the bag
        declaration: Dict with 'good_id' and 'count'
        sheriff: Sheriff object

    Returns:
        dict with keys:
            - 'was_honest': bool
            - 'caught_lie': bool
            - 'goods_passed': list[Good] - Goods that made it through
            - 'goods_confiscated': list[Good] - Goods that were confiscated
            - 'penalty_paid': int - Gold paid by merchant to sheriff
            - 'sheriff_gold_gained': int - Gold sheriff received
    """
    # Check if declaration matches reality
    declared_id = declaration["good_id"]
    declared_count = declaration["count"]

    # Separate declared goods from undeclared goods
    # This allows partial honesty (e.g., declaring 3 apples when you have 2 apples + 1 silk)
    declared_goods, undeclared_goods = separate_declared_and_undeclared(
        actual_goods, declaration
    )

    # Merchant is FULLY honest if bag exactly matches declaration
    is_fully_honest = len(actual_goods) == declared_count and all(
        g.id == declared_id for g in actual_goods
    )

    if is_fully_honest:
        # COMPLETELY HONEST: All goods pass through, no penalties
        return {
            "was_honest": True,
            "caught_lie": False,
            "goods_passed": actual_goods,
            "goods_confiscated": [],
            "penalty_paid": 0,
            "sheriff_gold_gained": 0,
        }

    # LIED (at least partially): Check if sheriff catches the lie
    # Sheriff rolls (1-10 + perception) vs Merchant's bluff (1-10 + bluff_skill)
    sheriff_roll = random.randint(1, 10) + sheriff.perception
    merchant_roll = merchant.roll_bluff()  # 1-10 + bluff_skill

    caught_lie = sheriff_roll >= merchant_roll

    if not caught_lie:
        # Merchant's bluff succeeded! All goods pass through undetected
        return {
            "was_honest": False,
            "caught_lie": False,
            "goods_passed": actual_goods,  # Everything passes!
            "goods_confiscated": [],
            "penalty_paid": 0,
            "sheriff_gold_gained": 0,
        }

    # Sheriff caught the lie! Apply penalties
    # Truthfully declared goods still pass, undeclared goods confiscated

    # Calculate penalty (50% of confiscated goods value)
    penalty = calculate_confiscation_penalty(undeclared_goods)

    # Merchant must pay penalty (if they have enough gold)
    actual_penalty = min(penalty, merchant.gold)
    merchant.gold -= actual_penalty

    # Sheriff receives the penalty payment
    sheriff_gold_gained = actual_penalty

    return {
        "was_honest": False,
        "caught_lie": True,
        "goods_passed": declared_goods,  # Only truthfully declared goods pass
        "goods_confiscated": undeclared_goods,  # ALL undeclared goods confiscated
        "penalty_paid": actual_penalty,
        "sheriff_gold_gained": sheriff_gold_gained,
    }


def handle_pass_without_inspection(
    merchant, actual_goods: list[Good], declaration: dict
) -> dict:
    """
    Handle merchant passing without inspection.

    Args:
        merchant: Merchant object
        actual_goods: List of Good objects in the bag
        declaration: Dict with 'good_id' and 'count'

    Returns:
        dict with inspection result info
    """
    # Check if they were honest
    declared_id = declaration["good_id"]
    declared_count = declaration["count"]

    is_honest = len(actual_goods) == declared_count and all(
        g.id == declared_id for g in actual_goods
    )

    # All goods pass through when not inspected
    return {
        "was_honest": is_honest,
        "caught_lie": False,  # Can't catch a lie if you don't inspect
        "goods_passed": actual_goods,
        "goods_confiscated": [],
        "penalty_paid": 0,
        "sheriff_gold_gained": 0,
    }
