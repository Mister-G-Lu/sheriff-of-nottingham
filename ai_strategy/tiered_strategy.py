"""
Tiered Merchant Strategy System

This module implements difficulty-based merchant behavior:
- Easy: Simple, safe decisions with minimal history analysis
- Medium: Moderate risk-taking with pattern recognition
- Hard: Advanced strategies with full history analysis and bluff tactics

Each tier has different:
- History access (1-2 events vs 3-4 vs full)
- Decision complexity
- Bribe frequency and sophistication
- Bluff strategies
"""

import random
from core.systems.game_master_state import MerchantTier, get_game_master_state
from ai_strategy.bribe_strategy import calculate_scaled_bribe, should_accept_counter_offer
from ai_strategy.declaration_builder import build_declaration


class TieredMerchantStrategy:
    """
    Manager-level decision flow for tiered merchant behavior.
    
    Decision Flow:
    1. Evaluate hand (legal vs contraband available)
    2. Select strategy type based on hand + personality + tier
    3. Choose bag contents and plausible declarations
    4. Estimate inspection risk using history slice
    5. Decide bribe amount with advanced logic
    6. Return final decision: bag, declared_type, bribe
    """
    
    @staticmethod
    def choose_declaration(
        merchant_personality: dict,
        tier: MerchantTier,
        available_goods: dict = None
    ) -> dict:
        """
        Main entry point for tiered merchant decisions.
        
        Args:
            merchant_personality: Dict with risk_tolerance, greed, honesty_bias
            tier: Merchant difficulty tier
            available_goods: Optional dict of available goods (drawn hand)
            
        Returns:
            dict with declared_id, count, actual_ids, lie, bribe_amount
        """
        # Get game master state for history
        game_state = get_game_master_state()
        history = game_state.get_history_for_tier(tier)
        sheriff_stats = game_state.get_sheriff_stats()
        
        # Draw a hand if not provided (7 cards for AI merchants)
        if available_goods is None:
            from core.mechanics.deck import draw_hand, analyze_hand, should_redraw_for_contraband, redraw_cards
            
            # Initial draw
            hand = draw_hand(hand_size=7)
            
            # Check if merchant wants to redraw for better cards
            risk_tolerance = merchant_personality.get('risk_tolerance', 5)
            honesty = merchant_personality.get('honesty_bias', 5)
            
            num_to_redraw = should_redraw_for_contraband(hand, risk_tolerance, honesty)
            if num_to_redraw > 0:
                # Determine redraw preference based on personality
                if honesty >= 7 and risk_tolerance <= 4:
                    # Honest merchants: keep legal goods, discard contraband
                    hand = redraw_cards(hand, num_to_redraw, prefer_legal=True, prefer_high_value=True)
                elif risk_tolerance >= 7 and honesty <= 4:
                    # Aggressive merchants: keep contraband, discard legal goods
                    hand = redraw_cards(hand, num_to_redraw, prefer_contraband=True)
                else:
                    # Moderate merchants: keep high-value cards
                    hand = redraw_cards(hand, num_to_redraw, prefer_high_value=True)
            
            available_goods = analyze_hand(hand)
        
        # Step 1: Evaluate hand and select strategy type
        strategy_type = TieredMerchantStrategy._select_strategy_type(
            merchant_personality, tier, sheriff_stats, history
        )
        
        # Step 2: Build bag and declaration based on strategy and available goods
        declaration = TieredMerchantStrategy._build_declaration(
            strategy_type, merchant_personality, tier, available_goods
        )
        
        # Step 3: Calculate bribe amount (if applicable)
        bribe_amount = calculate_scaled_bribe(
            declared_good_id=declaration['declared_id'],
            declared_count=declaration['count'],
            actual_good_ids=declaration['actual_ids'],
            is_lying=declaration['lie'],
            personality=merchant_personality,
            sheriff_stats=sheriff_stats,
            tier=tier
        )
        
        declaration['bribe_amount'] = bribe_amount
        declaration['tier'] = tier.value
        
        return declaration
    
    @staticmethod
    def _calculate_risk_score(
        honesty: int,
        risk: int,
        greed: int,
        inspection_rate: float,
        catch_rate: float,
        tier: MerchantTier,
        history: list[dict] = None
    ) -> float:
        """
        Calculate risk score based on personality and sheriff behavior.
        
        Returns:
            float: Risk score (0-10), higher = more aggressive smuggling
        """
        # Base risk score: primarily risk_tolerance, modified by greed and honesty
        if tier == MerchantTier.EASY:
            # Easy: Simple formula, honesty has strong effect
            risk_score = risk - (honesty - 5) * 0.5
        else:
            # Medium/Hard: More complex, greed also matters
            risk_score = risk + (greed - 5) * 0.3 - (honesty - 5) * 0.5
        
        # Adjust for sheriff behavior
        if inspection_rate > 0.6:
            risk_score -= 3 if tier == MerchantTier.EASY else 2.5
        elif inspection_rate < 0.3:
            risk_score += 2 if tier == MerchantTier.EASY else 2.5
        
        # Medium/Hard tiers also consider catch rate
        if tier != MerchantTier.EASY:
            if catch_rate > 0.7:
                risk_score -= 2
            elif catch_rate < 0.3:
                risk_score += 1.5
        
        # Hard tier: Advanced pattern analysis
        if tier == MerchantTier.HARD and history and len(history) >= 3:
            recent = history[-5:]
            recent_passes = [h for h in recent if not h.get('opened', False)]
            
            # Exploit lenient sheriffs
            if len(recent_passes) >= 4:
                risk_score += 4
            
            # Counter-strategy for effective sheriffs
            if catch_rate > 0.7:
                risk_score -= 3
            
            # Detect greedy sheriffs
            bribes_accepted = [h for h in recent if h.get('bribe_accepted', False)]
            if len(bribes_accepted) >= 2:
                risk_score += 2
            
            # Calculate danger level
            danger_level = (inspection_rate * 0.6) + (catch_rate * 0.4)
            risk_score -= (danger_level * 4)
        
        # Clamp to 0-10
        return max(0, min(10, risk_score))
    
    @staticmethod
    def _get_strategy_weights(risk_score: float, tier: MerchantTier) -> list[float]:
        """
        Get strategy weights based on risk score and tier.
        
        Returns:
            list: Weights for [honest, legal_lie, mixed, contraband_low, contraband_high]
        """
        # Define weight tables for each tier
        if tier == MerchantTier.EASY:
            # Easy: Most cautious
            if risk_score <= 0:
                return [0.95, 0.04, 0.01, 0.0, 0.0]
            elif risk_score <= 2:
                return [0.75, 0.20, 0.04, 0.01, 0.0]
            elif risk_score <= 4:
                return [0.50, 0.35, 0.12, 0.03, 0.0]
            elif risk_score <= 6:
                return [0.35, 0.35, 0.20, 0.08, 0.02]
            elif risk_score <= 8:
                return [0.20, 0.30, 0.30, 0.15, 0.05]
            else:
                return [0.05, 0.15, 0.25, 0.35, 0.20]
        
        elif tier == MerchantTier.MEDIUM:
            # Medium: Moderate risk-taking
            if risk_score <= 0:
                return [0.90, 0.08, 0.02, 0.0, 0.0]
            elif risk_score <= 2:
                return [0.65, 0.25, 0.08, 0.02, 0.0]
            elif risk_score <= 4:
                return [0.40, 0.30, 0.22, 0.06, 0.02]
            elif risk_score <= 6:
                return [0.25, 0.25, 0.30, 0.15, 0.05]
            elif risk_score <= 8:
                return [0.12, 0.18, 0.30, 0.28, 0.12]
            else:
                return [0.05, 0.10, 0.25, 0.40, 0.20]
        
        else:  # HARD
            # Hard: Most aggressive
            if risk_score <= 2:
                return [0.40, 0.30, 0.20, 0.08, 0.02]
            elif risk_score <= 4:
                return [0.25, 0.25, 0.30, 0.15, 0.05]
            elif risk_score <= 6:
                return [0.15, 0.20, 0.30, 0.25, 0.10]
            elif risk_score <= 8:
                return [0.08, 0.15, 0.27, 0.35, 0.15]
            else:
                return [0.05, 0.10, 0.25, 0.40, 0.20]
    
    @staticmethod
    def _select_strategy_type(
        personality: dict,
        tier: MerchantTier,
        sheriff_stats: dict,
        history: list[dict]
    ) -> str:
        """
        Select which strategy type to use.
        
        Returns:
            Strategy type: 'honest', 'legal_lie', 'mixed', 'contraband_low', 'contraband_high'
        """
        honesty = personality.get('honesty_bias', 5)
        risk = personality.get('risk_tolerance', 5)
        greed = personality.get('greed', 5)
        
        inspection_rate = sheriff_stats.get('inspection_rate', 0.5)
        catch_rate = sheriff_stats.get('catch_rate', 0.5)
        
        # CONSCIENCE CHECK: High honesty_bias merchants may refuse to lie
        # This makes honesty_bias's effect more explicit and direct
        # Chance to "feel guilty" and stay honest increases with honesty_bias
        if honesty >= 8:
            # Very honest merchants (8-10): 20-40% chance to refuse lying
            conscience_check = (honesty - 7) * 0.1  # 10%, 20%, 30% for honesty 8, 9, 10
            if random.random() < conscience_check:
                return 'honest'  # Conscience says no!
        
        # Hard tier: Check for reverse psychology opportunity
        if tier == MerchantTier.HARD and catch_rate > 0.7 and random.random() < 0.25:
            return 'honest'  # Reverse psychology
        
        # Calculate risk score
        risk_score = TieredMerchantStrategy._calculate_risk_score(
            honesty, risk, greed, inspection_rate, catch_rate, tier, history
        )
        
        # Get weights and select strategy
        weights = TieredMerchantStrategy._get_strategy_weights(risk_score, tier)
        
        strategy = random.choices(
            ['honest', 'legal_lie', 'mixed', 'contraband_low', 'contraband_high'],
            weights=weights
        )[0]
        
        # SECOND CONSCIENCE CHECK: Even if strategy selected is dishonest,
        # high honesty merchants may change their mind
        if strategy in ['contraband_low', 'contraband_high'] and honesty >= 7:
            # 10-30% chance to back out of smuggling for honest merchants
            guilt_factor = (honesty - 6) * 0.05  # 5%, 10%, 15%, 20% for honesty 7, 8, 9, 10
            if random.random() < guilt_factor:
                return 'honest'  # Changed mind, too risky/wrong
        
        return strategy
    
    @staticmethod
    def _build_declaration(
        strategy_type: str,
        personality: dict,
        tier: MerchantTier,
        available_goods: dict = None
    ) -> dict:
        """
        Build bag contents and declaration based on strategy and available goods.
        
        Uses the consolidated declaration_builder module to avoid code duplication.
        If available_goods is provided, the merchant will choose from their drawn hand.
        
        Args:
            strategy_type: Strategy to use (honest, legal_lie, mixed, contraband_low, contraband_high)
            personality: Merchant personality traits
            tier: Merchant difficulty tier
            available_goods: Optional dict with 'legal', 'contraband', 'counts' from analyze_hand()
        
        Returns:
            dict with declared_id, count, actual_ids, lie, lie_type, strategy
        """
        return build_declaration(strategy_type, available_goods)


def get_tiered_declaration(
    merchant_personality: dict,
    tier: MerchantTier
) -> dict:
    """
    Public interface for tiered merchant decisions.
    
    Args:
        merchant_personality: Dict with risk_tolerance, greed, honesty_bias
        tier: Merchant difficulty tier
        
    Returns:
        dict with declared_id, count, actual_ids, lie, bribe_amount
    """
    return TieredMerchantStrategy.choose_declaration(merchant_personality, tier)
