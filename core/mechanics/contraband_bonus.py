"""
Contraband Set Bonus System

Smuggling multiple of the same contraband type gives bonus multipliers:
- 2 of same type: 1.5x payout
- 3 of same type: 2x payout
- 4 of same type: 3x payout
- 5 of same type: 5x payout

This rewards specialization and creates interesting strategic decisions.
"""

from core.mechanics.goods import Good

# Contraband set bonus multipliers
CONTRABAND_BONUS_MULTIPLIERS = {
    1: 1.0,
    2: 1.5,
    3: 2.0,
    4: 2.5,
    5: 3.0,
}


def calculate_contraband_bonus(goods: list[Good]) -> dict:
    """
    Calculate the total value of goods including contraband set bonuses.

    Args:
        goods: List of Good objects

    Returns:
        dict with:
            - 'base_value': Total value without bonuses
            - 'bonus_value': Total value with bonuses applied
            - 'bonus_amount': Extra gold from bonuses
            - 'sets': Dict of contraband_id -> (count, multiplier, bonus_value)
    """
    # Separate legal and contraband
    legal_goods = [g for g in goods if g.is_legal()]
    contraband_goods = [g for g in goods if g.is_contraband()]

    # Calculate legal goods value (no bonuses)
    legal_value = sum(g.value for g in legal_goods)

    # Count contraband by type
    contraband_counts = {}
    for good in contraband_goods:
        contraband_counts[good.id] = contraband_counts.get(good.id, 0) + 1

    # Calculate contraband value with bonuses
    contraband_base_value = sum(g.value for g in contraband_goods)
    contraband_bonus_value = 0
    contraband_sets = {}

    for contraband_id, count in contraband_counts.items():
        # Get the good to find its base value
        good = next(g for g in contraband_goods if g.id == contraband_id)
        base_value = good.value * count

        # Apply multiplier based on count
        multiplier = CONTRABAND_BONUS_MULTIPLIERS.get(count, 1.0)
        bonus_value = int(base_value * multiplier)

        contraband_bonus_value += bonus_value
        contraband_sets[contraband_id] = {
            "count": count,
            "multiplier": multiplier,
            "base_value": base_value,
            "bonus_value": bonus_value,
            "bonus_amount": bonus_value - base_value,
        }

    # Total values
    base_value = legal_value + contraband_base_value
    bonus_value = legal_value + contraband_bonus_value
    bonus_amount = bonus_value - base_value

    return {
        "base_value": base_value,
        "bonus_value": bonus_value,
        "bonus_amount": bonus_amount,
        "legal_value": legal_value,
        "contraband_base_value": contraband_base_value,
        "contraband_bonus_value": contraband_bonus_value,
        "sets": contraband_sets,
    }


def get_best_contraband_for_set(contraband_goods: list[Good]) -> tuple[str, int, int]:
    """
    Determine which contraband type would give the best set bonus.

    Prioritizes:
    1. Most common contraband (higher multiplier)
    2. Highest value contraband (if tied on count)

    Args:
        contraband_goods: List of contraband Good objects

    Returns:
        tuple: (best_contraband_id, current_count, potential_value_with_more)
    """
    if not contraband_goods:
        return None, 0, 0

    # Count contraband by type
    contraband_counts = {}
    contraband_values = {}

    for good in contraband_goods:
        contraband_counts[good.id] = contraband_counts.get(good.id, 0) + 1
        contraband_values[good.id] = good.value

    # Find the best contraband to collect more of
    # Priority: most common, then highest value
    best_id = max(
        contraband_counts.keys(),
        key=lambda cid: (contraband_counts[cid], contraband_values[cid]),
    )

    current_count = contraband_counts[best_id]
    base_value = contraband_values[best_id]

    # Calculate potential value if we get one more
    next_count = min(current_count + 1, 5)
    next_multiplier = CONTRABAND_BONUS_MULTIPLIERS.get(next_count, 1.0)
    potential_value = int(base_value * next_count * next_multiplier)

    return best_id, current_count, potential_value


def should_redraw_for_contraband_set(
    hand: list[Good], risk_tolerance: int, greed: int
) -> tuple[bool, int, str]:
    """
    Determine if a greedy merchant should redraw to complete a contraband set.

    Logic:
    - If merchant has 1-2 of the same contraband, they might redraw to get more
    - Higher greed + risk = more likely to redraw
    - Focuses on most common or most valuable contraband

    Args:
        hand: Current hand of Good objects
        risk_tolerance: Merchant's risk tolerance (0-10)
        greed: Merchant's greed level (0-10)

    Returns:
        tuple: (should_redraw, num_to_redraw, target_contraband_id)
    """
    from core.mechanics.deck import analyze_hand

    analysis = analyze_hand(hand)
    contraband_goods = analysis.get("contraband", [])
    legal_goods = analysis.get("legal", [])

    if not contraband_goods:
        return False, 0, None

    # Only greedy merchants (greed >= 6) consider set collection
    # High greed + high risk = strong desire to complete sets
    if greed < 6:
        return False, 0, None

    # Find the best contraband to collect
    best_contraband_id, current_count, potential_value = get_best_contraband_for_set(
        contraband_goods
    )

    if not best_contraband_id:
        return False, 0, None

    # Decision logic based on current count
    if current_count == 1:
        # Have 1 contraband - very greedy merchants (greed >= 8) might redraw
        if greed >= 8 and risk_tolerance >= 7:
            # Redraw 2-3 legal goods to try to get more of this contraband
            num_to_redraw = min(len(legal_goods), 3)
            return True, num_to_redraw, best_contraband_id

    elif current_count == 2:
        # Have 2 contraband (1.5x bonus) - greedy merchants want to reach 3 (2x bonus!)
        if greed >= 7 and risk_tolerance >= 6:
            # Redraw 1-2 legal goods
            num_to_redraw = min(len(legal_goods), 2)
            return True, num_to_redraw, best_contraband_id

    elif current_count == 3:
        # Have 3 contraband (2x bonus) - very greedy want to reach 4 (3x bonus!)
        if greed >= 9 and risk_tolerance >= 8:
            # Redraw 1 legal good
            num_to_redraw = min(len(legal_goods), 1)
            return True, num_to_redraw, best_contraband_id

    # Already have 4+ or not greedy enough
    return False, 0, None
