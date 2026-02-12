"""
Declaration Builder - Consolidated Declaration Creation

This module provides reusable functions for building merchant declarations.
All strategy modules should use these functions to avoid code duplication.

Provides 5 core declaration types:
1. Honest - Declare and carry the same legal goods
2. Legal Lie - Declare one legal good, carry different legal goods
3. Mixed - Declare legal, carry mostly legal + 1 contraband
4. Contraband Low - Declare legal, carry 1-2 contraband items
5. Contraband High - Declare legal, carry 3-5 high-value contraband
"""

import random

from core.constants import BAG_SIZE_LIMIT
from core.mechanics.goods import ALL_CONTRABAND, ALL_LEGAL


def _find_most_common_good(goods: list, counts: dict) -> tuple[str, int]:
    """
    Helper function to find the most common good in a list.

    Args:
        goods: List of Good objects
        counts: Dict of good_id -> count from analyze_hand()

    Returns:
        tuple: (most_common_good_id, count)
    """
    if not goods or not counts:
        return None, 0

    # Filter counts to only include goods in the provided list
    good_ids = {g.id for g in goods}
    filtered_counts = {gid: count for gid, count in counts.items() if gid in good_ids}

    if not filtered_counts:
        return None, 0

    most_common_id = max(filtered_counts, key=filtered_counts.get)
    most_common_count = filtered_counts[most_common_id]

    return most_common_id, most_common_count


def build_honest_declaration(available_goods: dict = None) -> dict:
    """
    Strategy 1: All Legal (Honest)
    Risk: 0/10, Reward: 0

    Declare and carry the same legal goods.
    If available_goods is provided, choose from hand. Otherwise, choose any legal goods.
    """
    if available_goods and available_goods.get("legal"):
        # Choose from available legal goods in hand
        legal_in_hand = available_goods["legal"]
        if legal_in_hand:
            # Pick the most common legal good in hand
            counts = available_goods.get("counts", {})
            legal_ids = [g.id for g in legal_in_hand]
            # Sort by count (most common first)
            legal_ids_sorted = sorted(
                set(legal_ids), key=lambda gid: counts.get(gid, 0), reverse=True
            )
            declared = legal_ids_sorted[0]
            # Count how many we have
            available_count = counts.get(declared, 0)
            count = min(available_count, BAG_SIZE_LIMIT)
        else:
            # No legal goods in hand, fall back to any legal
            declared = random.choice([g.id for g in ALL_LEGAL])
            count = min(random.randint(2, 4), BAG_SIZE_LIMIT)
    else:
        # No hand constraint - choose any legal goods
        declared = random.choice([g.id for g in ALL_LEGAL])
        count = min(random.randint(2, 4), BAG_SIZE_LIMIT)

    return {
        "declared_id": declared,
        "count": count,
        "actual_ids": [declared] * count,
        "lie": False,
        "lie_type": "none",
        "strategy": "honest",
    }


def build_legal_lie_declaration(
    available_goods: dict = None, risk_tolerance: int = 5
) -> dict:
    """
    Strategy 2: All Legal (Lie about Mix)
    Risk: 3/10, Reward: 5-14 gold

    Declare homogeneous bag, carry mixed bag with different-value legal items.

    Strategy: Declare the most common legal good in hand, but actually carry
    different legal goods based on risk tolerance.

    Risk Tolerance:
    - Low risk (0-3): Carry LOWER-value legal goods (small penalty if caught)
    - Medium risk (4-6): Carry SIMILAR-value legal goods (moderate penalty)
    - High risk (7-10): Carry HIGHER-value legal goods (maximize profit, higher penalty)

    Examples:
    - Low risk: Declare "4x Chicken", Carry "3x Apple + 1x Cheese" (lower value, safer)
    - High risk: Declare "4x Apple", Carry "3x Chicken + 1x Cheese" (higher value, riskier)

    Args:
        available_goods: Dict with 'legal', 'contraband', 'counts' from analyze_hand()
        risk_tolerance: Merchant's risk tolerance (0-10)
    """
    if available_goods:
        # Use actual hand to make smart decisions
        legal_goods = available_goods.get("legal", [])
        counts = available_goods.get("counts", {})

        if legal_goods and counts:
            # Find the most common legal good in hand using helper function
            most_common_id, most_common_count = _find_most_common_good(
                legal_goods, counts
            )

            if most_common_id:
                # Declare 2-4 of the most common good (or however many we have)
                declare_count = min(
                    random.randint(2, 4), most_common_count + 1, BAG_SIZE_LIMIT
                )

                # Select goods to carry based on risk tolerance
                if risk_tolerance <= 3:
                    # LOW RISK: Carry lower-value legal goods (small penalty if caught)
                    legal_by_value = sorted(
                        legal_goods, key=lambda g: g.value
                    )  # Ascending
                    actual_goods = legal_by_value[:declare_count]
                elif risk_tolerance >= 7:
                    # HIGH RISK: Carry higher-value legal goods (maximize profit)
                    legal_by_value = sorted(
                        legal_goods, key=lambda g: g.value, reverse=True
                    )  # Descending
                    actual_goods = legal_by_value[:declare_count]
                else:
                    # MEDIUM RISK: Carry mix of values (balanced approach)
                    legal_by_value = sorted(legal_goods, key=lambda g: g.value)
                    # Take from middle of the value range
                    mid_start = len(legal_by_value) // 3
                    mid_goods = legal_by_value[mid_start:]
                    actual_goods = mid_goods[:declare_count]

                actual_ids = [g.id for g in actual_goods]

                return {
                    "declared_id": most_common_id,
                    "count": declare_count,
                    "actual_ids": actual_ids,
                    "lie": True,
                    "lie_type": "legal",
                    "strategy": "legal_lie",
                    "risk_level": "low"
                    if risk_tolerance <= 3
                    else "high"
                    if risk_tolerance >= 7
                    else "medium",
                }

    # Fallback: If no available_goods provided, use old random logic
    legal_by_value = sorted(ALL_LEGAL, key=lambda g: g.value)

    # Declare low-to-mid value good
    declared = random.choice([g.id for g in legal_by_value[: len(legal_by_value) // 2]])
    count = min(random.randint(2, 4), BAG_SIZE_LIMIT)

    # Carry higher-value legal goods
    high_value_good = random.choice(legal_by_value[len(legal_by_value) // 2 :])
    actual_ids = [high_value_good.id] * count

    return {
        "declared_id": declared,
        "count": count,
        "actual_ids": actual_ids,
        "lie": True,
        "lie_type": "legal",
        "strategy": "legal_lie",
    }


def build_mixed_declaration(available_goods: dict = None) -> dict:
    """
    Strategy 3: Mostly Legal + Low Contraband
    Risk: 6/10, Reward: 15-30 gold

    Declare the most common legal good in hand, carry mostly legal + 1 low-value contraband.

    Strategy: Declare what you have most of (believable!), but sneak in 1 contraband.

    Example:
    - Hand: 3x Cheese, 2x Apple, 1x Silk (contraband)
    - Declare: "4x Cheese" (most common legal good)
    - Carry: "2x Cheese + 1x Apple + 1x Silk" (mostly legal + 1 contraband)
    """
    if available_goods:
        # Use actual hand to make smart decisions
        legal_goods = available_goods.get("legal", [])
        contraband_goods = available_goods.get("contraband", [])
        counts = available_goods.get("counts", {})

        if legal_goods and contraband_goods and counts:
            # Find the most common legal good in hand
            most_common_id, most_common_count = _find_most_common_good(
                legal_goods, counts
            )

            if most_common_id and most_common_count >= 2:
                # Declare 3-4 of the most common legal good
                declare_count = min(
                    random.randint(3, 4), most_common_count + 1, BAG_SIZE_LIMIT
                )

                # Carry mostly legal goods + 1 low-value contraband
                # Sort contraband by value and pick a low-value one
                contraband_by_value = sorted(contraband_goods, key=lambda g: g.value)
                low_contraband = contraband_by_value[0]  # Lowest value contraband

                # Fill rest with legal goods (prefer higher value for profit)
                legal_by_value = sorted(
                    legal_goods, key=lambda g: g.value, reverse=True
                )
                num_legal = declare_count - 1
                legal_to_carry = legal_by_value[:num_legal]

                actual_ids = [g.id for g in legal_to_carry] + [low_contraband.id]

                return {
                    "declared_id": most_common_id,
                    "count": declare_count,
                    "actual_ids": actual_ids,
                    "lie": True,
                    "lie_type": "mixed",
                    "strategy": "mixed",
                }

    # Fallback: If no available_goods provided, use old random logic
    legal_by_value = sorted(ALL_LEGAL, key=lambda g: g.value)
    contraband_by_value = sorted(ALL_CONTRABAND, key=lambda g: g.value)

    # Declare legal good
    declared = random.choice([g.id for g in legal_by_value])
    count = min(random.randint(3, 4), BAG_SIZE_LIMIT)

    # Carry mostly legal + 1 low-value contraband
    low_contraband = random.choice(contraband_by_value[: len(contraband_by_value) // 2])
    legal_good = random.choice(legal_by_value)

    actual_ids = [legal_good.id] * (count - 1) + [low_contraband.id]

    return {
        "declared_id": declared,
        "count": count,
        "actual_ids": actual_ids,
        "lie": True,
        "lie_type": "mixed",
        "strategy": "mixed",
    }


def build_contraband_low_declaration(available_goods: dict = None) -> dict:
    """
    Strategy 4: All Contraband (1-2 items)
    Risk: 8/10, Reward: 40-80 gold

    Declare legal goods, carry 1-2 contraband items.

    Example:
    - Declare: "2x Cheese"
    - Carry: "2x Weapons (contraband)"
    """
    legal_by_value = sorted(ALL_LEGAL, key=lambda g: g.value)
    contraband_by_value = sorted(ALL_CONTRABAND, key=lambda g: g.value)

    # Declare legal good
    declared = random.choice([g.id for g in legal_by_value])
    count = min(random.randint(2, 3), BAG_SIZE_LIMIT)

    # Carry mid-value contraband
    contraband = random.choice(contraband_by_value[len(contraband_by_value) // 3 :])
    actual_ids = [contraband.id] * count

    return {
        "declared_id": declared,
        "count": count,
        "actual_ids": actual_ids,
        "lie": True,
        "lie_type": "contraband",
        "strategy": "contraband_low",
    }


def build_contraband_high_declaration(available_goods: dict = None) -> dict:
    """
    Strategy 5: All Contraband (3-5 high-value items) - EXTREME RISK
    Risk: 10/10, Reward: 100-250 gold

    Declare legal goods, carry 3-5 high-value contraband items.
    This is a desperate or extremely bold move.

    Example:
    - Declare: "5x Cheese"
    - Carry: "5x Silk (high-value contraband)"
    """
    legal_by_value = sorted(ALL_LEGAL, key=lambda g: g.value)
    contraband_by_value = sorted(ALL_CONTRABAND, key=lambda g: g.value)

    # Declare low-value legal good (to keep bribe expectations lower)
    declared_good = random.choice(legal_by_value[: len(legal_by_value) // 2])
    declared = declared_good.id
    count = min(random.randint(3, 5), BAG_SIZE_LIMIT)

    # Carry high-value contraband
    contraband = random.choice(contraband_by_value[len(contraband_by_value) // 2 :])
    actual_ids = [contraband.id] * count

    return {
        "declared_id": declared,
        "count": count,
        "actual_ids": actual_ids,
        "lie": True,
        "lie_type": "contraband",
        "strategy": "contraband_high",
    }


# Strategy name to builder function mapping
STRATEGY_BUILDERS = {
    "honest": build_honest_declaration,
    "legal_lie": build_legal_lie_declaration,
    "mixed": build_mixed_declaration,
    "contraband_low": build_contraband_low_declaration,
    "contraband_high": build_contraband_high_declaration,
    "contraband_all_in": build_contraband_high_declaration,  # Alias
}


def build_declaration(
    strategy_type: str, available_goods: dict = None, risk_tolerance: int = 5
) -> dict:
    """
    Build a declaration based on strategy type and available goods.

    Args:
        strategy_type: One of 'honest', 'legal_lie', 'mixed',
                      'contraband_low', 'contraband_high'
        available_goods: Optional dict with 'legal', 'contraband', 'counts' from analyze_hand()
                        If None, merchant can choose any goods (unlimited selection)
        risk_tolerance: Merchant's risk tolerance (0-10), affects legal_lie strategy

    Returns:
        dict with declared_id, count, actual_ids, lie, lie_type, strategy
    """
    builder = STRATEGY_BUILDERS.get(strategy_type, build_honest_declaration)

    # If available_goods is provided, pass it to the builder
    if available_goods is not None:
        # For legal_lie strategy, pass risk_tolerance parameter
        if strategy_type == "legal_lie":
            return builder(available_goods, risk_tolerance)
        else:
            return builder(available_goods)
    else:
        # No hand constraint - merchant can choose any goods
        # For legal_lie strategy, still pass risk_tolerance
        if strategy_type == "legal_lie":
            return builder(None, risk_tolerance)
        else:
            return builder()
