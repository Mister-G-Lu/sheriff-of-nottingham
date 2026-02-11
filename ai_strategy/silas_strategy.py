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
    def should_tell_truth(analysis: dict) -> bool:
        """
        Determine if Silas should tell the truth this round.
        
        Silas tells the truth when:
        1. Sheriff is catching most smugglers (>60% catch rate)
        2. Sheriff is very aggressive with inspections (>70% inspection rate)
        
        This is a defensive strategy - when the environment is too dangerous,
        Silas plays it safe and waits for better opportunities.
        
        Args:
            analysis: Sheriff behavior analysis from analyze_sheriff_behavior()
            
        Returns:
            bool: True if Silas should tell truth, False if he should lie
        """
        catch_rate = analysis['catch_rate']
        inspection_rate = analysis['inspection_rate']
        
        # If sheriff is catching most smugglers, too dangerous to lie
        if catch_rate > 0.6:
            return True
        
        # If sheriff is very aggressive with inspections, play it safe
        if inspection_rate > 0.7:
            return True
        
        return False
    
    @staticmethod
    def calculate_optimal_contraband_count(analysis: dict) -> int:
        """
        Calculate how many contraband items Silas should smuggle.
        
        Silas scales his risk based on how lenient the sheriff is:
        - Very lenient sheriff: 3-4 items (moderate risk, within 6-card limit)
        - Active sheriff: 2-3 items (conservative)
        - Dangerous sheriff: 1-2 items (very conservative)
        
        Always respects the 6-card bag limit.
        
        Args:
            analysis: Sheriff behavior analysis
            
        Returns:
            int: Number of contraband items to smuggle (1-4, within bag limit)
        """
        catch_rate = analysis['catch_rate']
        inspection_rate = analysis['inspection_rate']
        
        # Sheriff is very lenient - can take moderate risk (3-4 items)
        if catch_rate < 0.3 and inspection_rate < 0.4:
            return min(random.randint(3, 4), BAG_SIZE_LIMIT)
        
        # Sheriff is somewhat active - stay conservative (2-3 items)
        elif catch_rate < 0.5:
            return min(random.randint(2, 3), BAG_SIZE_LIMIT)
        
        # Sheriff is dangerous - very conservative (1-2 items)
        return min(random.randint(1, 2), BAG_SIZE_LIMIT)
    
    @staticmethod
    def select_contraband_value(analysis: dict) -> object:
        """
        Select which contraband item to smuggle based on risk assessment.
        
        Silas chooses contraband value based on how safe the environment is:
        - Very safe: Highest value items
        - Moderate: Mid-high value items
        - Risky: Mid value items only
        
        This ensures his bribe offers scale appropriately with risk.
        
        Args:
            analysis: Sheriff behavior analysis
            
        Returns:
            Good: The contraband item to smuggle
        """
        catch_rate = analysis['catch_rate']
        contraband_options = sorted(ALL_CONTRABAND, key=lambda g: g.value)
        
        if catch_rate < 0.2:
            # Very safe - go for highest value
            return contraband_options[-1]
        elif catch_rate < 0.4:
            # Moderate safety - mid-high value
            index = len(contraband_options) * 2 // 3
            return contraband_options[index]
        else:
            # Risky - stick to mid value
            index = len(contraband_options) // 2
            return contraband_options[index]
    
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
        # Calculate optimal risk level
        contraband_count = SilasStrategy.calculate_optimal_contraband_count(analysis)
        
        # Step 4: Select contraband based on risk assessment
        contraband = SilasStrategy.select_contraband_value(analysis)
        
        # Step 5: Build declaration (within bag limit)
        declared = random.choice([g.id for g in ALL_LEGAL])
        actual_ids = [contraband.id] * min(contraband_count, BAG_SIZE_LIMIT)
        
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
    
    Args:
        history: Optional list of previous encounters. None for first round.
        
    Returns:
        dict: What Silas declares and actually carries
    """
    if not history:
        return SilasStrategy.choose_declaration_first_round()
    else:
        return SilasStrategy.choose_declaration_with_history(history)
