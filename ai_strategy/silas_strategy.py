"""
Silas Voss - Information Broker Strategy Module

This module contains the sophisticated decision-making logic for Silas. His strategy is based on analyzing patterns, calculating
risks, and making economically rational decisions.

DESIGN PHILOSOPHY:
==================
Silas is not just another merchant - he's an analyst who learns from others.
His approach is:
1. Data-driven: Analyzes sheriff's behavior patterns
2. Risk-aware: Adjusts strategy based on danger level
3. Economically rational: Never takes losing bets
4. Sustainable: Focuses on long-term profit over single big scores
5. Adaptive: Changes tactics as the game progresses

KEY INSIGHT:
============
Silas understands that the sheriff learns too. A massive bribe is a red flag.
He starts small, builds trust, and only escalates when the sheriff is lenient.

GAME RULES:
===========
- Maximum bag size: 6 items
- Merchants start with 50 gold
- Bluff skill affects lie detection
- Partial honesty: Truthfully declared goods pass even when lying
"""

import random
from core.mechanics.goods import ALL_LEGAL, ALL_CONTRABAND, GOOD_BY_ID
from core.players.sheriff_analysis import analyze_sheriff_detailed
from core.game.game_rules import BAG_SIZE_LIMIT


class SilasStrategy:
    """
    Strategic decision-making for Silas Voss, the Information Broker.
    
    This class encapsulates all of Silas's analytical and decision-making logic,
    keeping it separate from the base Merchant class for clarity and maintainability.
    
    Note: Silas uses the shared analyze_sheriff_detailed() utility from core.sheriff_analysis
    for his sophisticated behavior analysis.
    """
    
    @staticmethod
    def detect_corrupt_sheriff(history: list[dict]) -> bool:
        """
        Detect if sheriff is "corrupt & greedy" - accepts all bribes.
        
        Pattern: Sheriff accepts 90%+ of bribes offered.
        Against corrupt sheriffs, smuggling is LESS profitable because:
        - Bribes always cost gold (even if minimal)
        - Honest goods have no cost
        - Cumulative bribe costs reduce profit margins
        
        Returns:
            True if sheriff appears to be corrupt (accepts all bribes)
        """
        if len(history) < 5:
            return False
        
        recent = history[-10:] if len(history) >= 10 else history
        bribed_encounters = [h for h in recent if h.get('bribe_offered', 0) > 0]
        
        if len(bribed_encounters) < 3:
            return False
        
        bribes_accepted = sum(1 for h in bribed_encounters if h.get('bribe_accepted', False))
        acceptance_rate = bribes_accepted / len(bribed_encounters)
        
        # Corrupt: accepts 90%+ of bribes
        return acceptance_rate >= 0.9
    
    @staticmethod
    def detect_adaptive_sheriff(history: list[dict]) -> bool:
        """
        Detect if sheriff is "adaptive" - changes inspection rate based on results.
        
        Pattern: Inspection rate varies significantly over time (not consistent).
        Adaptive sheriffs inspect more when catching smugglers, less when not.
        
        Returns:
            True if sheriff appears to be adaptive
        """
        if len(history) < 10:
            return False
        
        # Split history into two halves
        mid = len(history) // 2
        first_half = history[:mid]
        second_half = history[mid:]
        
        # Calculate inspection rates for each half
        first_inspections = sum(1 for h in first_half if h.get('opened', False))
        first_rate = first_inspections / len(first_half) if first_half else 0.5
        
        second_inspections = sum(1 for h in second_half if h.get('opened', False))
        second_rate = second_inspections / len(second_half) if second_half else 0.5
        
        # Adaptive: inspection rate changes by 20%+ between halves
        return abs(first_rate - second_rate) >= 0.2
    
    @staticmethod
    def calculate_strategy_expected_value(history: list[dict], strategy_type: str) -> float:
        """
        Calculate expected profit for a given strategy based on historical data.
        
        Args:
            history: List of previous encounters
            strategy_type: Either 'honest' or 'smuggling'
        
        Returns:
            float: Expected profit in gold from the strategy
        """
        if len(history) < 5:
            return 8.0  # Default: assume ~8g average
        
        recent = history[-15:] if len(history) >= 15 else history
        
        # Filter attempts based on strategy type
        if strategy_type == 'honest':
            attempts = [h for h in recent if not h.get('contraband', False)]
            min_attempts = 2
        else:  # smuggling
            attempts = [h for h in recent if h.get('contraband', False)]
            min_attempts = 3
        
        if len(attempts) < min_attempts:
            return 8.0  # Not enough data, use default
        
        # Calculate average profit
        total_profit = sum(h.get('gold_earned', 0) - h.get('gold_lost', 0) for h in attempts)
        avg_profit = total_profit / len(attempts)
        
        return max(5.0, avg_profit) if strategy_type == 'honest' else avg_profit
    
    @staticmethod
    def calculate_smuggling_profitability(history: list[dict]) -> float:
        """
        Compare smuggling vs honest strategies using expected value.
        
        Returns:
            float: Profitability ratio (smuggling_EV / honest_EV)
                  >1.0 = smuggling more profitable
                  <1.0 = honest more profitable
        """
        honest_EV = SilasStrategy.calculate_strategy_expected_value(history, 'honest')
        smuggling_EV = SilasStrategy.calculate_strategy_expected_value(history, 'smuggling')
        
        # Calculate profitability ratio
        profitability_ratio = smuggling_EV / honest_EV if honest_EV > 0 else 1.0
        
        # Clamp to reasonable range (0.1 to 3.0)
        return max(0.1, min(3.0, profitability_ratio))
    
    @staticmethod
    def should_tell_truth(analysis: dict) -> bool:
        """
        Decide if Silas should tell the truth based on sheriff behavior.
        
        Silas uses data-driven analysis to determine if smuggling is profitable.
        Key insight: Don't just look at catch rate, look at actual profitability.
        
        Args:
            analysis: Sheriff behavior analysis
            
        Returns:
            bool: True if should tell truth, False if should smuggle
        """
        catch_rate = analysis['catch_rate']
        inspection_rate = analysis['inspection_rate']
        history = analysis.get('history', [])
        
        # FIRST: Calculate if smuggling is actually profitable
        profitability = SilasStrategy.calculate_smuggling_profitability(history)
        
        # If smuggling is very unprofitable (<0.5), stay honest most of the time
        if profitability < 0.5:
            return random.random() < 0.9  # 90% honest
        
        # If smuggling is unprofitable (0.5-0.8), stay honest often
        if profitability < 0.8:
            return random.random() < 0.75  # 75% honest
        
        # Check for corrupt sheriff pattern
        # Against corrupt sheriffs, stay honest MORE often (70% of the time)
        # because cumulative bribe costs make smuggling unprofitable
        if SilasStrategy.detect_corrupt_sheriff(history):
            return random.random() < 0.7  # 70% chance to stay honest
        
        # Check for adaptive sheriff pattern
        is_adaptive = SilasStrategy.detect_adaptive_sheriff(history)
        
        if is_adaptive:
            # Against adaptive sheriffs, use cautious dynamic strategy
            # Key insight: Frequent smuggling triggers adaptive response
            # Better to smuggle LESS but at optimal times
            
            # Adjust base honesty based on profitability
            if profitability > 1.3:
                base_honesty = 0.4  # Very profitable, smuggle more
            elif profitability > 1.0:
                base_honesty = 0.6  # Moderately profitable
            else:
                base_honesty = 0.75  # Barely profitable, be cautious
            
            if inspection_rate > 0.6:
                # Sheriff is aggressive - very cautious
                return random.random() < min(0.85, base_honesty + 0.25)
            elif inspection_rate > 0.5:
                # Sheriff is moderately aggressive - cautious
                return random.random() < min(0.75, base_honesty + 0.15)
            elif inspection_rate > 0.4:
                # Sheriff is moderate - balanced
                return random.random() < base_honesty
            elif inspection_rate > 0.3:
                # Sheriff is lenient - opportunistic
                return random.random() < max(0.3, base_honesty - 0.15)
            else:
                # Sheriff is very lenient - exploit it
                return random.random() < max(0.2, base_honesty - 0.25)
        
        # Non-adaptive sheriff - use profitability-based logic
        # If smuggling is profitable (>1.0), be more aggressive
        if profitability > 1.2:
            # Very profitable - smuggle more often
            if catch_rate > 0.7:
                return True  # Still too risky
            elif inspection_rate > 0.8:
                return True  # Too much inspection
            else:
                return random.random() < 0.3  # 30% honest, 70% smuggle
        
        # Standard logic for moderate profitability
        if catch_rate > 0.6:
            return True
        
        if inspection_rate > 0.7:
            return True
        
        # Otherwise, smuggle!
        return False
    
    @staticmethod
    def select_contraband_strategy(analysis: dict) -> tuple[int, any]:
        """
        Select contraband count and value based on risk assessment.
        
        Silas scales both quantity and value based on sheriff danger level.
        
        Args:
            analysis: Sheriff behavior analysis
            
        Returns:
            tuple: (count, contraband_good)
        """
        catch_rate = analysis['catch_rate']
        inspection_rate = analysis['inspection_rate']
        contraband_options = sorted(ALL_CONTRABAND, key=lambda g: g.value)
        
        # Determine risk level and select accordingly
        if catch_rate < 0.3 and inspection_rate < 0.4:
            # Very safe: 3-4 items, high value
            count = min(random.randint(3, 4), BAG_SIZE_LIMIT)
            contraband = random.choice(contraband_options[len(contraband_options) * 2 // 3:])
        elif catch_rate < 0.5:
            # Moderate: 2-3 items, mid-high value
            count = min(random.randint(2, 3), BAG_SIZE_LIMIT)
            mid_start = len(contraband_options) // 3
            mid_end = len(contraband_options) * 2 // 3
            contraband = random.choice(contraband_options[mid_start:mid_end])
        else:
            # Dangerous: 1-2 items, lower value
            count = min(random.randint(1, 2), BAG_SIZE_LIMIT)
            contraband = contraband_options[random.randint(0, len(contraband_options) // 2)]
        
        return count, contraband
    
    @staticmethod
    def detect_trigger_happy_sheriff(history: list[dict]) -> bool:
        """
        Detect if sheriff is "trigger happy" - inspects whenever bribed.
        
        Pattern: Sheriff inspects all merchants who offer bribes, but lets others pass.
        This is exploitable with the "honest bribe trick".
        
        Returns:
            True if sheriff appears to be trigger happy
        """
        if len(history) < 5:
            return False  # Need enough data
        
        recent = history[-10:] if len(history) >= 10 else history
        
        # Look for bribes in history (merchants who offered bribes)
        bribed_encounters = [h for h in recent if h.get('bribe_offered', 0) > 0 or h.get('bribe_accepted', False)]
        non_bribed_encounters = [h for h in recent if h.get('bribe_offered', 0) == 0 and not h.get('bribe_accepted', False)]
        
        if len(bribed_encounters) < 3:
            return False  # Not enough bribe data
        
        # Check if sheriff inspects ALL bribes but lets non-bribes pass
        bribes_inspected = sum(1 for h in bribed_encounters if h.get('opened', False))
        non_bribes_inspected = sum(1 for h in non_bribed_encounters if h.get('opened', False))
        
        # Trigger happy: inspects 80%+ of bribes, but only 30% or less of non-bribes
        bribe_inspection_rate = bribes_inspected / len(bribed_encounters) if bribed_encounters else 0
        non_bribe_inspection_rate = non_bribes_inspected / len(non_bribed_encounters) if non_bribed_encounters else 0
        
        return bribe_inspection_rate >= 0.8 and non_bribe_inspection_rate <= 0.3
    
    @staticmethod
    def choose_declaration_with_history(history: list[dict]) -> dict:
        """
        Main decision function - determines what Silas declares and carries.
        
        This is the entry point for Silas's strategy when he has historical data.
        It orchestrates all the analysis and decision-making steps.
        
        Args:
            history: List of previous merchant encounters
            
        Returns:
            dict with keys:
                - declared_id: What good he declares
                - count: How many he declares
                - actual_ids: What he's actually carrying
                - lie: Whether he's lying
        """
        # Step 1: Analyze sheriff's behavior using shared utility
        analysis = analyze_sheriff_detailed(history)
        
        # Step 1.5: Check for "trigger happy" sheriff pattern
        is_trigger_happy = SilasStrategy.detect_trigger_happy_sheriff(history)
        
        if is_trigger_happy:
            # EXPLOIT: Use "honest bribe trick"
            # Carry honest goods, declare honestly, but offer small bribe
            # Sheriff will inspect (because bribe), find honest goods, and pay full value!
            # 
            # Example: Carry 3x Cheese (9g), declare 3x Cheese, bribe 2g
            # Sheriff inspects → finds honest → Silas gets 9g goods + keeps 2g bribe = 11g profit!
            
            # Choose high-value legal goods to maximize profit
            legal_by_value = sorted(ALL_LEGAL, key=lambda g: g.value, reverse=True)
            high_value_legal = random.choice(legal_by_value[:2])  # Top 2 highest value
            
            count = min(random.randint(3, 4), BAG_SIZE_LIMIT)  # Maximize value
            
            return {
                "declared_id": high_value_legal.id,
                "count": count,
                "actual_ids": [high_value_legal.id] * count,
                "lie": False,  # Honest!
                "lie_type": "none",
                "trigger_happy_exploit": True  # Flag for bribe calculation
            }
        
        # Step 2: Decide if environment is too dangerous
        if SilasStrategy.should_tell_truth(analysis):
            # Play it safe - tell the truth
            # Use 2-4 items to maximize honest profit (within bag limit)
            declared = random.choice([g.id for g in ALL_LEGAL])
            count = min(random.randint(2, 4), BAG_SIZE_LIMIT)
            return {
                "declared_id": declared,
                "count": count,
                "actual_ids": [declared] * count,
                "lie": False,
                "lie_type": "none"
            }
        
        # Step 3: Environment is safe enough to smuggle
        # Select contraband count and value based on risk
        contraband_count, contraband = SilasStrategy.select_contraband_strategy(analysis)
        
        # Step 4: Build declaration (within bag limit)
        declared = random.choice([g.id for g in ALL_LEGAL])
        actual_ids = [contraband.id] * contraband_count
        
        return {
            "declared_id": declared,
            "count": len(actual_ids),
            "actual_ids": actual_ids,
            "lie": True,
            "lie_type": "contraband"
        }
    
    @staticmethod
    def choose_declaration_first_round() -> dict:
        """
        Decision function for Silas's first encounter (no historical data).
        
        With no data, Silas starts conservatively:
        - 2-3 items (not too greedy, within bag limit)
        - Mid-value contraband (not highest value)
        - Tests the waters before escalating
        
        A smart broker doesn't go all-in on the first round.
        
        Returns:
            dict: Declaration for first round
        """
        # Start conservatively with mid-value contraband
        contraband_options = sorted(ALL_CONTRABAND, key=lambda g: g.value)
        mid_value_contraband = contraband_options[len(contraband_options) // 2]
        
        # Use 2-3 items (conservative but not suspicious)
        count = min(random.randint(2, 3), BAG_SIZE_LIMIT)
        declared = random.choice([g.id for g in ALL_LEGAL])
        actual_ids = [mid_value_contraband.id] * count
        
        return {
            "declared_id": declared,
            "count": count,
            "actual_ids": actual_ids,
            "lie": True,
            "lie_type": "contraband"
        }


def get_silas_declaration(history: list[dict] | None = None) -> dict:
    """
    Public interface for Silas's decision-making.
    
    This is the function that should be called by the InformationBroker class.
    It handles both first-round and subsequent-round logic.
    
    Silas now uses the deck system with intelligent redraws based on sheriff behavior:
    - Against corrupt/trigger happy: Redraws for high-value legal goods (honest bribe trick)
    - Against lenient sheriffs: Redraws for high-value contraband (maximize profit)
    - Against aggressive sheriffs: Plays it safe with whatever hand he gets
    
    Args:
        history: Optional list of previous encounters. None for first round.
        
    Returns:
        dict: What Silas declares and actually carries
    """
    # Import deck functions
    from core.mechanics.deck import draw_hand, analyze_hand, should_redraw_for_silas, redraw_cards
    
    # Draw initial hand
    hand = draw_hand(hand_size=7)
    
    # If we have history, use Silas's smart redraw logic
    if history:
        # Analyze sheriff behavior
        sheriff_analysis = analyze_sheriff_detailed(history)
        sheriff_analysis['history'] = history  # Include history for detection
        
        # Determine if Silas should redraw
        num_to_redraw = should_redraw_for_silas(hand, sheriff_analysis)
        if num_to_redraw > 0:
            # Determine Silas's redraw preference based on sheriff type
            history = sheriff_analysis.get('history', [])
            
            # Detect sheriff patterns
            is_trigger_happy = False
            is_corrupt = False
            if len(history) >= 5:
                bribed = [h for h in history[-10:] if h.get('bribe_offered', 0) > 0]
                if len(bribed) >= 3:
                    inspected_bribes = sum(1 for h in bribed if h.get('opened', False))
                    is_trigger_happy = (inspected_bribes / len(bribed)) >= 0.9
                    
                    accepted_bribes = sum(1 for h in bribed if h.get('bribe_accepted', False))
                    is_corrupt = (accepted_bribes / len(bribed)) >= 0.9
            
            # Apply intelligent discard based on sheriff type
            if is_trigger_happy:
                # Keep legal goods (especially high-value), discard contraband
                hand = redraw_cards(hand, num_to_redraw, prefer_legal=True, prefer_high_value=True)
            elif is_corrupt:
                # Keep contraband (especially high-value), discard legal goods
                hand = redraw_cards(hand, num_to_redraw, prefer_contraband=True)
            else:
                # Keep high-value cards regardless of type
                hand = redraw_cards(hand, num_to_redraw, prefer_high_value=True)
    
    # Analyze the final hand
    hand_analysis = analyze_hand(hand)
    
    # Make decision based on hand and history
    if not history:
        return SilasStrategy.choose_declaration_first_round()
    else:
        return SilasStrategy.choose_declaration_with_history(history)
