"""Merchants: loaded from characters/data/ with personality, lore, tells, bluff skill."""

import json
import random
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

from core.mechanics.goods import Good, ALL_LEGAL, ALL_CONTRABAND, GOOD_BY_ID


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
            # Honest merchants rarely offer proactive bribes (goodwill gesture)
            return random.random() < 0.1
    
    def calculate_proactive_bribe(self, actual_goods: list, is_lying: bool, 
                                   sheriff_authority: int) -> int:
        """Calculate how much to offer as a proactive bribe.
        
        A rational merchant will NEVER offer less than the value of their goods.
        The bribe must be worth more than losing the contraband.
        
        Amount is based on:
        - Total value of goods (minimum baseline)
        - Value of contraband (if any)
        - Sheriff's authority level
        - Merchant's greed/caution
        """
        # Calculate total value of all goods
        total_goods_value = sum(g.value for g in actual_goods)
        
        # Calculate value of contraband specifically
        contraband_value = sum(g.value for g in actual_goods if not g.is_legal())
        
        if contraband_value > 0:
            # Has contraband - offer 40-60% of contraband value, but at least the total goods value
            contraband_offer = contraband_value * random.uniform(0.4, 0.6)
            base_offer = max(total_goods_value, contraband_offer)
        elif is_lying:
            # Lying about legal goods mix - offer slightly more than goods value to avoid inspection
            base_offer = total_goods_value * random.uniform(1.1, 1.3)
        else:
            # Honest goodwill gesture - small amount (not based on goods value)
            base_offer = random.randint(3, 8)
        
        # Adjust for sheriff authority (higher authority = higher bribes)
        authority_multiplier = 1.0 + (sheriff_authority * 0.1)
        
        return max(1, int(base_offer * authority_multiplier))
    
    def choose_declaration(self, history: list[dict] | None = None) -> dict:
        """
        Choose what to declare and what to actually carry.
        
        This is the core strategic decision-making method for merchants.
        Merchants analyze sheriff behavior and choose between:
        - Honest declaration (safest)
        - Legal goods lying (moderate risk/reward)
        - Contraband smuggling (highest risk/reward)
        
        Args:
            history: Optional list of previous encounters with keys:
                - 'declaration': {'good_id': str, 'count': int}
                - 'actual_ids': list[str]
                - 'caught_lie': bool
                - 'opened': bool
                - optionally 'profit': int
        
        Returns:
            dict with keys:
                - 'declared_id': str - What good they claim to have
                - 'count': int - How many they claim
                - 'actual_ids': list[str] - What they actually carry
                - 'lie': bool - Whether they're lying
        
        Strategy decision tree:
            1. Analyze sheriff behavior (if history available)
            2. Consider legal goods lying strategy (safe, moderate profit)
            3. Consider contraband smuggling (risky, high profit)
            4. Default to honest declaration
        """
        from ai_strategy.legal_goods_strategy import should_use_legal_goods_lie, choose_legal_goods_lie
        from core.players.sheriff_analysis import calculate_catch_rate
        
        # Calculate sheriff catch rate from history using shared utility
        sheriff_catch_rate = calculate_catch_rate(history)
        
        # Build personality dict for strategy decision
        merchant_personality = {
            'risk_tolerance': getattr(self, 'risk_tolerance', 5),
            'greed': getattr(self, 'greed', 5),
            'honesty_bias': getattr(self, 'honesty_bias', 5)
        }
        
        # Check if we should use legal goods lying strategy
        if should_use_legal_goods_lie(merchant_personality, sheriff_catch_rate):
            return choose_legal_goods_lie()
        
        # Check if we should smuggle contraband (high risk/reward)
        # Only if: low honesty_bias, high risk_tolerance, and sheriff isn't too aggressive
        if (merchant_personality['honesty_bias'] < 5 and 
            merchant_personality['risk_tolerance'] > 5 and 
            sheriff_catch_rate < 0.6):
            # Smuggle contraband - respect 6 card bag limit
            from core.game.game_rules import BAG_SIZE_LIMIT
            contraband_ids = [g.id for g in ALL_CONTRABAND]
            declared = random.choice([g.id for g in ALL_LEGAL])
            # Choose 1-3 contraband items (within bag limit)
            bag_size = min(random.randint(1, 3), BAG_SIZE_LIMIT)
            actual_ids = [random.choice(contraband_ids) for _ in range(bag_size)]
            return {"declared_id": declared, "count": bag_size, "actual_ids": actual_ids, "lie": True, "lie_type": "contraband"}
        
        # Default: honest declaration - respect 6 card bag limit
        from core.game.game_rules import BAG_SIZE_LIMIT
        declared = random.choice([g.id for g in ALL_LEGAL])
        count = min(random.randint(2, 4), BAG_SIZE_LIMIT)  # 2-4 items is reasonable
        actual_ids = [declared] * count
        return {"declared_id": declared, "count": count, "actual_ids": actual_ids, "lie": False, "lie_type": "none"}

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
        
        Args:
            goods_value: Total value of contraband in bag
            threat_level: How serious the inspection threat is (1-10)
        
        Returns:
            Gold amount to offer as bribe
        """
        # Base offer on goods value and threat level
        # Greedy merchants offer less, cautious merchants offer more
        
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
        
        Args:
            sheriff_demand: Amount sheriff is demanding
            original_offer: Merchant's original offer
            goods_value: Total value of contraband in bag
        
        Returns:
            True if merchant accepts the demand, False to continue negotiating
        """
        # Accept if demand is reasonable compared to goods value
        demand_ratio = sheriff_demand / goods_value if goods_value > 0 else 1.0
        
        # Greedy merchants are less willing to accept high demands
        greed_threshold = 0.5 + (self.greed / 20)  # 0.5 to 1.0
        
        # Risk-tolerant merchants are more willing to gamble and reject
        risk_threshold = 0.7 - (self.risk_tolerance / 20)  # 0.2 to 0.7
        
        # Accept if demand is below threshold
        if demand_ratio < min(greed_threshold, risk_threshold):
            return True
        
        # Add some randomness
        return random.random() < 0.3


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


def characters_dir() -> Path:
    root = Path(__file__).resolve().parent.parent
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
            )
            merchants.append(m)
        except (json.JSONDecodeError, KeyError) as e:
            continue
    return merchants
