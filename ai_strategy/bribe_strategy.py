"""
Bribe Strategy Module - Intelligent Bribe Calculation

This module implements sophisticated bribe calculation that:
1. Scales with declared value (not just actual value)
2. Considers personality traits (greed, risk, honesty)
3. Implements advanced bluff strategies (Hard AI only)
4. Makes bribes feel natural and strategic

KEY INSIGHT:
============
A merchant declaring "1x Apples" (worth 2g) offering 9g bribe is SUSPICIOUS.
The sheriff thinks: "Why pay 9g for 2g of apples? Must be contraband!"

High bribes should be combined with High claims of goods to make Sheriff think twice about inspecting.
Ex. "4 apple and offer 9 gold? If they're correct, I have to pay 10 gold during inspection... and if I let them pass I'll get 9g!"

- Bribe should be proportional to DECLARED value
- Add noise/variance to avoid obvious patterns
- High-value declarations justify higher bribes
- Low bribes on high declarations are red flags

ADVANCED BLUFF (Hard AI Only):
===============================
Offer a small "goodwill" bribe on a PERFECT legal bag:
- Declare: "3x Cheese" (worth 9g)
- Carry: "3x Cheese" (actually honest!)
- Bribe: 2-3g (small goodwill gesture)
- If sheriff demands more: REFUSE (because bag is actually legal)
- This manipulates sheriff's expectations and creates uncertainty
"""

import random

from core.mechanics.goods import GOOD_BY_ID
from core.systems.game_master_state import MerchantTier


def calculate_declared_value(declared_good_id, count: int) -> int:
    """Calculate the value of declared goods.

    Args:
        declared_good_id: Either a string ID or a Good object
        count: Number of items
    """
    # Handle both string IDs and Good objects
    if isinstance(declared_good_id, str):
        good = GOOD_BY_ID.get(declared_good_id)
        if not good:
            return 0
        return good.value * count
    else:
        # Assume it's a Good object
        return declared_good_id.value * count


def calculate_actual_value(actual_good_ids: list) -> int:
    """Calculate the value of actual goods in bag.

    Args:
        actual_good_ids: List of either string IDs or Good objects
    """
    total = 0
    for item in actual_good_ids:
        # Handle both string IDs and Good objects
        if isinstance(item, str):
            good = GOOD_BY_ID.get(item)
            if good:
                total += good.value
        else:
            # Assume it's a Good object
            total += item.value
    return total


def calculate_contraband_value(actual_good_ids: list) -> int:
    """Calculate the value of contraband items only.

    Args:
        actual_good_ids: List of either string IDs or Good objects
    """
    total = 0
    for item in actual_good_ids:
        # Handle both string IDs and Good objects
        if isinstance(item, str):
            good = GOOD_BY_ID.get(item)
            if good and good.is_contraband():
                total += good.value
        else:
            # Assume it's a Good object
            if item.is_contraband():
                total += item.value
    return total


def calculate_scaled_bribe(
    declared_good_id: str,
    declared_count: int,
    actual_good_ids: list[str],
    is_lying: bool,
    personality: dict,
    sheriff_stats: dict,
    tier: MerchantTier,
) -> int:
    """
    Calculate intelligent bribe amount that scales with declared value.

    Args:
        declared_good_id: What merchant claims to carry
        declared_count: How many they claim
        actual_good_ids: What they're actually carrying
        is_lying: Whether declaration is false
        personality: Dict with risk_tolerance, greed, honesty_bias
        sheriff_stats: Sheriff behavior stats (inspection_rate, etc.)
        tier: Merchant difficulty tier

    Returns:
        Gold amount to offer as bribe (0 if shouldn't bribe)
    """
    # Calculate values
    declared_value = calculate_declared_value(declared_good_id, declared_count)
    actual_value = calculate_actual_value(actual_good_ids)
    contraband_value = calculate_contraband_value(actual_good_ids)

    # Get personality traits
    greed = personality.get("greed", 5)
    risk_tolerance = personality.get("risk_tolerance", 5)

    # Get sheriff behavior
    inspection_rate = sheriff_stats.get("inspection_rate", 0.5)
    bribe_acceptance_rate = sheriff_stats.get("bribe_acceptance_rate", 0.3)

    # Decide if should bribe at all
    if not should_offer_bribe(
        is_lying,
        contraband_value,
        inspection_rate,
        bribe_acceptance_rate,
        personality,
        tier,
    ):
        return 0

    # Calculate base bribe amount
    if is_lying and contraband_value > 0:
        # Has contraband - bribe based on DECLARED value + risk premium
        base_bribe = calculate_contraband_bribe(
            declared_value, contraband_value, greed, risk_tolerance
        )
    elif is_lying:
        # Legal lie (mixed bag) - smaller bribe based on declared value
        base_bribe = calculate_legal_lie_bribe(declared_value, actual_value, greed)
    else:
        # Honest bag - advanced bluff (Hard AI only)
        if tier == MerchantTier.HARD and random.random() < 0.15:
            # 15% chance for advanced bluff
            base_bribe = calculate_advanced_bluff_bribe(declared_value)
        else:
            return 0  # Don't bribe if honest (unless advanced bluff)

    # Apply sheriff behavior modifiers
    if inspection_rate > 0.7:
        # Aggressive sheriff - increase bribe
        base_bribe = int(base_bribe * 1.3)
    elif inspection_rate < 0.3:
        # Lenient sheriff - decrease bribe
        base_bribe = int(base_bribe * 0.7)

    # Add variance to avoid predictable patterns
    variance = random.uniform(0.85, 1.15)
    final_bribe = int(base_bribe * variance)

    # Ensure minimum of 1 gold if bribing
    return max(1, final_bribe)


def should_offer_bribe(
    is_lying: bool,
    contraband_value: int,
    inspection_rate: float,
    bribe_acceptance_rate: float,
    personality: dict,
    tier: MerchantTier,
) -> bool:
    """
    Decide if merchant should offer a bribe.

    Args:
        is_lying: Whether merchant is lying
        contraband_value: Value of contraband (0 if none)
        inspection_rate: How often sheriff inspects
        bribe_acceptance_rate: How often sheriff accepts bribes
        personality: Merchant personality traits
        tier: Merchant difficulty tier

    Returns:
        True if should offer bribe
    """
    # Easy merchants rarely bribe
    if tier == MerchantTier.EASY:
        if contraband_value > 0 and inspection_rate > 0.6:
            return random.random() < 0.3  # 30% chance even with contraband
        return False

    # Medium merchants bribe risky bags
    if tier == MerchantTier.MEDIUM:
        if contraband_value > 0:
            # Bribe if sheriff is active
            if inspection_rate > 0.5:
                return random.random() < 0.6  # 60% chance
            return random.random() < 0.3  # 30% chance if lenient
        elif is_lying:
            # Legal lie - only bribe if very risky
            return inspection_rate > 0.7 and random.random() < 0.4
        return False

    # Hard merchants use sophisticated logic
    if tier == MerchantTier.HARD:
        if contraband_value > 0:
            # Always consider bribing with contraband
            base_chance = 0.7
            # Adjust for sheriff behavior
            if bribe_acceptance_rate > 0.5:
                base_chance += 0.2
            if inspection_rate > 0.6:
                base_chance += 0.1
            return random.random() < min(base_chance, 0.95)
        elif is_lying:
            # Legal lie - bribe if sheriff is aggressive
            return inspection_rate > 0.6 and random.random() < 0.5
        else:
            # Advanced bluff on honest bag (15% chance)
            return random.random() < 0.15

    return False


def calculate_contraband_bribe(
    declared_value: int, contraband_value: int, greed: int, risk_tolerance: int
) -> int:
    """
    Calculate bribe for contraband smuggling.

    CRITICAL INSIGHT: Bribe should be proportional to DECLARED value to avoid suspicion!

    Example:
    - Declare "1x Apple" (2g) + 9g bribe = SUSPICIOUS (450% of declared value)
    - Declare "4x Apple" (8g) + 9g bribe = REASONABLE (112% of declared value)

    Sheriff's calculation:
    - "If honest, I pay declared_value penalty"
    - "If I accept bribe, I get bribe_amount"
    - "If bribe ≈ declared_value, it's a good deal to accept"

    Strategy: Bribe should be 80-120% of declared value for high claims,
    making sheriff think twice about inspecting.

    Args:
        declared_value: Value of declared goods
        contraband_value: Value of contraband
        greed: Merchant greed (0-10, higher = lower bribe)
        risk_tolerance: Risk tolerance (0-10, higher = lower bribe)

    Returns:
        Bribe amount in gold
    """
    # CORE STRATEGY: Base bribe on declared value, not contraband value
    # This makes the bribe proportional to the claim

    # Target: 70-110% of declared value (makes sheriff think it's worth accepting)
    base_percentage = random.uniform(0.7, 1.1)
    base_bribe = declared_value * base_percentage

    # BUT: Merchant must still profit from the deal
    # If contraband value is high, merchant can afford higher bribe
    # If contraband value is low, merchant must offer less

    # Calculate maximum rational bribe (can't exceed contraband profit)
    # Merchant needs to profit at least 20% of contraband value
    max_rational_bribe = contraband_value * 0.8

    # Use the lower of: (declared-based bribe) or (max rational bribe)
    # This ensures bribe scales with declaration but merchant still profits
    base_bribe = min(base_bribe, max_rational_bribe)

    # Greed modifier (greedy merchants offer less)
    greed_factor = 1.0 - (greed / 30.0)  # 0.67 to 1.0

    # Risk tolerance modifier (risk-takers offer less)
    risk_factor = 1.0 - (risk_tolerance / 40.0)  # 0.75 to 1.0

    final_bribe = base_bribe * greed_factor * risk_factor

    # Ensure minimum bribe of 1 gold
    # But also ensure it doesn't exceed what merchant can afford
    min_bribe = max(1, int(contraband_value * 0.2))  # At least 20% of contraband
    max_bribe = int(contraband_value * 0.8)  # At most 80% of contraband

    return int(max(min_bribe, min(final_bribe, max_bribe)))


def calculate_legal_lie_bribe(
    declared_value: int, actual_value: int, greed: int
) -> int:
    """
    Calculate bribe for legal goods lie (mixed bag).

    This is lower risk, so bribe is smaller.

    Args:
        declared_value: Value of declared goods
        actual_value: Value of actual goods
        greed: Merchant greed

    Returns:
        Bribe amount in gold
    """
    # Base: 20-30% of the value difference
    value_diff = abs(actual_value - declared_value)
    base_bribe = value_diff * random.uniform(0.2, 0.3)

    # Scale with declared value
    declared_scaling = 1.0 + (declared_value / 150.0)

    # Greed modifier
    greed_factor = 1.0 - (greed / 25.0)  # 0.6 to 1.0

    final_bribe = base_bribe * declared_scaling * greed_factor

    # Minimum 2 gold for legal lies
    return int(max(2, final_bribe))


def calculate_advanced_bluff_bribe(declared_value: int) -> int:
    """
    Calculate small "goodwill" bribe for advanced bluff strategy.

    This is for Hard AI only: offering a small bribe on a PERFECT legal bag
    to manipulate sheriff's expectations.

    Args:
        declared_value: Value of declared goods

    Returns:
        Small bribe amount (2-4 gold typically)
    """
    # Small goodwill gesture: 15-25% of declared value
    base = declared_value * random.uniform(0.15, 0.25)

    # Cap at reasonable range (2-5 gold)
    return int(max(2, min(5, base)))


def should_accept_counter_offer(
    sheriff_demand: int,
    original_offer: int,
    actual_good_ids: list[str],
    is_lying: bool,
    personality: dict,
    tier: MerchantTier,
) -> bool:
    """
    Decide whether to accept sheriff's counter-demand.

    Args:
        sheriff_demand: Amount sheriff is demanding
        original_offer: Merchant's original offer
        actual_good_ids: What merchant is actually carrying
        is_lying: Whether merchant is lying
        personality: Merchant personality traits
        tier: Merchant difficulty tier

    Returns:
        True if merchant accepts, False to refuse/negotiate
    """
    actual_value = calculate_actual_value(actual_good_ids)
    contraband_value = calculate_contraband_value(actual_good_ids)

    greed = personality.get("greed", 5)
    risk_tolerance = personality.get("risk_tolerance", 5)

    # Advanced bluff: If honest bag and demand is too high, REFUSE
    if not is_lying and tier == MerchantTier.HARD:
        # Honest bag - refuse if demand exceeds declared value significantly
        if sheriff_demand > actual_value * 0.5:
            return False  # Call sheriff's bluff

    # If demand exceeds value of goods, refuse (irrational to accept)
    if contraband_value > 0:
        max_acceptable = contraband_value * 0.8  # 80% of contraband value
    else:
        max_acceptable = actual_value * 0.6  # 60% of actual value

    if sheriff_demand > max_acceptable:
        return False

    # Calculate acceptance threshold based on personality
    greed_threshold = 0.5 + (greed / 20.0)  # 0.5 to 1.0
    risk_threshold = 0.7 - (risk_tolerance / 20.0)  # 0.2 to 0.7

    demand_ratio = sheriff_demand / max_acceptable if max_acceptable > 0 else 1.0

    # Accept if demand is reasonable
    if demand_ratio < min(greed_threshold, risk_threshold):
        return True

    # Tier-based acceptance
    if tier == MerchantTier.EASY:
        # Easy merchants accept more readily (nervous)
        return random.random() < 0.6
    elif tier == MerchantTier.MEDIUM:
        # Medium merchants negotiate
        return random.random() < 0.4
    else:  # HARD
        # Hard merchants are tough negotiators
        return random.random() < 0.2
