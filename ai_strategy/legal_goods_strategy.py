"""
Legal Goods Lying Strategy

This module implements the sophisticated "lie about legal goods" strategy.

STRATEGIC INSIGHT:
==================
A clever merchant can lie about their legal goods mix to earn extra profit
with minimal risk:

1. Declare: "3x Cheese" (homogeneous, safe-looking)
2. Actually carry: "2x Cheese + 1x Mead" (mixed bag with higher-value item)
3. If caught: Only lose the goods (no contraband penalty)
4. If not caught: Sell the higher-value item for extra profit

The key: Honest merchants bring homogeneous bags (3x Cheese = 3x Cheese).
Lying merchants sneak in 1-2 higher-value items in a "safe" declared bag.

RISK/REWARD ANALYSIS:
=====================
- Risk: Low (no contraband, just lose legal goods if caught)
- Reward: Moderate (difference in value between declared and actual)
- Bribe cost: 110-130% of goods value (still profitable if not inspected often)
- Best when: Sheriff is moderately active (not too lenient, not too aggressive)

WHEN TO USE:
============
This strategy is optimal when:
1. Sheriff is catching some smugglers (contraband is too risky)
2. Sheriff isn't inspecting everyone (some chance to pass)
3. Merchant wants steady, safe profits
4. Building reputation without major risk

MERCHANT PERSONALITY FIT:
=========================
- Cautious merchants: Perfect fit (safe profit)
- Greedy merchants: Good fit (extra profit without major risk)
- Bold merchants: Less likely (prefer high-risk contraband)
- Honest merchants: Never (against their nature)
"""

import random
from core.mechanics.goods import ALL_LEGAL


def should_use_legal_goods_lie(merchant_personality: dict, sheriff_catch_rate: float = 0.5) -> bool:
    """
    Determine if a merchant should use the legal goods lying strategy.
    
    This strategy is appealing to cautious and greedy merchants when the
    environment is moderately risky (contraband is dangerous, but some lying works).
    
    Args:
        merchant_personality: Dict with 'risk_tolerance', 'greed', 'honesty_bias'
        sheriff_catch_rate: % of smugglers caught (0.0 to 1.0)
        
    Returns:
        bool: True if merchant should lie about legal goods
    """
    risk_tolerance = merchant_personality.get('risk_tolerance', 5)
    greed = merchant_personality.get('greed', 5)
    honesty_bias = merchant_personality.get('honesty_bias', 5)
    
    # Honest merchants (high honesty_bias) rarely use this strategy
    if honesty_bias > 7:
        return random.random() < 0.1  # 10% chance even for honest merchants
    
    # If sheriff is very lenient (<30% catch rate), go for contraband instead
    if sheriff_catch_rate < 0.3:
        return False  # Contraband is safer, more profitable
    
    # If sheriff is very aggressive (>70% catch rate), too risky even for legal lies
    if sheriff_catch_rate > 0.7:
        return random.random() < 0.2  # 20% chance (desperate for any profit)
    
    # Sweet spot: 30-70% catch rate - legal lying is optimal
    
    # Cautious merchants (low risk_tolerance) love this strategy
    if risk_tolerance < 4:
        return random.random() < 0.7  # 70% chance
    
    # Greedy merchants (high greed) like the extra profit
    if greed > 7:
        return random.random() < 0.6  # 60% chance
    
    # Moderate merchants use it sometimes
    return random.random() < 0.4  # 40% chance


def choose_legal_goods_lie() -> dict:
    """
    Create a declaration where merchant lies about legal goods mix.
    
    Strategy:
    1. Declare homogeneous bag (e.g., "3x Cheese") - looks safe and honest
    2. Actually carry mostly declared item + 1-2 higher-value items
       Example: Declare "3x Cheese", actually carry "2x Cheese + 1x Mead"
    3. Profit = value of substituted higher-value items
    
    Key insight: Honest merchants bring homogeneous bags (3x Cheese = 3x Cheese).
    Lying merchants sneak higher-value items into a "safe" declared bag.
    
    GAME RULES: Maximum bag size is 6 items.
    
    Returns:
        dict with keys:
            - declared_id: Mid-value legal good (the "safe" declaration)
            - count: Number of items (3-4 for believability, within 6-card limit)
            - actual_ids: Mix of declared good + higher-value items
            - lie: True
            - lie_type: 'legal_goods_mix' (for tracking)
    """
    from core.game_rules import BAG_SIZE_LIMIT
    
    # Sort legal goods by value
    legal_by_value = sorted(ALL_LEGAL, key=lambda g: g.value)
    
    # Declare mid-value goods (looks safe, not suspiciously cheap)
    # Use middle 60% of legal goods
    mid_start = len(legal_by_value) // 5
    mid_end = len(legal_by_value) * 4 // 5
    declared_good = random.choice(legal_by_value[mid_start:mid_end] if mid_end > mid_start else legal_by_value)
    
    # Choose count (3-4 items is believable, within bag limit)
    total_count = min(random.randint(3, 4), BAG_SIZE_LIMIT)
    
    # Sneak in 1-2 higher-value items
    # Find goods worth more than declared good
    higher_value_options = [g for g in legal_by_value if g.value > declared_good.value]
    
    if not higher_value_options:
        # Declared good is already highest value, can't lie profitably
        # Just return honest declaration
        return {
            "declared_id": declared_good.id,
            "count": total_count,
            "actual_ids": [declared_good.id] * total_count,
            "lie": False,
            "lie_type": "none"
        }
    
    # Choose how many high-value items to sneak in (1-2, never more than half the bag)
    num_high_value = min(2, random.randint(1, total_count // 2))
    num_declared = total_count - num_high_value
    
    # Pick the high-value item(s) - prefer highest value for max profit
    high_value_good = random.choice(higher_value_options[-2:])  # Top 2 highest value options
    
    # Build actual bag: mostly declared good + some high-value items
    actual_ids = [declared_good.id] * num_declared + [high_value_good.id] * num_high_value
    
    return {
        "declared_id": declared_good.id,
        "count": total_count,
        "actual_ids": actual_ids,
        "lie": True,
        "lie_type": "legal_goods_mix"
    }


def calculate_legal_lie_profit(declared_good_value: int, actual_good_value: int, 
                                count: int, bribe_paid: int = 0) -> int:
    """
    Calculate profit from legal goods lying strategy.
    
    Profit = (actual_value - declared_value) * count - bribe_paid
    
    Args:
        declared_good_value: Value of declared goods
        actual_good_value: Value of actual goods
        count: Number of items
        bribe_paid: Amount paid in bribes
        
    Returns:
        int: Net profit (can be negative if caught or bribe too high)
    """
    declared_total = declared_good_value * count
    actual_total = actual_good_value * count
    
    return (actual_total - declared_total) - bribe_paid


def get_legal_lie_examples() -> list[dict]:
    """
    Return example scenarios for legal goods lying.
    
    Useful for testing and understanding the strategy.
    
    Returns:
        list of example scenarios with risk/reward analysis
    """
    return [
        {
            "scenario": "Conservative Lie",
            "declared": "3x Cheese (value: 5 each, total: 15)",
            "actual": "2x Cheese + 1x Chicken (2×5 + 1×6 = 16)",
            "profit_if_pass": 1,
            "loss_if_caught": 16,
            "bribe_cost": "17-20 gold (110-130% of 15)",
            "net_profit_with_bribe": "-16 to -19 (not profitable, too conservative)"
        },
        {
            "scenario": "Moderate Lie",
            "declared": "4x Cheese (value: 5 each, total: 20)",
            "actual": "2x Cheese + 2x Mead (2×5 + 2×10 = 30)",
            "profit_if_pass": 10,
            "loss_if_caught": 30,
            "bribe_cost": "22-26 gold (110-130% of 20)",
            "net_profit_with_bribe": "-12 to -16 (needs to pass to profit)"
        },
        {
            "scenario": "Optimal Lie",
            "declared": "3x Cheese (value: 5 each, total: 15)",
            "actual": "2x Cheese + 1x Mead (2×5 + 1×10 = 20)",
            "profit_if_pass": 5,
            "loss_if_caught": 20,
            "bribe_cost": "17-20 gold (110-130% of 15)",
            "net_profit_with_bribe": "-12 to -15 (needs 60%+ pass rate)"
        },
        {
            "scenario": "Aggressive Lie",
            "declared": "4x Bread (value: 3 each, total: 12)",
            "actual": "2x Bread + 2x Mead (2×3 + 2×10 = 26)",
            "profit_if_pass": 14,
            "loss_if_caught": 26,
            "bribe_cost": "13-16 gold (110-130% of 12)",
            "net_profit_with_bribe": "-2 to 1 (break-even, good with high pass rate)"
        }
    ]
