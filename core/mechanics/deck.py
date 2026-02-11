"""
Deck System for Sheriff of Nottingham

Implements an infinite deck with weighted probabilities based on the original game's
card distribution. Merchants draw 7 cards per turn.

Card Distribution (probabilities):
- Apples: 48 cards (23.3%)
- Cheese: 36 cards (17.5%)
- Bread: 36 cards (17.5%)
- Chicken: 24 cards (11.7%)
- Pepper: 22 cards (10.7%)
- Mead: 22 cards (10.7%)
- Silk: 12 cards (5.8%)
- Crossbow: 5 cards (2.4%)
Total: 205 cards
"""

import random
from typing import List
from core.mechanics.goods import GOOD_BY_ID, Good
from core.constants import HAND_SIZE_LIMIT

# Card distribution weights (based on original game)
CARD_WEIGHTS = {
    'apple': 48,
    'cheese': 36,
    'bread': 36,
    'chicken': 24,
    'pepper': 22,
    'mead': 22,
    'silk': 12,
    'crossbow': 5
}

# Total cards for probability calculation
TOTAL_CARDS = sum(CARD_WEIGHTS.values())  # 205


def draw_hand(hand_size: int = HAND_SIZE_LIMIT) -> List[Good]:
    """
    Draw a hand of cards from the infinite deck.
    
    Uses weighted random selection based on the original game's card distribution.
    This simulates drawing from a deck without replacement, but with an infinite deck
    so we never run out of cards.
    
    Args:
        hand_size: Number of cards to draw (default 7)
        
    Returns:
        List of Good objects representing the drawn cards
    """
    # Create weighted list of good IDs
    good_ids = list(CARD_WEIGHTS.keys())
    weights = list(CARD_WEIGHTS.values())
    
    # Draw cards with weighted probabilities
    drawn_ids = random.choices(good_ids, weights=weights, k=hand_size)
    
    # Convert IDs to Good objects
    hand = [GOOD_BY_ID[good_id] for good_id in drawn_ids]
    
    return hand


def redraw_cards(current_hand: List[Good], num_to_redraw: int, prefer_contraband: bool = False, prefer_legal: bool = False, prefer_high_value: bool = False) -> List[Good]:
    """
    Redraw a specified number of cards from the current hand.
    
    This allows merchants to DISCARD unwanted cards and draw new ones.
    The function intelligently chooses which cards to discard based on preferences.
    
    Args:
        current_hand: Current hand of Good objects
        num_to_redraw: Number of cards to discard and redraw (1-7)
        prefer_contraband: If True, keep contraband and discard legal goods
        prefer_legal: If True, keep legal goods and discard contraband
        prefer_high_value: If True, keep high-value cards and discard low-value ones
        
    Returns:
        New hand with unwanted cards discarded and replaced with new draws
    """
    if num_to_redraw <= 0 or num_to_redraw > len(current_hand):
        return current_hand
    
    # Determine which cards to DISCARD (not keep!)
    num_to_keep = len(current_hand) - num_to_redraw
    
    # Sort cards by preference to determine what to keep vs discard
    if prefer_contraband:
        # Keep contraband, discard legal goods
        sorted_hand = sorted(current_hand, key=lambda g: (not g.is_contraband(), -g.value))
    elif prefer_legal:
        # Keep legal goods, discard contraband
        sorted_hand = sorted(current_hand, key=lambda g: (g.is_contraband(), -g.value))
    elif prefer_high_value:
        # Keep high-value cards, discard low-value ones
        sorted_hand = sorted(current_hand, key=lambda g: -g.value)
    else:
        # Random selection (no preference)
        sorted_hand = random.sample(current_hand, len(current_hand))
    
    # Keep the top cards based on preference, discard the rest
    kept_cards = sorted_hand[:num_to_keep]
    discarded_cards = sorted_hand[num_to_keep:]
    
    # Draw new cards to replace the discarded ones
    new_cards = draw_hand(hand_size=num_to_redraw)
    
    # Combine kept cards with newly drawn cards
    new_hand = kept_cards + new_cards
    
    return new_hand


def should_redraw_for_better_hand(hand: List[Good], risk_tolerance: int, honesty: int) -> int:
    """
    Determine if a merchant should redraw cards to improve their hand.
    
    - High risk + low honesty = redraw for more contraband
    - Low risk + high honesty = redraw for more of the same legal good (consistency)
    
    Args:
        hand: Current hand of Good objects
        risk_tolerance: Merchant's risk tolerance (0-10)
        honesty: Merchant's honesty bias (0-10)
        
    Returns:
        Number of cards to redraw (0 = no redraw, 1-4 = redraw that many)
    """
    analysis = analyze_hand(hand)
    contraband_count = len(analysis['contraband'])
    legal_count = len(analysis['legal'])
    counts = analysis['counts']
    
    # HONEST MERCHANTS: Want consistency (more of the same legal good)
    if honesty >= 7 and risk_tolerance <= 4:
        # Find the most common legal good in hand
        legal_goods = [g for g in hand if g.is_legal()]
        if not legal_goods:
            return 0  # No legal goods to work with
        
        # Count each legal good type
        legal_counts = {}
        for good in legal_goods:
            legal_counts[good.id] = legal_counts.get(good.id, 0) + 1
        
        # Find the most common legal good
        max_count = max(legal_counts.values())
        
        # If we have 2-3 of the same legal good, redraw to try to get more
        if max_count == 2:
            # Redraw 2-3 cards to try to get more of this good
            return random.randint(2, 3)
        elif max_count == 3:
            # Redraw 1-2 cards to try to get more
            return random.randint(1, 2)
        elif max_count >= 4:
            # Already have a good set, don't redraw
            return 0
        else:
            # Only have 1 of each, redraw 2-3 to try to get duplicates
            return random.randint(2, 3)
    
    # AGGRESSIVE SMUGGLERS: Want contraband
    # If already have good contraband options, don't redraw
    if contraband_count >= 3:
        return 0
    
    # Aggressive smugglers (risk >= 7, honesty <= 4) want contraband
    if risk_tolerance >= 7 and honesty <= 4:
        # If hand is mostly legal, redraw 3-4 cards
        if contraband_count <= 1:
            return random.randint(3, 4)
        # If hand has some contraband, redraw 1-2 cards
        elif contraband_count == 2:
            return random.randint(1, 2)
    
    # Moderate risk-takers (risk >= 5, honesty <= 6) sometimes redraw for contraband
    elif risk_tolerance >= 5 and honesty <= 6:
        # Only redraw if hand has no contraband
        if contraband_count == 0:
            return random.randint(1, 2)
    
    # Default: no redraw
    return 0


# Keep old name for backward compatibility
should_redraw_for_contraband = should_redraw_for_better_hand


def should_redraw_for_silas(hand: List[Good], sheriff_analysis: dict) -> int:
    """
    Determine if Silas should redraw cards based on sheriff behavior analysis.
    
    Silas's redraw strategy is data-driven:
    - Against CORRUPT sheriffs (accept all bribes): Redraw for HIGH-VALUE CONTRABAND
      → Use expensive contraband + small bribes to pass without inspection
    - Against TRIGGER HAPPY sheriffs (inspect all bribes): Redraw for HIGH-VALUE LEGAL goods
      → Use honest bribe trick: 16g legal + bribe → sheriff inspects, finds honest, loses 16g!
    - Against lenient sheriffs: Redraw for high-value contraband (maximize profit)
    - Against aggressive sheriffs: Play it safe with whatever hand
    
    Args:
        hand: Current hand of Good objects
        sheriff_analysis: Dict with sheriff behavior data (inspection_rate, catch_rate, etc.)
        
    Returns:
        Number of cards to redraw (0 = no redraw, 1-4 = redraw that many)
    """
    analysis = analyze_hand(hand)
    legal_goods = analysis['legal']
    contraband_goods = analysis['contraband']
    
    inspection_rate = sheriff_analysis.get('inspection_rate', 0.5)
    catch_rate = sheriff_analysis.get('catch_rate', 0.5)
    
    # Check if sheriff is trigger happy or corrupt (from history)
    history = sheriff_analysis.get('history', [])
    is_trigger_happy = False
    is_corrupt = False
    
    if len(history) >= 5:
        # Detect trigger happy: inspects all bribes
        bribed = [h for h in history[-10:] if h.get('bribe_offered', 0) > 0]
        if len(bribed) >= 3:
            inspected_bribes = sum(1 for h in bribed if h.get('opened', False))
            is_trigger_happy = (inspected_bribes / len(bribed)) >= 0.9
        
        # Detect corrupt: accepts all bribes
        if len(bribed) >= 3:
            accepted_bribes = sum(1 for h in bribed if h.get('bribe_accepted', False))
            is_corrupt = (accepted_bribes / len(bribed)) >= 0.9
    
    # STRATEGY 1: Against TRIGGER HAPPY sheriffs (inspect all bribes)
    # Redraw for HIGH-VALUE LEGAL goods (honest bribe trick)
    # Carry 4x Chicken (16g), declare honestly, bribe 2g
    # Sheriff MUST inspect (trigger happy) → finds honest → loses 16g to Silas!
    if is_trigger_happy:
        # Count high-value legal goods (Chicken = 4g)
        high_value_legal = [g for g in legal_goods if g.value >= 4]
        
        if len(high_value_legal) >= 4:
            # Already have good legal hand for the trick
            return 0
        elif len(high_value_legal) >= 2:
            # Have some, redraw 1-2 to get more
            return random.randint(1, 2)
        else:
            # Need more high-value legal goods, redraw 3-4
            return random.randint(3, 4)
    
    # STRATEGY 2: Against CORRUPT sheriffs (accept all bribes)
    # Redraw for HIGH-VALUE CONTRABAND (maximize smuggling profit)
    # Carry 4x Crossbow (60g!), declare apples, bribe 5g
    # Sheriff accepts bribe → doesn't inspect → Silas profits 55g!
    if is_corrupt:
        # Count high-value contraband (Mead = 10g, Crossbow = 15g)
        high_value_contraband = [g for g in contraband_goods if g.value >= 10]
        
        if len(high_value_contraband) >= 4:
            # Already have excellent contraband hand
            return 0
        elif len(high_value_contraband) >= 2:
            # Have some, redraw 1-2 to get more
            return random.randint(1, 2)
        else:
            # Need more high-value contraband, redraw 3-4
            return random.randint(3, 4)
    
    # STRATEGY 3: Against lenient sheriffs (low inspection/catch rate)
    # Redraw for HIGH-VALUE CONTRABAND (maximize smuggling profit)
    if inspection_rate < 0.4 and catch_rate < 0.4:
        high_value_contraband = [g for g in contraband_goods if g.value >= 10]
        
        if len(high_value_contraband) >= 3:
            return 0
        elif len(high_value_contraband) >= 1:
            return random.randint(1, 2)
        else:
            return random.randint(3, 4)
    
    # STRATEGY 4: Against aggressive sheriffs (high inspection/catch rate)
    # Don't redraw - play it safe with whatever we have
    if inspection_rate > 0.6 or catch_rate > 0.6:
        return 0
    
    # STRATEGY 5: Against moderate sheriffs
    # Slight preference for contraband, but not aggressive
    if len(contraband_goods) <= 1:
        return random.randint(1, 2)
    
    return 0


def get_card_probability(good_id: str) -> float:
    """
    Get the probability of drawing a specific card.
    
    Args:
        good_id: ID of the good (e.g., 'apple', 'crossbow')
        
    Returns:
        Probability as a float (0.0 to 1.0)
    """
    if good_id not in CARD_WEIGHTS:
        return 0.0
    
    return CARD_WEIGHTS[good_id] / TOTAL_CARDS


def get_expected_count_in_hand(good_id: str, hand_size: int = HAND_SIZE_LIMIT) -> float:
    """
    Calculate the expected number of a specific card in a hand.
    
    Args:
        good_id: ID of the good
        hand_size: Size of the hand (default 6)
        
    Returns:
        Expected count as a float
    """
    probability = get_card_probability(good_id)
    return probability * hand_size


def analyze_hand(hand: List[Good]) -> dict:
    """
    Analyze a hand to see what's available.
    
    Args:
        hand: List of Good objects
        
    Returns:
        dict with keys:
            - 'legal': List of legal goods in hand
            - 'contraband': List of contraband in hand
            - 'counts': Dict of {good_id: count}
            - 'total_value': Total value of all cards
            - 'legal_value': Total value of legal goods
            - 'contraband_value': Total value of contraband
    """
    legal = [g for g in hand if g.is_legal()]
    contraband = [g for g in hand if not g.is_legal()]
    
    # Count each good type
    counts = {}
    for good in hand:
        counts[good.id] = counts.get(good.id, 0) + 1
    
    # Calculate values
    total_value = sum(g.value for g in hand)
    legal_value = sum(g.value for g in legal)
    contraband_value = sum(g.value for g in contraband)
    
    return {
        'legal': legal,
        'contraband': contraband,
        'counts': counts,
        'total_value': total_value,
        'legal_value': legal_value,
        'contraband_value': contraband_value
    }


def select_from_hand(hand: List[Good], desired_ids: List[str], max_count: int = 6) -> List[Good]:
    """
    Select specific goods from a hand.
    
    This is used by the AI to choose which cards from their hand to put in the bag.
    If the desired goods aren't available, it will take what it can get.
    
    Args:
        hand: List of Good objects available
        desired_ids: List of good IDs the merchant wants
        max_count: Maximum number of goods to select (bag limit)
        
    Returns:
        List of Good objects selected from the hand
    """
    selected = []
    remaining_hand = hand.copy()
    
    for desired_id in desired_ids[:max_count]:
        # Try to find this good in the remaining hand
        for i, good in enumerate(remaining_hand):
            if good.id == desired_id:
                selected.append(good)
                remaining_hand.pop(i)
                break
        
        # If we've selected enough, stop
        if len(selected) >= max_count:
            break
    
    return selected


def get_best_available_substitute(hand: List[Good], desired_id: str, is_legal: bool = None) -> Good:
    """
    Find the best substitute for a desired good that isn't in hand.
    
    Args:
        hand: List of Good objects available
        desired_id: ID of the good we wanted
        is_legal: If True, only return legal goods. If False, only contraband. If None, any.
        
    Returns:
        Best substitute Good object, or None if no suitable substitute
    """
    # Filter by legal/contraband if specified
    if is_legal is not None:
        candidates = [g for g in hand if g.is_legal() == is_legal]
    else:
        candidates = hand
    
    if not candidates:
        return None
    
    # Get the desired good's value
    desired_good = GOOD_BY_ID.get(desired_id)
    if not desired_good:
        # If desired good doesn't exist, just return highest value
        return max(candidates, key=lambda g: g.value)
    
    # Find the good with closest value
    return min(candidates, key=lambda g: abs(g.value - desired_good.value))
