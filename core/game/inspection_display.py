"""
Inspection Display - Handles formatting and display of inspection results
Loads messages from JSON for maintainability
"""

import json
from pathlib import Path
from core.mechanics.goods import Good


def load_inspection_messages() -> dict:
    """Load inspection messages from JSON file."""
    messages_path = Path(__file__).parent.parent.parent / "data" / "inspection_messages.json"
    try:
        with open(messages_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load inspection messages: {e}")
        return {}


def show_inspection_header(merchant_name: str, declaration_count: int, declaration_good: str, messages: dict = None):
    """Display inspection header with declaration."""
    if messages is None:
        messages = load_inspection_messages()
    
    header = messages.get('inspection_header', {})
    separator = header.get('separator', '=' * 60)
    title = header.get('title', '🔍 INSPECTION RESULTS - {merchant_name}\'s Bag')
    
    print(f"\n{separator}")
    print(title.format(merchant_name=merchant_name))
    print(separator)
    
    decl_label = messages.get('declaration', {}).get('label', '📋 DECLARED: {count}x {good_id}')
    print(f"\n{decl_label.format(count=declaration_count, good_id=declaration_good)}")


def show_bag_contents(actual_goods: list[Good], messages: dict = None):
    """Display actual bag contents."""
    if messages is None:
        messages = load_inspection_messages()
    
    bag_config = messages.get('bag_contents', {})
    label = bag_config.get('label', '🎒 ACTUAL BAG CONTENTS:')
    item_format = bag_config.get('item_format', '   {index}. {good_id} (value: {value}g){contraband_marker}')
    contraband_marker = bag_config.get('contraband_marker', ' ⚠️ CONTRABAND')
    
    print(f"\n{label}")
    for i, good in enumerate(actual_goods, 1):
        marker = contraband_marker if good.is_contraband() else ""
        print(item_format.format(
            index=i,
            good_id=good.id,
            value=good.value,
            contraband_marker=marker
        ))


def show_bluff_succeeded(merchant_name: str, goods_value: int, merchant_gold: int, messages: dict = None):
    """Display message when merchant's bluff succeeded."""
    if messages is None:
        messages = load_inspection_messages()
    
    bluff_config = messages.get('verdicts', {}).get('bluff_succeeded', {})
    title = bluff_config.get('title', '🎭 {merchant_name}\'s BLUFF SUCCEEDED!')
    lines = bluff_config.get('lines', [])
    
    print(f"\n{title.format(merchant_name=merchant_name)}")
    for line in lines:
        print(line)
    
    financial = messages.get('financial', {})
    sold_msg = financial.get('merchant_sold_all', '💰 [{merchant_name}] Sold all goods for {value}g. Total: {total}g')
    print(f"\n{sold_msg.format(merchant_name=merchant_name, value=goods_value, total=merchant_gold)}")


def show_honest_verdict(goods_count: int, goods_value: int, merchant_name: str, merchant_gold: int, messages: dict = None):
    """Display verdict for honest merchant."""
    if messages is None:
        messages = load_inspection_messages()
    
    honest_config = messages.get('verdicts', {}).get('honest', {})
    title = honest_config.get('title', '✅ VERDICT: HONEST - Declaration matches contents!')
    message = honest_config.get('message', '   All {count} goods pass through.')
    
    print(f"\n{title}")
    print(message.format(count=goods_count))
    
    financial = messages.get('financial', {})
    sold_msg = financial.get('merchant_sold', '💰 [{merchant_name}] Sold goods for {value}g. Total: {total}g')
    print(f"\n{sold_msg.format(merchant_name=merchant_name, value=goods_value, total=merchant_gold)}")


def show_lying_verdict(goods_passed: list[Good], goods_confiscated: list[Good], 
                       penalty_paid: int, merchant_name: str, merchant_gold: int, messages: dict = None):
    """Display verdict for lying merchant with confiscation details."""
    if messages is None:
        messages = load_inspection_messages()
    
    lying_config = messages.get('verdicts', {}).get('lying', {})
    title = lying_config.get('title', '❌ VERDICT: LYING - Declaration does NOT match contents!')
    print(f"\n{title}")
    
    goods_status = messages.get('goods_status', {})
    financial = messages.get('financial', {})
    
    # Show allowed goods
    if goods_passed:
        allowed_config = goods_status.get('allowed_through', {})
        header = allowed_config.get('header', '✓ ALLOWED THROUGH ({count} items - truthfully declared):')
        item_format = allowed_config.get('item_format', '   • {good_id} (value: {value}g)')
        
        print(f"\n{header.format(count=len(goods_passed))}")
        for good in goods_passed:
            print(item_format.format(good_id=good.id, value=good.value))
    
    # Show confiscated goods
    if goods_confiscated:
        confiscated_config = goods_status.get('confiscated', {})
        header = confiscated_config.get('header', '⛔ CONFISCATED ({count} items - undeclared):')
        item_format = confiscated_config.get('item_format', '   • {good_id} (value: {value}g){contraband_marker}')
        marker_legal = confiscated_config.get('contraband_marker_legal', ' [LEGAL]')
        marker_illegal = confiscated_config.get('contraband_marker_illegal', ' [CONTRABAND]')
        
        total_confiscated_value = sum(g.value for g in goods_confiscated)
        
        print(f"\n{header.format(count=len(goods_confiscated))}")
        for good in goods_confiscated:
            marker = marker_illegal if good.is_contraband() else marker_legal
            print(item_format.format(good_id=good.id, value=good.value, contraband_marker=marker))
        
        # Show penalty
        penalty_msg = financial.get('penalty', '💸 PENALTY: {penalty}g (50% of {total_value}g confiscated value)')
        print(f"\n{penalty_msg.format(penalty=penalty_paid, total_value=total_confiscated_value)}")
        
        remaining_msg = financial.get('merchant_remaining', '   [{merchant_name}] Gold remaining: {gold}g')
        print(remaining_msg.format(merchant_name=merchant_name, gold=merchant_gold))
    
    # Show goods sold (if any passed)
    if goods_passed:
        goods_value = sum(g.value for g in goods_passed)
        sold_msg = financial.get('merchant_sold', '💰 [{merchant_name}] Sold goods for {value}g. Total: {total}g')
        print(f"\n{sold_msg.format(merchant_name=merchant_name, value=goods_value, total=merchant_gold)}")


def show_inspection_footer(messages: dict = None):
    """Display inspection footer separator."""
    if messages is None:
        messages = load_inspection_messages()
    
    separator = messages.get('inspection_header', {}).get('separator', '=' * 60)
    print(f"\n{separator}\n")


def show_tell(tell: str, messages: dict = None):
    """Display a merchant's tell."""
    if tell:
        if messages is None:
            messages = load_inspection_messages()
        
        tell_format = messages.get('tells', {}).get('notice_format', 'You notice: {tell}.')
        print(tell_format.format(tell=tell))


def show_bribe_accepted_status(amount: int, sheriff_reputation: int, messages: dict = None):
    """Display sheriff status after accepting bribe."""
    if messages is None:
        messages = load_inspection_messages()
    
    status_msg = messages.get('sheriff_status', {}).get('bribe_accepted', 
                                                         '[Sheriff] Gold: +{amount}  Reputation: {reputation} (-1 for accepting bribe)')
    print(status_msg.format(amount=amount, reputation=sheriff_reputation))


def show_merchant_sold_goods(merchant_name: str, goods_value: int, merchant_gold: int, messages: dict = None):
    """Display message when merchant sells goods."""
    if messages is None:
        messages = load_inspection_messages()
    
    sold_msg = messages.get('financial', {}).get('merchant_sold', 
                                                  '💰 [{merchant_name}] Sold goods for {value}g. Total: {total}g')
    print(sold_msg.format(merchant_name=merchant_name, value=goods_value, total=merchant_gold))
