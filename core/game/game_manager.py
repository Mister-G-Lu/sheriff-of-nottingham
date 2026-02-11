"""
Game Manager - Handles main game loop and merchant encounters
Extracted from main.py to keep it minimal and focused
"""

import random
from core.players.merchant_loader import load_merchants
from core.players.merchants import Merchant
from core.players.sheriff import Sheriff
from core.game.rounds import Declaration
from core.mechanics.goods import GOOD_BY_ID, ALL_LEGAL, ALL_CONTRABAND, Good
from core.mechanics.negotiation import (
    initiate_threat, merchant_respond_to_threat, sheriff_respond_to_bribe,
    merchant_respond_to_counter, resolve_negotiation, NegotiationOutcome
)
from core.systems.reputation import update_sheriff_reputation
from core.mechanics.inspection import handle_inspection, handle_pass_without_inspection
from core.game.game_rules import BAG_SIZE_LIMIT, STARTING_GOLD
from ui.intro import print_intro
from ui.narration import (
    narrate_arrival, show_declaration, show_inspection_result,
    show_threat, show_bribe_offer, show_merchant_refuses, show_merchant_gives_up,
    show_bribe_accepted, show_bribe_rejected, prompt_negotiation_response,
    show_proactive_bribe, prompt_initial_decision
)
from core.systems.game_stats import GameStats
from core.game.end_game import show_end_game_summary
from core.mechanics.black_market import (
    BlackMarketContact, check_black_market_offer, show_black_market_offer,
    prompt_black_market_decision, accept_black_market_deal, reject_black_market_deal,
    add_black_market_ending_note
)


def build_bag_and_declaration(merchant: Merchant, history: list[dict] | None = None) -> tuple[Declaration, list[Good], bool]:
    """Create a bag (true contents) and what the merchant declares using merchant's strategy.
    
    Args:
        merchant: The merchant making the declaration
        history: Optional history of previous encounters for strategic merchants
        
    Returns:
        tuple: (declaration, actual_goods, is_honest)
    """
    # Use merchant's strategic decision-making
    decision = merchant.choose_declaration(history)
    
    declared_id = decision['declared_id']
    declared_count = decision['count']
    actual_ids = decision['actual_ids']
    is_honest = not decision['lie']
    
    # Convert IDs to Good objects
    actual_goods = [GOOD_BY_ID[good_id] for good_id in actual_ids]
    
    declaration = Declaration(good_id=declared_id, count=declared_count)
    return declaration, actual_goods, is_honest


def choose_tell(merchant: Merchant, is_honest: bool) -> str:
    """Pick a random tell line depending on whether the merchant is honest this round."""
    pool = merchant.tells_honest if is_honest else merchant.tells_lying
    return random.choice(pool) if pool else ""


def prompt_inspection(decision_prompt: str = "Inspect the bag or let them pass? [i/p]: ") -> bool:
    """Ask the player whether to inspect (True) or pass (False)."""
    while True:
        choice = input(decision_prompt).strip().lower()
        if choice in {"i", "inspect"}:
            return True
        if choice in {"p", "pass"}:
            return False
        print("Please answer with 'i' to inspect or 'p' to pass.")


def _update_stats_bar(sheriff, stats, merchant_idx, total_merchants):
    """Helper to update the stats bar UI (if available)."""
    try:
        from ui.pygame_ui import get_ui
        ui = get_ui()
        ui.update_stats(sheriff, stats, merchant_idx, total_merchants)
    except ImportError:
        pass  # Terminal mode, no UI


def run_negotiation(sheriff: Sheriff, merchant: Merchant, actual_goods: list[Good], stats: GameStats = None) -> bool:
    """Run the negotiation phase. Returns True if sheriff should inspect, False if bribed."""
    show_threat(merchant)
    
    # Calculate contraband value for merchant's decision-making
    contraband_value = sum(g.value for g in actual_goods if not g.is_legal())
    
    # Merchant decides whether to offer bribe or refuse
    outcome = initiate_threat(merchant, contraband_value, sheriff.authority)
    
    if outcome == "refuse":
        show_merchant_refuses(merchant)
        return True  # Inspect
    
    # Merchant offers initial bribe
    initial_offer = outcome
    show_bribe_offer(merchant, initial_offer, round_number=1)
    
    # Multi-round negotiation loop
    current_offer = initial_offer
    negotiation_round = 1
    
    while True:
        choice, demand = prompt_negotiation_response(current_offer)
        
        if choice == 'accept':
            # Sheriff accepts the bribe
            stats.record_bribe(current_offer)
            show_bribe_accepted(merchant, current_offer)
            sheriff.reputation = max(0, sheriff.reputation - 1)
            print(f"[Sheriff] Gold: +{current_offer}  Reputation: {sheriff.reputation} (-1 for accepting bribe)")
            return False  # Don't inspect
        
        elif choice == 'reject':
            # Sheriff rejects and will inspect
            show_bribe_rejected(merchant)
            return True  # Inspect
        
        elif choice == 'counter':
            # Sheriff demands more gold
            negotiation_round += 1
            merchant_response = merchant_respond_to_counter(
                merchant, demand, contraband_value, negotiation_round, sheriff.authority
            )
            
            if merchant_response == "give_up":
                show_merchant_gives_up(merchant)
                return True  # Inspect
            else:
                # Merchant makes counter-offer
                current_offer = merchant_response
                show_bribe_offer(merchant, current_offer, round_number=negotiation_round)


def run_game():
    """Main game loop - extracted from main.py"""
    # Initialize game state
    sheriff = Sheriff(reputation=5, authority=1)
    stats = GameStats()
    black_market = BlackMarketContact()
    
    # Show intro
    print_intro()
    
    # Load merchants
    merchants = load_merchants(limit=8)
    if not merchants:
        print("No merchants found in characters/data/. Add .json files to characters/data/ folder.")
        return
    
    # Track history for strategic merchants (like Silas)
    encounter_history = []
    
    # Update stats bar with initial state
    _update_stats_bar(sheriff, stats, 0, len(merchants))
    
    for idx, merchant in enumerate(merchants, 1):
        # Update stats bar for current merchant
        _update_stats_bar(sheriff, stats, idx, len(merchants))
        
        # Merchant arrives
        narrate_arrival(merchant)
        
        # Build bag and declaration using merchant's strategy
        declaration, actual_goods, is_honest = build_bag_and_declaration(merchant, encounter_history)
        
        # Show tell
        tell = choose_tell(merchant, is_honest)
        if tell:
            print(f"You notice: {tell}.")
        print()
        
        show_declaration(merchant, declaration)
        
        # Check if merchant offers proactive bribe (before threat)
        declared_goods = [GOOD_BY_ID[declaration.good_id]] * declaration.count
        offers_proactive = merchant.should_offer_proactive_bribe(
            sheriff.authority, sheriff.reputation, actual_goods, declared_goods
        )
        
        proactive_bribe_amount = 0
        if offers_proactive:
            proactive_bribe_amount = merchant.calculate_proactive_bribe(
                actual_goods, not is_honest, sheriff.authority
            )
            show_proactive_bribe(merchant, proactive_bribe_amount, not is_honest)
        
        # Player decides what to do
        decision = prompt_initial_decision(offers_proactive, proactive_bribe_amount)
        
        # Track if bag was opened for history
        was_opened = False
        caught_lie = False
        
        if decision == 'accept':
            # Accept proactive bribe
            stats.record_bribe(proactive_bribe_amount)
            show_bribe_accepted(merchant, proactive_bribe_amount)
            sheriff.reputation = max(0, sheriff.reputation - 1)
            print(f"[Sheriff] Gold: +{proactive_bribe_amount}  Reputation: {sheriff.reputation} (-1 for accepting bribe)")
            show_inspection_result(merchant, False, False)
            stats.record_pass(is_honest)
            was_opened = False
            caught_lie = False
            # Update stats bar after bribe
            _update_stats_bar(sheriff, stats, idx, len(merchants))
            print()
            
        elif decision == 'pass':
            # Let them pass without inspection
            result = handle_pass_without_inspection(merchant, actual_goods, 
                                                   {'good_id': declaration.good_id, 'count': declaration.count})
            stats.record_pass(result['was_honest'])
            show_inspection_result(merchant, False, False)
            
            # Merchant sells all goods that passed through
            goods_value = sum(g.value for g in result['goods_passed'])
            merchant.gold += goods_value
            
            update_sheriff_reputation(sheriff, False, result['was_honest'], stats, actual_goods)
            was_opened = False
            caught_lie = not result['was_honest']
            
            print(f"[{merchant.name}] Goods sold for {goods_value} gold. Total gold: {merchant.gold}")
            
        elif decision == 'inspect':
            # Inspect immediately (no negotiation) - Apply proper Sheriff of Nottingham rules
            result = handle_inspection(merchant, actual_goods, 
                                     {'good_id': declaration.good_id, 'count': declaration.count}, sheriff)
            
            stats.record_inspection(result['was_honest'], result['caught_lie'])
            show_inspection_result(merchant, True, result['caught_lie'])
            
            # Display inspection results
            print(f"\n{'='*60}")
            print(f"🔍 INSPECTION RESULTS - {merchant.name}'s Bag")
            print(f"{'='*60}")
            print(f"\n📋 DECLARED: {declaration.count}x {declaration.good_id}")
            print(f"\n🎒 ACTUAL BAG CONTENTS:")
            for i, good in enumerate(actual_goods, 1):
                contraband_marker = " ⚠️ CONTRABAND" if good.is_contraband() else ""
                print(f"   {i}. {good.id} (value: {good.value}g){contraband_marker}")
            
            # Show if merchant's bluff succeeded
            if not result['was_honest'] and not result['caught_lie']:
                print(f"\n🎭 {merchant.name}'s BLUFF SUCCEEDED!")
                print(f"   Despite the discrepancy, you didn't notice anything suspicious.")
                print(f"   All goods pass through undetected.")
                goods_value = sum(g.value for g in result['goods_passed'])
                merchant.gold += goods_value
                print(f"\n💰 [{merchant.name}] Sold all goods for {goods_value}g. Total: {merchant.gold}g")
                print(f"{'='*60}\n")
            elif result['was_honest']:
                print(f"\n✅ VERDICT: HONEST - Declaration matches contents!")
                print(f"   All {len(result['goods_passed'])} goods pass through.")
                goods_value = sum(g.value for g in result['goods_passed'])
                merchant.gold += goods_value
                print(f"\n💰 [{merchant.name}] Sold goods for {goods_value}g. Total: {merchant.gold}g")
            else:
                print(f"\n❌ VERDICT: LYING - Declaration does NOT match contents!")
                
                if result['goods_passed']:
                    print(f"\n✓ ALLOWED THROUGH ({len(result['goods_passed'])} items - truthfully declared):")
                    for good in result['goods_passed']:
                        print(f"   • {good.id} (value: {good.value}g)")
                
                if result['goods_confiscated']:
                    print(f"\n⛔ CONFISCATED ({len(result['goods_confiscated'])} items - undeclared):")
                    total_confiscated_value = 0
                    for good in result['goods_confiscated']:
                        contraband_marker = " [CONTRABAND]" if good.is_contraband() else " [LEGAL]"
                        print(f"   • {good.id} (value: {good.value}g){contraband_marker}")
                        total_confiscated_value += good.value
                    
                    print(f"\n💸 PENALTY: {result['penalty_paid']}g (50% of {total_confiscated_value}g confiscated value)")
                    print(f"   [{merchant.name}] Gold remaining: {merchant.gold}g")
                
                if result['goods_passed']:
                    goods_value = sum(g.value for g in result['goods_passed'])
                    merchant.gold += goods_value
                    print(f"\n💰 [{merchant.name}] Sold allowed goods for {goods_value}g. Total: {merchant.gold}g")
            
            print(f"{'='*60}\n")
            
            update_sheriff_reputation(sheriff, True, result['was_honest'], stats, actual_goods)
            was_opened = True
            caught_lie = result['caught_lie']
            
        elif decision == 'threaten':
            # Threaten inspection (may trigger negotiation)
            should_inspect = run_negotiation(sheriff, merchant, actual_goods, stats)
            
            if should_inspect:
                # Inspect the bag with proper rules
                result = handle_inspection(merchant, actual_goods, 
                                         {'good_id': declaration.good_id, 'count': declaration.count}, sheriff)
                
                stats.record_inspection(result['was_honest'], result['caught_lie'])
                show_inspection_result(merchant, True, result['caught_lie'])
                
                # Display detailed inspection results (same as direct inspect)
                print(f"\n{'='*60}")
                print(f"🔍 INSPECTION RESULTS - {merchant.name}'s Bag")
                print(f"{'='*60}")
                print(f"\n📋 DECLARED: {declaration.count}x {declaration.good_id}")
                print(f"\n🎒 ACTUAL BAG CONTENTS:")
                for i, good in enumerate(actual_goods, 1):
                    contraband_marker = " ⚠️ CONTRABAND" if good.is_contraband() else ""
                    print(f"   {i}. {good.id} (value: {good.value}g){contraband_marker}")
                
                # Show if merchant's bluff succeeded
                if not result['was_honest'] and not result['caught_lie']:
                    print(f"\n🎭 {merchant.name}'s BLUFF SUCCEEDED!")
                    print(f"   Despite the discrepancy, you didn't notice anything suspicious.")
                    print(f"   All goods pass through undetected.")
                    goods_value = sum(g.value for g in result['goods_passed'])
                    merchant.gold += goods_value
                    print(f"\n💰 [{merchant.name}] Sold all goods for {goods_value}g. Total: {merchant.gold}g")
                    print(f"{'='*60}\n")
                elif result['was_honest']:
                    print(f"\n✅ VERDICT: HONEST - Declaration matches contents!")
                    print(f"   All {len(result['goods_passed'])} goods pass through.")
                    goods_value = sum(g.value for g in result['goods_passed'])
                    merchant.gold += goods_value
                    print(f"\n💰 [{merchant.name}] Sold goods for {goods_value}g. Total: {merchant.gold}g")
                else:
                    print(f"\n❌ VERDICT: LYING - Declaration does NOT match contents!")
                    
                    if result['goods_passed']:
                        print(f"\n✓ ALLOWED THROUGH ({len(result['goods_passed'])} items - truthfully declared):")
                        for good in result['goods_passed']:
                            print(f"   • {good.id} (value: {good.value}g)")
                    
                    if result['goods_confiscated']:
                        print(f"\n⛔ CONFISCATED ({len(result['goods_confiscated'])} items - undeclared):")
                        total_confiscated_value = 0
                        for good in result['goods_confiscated']:
                            contraband_marker = " [CONTRABAND]" if good.is_contraband() else " [LEGAL]"
                            print(f"   • {good.id} (value: {good.value}g){contraband_marker}")
                            total_confiscated_value += good.value
                        
                        print(f"\n💸 PENALTY: {result['penalty_paid']}g (50% of {total_confiscated_value}g confiscated value)")
                        print(f"   [{merchant.name}] Gold remaining: {merchant.gold}g")
                    
                    if result['goods_passed']:
                        goods_value = sum(g.value for g in result['goods_passed'])
                        merchant.gold += goods_value
                        print(f"\n💰 [{merchant.name}] Sold allowed goods for {goods_value}g. Total: {merchant.gold}g")
                
                print(f"{'='*60}\n")
                
                update_sheriff_reputation(sheriff, True, result['was_honest'], stats, actual_goods)
                was_opened = True
                caught_lie = result['caught_lie']
            else:
                # Bribe accepted during negotiation, let them pass
                result = handle_pass_without_inspection(merchant, actual_goods,
                                                       {'good_id': declaration.good_id, 'count': declaration.count})
                stats.record_pass(result['was_honest'])
                show_inspection_result(merchant, False, False)
                
                # Merchant sells all goods
                goods_value = sum(g.value for g in result['goods_passed'])
                merchant.gold += goods_value
                print(f"[{merchant.name}] Goods sold for {goods_value} gold. Total: {merchant.gold}g")
                
                was_opened = False
                caught_lie = not result['was_honest']
        
        # Record this encounter in history for strategic merchants
        encounter_history.append({
            'declaration': {'good_id': declaration.good_id, 'count': declaration.count},
            'actual_ids': [g.id for g in actual_goods],
            'opened': was_opened,
            'caught_lie': caught_lie,
        })
    
    # Check for black market offer (if reputation is critically low)
    should_offer, contraband_value = check_black_market_offer(stats, sheriff)
    
    if should_offer and not black_market.has_appeared:
        black_market.has_appeared = True
        show_black_market_offer(black_market, contraband_value, sheriff)
        
        if prompt_black_market_decision():
            accept_black_market_deal(black_market, sheriff)
        else:
            reject_black_market_deal(black_market)
    
    # Show end game summary
    show_end_game_summary(sheriff, stats, black_market)
