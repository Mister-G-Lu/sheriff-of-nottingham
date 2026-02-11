"""Merchants: loaded from characters/data/ with personality, lore, tells, bluff skill."""

import json
import random
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

from core.mechanics.goods import Good, ALL_LEGAL, ALL_CONTRABAND, GOOD_BY_ID
from core.systems.game_master_state import MerchantTier


@dataclass
class Merchant:
    """A merchant with intro text and bluff/lie cues."""
    id: str
    name: str
    intro: str  # Two-paragraph introduction (personality + lore)
    tells_honest: list[str]   # cues when telling truth
    tells_lying: list[str]    # cues when lying
    bluff_skill: int = 5      # used vs Sheriff perception for lie detection
    portrait_file: Optional[str] = None  # e.g. "alice.txt"
    appearance: str = ""      # visual description to help generate images
    # Personality attributes for strategy decisions
    risk_tolerance: int = 5   # 0-10: willingness to take risks
    greed: int = 5            # 0-10: desire for profit
    honesty_bias: int = 5     # 0-10: tendency to be honest (10 = very honest)
    difficulty_tier: MerchantTier = MerchantTier.MEDIUM  # AI sophistication level
    # Aggregated history summary for inspector queries (only summaries, no ids)
    past_smuggles_count: int = 0
    past_smuggles_value: int = 0
    past_legal_sold_count: int = 0
    past_legal_sold_value: int = 0
    # Gold tracking
    gold: int = 50  # Starting gold per Sheriff of Nottingham rules

    def roll_bluff(self) -> int:
        """Roll for bluff (e.g. d10 + bluff_skill)."""
        return random.randint(1, 10) + self.bluff_skill
    
    def should_offer_proactive_bribe(self, sheriff_authority: int, sheriff_reputation: int, 
                                     actual_goods: list, declared_goods: list) -> bool:
        """Decide if merchant should offer a proactive bribe before being threatened.
        
        Merchants may offer bribes proactively if:
        - They're carrying contraband
        - They're nervous/cautious
        - The sheriff has high reputation (intimidating)
        """
        # Check if carrying contraband
        has_contraband = any(not g.is_legal() for g in actual_goods)
        
        # Check if lying about legal goods mix
        is_lying = len(actual_goods) != len(declared_goods) or \
                   any(a.id != d.id for a, d in zip(actual_goods, declared_goods))
        
        # More likely to offer bribe if:
        # - Has contraband (high chance)
        # - Is lying (moderate chance)
        # - Sheriff has high reputation (increases chance)
        
        if has_contraband:
            # 60% base chance, +5% per reputation point
            chance = 0.6 + (sheriff_reputation * 0.05)
            return random.random() < min(chance, 0.9)
        elif is_lying:
            # 30% base chance, +3% per reputation point
            chance = 0.3 + (sheriff_reputation * 0.03)
            return random.random() < min(chance, 0.7)
        else:
            # Honest merchants can use "honest bribe trick" (reverse psychology)
            # Offer small bribe when honest to seem suspicious
            # Sheriff inspects → finds honest goods → merchant gets double profit!
            
            # This is a risky bluff that depends on:
            # 1. Merchant's bluff skill (higher = more likely to try)
            # 2. Sheriff's reputation (higher = more intimidating, triggers trick)
            # 3. Merchant's greed (higher = more willing to risk for profit)
            
            # Only attempt if sheriff has high reputation (5+) and merchant is skilled/greedy
            if sheriff_reputation >= 5:
                # Chance based on bluff skill and greed
                # High bluff skill (7+) and high greed (7+) = ~20% chance
                # Low bluff skill (3-) or low greed (3-) = ~2% chance
                bluff_factor = self.bluff_skill / 10  # 0.0 to 1.0
                greed_factor = self.greed / 10  # 0.0 to 1.0
                
                # Combined chance: average of bluff and greed, scaled by reputation
                base_chance = (bluff_factor + greed_factor) / 2
                reputation_bonus = (sheriff_reputation - 4) * 0.02  # +2% per point above 4
                
                honest_bribe_chance = base_chance * 0.2 + reputation_bonus
                return random.random() < min(honest_bribe_chance, 0.25)  # Cap at 25%
            
            return False
    
    def calculate_proactive_bribe(self, actual_goods: list, is_lying: bool, 
                                   sheriff_authority: int, declared_goods: list = None) -> int:
        """Calculate how much to offer as a proactive bribe.
        
        Merchants start with LOW offers to test the sheriff's greed.
        They offer a small fraction of contraband value, not the full value.
        
        Amount is based on:
        - Value of contraband (if any) - offer 10-50% as initial bribe
        - Value of mismatched legal goods (if lying about legal goods)
        - Sheriff's authority level
        - Merchant's greed/caution
        """
        # Calculate value of contraband specifically
        contraband_value = sum(g.value for g in actual_goods if not g.is_legal())
        
        if contraband_value > 0:
            # Has contraband - bribe amount based on risk tolerance
            # LOW risk tolerance (cautious) = HIGH bribes (willing to pay to avoid risk)
            # HIGH risk tolerance (bold) = LOW/NO bribes (willing to risk inspection)
            
            # Invert risk tolerance: 10 becomes 0, 0 becomes 10
            caution_level = 10 - self.risk_tolerance
            
            # Cautious merchants (low risk tolerance) offer 30-95% of contraband value
            # Bold merchants (high risk tolerance) offer 5-30% or nothing
            min_percent = 0.05 + (caution_level / 20)  # 0.05 to 0.55
            max_percent = 0.30 + (caution_level / 15)  # 0.30 to 0.97
            
            # Very bold merchants (risk_tolerance >= 8) might offer nothing at all
            if self.risk_tolerance >= 8 and random.random() < 0.3:
                base_offer = 0  # No bribe - taking the risk!
            else:
                base_offer = contraband_value * random.uniform(min_percent, max_percent)
                # Cap at contraband_value - 1 (never offer more than goods are worth)
                base_offer = min(base_offer, contraband_value - 1)
        elif is_lying and declared_goods:
            # Lying about legal goods mix - calculate value of mismatched goods
            # Example: Declare "3x Cheese (9g)" but carry "2x Cheese + 1x Bread (9g)"
            # The mismatch is 1x Bread (3g), so bribe should be based on that
            
            # Calculate total value of actual goods
            actual_value = sum(g.value for g in actual_goods)
            # Calculate what was declared (all same type)
            declared_value = sum(g.value for g in declared_goods)
            
            # The "risk" is the value difference (though both are legal)
            # Bribe for the mismatch value - 1
            mismatch_value = abs(actual_value - declared_value)
            if mismatch_value > 0:
                base_offer = max(1, mismatch_value - 1)
            else:
                # Same total value, just different mix - small bribe
                base_offer = random.uniform(1, 3)
        else:
            # Honest bribe trick (reverse psychology)
            # Offer small bribe to seem suspicious, sheriff inspects, finds honest goods
            # Bribe should be small enough to not waste too much if accepted
            # But large enough to seem "suspicious" and trigger inspection
            
            total_value = sum(g.value for g in actual_goods)
            
            # Offer 15-30% of goods value (seems suspicious but not wasteful)
            # Merchants with higher bluff skill offer more convincing amounts
            bluff_factor = self.bluff_skill / 10  # 0.0 to 1.0
            min_percent = 0.15 + (bluff_factor * 0.05)  # 15-20%
            max_percent = 0.25 + (bluff_factor * 0.05)  # 25-30%
            
            base_offer = total_value * random.uniform(min_percent, max_percent)
            
            # Cap at (total_value / 2) - 1 to avoid wasting too much if accepted
            max_offer = max(1, (total_value // 2) - 1)
            base_offer = min(base_offer, max_offer)
        
        # Adjust for sheriff authority (higher authority = slightly higher bribes)
        authority_multiplier = 1.0 + (sheriff_authority * 0.05)
        
        # Calculate final offer
        final_offer = int(base_offer * authority_multiplier)
        
        # For contraband: cap at contraband_value - 1 (never offer more than it's worth)
        # For other cases: ensure minimum of 1 gold
        if contraband_value > 0:
            return max(0, min(final_offer, contraband_value - 1))  # Can be 0 for bold merchants
        else:
            return max(1, final_offer)  # Minimum 1 gold for non-contraband bribes
    
    def choose_declaration(self, history: list[dict] | None = None) -> dict:
        """
        Choose what to declare and what to actually carry.
        
        This is the core strategic decision-making method for merchants.
        Uses the new tiered strategy system with centralized game state.
        
        Args:
            history: Optional list of previous encounters (legacy parameter)
        
        Returns:
            dict with keys:
                - 'declared_id': str (good ID to declare)
                - 'count': int (how many to declare)
                - 'actual_ids': list[str] (what's actually in bag)
                - 'lie': bool (is declaration false?)
                - 'lie_type': str ('none', 'legal', 'contraband')
                - 'bribe_amount': int (calculated bribe, 0 if none)
        """
        # Use new tiered strategy system
        from ai_strategy.tiered_strategy import get_tiered_declaration
        
        # Build personality dict
        personality = {
            'risk_tolerance': self.risk_tolerance,
            'greed': self.greed,
            'honesty_bias': self.honesty_bias
        }
        
        return get_tiered_declaration(personality, self.difficulty_tier)
    
    def record_round_result(self, round_state) -> None:
        """Record summary statistics from a completed round.

        We only store aggregate counts and values so specific contraband ids
        are not exposed until the game end.
        - If contraband slipped past the sheriff this round, use the
          round_state.contraband_passed_* summary fields.
        - Legal goods are considered delivered to the market only if the
          sheriff did NOT open the bag (i.e. merchant's goods reached market).
        """
        # Update contraband smuggled past
        c_count = getattr(round_state, "contraband_passed_count", 0)
        c_value = getattr(round_state, "contraband_passed_value", 0)
        if c_count:
            self.past_smuggles_count += c_count
            self.past_smuggles_value += c_value

        # Update legal goods delivered to market when sheriff didn't open
        if not getattr(round_state, "sheriff_opens", False):
            legal_items = [g for g in getattr(round_state, "bag_actual", []) if g.is_legal()]
            self.past_legal_sold_count += len(legal_items)
            self.past_legal_sold_value += sum(g.value for g in legal_items)

    def smuggle_summary(self) -> dict:
        """Return a summary visible to the Inspector: only counts and totals.

        Returns dict with keys: `contraband_passed_count`, `contraband_passed_value`,
        `legal_sold_count`, `legal_sold_value`.
        """
        return {
            "contraband_passed_count": self.past_smuggles_count,
            "contraband_passed_value": self.past_smuggles_value,
            "legal_sold_count": self.past_legal_sold_count,
            "legal_sold_value": self.past_legal_sold_value,
        }
    
    def should_negotiate(self, threat_level: int, goods_value: int, round_number: int) -> bool:
        """Decide whether to negotiate/offer a bribe when threatened.
        
        Args:
            threat_level: How serious the inspection threat is (1-10)
            goods_value: Total value of contraband in bag
            round_number: Current negotiation round number
        
        Returns:
            True if merchant wants to negotiate, False otherwise
        """
        # Higher risk tolerance = more willing to gamble without bribing
        # Lower greed = more willing to pay bribes
        # Higher threat level = more likely to negotiate
        
        # Base willingness on threat level and risk tolerance
        willingness = threat_level * 10 - self.risk_tolerance * 5
        
        # Reduce willingness in later rounds (merchant gets tired)
        willingness -= (round_number - 1) * 10
        
        # Add some randomness
        willingness += random.randint(-10, 10)
        
        return willingness > 30
    
    def calculate_bribe_offer(self, goods_value: int, threat_level: int) -> int:
        """Calculate how much to offer as a bribe.
        
        NOTE: This method is deprecated in favor of the new bribe_strategy module.
        Kept for backward compatibility.
        
        Args:
            goods_value: Total value of contraband in bag
            threat_level: How serious the inspection threat is (1-10)
        
        Returns:
            Gold amount to offer as bribe
        """
        if goods_value == 0:
            return 0
        
        # Start with a percentage of goods value based on threat
        base_percentage = 0.3 + (threat_level / 20)  # 30-80% of value
        
        # Adjust for greed (higher greed = lower offer)
        greed_factor = 1.0 - (self.greed / 20)  # 0.5 to 1.0
        
        # Adjust for risk tolerance (higher risk = lower offer)
        risk_factor = 1.0 - (self.risk_tolerance / 30)  # 0.67 to 1.0
        
        offer = int(goods_value * base_percentage * greed_factor * risk_factor)
        
        # Ensure minimum offer of 1 gold
        return max(1, offer)
    
    def should_accept_counter(self, sheriff_demand: int, original_offer: int, goods_value: int) -> bool:
        """Decide whether to accept sheriff's counter-demand.
        
        NOTE: This method now uses the new bribe_strategy module for more sophisticated logic.
        
        Args:
            sheriff_demand: Amount sheriff is demanding
            original_offer: Merchant's original offer
            goods_value: Total value of contraband in bag
        
        Returns:
            True if merchant accepts the demand, False to continue negotiating
        """
        # Use new bribe strategy system
        from ai_strategy.bribe_strategy import should_accept_counter_offer
        
        # We need actual_good_ids, but we don't have them here in the old interface
        # Fall back to legacy logic for now
        demand_ratio = sheriff_demand / goods_value if goods_value > 0 else 1.0
        
        # Greedy merchants are less willing to accept high demands
        greed_threshold = 0.5 + (self.greed / 20)  # 0.5 to 1.0
        
        # Risk-tolerant merchants are more willing to gamble and reject
        risk_threshold = 0.7 - (self.risk_tolerance / 20)  # 0.2 to 0.7
        
        # Accept if demand is below threshold
        if demand_ratio < min(greed_threshold, risk_threshold):
            return True
        
        # Tier-based acceptance
        if self.difficulty_tier == MerchantTier.EASY:
            return random.random() < 0.6
        elif self.difficulty_tier == MerchantTier.MEDIUM:
            return random.random() < 0.4
        else:  # HARD
            return random.random() < 0.2


class InformationBroker(Merchant):
    """A special merchant that analyzes recent merchant history to decide strategy.

    See core/silas_strategy.py for detailed implementation and comments.
    """

    def choose_declaration(self, history: list[dict] | None = None) -> dict:
        """
        Delegate to Silas's sophisticated strategy module.
        
        The actual decision-making logic is in ai_strategy/silas_strategy.py to keep
        this file focused on the base Merchant class and simple merchant types.
        """
        from ai_strategy.silas_strategy import get_silas_declaration
        return get_silas_declaration(history)
    
    def should_offer_proactive_bribe(self, sheriff_authority: int, sheriff_reputation: int, 
                                     actual_goods: list, declared_goods: list) -> bool:
        """
        Silas can offer strategic bribes even when honest (reverse psychology).
        
        This is a mind game: offering a small bribe when honest makes the sheriff
        suspicious, potentially wasting their inspection on an honest merchant.
        
        Special case: If sheriff is "trigger happy" (inspects all bribes), 
        Silas ALWAYS bribes when honest to exploit this pattern.
        """
        # Check if actually honest
        has_contraband = any(not g.is_legal() for g in actual_goods)
        is_lying = len(actual_goods) != len(declared_goods) or \
                   any(a.id != d.id for a, d in zip(actual_goods, declared_goods))
        
        # If not honest, use normal bribe logic
        if has_contraband or is_lying:
            return super().should_offer_proactive_bribe(
                sheriff_authority, sheriff_reputation, actual_goods, declared_goods
            )
        
        # Silas is honest - check for trigger happy pattern
        from core.systems.game_master_state import get_game_master_state
        from ai_strategy.silas_strategy import SilasStrategy
        
        game_state = get_game_master_state()
        history = game_state.get_history_for_tier(None)  # Get full history
        
        # If trigger happy sheriff detected, ALWAYS bribe (exploit!)
        if SilasStrategy.detect_trigger_happy_sheriff(history):
            return True  # Always bribe to trigger inspection on honest goods
        
        # Otherwise, use normal strategic bribe logic
        # 20% chance if sheriff has high reputation (5+) and authority
        if sheriff_reputation >= 5 and sheriff_authority >= 2:
            return random.random() < 0.2
        
        # 10% chance if sheriff has moderate reputation
        if sheriff_reputation >= 3:
            return random.random() < 0.1
        
        # Otherwise, no bribe when honest
        return False
    
    def calculate_proactive_bribe(self, actual_goods: list, is_lying: bool, 
                                   sheriff_authority: int, declared_goods: list = None) -> int:
        """
        Calculate Silas's strategic bribe amount.
        
        When honest: Offers small "suspicious" bribe (less than half goods value)
        to trick sheriff into wasting an inspection.
        
        When lying: Detects sheriff patterns and optimizes bribe amount.
        - Corrupt sheriff (accepts all bribes): Minimal bribes (1-3g)
        - Normal sheriff: Standard calculation
        """
        # Check if actually honest
        has_contraband = any(not g.is_legal() for g in actual_goods)
        
        # If lying or has contraband, check for sheriff patterns
        if has_contraband or is_lying:
            from core.systems.game_master_state import get_game_master_state
            from ai_strategy.silas_strategy import SilasStrategy
            
            game_state = get_game_master_state()
            history = game_state.get_history_for_tier(None)
            
            if len(history) >= 5:
                recent = history[-10:] if len(history) >= 10 else history
                
                # Detect "corrupt & greedy" sheriff (accepts all bribes)
                if SilasStrategy.detect_corrupt_sheriff(history):
                    # Corrupt sheriffs accept ANY bribe, so offer the absolute minimum
                    # This maximizes profit: expensive contraband - tiny bribe = huge profit!
                    # Offer 1-2g (occasionally 3g to avoid suspicion pattern)
                    minimal_bribe = random.choice([1, 1, 1, 2, 2, 3])  # Weighted toward 1g
                    return minimal_bribe
                
                # Detect "adaptive" sheriff (changes behavior based on results)
                if SilasStrategy.detect_adaptive_sheriff(history):
                    # Against adaptive sheriffs, use DECLARED value for initial bribe
                    # This makes the bribe seem reasonable to the sheriff
                    # (Sheriff can't see actual goods, only declaration)
                    
                    # Calculate declared value
                    if declared_goods:
                        declared_value = sum(g.value for g in declared_goods)
                    else:
                        # Fallback: use actual goods value
                        declared_value = sum(g.value for g in actual_goods)
                    
                    # Offer 25-35% of DECLARED value (seems reasonable to sheriff)
                    # Smart sheriffs reject bribes > 40% of declared value
                    # Smart sheriffs accept bribes < 30% of declared value
                    optimal_percent = random.uniform(0.25, 0.35)
                    optimal_bribe = int(declared_value * optimal_percent)
                    return max(1, optimal_bribe)
            
            # Normal calculation for non-pattern sheriffs
            return super().calculate_proactive_bribe(
                actual_goods, is_lying, sheriff_authority, declared_goods
            )
        
        # Silas is honest but offering strategic bribe (reverse psychology)
        # Offer small amount - less than half the value of goods
        total_value = sum(g.value for g in actual_goods)
        
        # Offer 20-40% of goods value (suspicious but not too high)
        bribe_percent = random.uniform(0.2, 0.4)
        strategic_bribe = int(total_value * bribe_percent)
        
        # Cap at half goods value - 1
        max_bribe = (total_value // 2) - 1
        
        return max(1, min(strategic_bribe, max_bribe))
    
    def calculate_counter_offer(self, actual_goods: list, is_lying: bool, 
                                sheriff_authority: int, current_bribe: int,
                                declared_goods: list = None) -> int:
        """
        Calculate Silas's counter-offer when sheriff threatens to inspect.
        
        This is the second stage of Silas's bribery strategy:
        - Initial bribe: Based on DECLARED value (to seem reasonable)
        - Counter-offer: Based on ACTUAL value (to protect contraband)
        
        Silas knows his actual contraband value and can decide if it's worth
        paying more to avoid losing 2x the contraband value as a penalty.
        
        Args:
            actual_goods: What Silas is actually carrying
            is_lying: Whether he's lying about contents
            sheriff_authority: Sheriff's authority level
            current_bribe: The bribe amount already offered
            declared_goods: What Silas declared (for comparison)
            
        Returns:
            New bribe amount (0 = refuse to raise, keep current offer)
        """
        # Check if actually honest
        has_contraband = any(not g.is_legal() for g in actual_goods)
        
        if not has_contraband and not is_lying:
            # Honest - don't raise bribe, let sheriff inspect
            return 0
        
        # Calculate actual contraband value
        contraband_value = sum(g.value for g in actual_goods if not g.is_legal())
        
        if contraband_value == 0:
            # No contraband (just lying about legal goods mix)
            # Small raise is acceptable
            return current_bribe + random.randint(1, 3)
        
        # Has contraband - calculate if raising bribe is worth it
        # If caught: lose 2x contraband value
        # If bribe accepted: lose bribe amount but keep contraband
        
        # Maximum reasonable bribe: half of contraband value
        # (If bribe > contraband_value / 2, better to risk inspection)
        max_reasonable_bribe = contraband_value // 2
        
        # Silas's strategy: offer up to 40% of contraband value
        # This is less than the penalty (2x value) but more than initial bribe
        target_bribe = int(contraband_value * random.uniform(0.3, 0.4))
        
        # Don't exceed maximum reasonable amount
        target_bribe = min(target_bribe, max_reasonable_bribe)
        
        # Only raise if target is higher than current bribe
        if target_bribe > current_bribe:
            return target_bribe
        else:
            # Current bribe is already high enough, don't raise
            return 0


def characters_dir() -> Path:
    # Go up two levels from core/players/ to reach project root
    root = Path(__file__).resolve().parent.parent.parent
    return root / "characters"


def load_merchants(limit: Optional[int] = None) -> list[Merchant]:
    """Load merchants from characters/data/*.json, randomly ordered. Optionally limit count."""
    chars_dir = characters_dir() / "data"
    if not chars_dir.exists():
        return []

    jsons = list(chars_dir.glob("*.json"))
    if limit is not None:
        # Use random.sample for efficient random selection
        jsons = random.sample(jsons, min(limit, len(jsons)))
    else:
        random.shuffle(jsons)

    merchants: list[Merchant] = []
    for path in jsons:
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            role = data.get("role")
            cls = Merchant
            if role == "broker":
                cls = InformationBroker
            # Determine difficulty tier
            # Brokers are HARD, others assigned based on personality
            if role == "broker":
                tier = MerchantTier.HARD
            else:
                # Assign tier based on personality traits
                risk = int(data.get("risk_tolerance", 5))
                greed_val = int(data.get("greed", 5))
                honesty = int(data.get("honesty_bias", 5))
                
                # Calculate sophistication score
                sophistication = risk + greed_val - honesty
                
                if sophistication <= 5:
                    tier = MerchantTier.EASY
                elif sophistication <= 10:
                    tier = MerchantTier.MEDIUM
                else:
                    tier = MerchantTier.HARD
            
            m = cls(
                id=data.get("id", path.stem),
                name=data.get("name", path.stem),
                intro=data.get("intro", ""),
                tells_honest=data.get("tells_honest", []),
                tells_lying=data.get("tells_lying", []),
                bluff_skill=int(data.get("bluff_skill", 5)),
                portrait_file=data.get("portrait_file"),
                appearance=data.get("appearance", ""),
                risk_tolerance=int(data.get("risk_tolerance", 5)),
                greed=int(data.get("greed", 5)),
                honesty_bias=int(data.get("honesty_bias", 5)),
                difficulty_tier=tier,
            )
            merchants.append(m)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Failed to load merchant from {path.name}: {e}")
            continue
        except Exception as e:
            print(f"Warning: Unexpected error loading merchant from {path.name}: {e}")
            import traceback
            traceback.print_exc()
            continue
    return merchants
