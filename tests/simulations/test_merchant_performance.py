"""
Merchant Performance Simulation

Runs 100-round games with different sheriff strategies to compare merchant performance.
This helps identify which merchant strategies are most effective against different playstyles.

Sheriff Types:
1. "Trigger Happy" - Inspects whenever bribed, otherwise lets pass (suspicious but dumb)
2. "Corrupt & Greedy" - Threatens everyone, accepts all bribes (greedy but predictable)
3. "Random" - 50/50 inspect/pass (baseline)
4. "Smart" - Adapts based on patterns (realistic player)
"""

import random
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List

from core.players.merchants import Merchant, InformationBroker, load_merchants
from core.players.sheriff import Sheriff
from core.mechanics.bag_builder import build_bag_and_declaration
from core.mechanics.inspection import handle_inspection, handle_pass_without_inspection
from core.mechanics.goods import Good
from core.systems.game_master_state import reset_game_master_state, get_game_master_state


@dataclass
class MerchantStats:
    """Track performance stats for a merchant."""
    name: str
    total_gold_earned: int = 0
    total_gold_lost: int = 0  # Fines + bribes paid
    times_caught: int = 0
    times_passed: int = 0
    bribes_attempted: int = 0  # How many times they offered a bribe
    bribes_accepted: int = 0   # How many times sheriff accepted
    contraband_smuggled: int = 0
    
    @property
    def net_profit(self) -> int:
        return self.total_gold_earned - self.total_gold_lost
    
    @property
    def success_rate(self) -> float:
        total = self.times_caught + self.times_passed
        return self.times_passed / total if total > 0 else 0.0


class SheriffStrategy:
    """Different sheriff playstyles for simulation."""
    
    @staticmethod
    def trigger_happy(merchant: Merchant, bribe_offered: int, declaration: dict, 
                     actual_goods: List[Good], history: List[dict]) -> tuple[bool, bool]:
        """
        Trigger Happy Sheriff: Inspects whenever bribed, otherwise lets pass.
        Logic: "If they're bribing, they must be hiding something!"
        
        Returns: (should_inspect, accept_bribe)
        """
        if bribe_offered > 0:
            # Suspicious! Inspect them!
            return True, False  # Inspect, reject bribe
        else:
            # No bribe? Must be honest, let them pass
            return False, False  # Don't inspect
    
    @staticmethod
    def corrupt_greedy(merchant: Merchant, bribe_offered: int, declaration: dict,
                      actual_goods: List[Good], history: List[dict]) -> tuple[bool, bool]:
        """
        Corrupt & Greedy Sheriff: Threatens everyone, accepts all bribes.
        Logic: "Everyone pays, or I inspect!"
        
        Returns: (should_inspect, accept_bribe)
        """
        if bribe_offered > 0:
            # Take the bribe!
            return False, True  # Don't inspect, accept bribe
        else:
            # No bribe? Threaten them! (50% chance they'll offer one)
            # For simulation, we'll just inspect if no bribe
            return True, False  # Inspect
    
    @staticmethod
    def smart_sheriff(merchant: Merchant, bribe_offered: int, declaration: dict,
                     actual_goods: List[Good], history: List[dict]) -> tuple[bool, bool]:
        """
        Smart Sheriff: Adapts based on patterns (realistic player).
        - Tracks which merchants lie frequently
        - Accepts small bribes, rejects suspicious ones
        - Inspects more when catching smugglers
        
        Returns: (should_inspect, accept_bribe)
        """
        # Analyze recent history
        recent = history[-10:] if len(history) >= 10 else history
        
        if not recent:
            # No history, use moderate strategy
            if bribe_offered > 0:
                return random.random() < 0.4, random.random() < 0.6
            return random.random() < 0.5, False
        
        # Calculate catch rate
        inspections = [h for h in recent if h.get('opened', False)]
        catches = [h for h in inspections if h.get('caught_lie', False)]
        catch_rate = len(catches) / len(inspections) if inspections else 0.5
        
        # If catching lots of smugglers, inspect more
        if catch_rate > 0.6:
            inspection_rate = 0.7
        elif catch_rate < 0.3:
            inspection_rate = 0.3
        else:
            inspection_rate = 0.5
        
        if bribe_offered > 0:
            # Sheriff can only see DECLARED goods, not actual goods!
            # Calculate value based on what merchant CLAIMS to carry
            from core.mechanics.goods import GOOD_BY_ID
            declared_good = GOOD_BY_ID[declaration.good_id]
            declared_value = declared_good.value * declaration.count
            
            # Suspicious high bribe? (More than 40% of declared value)
            # This could mean they're hiding expensive contraband
            if bribe_offered > declared_value * 0.4:
                return True, False  # Suspicious, inspect
            
            # Small bribe? (Less than 30% of declared value)
            # Seems reasonable, accept it
            if bribe_offered < declared_value * 0.3:
                return False, True  # Accept small bribe
            
            # Medium bribe? (30-40% of declared value)
            # Uncertain, use adaptive inspection rate
            return random.random() < inspection_rate, random.random() < 0.5
        else:
            # No bribe, use adaptive inspection rate
            return random.random() < inspection_rate, False


def simulate_encounter(merchant: Merchant, sheriff: Sheriff, sheriff_strategy: callable,
                      history: List[dict]) -> Dict:
    """Simulate a single merchant encounter."""
    # Build bag and declaration
    declaration, actual_goods, is_honest = build_bag_and_declaration(merchant, history)
    
    # Get the declared good from GOOD_BY_ID
    from core.mechanics.goods import GOOD_BY_ID
    declared_good = GOOD_BY_ID[declaration.good_id]
    declared_goods = [declared_good] * declaration.count
    
    # Check if merchant offers proactive bribe
    bribe_offered = 0
    if merchant.should_offer_proactive_bribe(sheriff.authority, sheriff.reputation, 
                                             actual_goods, declared_goods):
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
        gold_earned += sum(g.value for g in actual_goods)
    elif should_inspect:
        # Sheriff inspects - NO bribe is paid (inspection instead of bribe)
        if not is_honest:
            # Caught lying!
            caught = True
            # Pay fine (double contraband value)
            contraband_value = sum(g.value for g in actual_goods if not g.is_legal())
            gold_lost += contraband_value * 2
            # Bribe is NOT paid when inspected
        else:
            # Honest, goods pass
            # RULE: Sheriff must pay merchant the value of goods for wrongful inspection
            goods_value = sum(g.value for g in actual_goods)
            gold_earned += goods_value  # Keep the goods
            gold_earned += goods_value  # Sheriff pays penalty (DOUBLE profit!)
            # Bribe is NOT paid when inspected
    else:
        # Sheriff lets pass without inspection (no bribe was offered)
        gold_earned += sum(g.value for g in actual_goods)
    
    return {
        'merchant_name': merchant.name,
        'gold_earned': gold_earned,
        'gold_lost': gold_lost,
        'caught': caught,
        'passed': not caught,
        'bribe_attempted': bribe_offered > 0,  # Did they try to bribe?
        'bribe_offered': bribe_offered,        # Amount offered (for Silas detection)
        'bribed': accept_bribe,                # Did sheriff accept?
        'bribe_accepted': accept_bribe,        # Alias for compatibility
        'contraband': not is_honest,
        'opened': should_inspect,
        'caught_lie': caught,
    }


def run_simulation(sheriff_strategy_name: str, sheriff_strategy: callable, 
                  rounds: int = 100) -> Dict[str, MerchantStats]:
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
    for round_num in range(rounds):
        # Each merchant gets a turn
        for merchant in merchants:
            try:
                result = simulate_encounter(merchant, sheriff, sheriff_strategy, history)
                
                # Update stats
                merchant_stats = stats[merchant.name]
                merchant_stats.total_gold_earned += result['gold_earned']
                merchant_stats.total_gold_lost += result['gold_lost']
                
                if result['caught']:
                    merchant_stats.times_caught += 1
                if result['passed']:
                    merchant_stats.times_passed += 1
                if result['bribe_attempted']:
                    merchant_stats.bribes_attempted += 1
                if result['bribed']:
                    merchant_stats.bribes_accepted += 1
                if result['contraband']:
                    merchant_stats.contraband_smuggled += 1
                
                # Add to history
                history.append(result)
            except Exception as e:
                # Skip this merchant if there's an error
                print(f"Error with {merchant.name}: {e}")
                continue
    
    return stats


def print_results(sheriff_name: str, stats: Dict[str, MerchantStats]):
    """Print simulation results in a nice format."""
    print(f"\n{'='*80}")
    print(f"SIMULATION RESULTS: {sheriff_name}")
    print(f"{'='*80}")
    
    # Sort by net profit
    sorted_merchants = sorted(stats.values(), key=lambda s: s.net_profit, reverse=True)
    
    print(f"\n{'Merchant':<25} {'Net Profit':<12} {'Success':<10} {'Caught':<8} {'Bribe Try':<11} {'Accepted':<10}")
    print(f"{'-'*90}")
    
    for merchant_stats in sorted_merchants:
        bribe_success_rate = (merchant_stats.bribes_accepted / merchant_stats.bribes_attempted * 100) if merchant_stats.bribes_attempted > 0 else 0
        print(f"{merchant_stats.name:<25} "
              f"{merchant_stats.net_profit:>10}g  "
              f"{merchant_stats.success_rate:>7.1%}  "
              f"{merchant_stats.times_caught:>6}  "
              f"{merchant_stats.bribes_attempted:>9}  "
              f"{merchant_stats.bribes_accepted:>8} ({bribe_success_rate:>3.0f}%)")
    
    print(f"\n{'='*80}")
    print(f"Winner: {sorted_merchants[0].name} with {sorted_merchants[0].net_profit}g profit!")
    print(f"{'='*80}\n")


def main():
    """Run all simulations and compare results."""
    print("\n" + "="*80)
    print("MERCHANT STRATEGY PERFORMANCE SIMULATION")
    print("Running 100 rounds per sheriff type...")
    print("="*80)
    
    sheriff_strategies = {
        "Trigger Happy (Inspects all bribes)": SheriffStrategy.trigger_happy,
        "Corrupt & Greedy (Accepts all bribes)": SheriffStrategy.corrupt_greedy,
        "Smart (Adaptive player)": SheriffStrategy.smart_sheriff,
    }
    
    all_results = {}
    
    for sheriff_name, sheriff_strategy in sheriff_strategies.items():
        print(f"\nRunning simulation: {sheriff_name}...")
        stats = run_simulation(sheriff_name, sheriff_strategy, rounds=100)
        all_results[sheriff_name] = stats
        print_results(sheriff_name, stats)
    
    # Summary comparison
    print("\n" + "="*80)
    print("OVERALL WINNER BY SHERIFF TYPE")
    print("="*80)
    for sheriff_name, stats in all_results.items():
        winner = max(stats.values(), key=lambda s: s.net_profit)
        print(f"{sheriff_name:<40} → {winner.name} ({winner.net_profit}g)")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
