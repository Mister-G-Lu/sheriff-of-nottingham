"""
Game Manager - Main game loop orchestrator
Refactored for clarity, testability, and maintainability
"""

from core.players.merchants import load_merchants
from core.players.sheriff import Sheriff
from core.mechanics.goods import GOOD_BY_ID
from core.systems.reputation import update_sheriff_reputation
from core.mechanics.inspection import handle_inspection, handle_pass_without_inspection
from core.game.game_rules import STARTING_GOLD
from core.systems.game_stats import GameStats
from core.systems.game_master_state import get_game_master_state, reset_game_master_state
from core.game.end_game import show_end_game_summary
from ui.intro import print_intro
from ui.narration import narrate_arrival, show_declaration, show_inspection_result, show_proactive_bribe, prompt_initial_decision

# Import extracted modules
from core.mechanics.bag_builder import build_bag_and_declaration, choose_tell
from core.game.merchant_encounter import run_negotiation
from core.game.decision_handling import update_stats_bar
from core.game.inspection_display import (
    show_inspection_header, show_bag_contents, show_bluff_succeeded,
    show_honest_verdict, show_lying_verdict, show_inspection_footer,
    show_tell, show_bribe_accepted_status, show_merchant_sold_goods
)


def process_proactive_bribe(merchant, proactive_bribe_amount, sheriff, stats, idx, total_merchants):
    """Handle proactive bribe acceptance."""
    stats.record_bribe(proactive_bribe_amount)
    sheriff.reputation = max(0, sheriff.reputation - 1)
    show_bribe_accepted_status(proactive_bribe_amount, sheriff.reputation)
    update_stats_bar(sheriff, stats, idx, total_merchants)
    print()


def process_pass_without_inspection(merchant, actual_goods, declaration, stats):
    """Handle merchant passing without inspection."""
    result = handle_pass_without_inspection(
        merchant, actual_goods,
        {'good_id': declaration.good_id, 'count': declaration.count}
    )
    stats.record_pass(result['was_honest'])
    show_inspection_result(merchant, False, False)
    
    goods_value = sum(g.value for g in result['goods_passed'])
    merchant.gold += goods_value
    show_merchant_sold_goods(merchant.name, goods_value, merchant.gold)
    
    return result['was_honest'], False


def display_inspection_results(merchant, declaration, actual_goods, result):
    """Display detailed inspection results using JSON-based messages."""
    show_inspection_header(merchant.name, declaration.count, declaration.good_id)
    show_bag_contents(actual_goods)
    
    if not result['was_honest'] and not result['caught_lie']:
        # Bluff succeeded
        goods_value = sum(g.value for g in result['goods_passed'])
        merchant.gold += goods_value
        show_bluff_succeeded(merchant.name, goods_value, merchant.gold)
    elif result['was_honest']:
        # Honest merchant
        goods_value = sum(g.value for g in result['goods_passed'])
        merchant.gold += goods_value
        show_honest_verdict(len(result['goods_passed']), goods_value, merchant.name, merchant.gold)
    else:
        # Lying merchant caught
        show_lying_verdict(
            result['goods_passed'],
            result['goods_confiscated'],
            result['penalty_paid'],
            merchant.name,
            merchant.gold
        )
        # Add sold goods value if any passed
        if result['goods_passed']:
            goods_value = sum(g.value for g in result['goods_passed'])
            merchant.gold += goods_value
    
    show_inspection_footer()


def process_inspection(merchant, actual_goods, declaration, sheriff, stats):
    """Handle bag inspection with proper rules."""
    result = handle_inspection(
        merchant, actual_goods,
        {'good_id': declaration.good_id, 'count': declaration.count},
        sheriff
    )
    
    stats.record_inspection(result['was_honest'], result['caught_lie'])
    show_inspection_result(merchant, True, result['caught_lie'])
    display_inspection_results(merchant, declaration, actual_goods, result)
    update_sheriff_reputation(sheriff, True, result['was_honest'], stats, actual_goods)
    
    return result['was_honest'], result['caught_lie']


def record_encounter(game_state, merchant, declaration, actual_goods, was_opened, caught_lie, bribe_info):
    """Record encounter in game master state."""
    game_state.record_event(
        merchant_name=merchant.name,
        declared_good=declaration.good_id,
        declared_count=declaration.count,
        actual_goods=[g.id for g in actual_goods],
        was_opened=was_opened,
        caught_lie=caught_lie,
        bribe_offered=bribe_info.get('amount', 0),
        bribe_accepted=bribe_info.get('accepted', False),
        proactive_bribe=bribe_info.get('proactive', False)
    )


def run_game():
    """Main game loop - orchestrates merchant encounters."""
    # Initialize game state
    sheriff = Sheriff(reputation=5, authority=1)
    stats = GameStats()
    reset_game_master_state()
    game_state = get_game_master_state()
    
    # Show intro
    print_intro()
    
    # Load merchants
    merchants = load_merchants(limit=8)
    if not merchants:
        print("No merchants found in characters/data/. Add .json files to characters/data/ folder.")
        return
    
    # Track history for strategic merchants
    encounter_history = []
    
    # Update stats bar with initial state
    update_stats_bar(sheriff, stats, 0, len(merchants))
    
    # Process each merchant
    for idx, merchant in enumerate(merchants, 1):
        update_stats_bar(sheriff, stats, idx, len(merchants))
        
        # Merchant arrives
        narrate_arrival(merchant)
        
        # Build bag and declaration using merchant's strategy
        declaration, actual_goods, is_honest = build_bag_and_declaration(merchant, encounter_history)
        
        # Show tell
        tell = choose_tell(merchant, is_honest)
        if tell:
            show_tell(tell)
            print()
        
        show_declaration(merchant, declaration)
        
        # Check for proactive bribe
        declared_goods = [GOOD_BY_ID[declaration.good_id]] * declaration.count
        offers_proactive = merchant.should_offer_proactive_bribe(
            sheriff.authority, sheriff.reputation, actual_goods, declared_goods
        )
        
        proactive_bribe_amount = 0
        if offers_proactive:
            proactive_bribe_amount = merchant.calculate_proactive_bribe(
                actual_goods, not is_honest, sheriff.authority, declared_goods
            )
            show_proactive_bribe(merchant, proactive_bribe_amount, not is_honest)
        
        # Player decides what to do
        decision = prompt_initial_decision(offers_proactive, proactive_bribe_amount)
        
        was_opened = False
        caught_lie = False
        bribe_info = {'amount': 0, 'accepted': False, 'proactive': False}
        
        if decision == 'accept':
            # Accept proactive bribe
            process_proactive_bribe(merchant, proactive_bribe_amount, sheriff, stats, idx, len(merchants))
            was_honest, caught_lie = process_pass_without_inspection(merchant, actual_goods, declaration, stats)
            bribe_info = {'amount': proactive_bribe_amount, 'accepted': True, 'proactive': True}
            
        elif decision == 'pass':
            # Let them pass without inspection
            was_honest, caught_lie = process_pass_without_inspection(merchant, actual_goods, declaration, stats)
            update_sheriff_reputation(sheriff, False, was_honest, stats, actual_goods)
            
        elif decision == 'inspect':
            # Inspect immediately (no negotiation)
            was_honest, caught_lie = process_inspection(merchant, actual_goods, declaration, sheriff, stats)
            was_opened = True
            
        elif decision == 'threaten':
            # Threaten inspection (may trigger negotiation)
            should_inspect = run_negotiation(sheriff, merchant, actual_goods, stats)
            
            if should_inspect:
                # Inspect the bag
                was_honest, caught_lie = process_inspection(merchant, actual_goods, declaration, sheriff, stats)
                was_opened = True
            else:
                # Bribe accepted during negotiation
                was_honest, caught_lie = process_pass_without_inspection(merchant, actual_goods, declaration, stats)
        
        # Record encounter in history
        encounter_history.append({
            'declaration': {'good_id': declaration.good_id, 'count': declaration.count},
            'actual_ids': [g.id for g in actual_goods],
            'opened': was_opened,
            'caught_lie': caught_lie,
        })
        
        # Record in game master state
        record_encounter(game_state, merchant, declaration, actual_goods, was_opened, caught_lie, bribe_info)
    
    # Show end game summary
    show_end_game_summary(sheriff, stats)
