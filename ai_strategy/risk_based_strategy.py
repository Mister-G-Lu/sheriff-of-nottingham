"""
Risk-Based Merchant Strategy Framework

This module implements a comprehensive risk-based decision system for merchants,
considering their risk tolerance and the current environment.

RISK LEVELS (from safest to riskiest):
========================================

1. ALL LEGAL (Honest) - Risk Level: 0/10
   - Declare: "3x Cheese"
   - Carry: "3x Cheese"
   - Risk: None
   - Reward: None
   - Best for: Very risk-averse, honest merchants

2. ALL LEGAL (Lie about Mix) - Risk Level: 3/10
   - Declare: "3x Cheese"
   - Carry: "2x Cheese + 1x Mead"
   - Risk: Low (only lose goods if caught)
   - Reward: Moderate (5-14 gold profit)
   - Best for: Risk-averse, cautious merchants

3. MOSTLY LEGAL + LOW CONTRABAND - Risk Level: 6/10
   - Declare: "3x Cheese"
   - Carry: "2x Cheese + 1x Silk (contraband)"
   - Risk: Moderate (contraband penalty if caught)
   - Reward: Good (15-30 gold profit)
   - Best for: Moderate risk tolerance

4. ALL CONTRABAND (1-2 items) - Risk Level: 8/10
   - Declare: "2x Cheese"
   - Carry: "2x Weapons (contraband)"
   - Risk: High (major penalty if caught)
   - Reward: High (40-80 gold profit)
   - Best for: Bold, risk-taking merchants

5. ALL CONTRABAND (3-5 items) - Risk Level: 10/10
   - Declare: "5x Cheese"
   - Carry: "5x Silk (contraband)"
   - Risk: Extreme (massive penalty, huge bribe)
   - Reward: Extreme (100-250 gold profit)
   - Best for: Desperate or extremely bold merchants (rare)

DECISION FRAMEWORK:
===================
Merchants choose strategy based on:
1. Personal risk tolerance (0-10)
2. Greed level (0-10)
3. Honesty bias (0-10)
4. Sheriff's catch rate (0-100%)
5. Current reputation/desperation
"""

import random
from core.mechanics.goods import ALL_LEGAL, ALL_CONTRABAND, GOOD_BY_ID


def calculate_risk_score(merchant_personality: dict, sheriff_catch_rate: float) -> int:
    """
    Calculate merchant's current risk tolerance score (0-10).
    
    Higher score = willing to take more risk
    
    Args:
        merchant_personality: Dict with risk_tolerance, greed, honesty_bias
        sheriff_catch_rate: % of smugglers caught (0.0 to 1.0)
        
    Returns:
        int: Risk score 0-10 (0=very cautious, 10=extremely bold)
    """
    base_risk = merchant_personality.get('risk_tolerance', 5)
    greed = merchant_personality.get('greed', 5)
    honesty = merchant_personality.get('honesty_bias', 5)
    
    # Start with base risk tolerance
    risk_score = base_risk
    
    # Greed increases risk-taking (+0 to +2)
    if greed > 7:
        risk_score += 2
    elif greed > 5:
        risk_score += 1
    
    # Honesty decreases risk-taking (-0 to -3)
    if honesty > 7:
        risk_score -= 3
    elif honesty > 5:
        risk_score -= 1
    
    # Sheriff's catch rate affects risk-taking
    if sheriff_catch_rate > 0.7:
        risk_score -= 3  # Very dangerous, reduce risk
    elif sheriff_catch_rate > 0.5:
        risk_score -= 1  # Somewhat dangerous
    elif sheriff_catch_rate < 0.3:
        risk_score += 2  # Very safe, increase risk
    
    return max(0, min(10, risk_score))


def choose_strategy_by_risk(risk_score: int, sheriff_catch_rate: float) -> str:
    """
    Choose which strategy to use based on risk score.
    
    Args:
        risk_score: Merchant's risk tolerance (0-10)
        sheriff_catch_rate: % of smugglers caught
        
    Returns:
        str: Strategy name ('honest', 'legal_lie', 'mixed', 'contraband_low', 'contraband_all_in')
    """
    # Add randomness to make it less predictable
    adjusted_risk = risk_score + random.uniform(-1, 1)
    
    if adjusted_risk <= 2:
        # Very risk-averse: honest or legal lie
        return 'honest' if random.random() < 0.7 else 'legal_lie'
    
    elif adjusted_risk <= 4:
        # Risk-averse: mostly legal lie, sometimes honest
        return 'legal_lie' if random.random() < 0.8 else 'honest'
    
    elif adjusted_risk <= 6:
        # Moderate: legal lie or mixed bag
        return 'legal_lie' if random.random() < 0.6 else 'mixed'
    
    elif adjusted_risk <= 8:
        # Bold: mixed or low contraband
        return 'mixed' if random.random() < 0.5 else 'contraband_low'
    
    else:
        # Very bold: contraband (low or all-in)
        # All-in is rare (10% chance) unless desperate
        if random.random() < 0.1 and sheriff_catch_rate < 0.4:
            return 'contraband_all_in'
        else:
            return 'contraband_low'


def create_honest_declaration() -> dict:
    """
    Strategy 1: All Legal (Honest)
    Risk: 0/10, Reward: 0
    Maximum bag size: 6 items
    """
    from core.game.game_rules import BAG_SIZE_LIMIT
    
    legal_by_value = sorted(ALL_LEGAL, key=lambda g: g.value)
    # Choose mid-value goods
    declared_good = random.choice(legal_by_value[len(legal_by_value)//3:])
    count = min(random.randint(2, 4), BAG_SIZE_LIMIT)
    
    return {
        "declared_id": declared_good.id,
        "count": count,
        "actual_ids": [declared_good.id] * count,
        "lie": False,
        "lie_type": "none",
        "strategy": "honest"
    }


def create_legal_lie_declaration() -> dict:
    """
    Strategy 2: All Legal (Lie about Mix)
    Risk: 3/10, Reward: 5-14 gold
    
    Declare homogeneous bag, carry mixed bag with higher-value items.
    """
    from ai_strategy.legal_goods_strategy import choose_legal_goods_lie
    result = choose_legal_goods_lie()
    result['strategy'] = 'legal_lie'
    return result


def create_mixed_declaration() -> dict:
    """
    Strategy 3: Mostly Legal + Low Contraband
    Risk: 6/10, Reward: 15-30 gold
    Maximum bag size: 6 items
    
    Declare legal goods, carry mostly legal + 1 low-value contraband.
    """
    from core.game.game_rules import BAG_SIZE_LIMIT
    
    legal_by_value = sorted(ALL_LEGAL, key=lambda g: g.value)
    contraband_by_value = sorted(ALL_CONTRABAND, key=lambda g: g.value)
    
    # Declare mid-value legal goods
    declared_good = random.choice(legal_by_value[len(legal_by_value)//3:])
    count = min(random.randint(3, 4), BAG_SIZE_LIMIT)
    
    # Carry mostly legal + 1 low-value contraband
    num_legal = count - 1
    num_contraband = 1
    
    # Choose low-value contraband (bottom 40%)
    contraband_good = random.choice(contraband_by_value[:max(1, len(contraband_by_value)*2//5)])
    
    actual_ids = [declared_good.id] * num_legal + [contraband_good.id] * num_contraband
    
    return {
        "declared_id": declared_good.id,
        "count": count,
        "actual_ids": actual_ids,
        "lie": True,
        "lie_type": "mixed",
        "strategy": "mixed"
    }


def create_contraband_low_declaration() -> dict:
    """
    Strategy 4: All Contraband (1-2 items)
    Risk: 8/10, Reward: 40-80 gold
    Maximum bag size: 6 items
    
    Declare legal goods, carry 1-2 contraband items.
    """
    from core.game.game_rules import BAG_SIZE_LIMIT
    
    legal_by_value = sorted(ALL_LEGAL, key=lambda g: g.value)
    contraband_by_value = sorted(ALL_CONTRABAND, key=lambda g: g.value)
    
    # Declare legal goods
    declared_good = random.choice(legal_by_value)
    count = min(random.randint(1, 2), BAG_SIZE_LIMIT)
    
    # Carry mid-to-high value contraband
    contraband_good = random.choice(contraband_by_value[len(contraband_by_value)//2:])
    
    actual_ids = [contraband_good.id] * count
    
    return {
        "declared_id": declared_good.id,
        "count": count,
        "actual_ids": actual_ids,
        "lie": True,
        "lie_type": "contraband",
        "strategy": "contraband_low"
    }


def create_contraband_all_in_declaration() -> dict:
    """
    Strategy 5: All Contraband (3-6 items) - EXTREME RISK
    Risk: 10/10, Reward: 100-250 gold
    Maximum bag size: 6 items
    
    Declare legal goods, carry 3-6 high-value contraband items.
    This is a desperate or extremely bold move.
    """
    from core.game.game_rules import BAG_SIZE_LIMIT
    
    legal_by_value = sorted(ALL_LEGAL, key=lambda g: g.value)
    contraband_by_value = sorted(ALL_CONTRABAND, key=lambda g: g.value)
    
    # Declare legal goods (low value to keep bribe lower)
    declared_good = random.choice(legal_by_value[:len(legal_by_value)//2])
    count = min(random.randint(3, 5), BAG_SIZE_LIMIT)
    
    # Carry high-value contraband (top 40%)
    contraband_good = random.choice(contraband_by_value[len(contraband_by_value)*3//5:])
    
    actual_ids = [contraband_good.id] * count
    
    return {
        "declared_id": declared_good.id,
        "count": count,
        "actual_ids": actual_ids,
        "lie": True,
        "lie_type": "contraband",
        "strategy": "contraband_all_in"
    }


def choose_merchant_strategy(merchant_personality: dict, sheriff_catch_rate: float = 0.5) -> dict:
    """
    Main entry point: Choose merchant strategy based on risk assessment.
    
    This is the function that should be called by merchants to decide what to do.
    
    Args:
        merchant_personality: Dict with risk_tolerance, greed, honesty_bias
        sheriff_catch_rate: % of smugglers caught (0.0 to 1.0)
        
    Returns:
        dict: Declaration with declared_id, count, actual_ids, lie, strategy
    """
    # Calculate risk score
    risk_score = calculate_risk_score(merchant_personality, sheriff_catch_rate)
    
    # Choose strategy based on risk
    strategy = choose_strategy_by_risk(risk_score, sheriff_catch_rate)
    
    # Execute chosen strategy
    if strategy == 'honest':
        return create_honest_declaration()
    elif strategy == 'legal_lie':
        return create_legal_lie_declaration()
    elif strategy == 'mixed':
        return create_mixed_declaration()
    elif strategy == 'contraband_low':
        return create_contraband_low_declaration()
    elif strategy == 'contraband_all_in':
        return create_contraband_all_in_declaration()
    else:
        # Fallback to honest
        return create_honest_declaration()


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
        "contraband_all_in": {
            "risk_level": 10,
            "reward_range": "100-250 gold",
            "description": "3-5 high-value contraband items (EXTREME)",
            "best_for": "Desperate or extremely bold merchants (rare)"
        }
    }
