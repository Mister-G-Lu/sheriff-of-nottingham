"""Merchants: loaded from characters/data/ with personality, lore, tells, bluff skill."""

import random
from dataclasses import dataclass
from typing import Optional

from core.constants import (
    BRIBE_PROB_HIGH,
    BRIBE_PROB_LOW,
    BRIBE_PROB_MODERATE,
    MERCHANT_ATTRIBUTE_MAX,
)
from core.systems.game_master_state import MerchantTier


@dataclass
class Merchant:
    """A merchant with intro text and bluff/lie cues."""

    id: str
    name: str
    intro: str  # Two-paragraph introduction (personality + lore)
    tells_honest: list[str]  # cues when telling truth
    tells_lying: list[str]  # cues when lying
    bluff_skill: int = 5  # used vs Sheriff perception for lie detection
    portrait_file: Optional[str] = None  # e.g. "alice.txt"
    appearance: str = ""  # visual description to help generate images
    # Personality attributes for strategy decisions
    risk_tolerance: int = 5  # 0-10: willingness to take risks
    greed: int = 5  # 0-10: desire for profit
    honesty_bias: int = 5  # 0-10: tendency to be honest (10 = very honest)
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

    def should_offer_proactive_bribe(
        self,
        sheriff_authority: int,
        sheriff_reputation: int,
        actual_goods: list,
        declared_goods: list,
    ) -> bool:
        """Decide if merchant should offer a proactive bribe before being threatened.

        Merchants may offer bribes proactively if:
        - They're carrying contraband
        - They're nervous/cautious
        - The sheriff has high reputation (intimidating)
        """
        # Check if carrying contraband
        has_contraband = any(not g.is_legal() for g in actual_goods)

        # Check if lying about legal goods mix
        is_lying = len(actual_goods) != len(declared_goods) or any(
            a.id != d.id for a, d in zip(actual_goods, declared_goods)
        )

        # More likely to offer bribe if:
        # - Has contraband (high chance)
        # - Is lying (moderate chance)
        # - Sheriff has high reputation (increases chance)

        if has_contraband:
            # Base chance adjusted by personality:
            # - Risk tolerance: Higher risk = more likely to bribe (0-10 scale)
            # - Greed: Higher greed = more likely to bribe to protect profit (0-10 scale)
            # - Honesty bias: STRONG effect - honest merchants think "why bribe if I'm honest?"

            # Calculate personality factor (0.0 to 1.0)
            risk_factor = self.risk_tolerance / 10  # 0.0 to 1.0
            greed_factor = self.greed / 10  # 0.0 to 1.0

            # Honesty has DOUBLE weight - honest merchants are very uncomfortable bribing
            # Honesty 10 = 0.0, Honesty 5 = 0.5, Honesty 0 = 1.0
            honesty_penalty = (10 - self.honesty_bias) / 10

            # Weighted average: honesty counts twice as much
            personality_factor = (risk_factor + greed_factor + honesty_penalty * 2) / 4

            # Very honest merchants (8+) get additional penalty
            if self.honesty_bias >= 8:
                # "Why should I bribe? I'm honest!" mentality
                # Honesty 8 = -30%, Honesty 9 = -45%, Honesty 10 = -60%
                honesty_confidence = (self.honesty_bias - 7) * 0.15
                personality_factor = max(0, personality_factor - honesty_confidence)

            # Base chance: 10-80% depending on personality (lower floor for honest merchants)
            base_chance = 0.1 + (personality_factor * 0.7)

            # Add reputation bonus (scaled by personality - cautious/honest merchants less affected)
            reputation_bonus = (
                sheriff_reputation * 0.015 * (0.3 + personality_factor * 0.7)
            )

            # Very honest merchants (9+) have a hard cap on bribe chance
            if self.honesty_bias >= 9:
                max_chance = 0.10  # Cap at 10% for very honest merchants
            elif self.honesty_bias >= 8:
                max_chance = 0.25  # Cap at 25% for honest merchants
            else:
                max_chance = 0.95  # Normal cap

            # Final chance
            chance = base_chance + reputation_bonus
            return random.random() < min(chance, max_chance)

        elif is_lying:
            # Similar logic for lying about legal goods
            risk_factor = self.risk_tolerance / MERCHANT_ATTRIBUTE_MAX
            greed_factor = self.greed / MERCHANT_ATTRIBUTE_MAX
            honesty_penalty = (
                MERCHANT_ATTRIBUTE_MAX - self.honesty_bias
            ) / MERCHANT_ATTRIBUTE_MAX

            personality_factor = (risk_factor + greed_factor + honesty_penalty) / 3

            # Base chance: 20-50% depending on personality
            base_chance = BRIBE_PROB_LOW + (personality_factor * BRIBE_PROB_MODERATE)

            # Add reputation bonus
            reputation_bonus = sheriff_reputation * 0.03

            # Final chance
            chance = base_chance + reputation_bonus
            return random.random() < min(chance, 0.75)  # Cap at 75%
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
                reputation_bonus = (
                    sheriff_reputation - 4
                ) * 0.02  # +2% per point above 4

                honest_bribe_chance = base_chance * 0.2 + reputation_bonus
                return random.random() < min(honest_bribe_chance, 0.25)  # Cap at 25%

            return False

    def calculate_proactive_bribe(
        self,
        actual_goods: list,
        is_lying: bool,
        sheriff_authority: int,
        declared_goods: list = None,
    ) -> int:
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

            # Offer 10% up to 70% of good value as basis
            bluff_factor = self.bluff_skill / 10  # 0.0 to 1.0
            min_percent = 0.10 + (bluff_factor * 0.1)  # 10-20%
            max_percent = 0.70 + (bluff_factor * 0.1)  # 70-80%

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
            return max(
                0, min(final_offer, contraband_value - 1)
            )  # Can be 0 for bold merchants
        else:
            return max(1, final_offer)  # Minimum 1 gold for non-contraband bribes

    def choose_declaration(self, history: list = None) -> dict:
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
            "risk_tolerance": self.risk_tolerance,
            "greed": self.greed,
            "honesty_bias": self.honesty_bias,
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
            legal_items = [
                g for g in getattr(round_state, "bag_actual", []) if g.is_legal()
            ]
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

    def should_negotiate(
        self, threat_level: int, goods_value: int, round_number: int
    ) -> bool:
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

    def should_accept_counter(
        self, sheriff_demand: int, original_offer: int, goods_value: int
    ) -> bool:
        """Decide whether to accept sheriff's counter-demand.

        NOTE: This method now uses the new bribe_strategy module for more sophisticated logic.

        Args:
            sheriff_demand: Amount sheriff is demanding
            original_offer: Merchant's original offer
            goods_value: Total value of contraband in bag

        Returns:
            True if merchant accepts the demand, False to continue negotiating
        """
        # Use legacy logic (bribe_strategy requires actual_good_ids which we don't have here)
        demand_ratio = sheriff_demand / goods_value if goods_value > 0 else 1.0

        # Greedy merchants are less willing to accept high demands
        greed_threshold = 0.5 + (self.greed / 20)  # 0.5 to 1.0

        # Risk-tolerant merchants are more willing to gamble and reject
        risk_threshold = 0.7 - (self.risk_tolerance / 20)  # 0.2 to 0.7

        # Accept if demand is below threshold
        if demand_ratio < min(greed_threshold, risk_threshold):
            return True

        # Tier-based acceptance
        if self.risk_tolerance >= 8:
            return random.random() < BRIBE_PROB_HIGH
        elif self.risk_tolerance >= 6:
            return random.random() < (BRIBE_PROB_LOW * 2)  # 0.4
        else:  # HARD
            return random.random() < BRIBE_PROB_LOW


# Note: load_merchants() and characters_dir() have been moved to merchant_loader.py
# to avoid circular import issues. Import from there instead:
# from core.players.merchant_loader import load_merchants, characters_dir
