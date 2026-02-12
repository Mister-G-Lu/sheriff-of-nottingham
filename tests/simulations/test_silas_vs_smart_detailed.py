"""
Detailed test of Silas Voss vs Smart Adaptive sheriff.
Analyzes Silas's detection logic and strategy decisions round by round.
"""

# Must be first import - sets up test environment
import tests.test_setup  # noqa: F401
from ai_strategy.ai_sheriffs import smart_adaptive
from core.mechanics.bag_builder import build_bag_and_declaration
from core.mechanics.contraband_bonus import calculate_contraband_bonus
from core.players.merchant_loader import load_merchants
from core.players.sheriff import Sheriff
from core.players.silas_voss import SilasVoss
from core.systems.game_master_state import reset_game_master_state


def simulate_silas_vs_smart_detailed(rounds: int = 50):
    """Simulate Silas against Smart Adaptive sheriff with detailed logging."""
    # Reset game state
    reset_game_master_state()

    # Load Silas
    merchants = load_merchants()
    silas = next((m for m in merchants if isinstance(m, SilasVoss)), None)

    if not silas:
        print("ERROR: Could not load Silas Voss")
        return None

    # Create sheriff
    sheriff = Sheriff(reputation=5, authority=2)

    # Track stats
    total_gold_earned = 0
    total_gold_lost = 0
    times_caught = 0
    times_passed = 0
    bribes_attempted = 0
    bribes_accepted = 0
    history = []

    # Track detection over time
    detection_log = []

    print(f"\n{'=' * 100}")
    print(f"SILAS VS SMART ADAPTIVE SHERIFF - DETAILED ANALYSIS ({rounds} ROUNDS)")
    print(f"{'=' * 100}\n")
    print(
        f"{'Round':<6} {'Detected':<10} {'Honest?':<8} {'Bribe?':<8} {'Bribe$':<8} {'Accept?':<8} {'Inspect?':<9} {'Caught?':<8} {'Net$':<8}"
    )
    print(f"{'-' * 100}")

    for round_num in range(rounds):
        # Build bag and declaration
        declaration, actual_goods, is_honest = build_bag_and_declaration(silas, history)

        # Get declared goods
        from core.mechanics.goods import GOOD_BY_ID

        declared_good = GOOD_BY_ID[declaration.good_id]
        declared_goods = [declared_good] * declaration.count

        # Detect sheriff type
        from core.systems.game_master_state import get_game_master_state

        game_state = get_game_master_state()
        full_history = game_state.get_history_for_tier(None)
        sheriff_type = silas._detect_sheriff_type(full_history)

        # Check if Silas offers bribe
        bribe_offered = 0
        if silas.should_offer_proactive_bribe(
            sheriff.authority, sheriff.reputation, actual_goods, declared_goods
        ):
            bribe_offered = silas.calculate_proactive_bribe(
                actual_goods, not is_honest, sheriff.authority, declared_goods
            )
            bribes_attempted += 1

        # Sheriff decides (Smart Adaptive strategy)
        should_inspect, accept_bribe = smart_adaptive(
            silas, bribe_offered, declaration, actual_goods, history
        )

        # Process outcome
        gold_earned = 0
        gold_lost = 0
        caught = False

        if accept_bribe:
            # Bribe accepted
            gold_lost += bribe_offered
            bribes_accepted += 1
            bonus_result = calculate_contraband_bonus(actual_goods)
            gold_earned += bonus_result["bonus_value"]
            times_passed += 1
        elif should_inspect:
            # Inspected
            if not is_honest:
                caught = True
                times_caught += 1
                contraband_value = sum(
                    g.value for g in actual_goods if not g.is_legal()
                )
                gold_lost += contraband_value * 2
            else:
                times_passed += 1
                goods_value = sum(g.value for g in actual_goods)
                gold_earned += goods_value * 2  # Sheriff pays penalty
        else:
            # Passed without inspection
            times_passed += 1
            bonus_result = calculate_contraband_bonus(actual_goods)
            gold_earned += bonus_result["bonus_value"]

        total_gold_earned += gold_earned
        total_gold_lost += gold_lost
        net_round = gold_earned - gold_lost

        # Record in history
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

        # Log detection
        detection_log.append(
            {
                "round": round_num + 1,
                "detected": sheriff_type,
                "honest": is_honest,
                "bribe_offered": bribe_offered,
                "bribe_accepted": accept_bribe,
                "inspected": should_inspect,
                "caught": caught,
                "net": net_round,
            }
        )

        # Print round details
        print(
            f"{round_num + 1:<6} {sheriff_type:<10} {str(is_honest):<8} "
            f"{str(bribe_offered > 0):<8} {bribe_offered if bribe_offered > 0 else '-':<8} "
            f"{str(accept_bribe):<8} {str(should_inspect):<9} {str(caught):<8} "
            f"{net_round:>+7}g"
        )

    # Final results
    net_profit = total_gold_earned - total_gold_lost
    success_rate = (
        times_passed / (times_passed + times_caught)
        if (times_passed + times_caught) > 0
        else 0
    )
    bribe_success_rate = (
        bribes_accepted / bribes_attempted if bribes_attempted > 0 else 0
    )

    print(f"\n{'=' * 100}")
    print("FINAL RESULTS")
    print(f"{'=' * 100}")
    print(f"Net Profit:        {net_profit:>6}g")
    print(f"Gold Earned:       {total_gold_earned:>6}g")
    print(f"Gold Lost:         {total_gold_lost:>6}g")
    print(f"Success Rate:      {success_rate:>6.1%}")
    print(f"Times Passed:      {times_passed:>6}")
    print(f"Times Caught:      {times_caught:>6}")
    print(f"Bribes Attempted:  {bribes_attempted:>6}")
    print(f"Bribes Accepted:   {bribes_accepted:>6} ({bribe_success_rate:.1%})")
    print(f"{'=' * 100}\n")

    # Analyze detection patterns
    print("DETECTION ANALYSIS")
    print(f"{'=' * 100}")

    from collections import Counter

    detection_counts = Counter(d["detected"] for d in detection_log)
    print("Sheriff Type Detections:")
    for sheriff_type, count in detection_counts.most_common():
        print(
            f"  {sheriff_type}: {count} rounds ({count / len(detection_log) * 100:.1f}%)"
        )

    print("\nStrategy by Detection:")
    for sheriff_type in ["corrupt", "greedy", "strict", "unknown"]:
        rounds_detected = [d for d in detection_log if d["detected"] == sheriff_type]
        if rounds_detected:
            honest_count = sum(1 for d in rounds_detected if d["honest"])
            bribe_count = sum(1 for d in rounds_detected if d["bribe_offered"] > 0)
            print(f"  {sheriff_type}:")
            print(
                f"    Played honest: {honest_count}/{len(rounds_detected)} ({honest_count / len(rounds_detected) * 100:.1f}%)"
            )
            print(
                f"    Offered bribes: {bribe_count}/{len(rounds_detected)} ({bribe_count / len(rounds_detected) * 100:.1f}%)"
            )

    print(f"\n{'=' * 100}\n")

    return {
        "net_profit": net_profit,
        "success_rate": success_rate,
        "bribes_attempted": bribes_attempted,
        "bribes_accepted": bribes_accepted,
        "bribe_success_rate": bribe_success_rate,
        "detection_log": detection_log,
    }


if __name__ == "__main__":
    results = simulate_silas_vs_smart_detailed(rounds=50)

    if results:
        print("TEST ANALYSIS")
        print("=" * 100)

        # Check if Silas is profitable
        if results["net_profit"] > 0:
            print(f"✅ Silas is profitable ({results['net_profit']}g)")
        else:
            print(f"❌ Silas is losing money ({results['net_profit']}g)")

        # Check success rate
        if results["success_rate"] > 0.60:
            print(f"✅ Good success rate ({results['success_rate']:.1%})")
        else:
            print(f"⚠️  Low success rate ({results['success_rate']:.1%})")

        # Check bribe effectiveness
        if results["bribe_success_rate"] > 0.30:
            print(
                f"✅ Bribes are effective ({results['bribe_success_rate']:.1%} acceptance)"
            )
        else:
            print(
                f"❌ Bribes are ineffective ({results['bribe_success_rate']:.1%} acceptance)"
            )

        print("=" * 100)
