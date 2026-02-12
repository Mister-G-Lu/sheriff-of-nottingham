"""
Merchant Performance Simulation

Runs 100-round games with different sheriff strategies to compare merchant performance.
This helps identify which merchant strategies are most effective against different playstyles.

Sheriff Types:
1. "Trigger Happy" - Inspects whenever bribed, otherwise lets pass (suspicious but dumb)
2. "Corrupt & Greedy" - Threatens everyone, accepts all bribes (greedy but predictable)
3. "Random" - 50/50 inspect/pass (baseline)
4. "Smart" - Adapts based on patterns (realistic player)

IMPORTANT FOR SILAS VOSS:
This test properly records events to the game master state using game_state.record_event().
This is CRITICAL for Silas Voss's sheriff detection to work correctly. Without recording
to game state, Silas will always detect sheriffs as "unknown" and his performance will be
significantly worse.
"""

from dataclasses import dataclass

from ai_strategy.ai_sheriffs import (
    corrupt_greedy,
    greedy,
    monte_carlo,
    smart_adaptive,
    strict_inspector,
    trigger_happy,
    vengeful,
)
from core.players.merchant_loader import load_merchants
from core.players.merchants import Merchant
from core.players.sheriff import Sheriff
from core.systems.game_master_state import reset_game_master_state

# Import simulate_encounter helper (works for both pytest and direct script execution)
try:
    from tests.simulations.simulation_helpers import simulate_encounter
except ModuleNotFoundError:
    from simulation_helpers import simulate_encounter


@dataclass
class MerchantStats:
    """Track performance stats for a merchant."""

    name: str
    total_gold_earned: int = 0
    total_gold_lost: int = 0  # Fines + bribes paid
    times_caught: int = 0
    times_passed: int = 0
    bribes_attempted: int = 0  # How many times they offered a bribe
    bribes_accepted: int = 0  # How many times sheriff accepted
    contraband_smuggled: int = 0

    @property
    def net_profit(self) -> int:
        return self.total_gold_earned - self.total_gold_lost

    @property
    def success_rate(self) -> float:
        total = self.times_caught + self.times_passed
        return self.times_passed / total if total > 0 else 0.0


# Sheriff strategies now imported from ai_strategy.ai_sheriffs module
# Encounter simulation logic moved to tests/simulations/simulation_helpers.py


def run_simulation(
    sheriff_strategy_name: str, sheriff_strategy: callable, rounds: int = 100
) -> dict[str, MerchantStats]:
    """Run a full simulation with the given sheriff strategy."""
    # Load all merchants
    merchants = load_merchants()
    if not merchants:
        print("No merchants found!")
        return {}

    # Initialize stats
    stats = {m.name: MerchantStats(name=m.name) for m in merchants}

    # Initialize sheriff
    sheriff = Sheriff(reputation=5, authority=2)

    # Reset game state
    reset_game_master_state()
    history = []

    # Run rounds
    for _round_num in range(rounds):
        # Each merchant gets a turn
        for merchant in merchants:
            try:
                result = simulate_encounter(
                    merchant, sheriff, sheriff_strategy, history
                )

                # Update stats
                merchant_stats = stats[merchant.name]
                merchant_stats.total_gold_earned += result["gold_earned"]
                merchant_stats.total_gold_lost += result["gold_lost"]

                if result["caught"]:
                    merchant_stats.times_caught += 1
                if result["passed"]:
                    merchant_stats.times_passed += 1
                if result["bribe_attempted"]:
                    merchant_stats.bribes_attempted += 1
                if result["bribed"]:
                    merchant_stats.bribes_accepted += 1
                if result["contraband"]:
                    merchant_stats.contraband_smuggled += 1

                # Add to history
                history.append(result)
            except Exception as e:
                # Skip this merchant if there's an error
                print(f"Error with {merchant.name}: {e}")
                continue

    return stats


def print_results(sheriff_name: str, stats: dict[str, MerchantStats]):
    """Print simulation results in a nice format."""
    print(f"\n{'=' * 80}")
    print(f"SIMULATION RESULTS: {sheriff_name}")
    print(f"{'=' * 80}")

    # Sort by net profit
    sorted_merchants = sorted(stats.values(), key=lambda s: s.net_profit, reverse=True)

    print(
        f"\n{'Merchant':<25} {'Net Profit':<12} {'Success':<10} {'Caught':<8} {'Bribe Try':<11} {'Accepted':<10}"
    )
    print(f"{'-' * 90}")

    for merchant_stats in sorted_merchants:
        bribe_success_rate = (
            (merchant_stats.bribes_accepted / merchant_stats.bribes_attempted * 100)
            if merchant_stats.bribes_attempted > 0
            else 0
        )
        print(
            f"{merchant_stats.name:<25} "
            f"{merchant_stats.net_profit:>10}g  "
            f"{merchant_stats.success_rate:>7.1%}  "
            f"{merchant_stats.times_caught:>6}  "
            f"{merchant_stats.bribes_attempted:>9}  "
            f"{merchant_stats.bribes_accepted:>8} ({bribe_success_rate:>3.0f}%)"
        )

    print(f"\n{'=' * 80}")
    print(
        f"Winner: {sorted_merchants[0].name} with {sorted_merchants[0].net_profit}g profit!"
    )
    print(f"{'=' * 80}\n")


def main():
    """Run all simulations and compare results."""
    print("\n" + "=" * 80)
    print("MERCHANT STRATEGY PERFORMANCE SIMULATION")
    print("Running 100 rounds per sheriff type...")
    print("=" * 80)

    sheriff_strategies = {
        "Strict Inspector (Inspects EVERYONE)": strict_inspector,
        "Trigger Happy (Inspects all bribes)": trigger_happy,
        "Corrupt & Greedy (Accepts all bribes)": corrupt_greedy,
        "Greedy (Demands high bribes 50%+)": greedy,
        "Smart (Adaptive player)": smart_adaptive,
        "Vengeful (Remembers liars)": vengeful,
        "Monte Carlo (Probabilistic/Optimal)": monte_carlo,
    }

    all_results = {}

    for sheriff_name, sheriff_strategy in sheriff_strategies.items():
        print(f"\nRunning simulation: {sheriff_name}...")
        stats = run_simulation(sheriff_name, sheriff_strategy, rounds=100)
        all_results[sheriff_name] = stats
        print_results(sheriff_name, stats)

    # Summary comparison
    print("\n" + "=" * 80)
    print("OVERALL WINNER BY SHERIFF TYPE")
    print("=" * 80)
    for sheriff_name, stats in all_results.items():
        winner = max(stats.values(), key=lambda s: s.net_profit)
        print(f"{sheriff_name:<40} → {winner.name} ({winner.net_profit}g)")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
