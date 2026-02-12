"""
Simulation Test Helpers

Helper functions for simulation tests, particularly for ensuring Silas Voss's
detection logic works correctly.

CRITICAL FOR SILAS VOSS TESTS:
Silas's sheriff detection relies on the game master state history. Tests MUST
record events to the game state, or Silas will always detect sheriffs as "unknown"
because he'll be looking at an empty history.
"""

from core.mechanics.bag_builder import build_bag_and_declaration
from core.mechanics.contraband_bonus import calculate_contraband_bonus
from core.mechanics.goods import GOOD_BY_ID
from core.players.merchants import Merchant
from core.players.sheriff import Sheriff
from core.systems.game_master_state import get_game_master_state


def simulate_encounter(
    merchant: Merchant,
    sheriff: Sheriff,
    sheriff_strategy: callable,
    history: list[dict],
) -> dict:
    """
    Simulate a single merchant encounter with proper game state recording.
    
    This is the canonical encounter simulation function used by all simulation tests.
    It handles:
    - Building bag and declaration
    - Proactive bribe calculation
    - Sheriff decision making
    - Outcome processing (gold, penalties, bonuses)
    - Recording to game master state (CRITICAL for Silas)
    - Recording to history list
    
    Args:
        merchant: The merchant being processed
        sheriff: The sheriff making decisions
        sheriff_strategy: Callable that takes (merchant, bribe_offered, declaration, actual_goods, history)
                         and returns (should_inspect, accept_bribe)
        history: List of previous encounter dicts
        
    Returns:
        dict with keys:
            - merchant_name: str
            - gold_earned: int
            - gold_lost: int
            - caught: bool
            - passed: bool
            - bribe_attempted: bool
            - bribe_offered: int
            - bribed: bool (alias: bribe_accepted)
            - contraband: bool
            - opened: bool
            - caught_lie: bool
    """
    # Build bag and declaration
    declaration, actual_goods, is_honest = build_bag_and_declaration(merchant, history)

    # Get declared goods
    declared_good = GOOD_BY_ID[declaration.good_id]
    declared_goods = [declared_good] * declaration.count

    # Check if merchant offers proactive bribe
    bribe_offered = 0
    if merchant.should_offer_proactive_bribe(
        sheriff.authority, sheriff.reputation, actual_goods, declared_goods
    ):
        bribe_offered = merchant.calculate_proactive_bribe(
            actual_goods, not is_honest, sheriff.authority, declared_goods
        )

    # Sheriff decides what to do
    should_inspect, accept_bribe = sheriff_strategy(
        merchant, bribe_offered, declaration, actual_goods, history
    )

    # Process outcome
    gold_earned = 0
    gold_lost = 0
    caught = False

    if accept_bribe:
        # Sheriff accepted bribe - merchant pays bribe and keeps goods
        gold_lost += bribe_offered
        # Apply contraband set bonuses!
        bonus_result = calculate_contraband_bonus(actual_goods)
        gold_earned += bonus_result["bonus_value"]
    elif should_inspect:
        # Sheriff inspects - NO bribe is paid (inspection instead of bribe)
        if not is_honest:
            # Caught lying!
            caught = True
            # Pay fine (double contraband value) - use BASE value for penalty, not bonus
            contraband_value = sum(g.value for g in actual_goods if not g.is_legal())
            gold_lost += contraband_value * 2
            # Bribe is NOT paid when inspected
        else:
            # Honest, goods pass
            # RULE: Sheriff must pay merchant the value of goods for wrongful inspection
            # Use base value for penalty calculation (sheriff doesn't pay bonuses)
            goods_value = sum(g.value for g in actual_goods)
            gold_earned += goods_value  # Keep the goods
            gold_earned += goods_value  # Sheriff pays penalty (DOUBLE profit!)
            # Bribe is NOT paid when inspected
    else:
        # Sheriff lets pass without inspection (no bribe was offered)
        # Apply contraband set bonuses!
        bonus_result = calculate_contraband_bonus(actual_goods)
        gold_earned += bonus_result["bonus_value"]

    result = {
        "merchant_name": merchant.name,
        "gold_earned": gold_earned,
        "gold_lost": gold_lost,
        "caught": caught,
        "passed": not caught,
        "bribe_attempted": bribe_offered > 0,  # Did they try to bribe?
        "bribe_offered": bribe_offered,  # Amount offered (for Silas detection)
        "bribed": accept_bribe,  # Did sheriff accept?
        "bribe_accepted": accept_bribe,  # Alias for compatibility
        "contraband": not is_honest,
        "opened": should_inspect,
        "caught_lie": caught,
    }

    # CRITICAL FOR SILAS VOSS: Record encounter to game master state
    # Silas's sheriff detection relies on this history. Without it, he will
    # always detect sheriffs as "unknown" and perform significantly worse.
    game_state = get_game_master_state()

    # Record event using proper method
    actual_good_ids = [g.id for g in actual_goods]
    game_state.record_event(
        merchant_name=merchant.name,
        declared_good=declared_good.id,
        declared_count=declaration.count,
        actual_goods=actual_good_ids,
        was_opened=should_inspect,
        caught_lie=caught,
        bribe_offered=bribe_offered,
        bribe_accepted=accept_bribe,
        proactive_bribe=bribe_offered > 0,
    )

    return result


def record_round_to_game_state(
    merchant_name,
    declaration,
    actual_goods,
    should_inspect,
    caught,
    bribe_offered,
    accept_bribe,
):
    """
    Record a round's outcome to the game master state.

    **CRITICAL FOR SILAS VOSS**: Silas's sheriff detection relies on the game master
    state history. Tests MUST call this function to record events, or Silas will
    always detect sheriffs as "unknown" because he'll be looking at an empty history.

    Args:
        merchant_name: Name of the merchant
        declaration: Declaration object with good_id and count
        actual_goods: List of Good objects in the bag
        should_inspect: Whether sheriff inspected
        caught: Whether merchant was caught lying
        bribe_offered: Amount of bribe offered (0 if none)
        accept_bribe: Whether sheriff accepted the bribe

    Usage:
        from tests.simulations.simulation_helpers import record_round_to_game_state

        # In your test loop:
        declaration, actual_goods, is_honest = build_bag_and_declaration(merchant, history)
        bribe_offered = merchant.calculate_proactive_bribe(...) if merchant.should_offer_proactive_bribe(...) else 0
        should_inspect, accept_bribe = sheriff_strategy(...)

        # CRITICAL: Record to game state for Silas's detection
        record_round_to_game_state(
            merchant_name=merchant.name,
            declaration=declaration,
            actual_goods=actual_goods,
            should_inspect=should_inspect,
            caught=caught,
            bribe_offered=bribe_offered,
            accept_bribe=accept_bribe
        )

    Why This Matters:
        - Silas uses game_state.get_history_for_tier(None) for sheriff detection
        - Without game state recording, detection always returns "unknown"
        - This affects Silas's strategy selection (strict, greedy, corrupt detection)
        - Silas's performance will be significantly worse without proper detection

    Example Test Pattern:
        ```python
        from core.systems.game_master_state import reset_game_master_state
        from tests.simulations.simulation_helpers import record_round_to_game_state

        def test_silas_vs_sheriff():
            reset_game_master_state()  # Start fresh

            for round_num in range(100):
                # ... build declaration, process round ...

                # CRITICAL: Record to game state
                record_round_to_game_state(
                    merchant_name=merchant.name,
                    declaration=declaration,
                    actual_goods=actual_goods,
                    should_inspect=should_inspect,
                    caught=caught,
                    bribe_offered=bribe_offered,
                    accept_bribe=accept_bribe
                )
        ```
    """
    from core.systems.game_master_state import get_game_master_state

    game_state = get_game_master_state()
    actual_good_ids = [g.id for g in actual_goods]

    game_state.record_event(
        merchant_name=merchant_name,
        declared_good=declaration.good_id,
        declared_count=declaration.count,
        actual_goods=actual_good_ids,
        was_opened=should_inspect,
        caught_lie=caught,
        bribe_offered=bribe_offered,
        bribe_accepted=accept_bribe,
        proactive_bribe=bribe_offered > 0,
    )
