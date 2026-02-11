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
from core.mechanics.goods import ALL_LEGAL, ALL_CONTRABAND, GOOD_BY_ID
from core.constants import HAND_SIZE_LIMIT, BAG_SIZE_LIMIT


def build_honest_declaration(available_goods: dict = None) -> dict:
    """
    Strategy 1: All Legal (Honest)
    Risk: 0/10, Reward: 0
    
    Declare and carry the same legal goods.
    If available_goods is provided, choose from hand. Otherwise, choose any legal goods.
    """
    if available_goods and available_goods.get('legal'):
        # Choose from available legal goods in hand
        legal_in_hand = available_goods['legal']
        if legal_in_hand:
            # Pick the most common legal good in hand
            counts = available_goods.get('counts', {})
            legal_ids = [g.id for g in legal_in_hand]
            # Sort by count (most common first)
            legal_ids_sorted = sorted(set(legal_ids), key=lambda gid: counts.get(gid, 0), reverse=True)
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
        'declared_id': declared,
        'count': count,
        'actual_ids': [declared] * count,
        'lie': False,
        'lie_type': 'none',
        'strategy': 'honest'
    }


def build_legal_lie_declaration(available_goods: dict = None) -> dict:
    """
    Strategy 2: All Legal (Lie about Mix)
    Risk: 3/10, Reward: 5-14 gold
    
    Declare homogeneous bag, carry mixed bag with higher-value legal items.
    
    Example:
    - Declare: "3x Cheese"
    - Carry: "2x Cheese + 1x Mead" (higher value)
    """
    legal_by_value = sorted(ALL_LEGAL, key=lambda g: g.value)
    
    # Declare low-to-mid value good
    declared = random.choice([g.id for g in legal_by_value[:len(legal_by_value)//2]])
    count = min(random.randint(2, 4), BAG_SIZE_LIMIT)
    
    # Carry higher-value legal goods
    high_value_good = random.choice(legal_by_value[len(legal_by_value)//2:])
    actual_ids = [high_value_good.id] * count
    
    return {
        'declared_id': declared,
        'count': count,
        'actual_ids': actual_ids,
        'lie': True,
        'lie_type': 'legal',
        'strategy': 'legal_lie'
    }


def build_mixed_declaration(available_goods: dict = None) -> dict:
    """
    Strategy 3: Mostly Legal + Low Contraband
    Risk: 6/10, Reward: 15-30 gold
    
    Declare legal goods, carry mostly legal + 1 low-value contraband.
    
    Example:
    - Declare: "3x Cheese"
    - Carry: "2x Cheese + 1x Silk (contraband)"
    """
    legal_by_value = sorted(ALL_LEGAL, key=lambda g: g.value)
    contraband_by_value = sorted(ALL_CONTRABAND, key=lambda g: g.value)
    
    # Declare legal good
    declared = random.choice([g.id for g in legal_by_value])
    count = min(random.randint(3, 4), BAG_SIZE_LIMIT)
    
    # Carry mostly legal + 1 low-value contraband
    low_contraband = random.choice(contraband_by_value[:len(contraband_by_value)//2])
    legal_good = random.choice(legal_by_value)
    
    actual_ids = [legal_good.id] * (count - 1) + [low_contraband.id]
    
    return {
        'declared_id': declared,
        'count': count,
        'actual_ids': actual_ids,
        'lie': True,
        'lie_type': 'mixed',
        'strategy': 'mixed'
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
    contraband = random.choice(contraband_by_value[len(contraband_by_value)//3:])
    actual_ids = [contraband.id] * count
    
    return {
        'declared_id': declared,
        'count': count,
        'actual_ids': actual_ids,
        'lie': True,
        'lie_type': 'contraband',
        'strategy': 'contraband_low'
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
    declared_good = random.choice(legal_by_value[:len(legal_by_value)//2])
    declared = declared_good.id
    count = min(random.randint(3, 5), BAG_SIZE_LIMIT)
    
    # Carry high-value contraband
    contraband = random.choice(contraband_by_value[len(contraband_by_value)//2:])
    actual_ids = [contraband.id] * count
    
    return {
        'declared_id': declared,
        'count': count,
        'actual_ids': actual_ids,
        'lie': True,
        'lie_type': 'contraband',
        'strategy': 'contraband_high'
    }


# Strategy name to builder function mapping
STRATEGY_BUILDERS = {
    'honest': build_honest_declaration,
    'legal_lie': build_legal_lie_declaration,
    'mixed': build_mixed_declaration,
    'contraband_low': build_contraband_low_declaration,
    'contraband_high': build_contraband_high_declaration,
    'contraband_all_in': build_contraband_high_declaration,  # Alias
}


def build_declaration(strategy_type: str, available_goods: dict = None) -> dict:
    """
    Build a declaration based on strategy type and available goods.
    
    Args:
        strategy_type: One of 'honest', 'legal_lie', 'mixed', 
                      'contraband_low', 'contraband_high'
        available_goods: Optional dict with 'legal', 'contraband', 'counts' from analyze_hand()
                        If None, merchant can choose any goods (unlimited selection)
    
    Returns:
        dict with declared_id, count, actual_ids, lie, lie_type, strategy
    """
    builder = STRATEGY_BUILDERS.get(strategy_type, build_honest_declaration)
    
    # If available_goods is provided, pass it to the builder
    if available_goods is not None:
        return builder(available_goods)
    else:
        # No hand constraint - merchant can choose any goods
        return builder()


def get_strategy_info() -> dict:
    """
    Return information about all available strategies.
    
    Useful for understanding the risk/reward tradeoffs.
    """
    return {
        "honest": {
            "risk_level": 0,
            "reward_range": "0 gold",
            "description": "Honest declaration, no lying",
            "best_for": "Very risk-averse, honest merchants"
        },
        "legal_lie": {
            "risk_level": 3,
            "reward_range": "5-14 gold",
            "description": "Declare homogeneous bag, carry mixed with higher-value items",
            "best_for": "Risk-averse, cautious merchants"
        },
        "mixed": {
            "risk_level": 6,
            "reward_range": "15-30 gold",
            "description": "Mostly legal goods + 1 low-value contraband",
            "best_for": "Moderate risk tolerance"
        },
        "contraband_low": {
            "risk_level": 8,
            "reward_range": "40-80 gold",
            "description": "1-2 contraband items only",
            "best_for": "Bold, risk-taking merchants"
        },
        "contraband_high": {
            "risk_level": 10,
            "reward_range": "100-250 gold",
            "description": "3-5 high-value contraband items (EXTREME)",
            "best_for": "Desperate or extremely bold merchants (rare)"
        }
    }
