"""
Test Silas's detection logic against Trigger Happy sheriff.
Trigger Happy inspects ALL bribes, so should be detected as 'strict'.

IMPORTANT: This test uses record_round_to_game_state() to ensure Silas's
detection works correctly. Silas relies on game master state history for
sheriff detection - without recording to game state, he always detects "unknown".
"""

# Must be first import - sets up test environment
import tests.test_setup  # noqa: F401
from ai_strategy.ai_sheriffs import trigger_happy
from core.mechanics.bag_builder import build_bag_and_declaration
from core.mechanics.contraband_bonus import calculate_contraband_bonus
from core.players.merchant_loader import load_merchants
from core.players.sheriff import Sheriff
from core.players.silas_voss import SilasVoss
from core.systems.game_master_state import (
    get_game_master_state,
    reset_game_master_state,
)
from tests.simulations.simulation_helpers import record_round_to_game_state


def test_silas_detection():
    """Test that Silas correctly detects Trigger Happy as 'strict'."""
    reset_game_master_state()

    merchants = load_merchants()
    silas = next((m for m in merchants if isinstance(m, SilasVoss)), None)

    if not silas:
        print("ERROR: Could not load Silas Voss")
        return

    sheriff = Sheriff(reputation=5, authority=2)
    history = []

    print(f"\n{'=' * 80}")
    print("TESTING SILAS DETECTION AGAINST TRIGGER HAPPY")
    print(f"{'=' * 80}\n")
    print("Trigger Happy sheriff: Inspects ALL bribes (100% inspection rate)")
    print("Expected: Silas should detect as 'strict' after gathering data\n")

    detection_log = []

    for round_num in range(30):
        # Build bag and declaration
        declaration, actual_goods, is_honest = build_bag_and_declaration(silas, history)

        from core.mechanics.goods import GOOD_BY_ID

        declared_good = GOOD_BY_ID[declaration.good_id]
        declared_goods = [declared_good] * declaration.count

        # Check if Silas offers bribe
        bribe_offered = 0
        if silas.should_offer_proactive_bribe(
            sheriff.authority, sheriff.reputation, actual_goods, declared_goods
        ):
            bribe_offered = silas.calculate_proactive_bribe(
                actual_goods, not is_honest, sheriff.authority, declared_goods
            )

        # Sheriff decides (Trigger Happy strategy)
        should_inspect, accept_bribe = trigger_happy(
            silas, bribe_offered, declaration, actual_goods, history
        )

        # Process outcome
        gold_earned = 0
        gold_lost = 0
        caught = False

        if accept_bribe:
            gold_lost += bribe_offered
            bonus_result = calculate_contraband_bonus(actual_goods)
            gold_earned += bonus_result["bonus_value"]
        elif should_inspect:
            if not is_honest:
                caught = True
                contraband_value = sum(
                    g.value for g in actual_goods if not g.is_legal()
                )
                gold_lost += contraband_value * 2
            else:
                goods_value = sum(g.value for g in actual_goods)
                gold_earned += goods_value * 2
        else:
            bonus_result = calculate_contraband_bonus(actual_goods)
            gold_earned += bonus_result["bonus_value"]

        # Record in local history
        result = {
            "merchant_name": silas.name,
            "gold_earned": gold_earned,
            "gold_lost": gold_lost,
            "caught": caught,
            "passed": not caught,
            "bribe_attempted": bribe_offered > 0,
            "bribe_offered": bribe_offered,
            "bribed": accept_bribe,
            "bribe_accepted": accept_bribe,
            "contraband": not is_honest,
            "opened": should_inspect,
            "caught_lie": caught,
            "declared_good": declaration.good_id,
            "declared_count": declaration.count,
        }
        history.append(result)

        # CRITICAL: Record to game state for Silas's detection
        # Without this, Silas will always detect sheriffs as "unknown"
        record_round_to_game_state(
            merchant_name=silas.name,
            declaration=declaration,
            actual_goods=actual_goods,
            should_inspect=should_inspect,
            caught=caught,
            bribe_offered=bribe_offered,
            accept_bribe=accept_bribe,
        )

        # Check Silas's detection
        game_state = get_game_master_state()
        full_history = game_state.get_history_for_tier(None)
        sheriff_type = silas._detect_sheriff_type(full_history)

        detection_log.append(
            {
                "round": round_num + 1,
                "detected": sheriff_type,
                "bribe_offered": bribe_offered > 0,
                "inspected": should_inspect,
                "honest": is_honest,
            }
        )

        if round_num >= 4:  # After 5 rounds, should have enough data
            print(
                f"Round {round_num + 1:2d}: Detected as '{sheriff_type}' | "
                f"Bribe: {str(bribe_offered > 0):5} | Inspected: {str(should_inspect):5} | "
                f"Honest: {str(is_honest):5}"
            )

    # Analyze detection
    print(f"\n{'=' * 80}")
    print("DETECTION ANALYSIS")
    print(f"{'=' * 80}\n")

    from collections import Counter

    detection_counts = Counter(
        d["detected"] for d in detection_log[5:]
    )  # After round 5

    print("Sheriff Type Detections (after round 5):")
    for sheriff_type, count in detection_counts.most_common():
        print(
            f"  {sheriff_type}: {count} rounds ({count / len(detection_log[5:]) * 100:.1f}%)"
        )

    # Check inspection rate among bribes
    bribes = [d for d in detection_log if d["bribe_offered"]]
    if bribes:
        inspected_bribes = sum(1 for d in bribes if d["inspected"])
        inspection_rate = inspected_bribes / len(bribes)
        print(f"\nInspection rate among bribes: {inspection_rate:.1%}")
        print(f"Total bribes offered: {len(bribes)}")
        print(f"Bribes inspected: {inspected_bribes}")

    # Validation
    print(f"\n{'=' * 80}")
    print("VALIDATION")
    print(f"{'=' * 80}\n")

    final_detection = detection_log[-1]["detected"]
    if final_detection == "strict":
        print("✅ PASS: Silas correctly detects Trigger Happy as 'strict'")
    else:
        print(
            f"❌ FAIL: Silas detects Trigger Happy as '{final_detection}' (expected: 'strict')"
        )

    if bribes and inspection_rate == 1.0:
        print("✅ PASS: Trigger Happy inspects 100% of bribes (as expected)")
    else:
        print(f"⚠️  WARNING: Inspection rate is {inspection_rate:.1%} (expected: 100%)")


if __name__ == "__main__":
    test_silas_detection()
