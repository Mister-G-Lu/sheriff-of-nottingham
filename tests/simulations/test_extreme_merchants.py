"""
Test Extreme Merchants Simulation

Tests two extreme merchant personalities:
1. Honest Abe - Always tells the truth (honesty_bias: 10, risk_tolerance: 0)
2. Lying Larry - Almost always lies (honesty_bias: 1, risk_tolerance: 10, greed: 10)

This helps us understand the boundaries of the strategy system.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.players.merchants import Merchant
from core.mechanics.goods import GOOD_BY_ID
from tests.simulations.test_merchant_performance import (
    SheriffStrategy, simulate_encounter, MerchantStats, print_results, run_simulation
)


def load_test_merchants():
    """Load the test merchants (Honest Abe and Lying Larry)."""
    import json
    
    merchants = []
    
    # Load Honest Abe
    abe_path = project_root / "characters" / "data" / "test_honest_abe.json"
    with open(abe_path) as f:
        abe_data = json.load(f)
        abe = Merchant(
            id=abe_data["id"],
            name=abe_data["name"],
            intro=abe_data["intro"],
            tells_honest=abe_data["tells_honest"],
            tells_lying=abe_data["tells_lying"],
            bluff_skill=abe_data["bluff_skill"],
            risk_tolerance=abe_data["risk_tolerance"],
            greed=abe_data["greed"],
            honesty_bias=abe_data["honesty_bias"]
        )
        merchants.append(abe)
    
    # Load Lying Larry
    larry_path = project_root / "characters" / "data" / "test_lying_larry.json"
    with open(larry_path) as f:
        larry_data = json.load(f)
        larry = Merchant(
            id=larry_data["id"],
            name=larry_data["name"],
            intro=larry_data["intro"],
            tells_honest=larry_data["tells_honest"],
            tells_lying=larry_data["tells_lying"],
            bluff_skill=larry_data["bluff_skill"],
            risk_tolerance=larry_data["risk_tolerance"],
            greed=larry_data["greed"],
            honesty_bias=larry_data["honesty_bias"]
        )
        merchants.append(larry)
    
    return merchants


def main():
    """Run simulation with extreme test merchants."""
    print("\n" + "="*80)
    print("EXTREME MERCHANTS TEST SIMULATION")
    print("Testing boundary cases: Always Honest vs Always Lying")
    print("="*80)
    
    sheriff_strategies = {
        "Trigger Happy (Inspects all bribes)": SheriffStrategy.trigger_happy,
        "Corrupt & Greedy (Accepts all bribes)": SheriffStrategy.corrupt_greedy,
        "Smart (Adaptive player)": SheriffStrategy.smart_sheriff,
    }
    
    for sheriff_name, sheriff_strategy in sheriff_strategies.items():
        print(f"\n{'='*80}")
        print(f"Testing against: {sheriff_name}")
        print(f"{'='*80}")
        
        # Load test merchants
        test_merchants = load_test_merchants()
        
        # Run 100 rounds for each merchant
        for merchant in test_merchants:
            print(f"\nTesting {merchant.name}...")
            print(f"  Stats: Honesty={merchant.honesty_bias}, Risk={merchant.risk_tolerance}, "
                  f"Greed={merchant.greed}, Bluff={merchant.bluff_skill}")
            
            # Run simulation (simplified version)
            from core.players.sheriff import Sheriff
            from core.systems.game_master_state import reset_game_master_state
            
            reset_game_master_state()
            sheriff = Sheriff(reputation=5, authority=2)
            history = []
            
            stats = MerchantStats(name=merchant.name)
            strategy_counts = {'honest': 0, 'legal_lie': 0, 'mixed': 0, 'contraband_low': 0, 'contraband_high': 0}
            
            for round_num in range(100):
                try:
                    from core.mechanics.bag_builder import build_bag_and_declaration
                    declaration, actual_goods, is_honest = build_bag_and_declaration(merchant, history)
                    
                    # Track which strategy was used
                    if hasattr(declaration, 'strategy'):
                        strategy_counts[declaration.strategy] = strategy_counts.get(declaration.strategy, 0) + 1
                    elif is_honest:
                        strategy_counts['honest'] += 1
                    else:
                        strategy_counts['contraband_low'] += 1  # Default assumption
                    
                    # Check if merchant offers proactive bribe
                    declared_goods = [GOOD_BY_ID[declaration.good_id]] * declaration.count
                    bribe_offered = 0
                    if merchant.should_offer_proactive_bribe(sheriff.authority, sheriff.reputation, 
                                                             actual_goods, declared_goods):
                        bribe_offered = merchant.calculate_proactive_bribe(
                            actual_goods, not is_honest, sheriff.authority, declared_goods
                        )
                    
                    # Sheriff decides
                    should_inspect, accept_bribe = sheriff_strategy(
                        merchant, bribe_offered, declaration, actual_goods, history
                    )
                    
                    # Process outcome
                    gold_earned = 0
                    gold_lost = 0
                    caught = False
                    
                    if accept_bribe:
                        gold_lost += bribe_offered
                        gold_earned += sum(g.value for g in actual_goods)
                    elif should_inspect:
                        if not is_honest:
                            caught = True
                            contraband_value = sum(g.value for g in actual_goods if not g.is_legal())
                            gold_lost += contraband_value * 2
                        else:
                            goods_value = sum(g.value for g in actual_goods)
                            gold_earned += goods_value * 2  # Sheriff penalty
                    else:
                        gold_earned += sum(g.value for g in actual_goods)
                    
                    # Update stats
                    stats.total_gold_earned += gold_earned
                    stats.total_gold_lost += gold_lost
                    if caught:
                        stats.times_caught += 1
                    else:
                        stats.times_passed += 1
                    if bribe_offered > 0:
                        stats.bribes_attempted += 1
                    if accept_bribe:
                        stats.bribes_accepted += 1
                    if not is_honest:
                        stats.contraband_smuggled += 1
                    
                    # Add to history
                    history.append({
                        'gold_earned': gold_earned,
                        'gold_lost': gold_lost,
                        'caught': caught,
                        'bribe_offered': bribe_offered,
                        'bribe_accepted': accept_bribe,
                        'contraband': not is_honest,
                        'opened': should_inspect,
                        'caught_lie': caught,
                    })
                    
                except Exception as e:
                    print(f"    Error in round {round_num}: {e}")
                    continue
            
            # Print results
            print(f"\n  Results after 100 rounds:")
            print(f"    Net Profit: {stats.net_profit}g")
            print(f"    Success Rate: {stats.success_rate:.1%}")
            print(f"    Times Caught: {stats.times_caught}")
            print(f"    Times Passed: {stats.times_passed}")
            print(f"    Contraband Smuggled: {stats.contraband_smuggled}")
            print(f"    Bribes Attempted: {stats.bribes_attempted}")
            print(f"    Bribes Accepted: {stats.bribes_accepted} ({stats.bribes_accepted/stats.bribes_attempted*100:.0f}%)" if stats.bribes_attempted > 0 else "    Bribes Accepted: 0 (0%)")
            print(f"\n  Strategy Distribution:")
            for strategy, count in sorted(strategy_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"    {strategy}: {count} times ({count}%)")
    
    print("\n" + "="*80)
    print("EXTREME MERCHANTS TEST COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
