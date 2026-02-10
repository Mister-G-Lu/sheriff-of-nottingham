"""Round logic: merchant arrival, declaration, bribe, lie detection."""

import random
from dataclasses import dataclass, field
from typing import Optional

from core.merchants import Merchant
from core.sheriff import Sheriff
from core.goods import Good


@dataclass
class Declaration:
    """What the merchant declares (one good type, count)."""
    good_id: str
    count: int


@dataclass
class RoundState:
    """State for one round: one merchant, declaration, bribe, inspection result."""
    merchant: Merchant
    declaration: Optional[Declaration] = None
    bribe: str = ""
    bag_actual: list[Good] = field(default_factory=list)  # true contents (for simulation)
    sheriff_opens: bool = False
    sheriff_caught_lie: bool = False
    # Summary of contraband that slipped past the sheriff this round.
    # We intentionally record only counts and total value, not specific item ids,
    # so the player doesn't learn precise contraband until the game ends.
    contraband_passed_count: int = 0
    contraband_passed_value: int = 0


def merchant_arrival(merchant: Merchant) -> None:
    """Hook for UI: narrate merchant arrival (handled in ui/narration)."""
    pass


def resolve_inspection(
    sheriff: Sheriff,
    merchant: Merchant,
    declaration: Declaration,
    actual_goods: list[Good],
    round_state: Optional[RoundState] = None,
) -> tuple[bool, bool]:
    """
    Decide if sheriff opens the bag and if they catch a lie.
    Returns (sheriff_opens, sheriff_caught_lie).
    """
    # Simple rule: sheriff rolls perception vs merchant bluff when declaration might be false
    actual_ids = [g.id for g in actual_goods]
    declared_ok = (
        declaration.count == len(actual_goods)
        and all(g.id == declaration.good_id for g in actual_goods)
    )
    if declared_ok:
        return (False, False)

    sheriff_roll = random.randint(1, 10) + sheriff.perception
    merchant_roll = merchant.roll_bluff()
    sheriff_opens = sheriff_roll >= merchant_roll
    sheriff_caught_lie = sheriff_opens
    # If the merchant lied and the sheriff did NOT open the bag, contraband
    # slipped past the inspector. Record a summary (count + total value)
    # on the provided RoundState if one was passed.
    if not declared_ok and not sheriff_opens and round_state is not None:
        contraband_items = [g for g in actual_goods if g.is_contraband()]
        round_state.contraband_passed_count = len(contraband_items)
        round_state.contraband_passed_value = sum(g.value for g in contraband_items)
        # Let the merchant record their own aggregated summary for inspector queries
        try:
            merchant.record_round_result(round_state)
        except Exception:
            # Be defensive: merchant may not implement the hook in older versions
            pass

    return (sheriff_opens, sheriff_caught_lie)
