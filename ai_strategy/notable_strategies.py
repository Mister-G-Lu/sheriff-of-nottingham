"""
Notable Merchant Strategies

This file contains reusable strategy patterns that can be applied by different merchants.
These are proven tactics that exploit specific sheriff behaviors.
"""


def legal_good_with_bribe_trick(merchant, history: list[dict]) -> dict:
    """
    Legal Good with Bribe Trick

    Why it works:
    - Bribes will not be paid when sheriff inspects bag (becomes a bluff)
    - Suspicious sheriffs who inspect bribes will open the bag
    - When they find only legal goods, they must pay a penalty (double the goods' value)
    - This turns their suspicion against them, making honest goods highly profitable

    Best against:
    - Trigger Happy sheriffs (inspect all bribes)
    - Strict Inspector sheriffs (inspect everyone)
    - Any sheriff with high inspection rates (>50%)

    Returns:
        dict: Detection result with 'should_use' boolean and 'reason' string
    """
    if len(history) < 3:
        return {"should_use": False, "reason": "Not enough data"}

    recent = history[-10:] if len(history) >= 10 else history

    # Calculate overall inspection rate
    inspections = sum(1 for h in recent if h.get("opened", False))
    inspection_rate = inspections / len(recent) if recent else 0.0

    # Calculate inspection rate among those who bribed
    bribed = [h for h in recent if h.get("bribe_offered", 0) > 0]
    if len(bribed) >= 3:
        bribed_inspections = sum(1 for h in bribed if h.get("opened", False))
        bribe_inspection_rate = bribed_inspections / len(bribed)

        # If sheriff inspects >50% of bribes, they're suspicious of bribes
        if bribe_inspection_rate > 0.50:
            return {
                "should_use": True,
                "reason": f"Sheriff inspects {bribe_inspection_rate:.0%} of bribes (strict)",
            }

    # If overall inspection rate is very high (>50%), sheriff is strict
    if inspection_rate > 0.50:
        return {
            "should_use": True,
            "reason": f"Sheriff has {inspection_rate:.0%} inspection rate (trigger happy)",
        }

    return {"should_use": False, "reason": "Sheriff not strict enough"}


def calculate_legal_good_bribe(actual_goods: list, declared_goods: list = None) -> int:
    """
    Calculate bribe amount for Legal Good Trick.

    Can be large to bluff the sheriff
    """
    import random

    if declared_goods:
        declared_value = sum(g.value for g in declared_goods)
    else:
        declared_value = sum(g.value for g in actual_goods)

    # Offer 10-90% of declared value as bribe
    return max(1, int(declared_value * random.uniform(0.10, 0.90)))
