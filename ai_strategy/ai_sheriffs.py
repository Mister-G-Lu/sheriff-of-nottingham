"""
AI Sheriff Strategies

This module contains different AI sheriff personalities that can be used
for testing or as opponents in the game.

Each sheriff has a unique decision-making pattern that creates different
challenges for merchants.
"""

import random

from core.mechanics.goods import Good


class SheriffStrategy:
    """Base class for sheriff strategies."""

    @staticmethod
    def decide(
        merchant,
        bribe_offered: int,
        declaration: dict,
        actual_goods: list[Good],
        history: list[dict],
    ) -> tuple[bool, bool]:
        """
        Decide whether to inspect and/or accept bribe.

        Args:
            merchant: The merchant making the declaration
            bribe_offered: Amount of bribe offered (0 if none)
            declaration: What the merchant declared
            actual_goods: What they're actually carrying (sheriff doesn't know this!)
            history: Previous encounters

        Returns:
            Tuple[bool, bool]: (should_inspect, accept_bribe)
        """
        raise NotImplementedError


class TriggerHappySheriff(SheriffStrategy):
    """
    Trigger Happy Sheriff: Inspects whenever bribed, otherwise lets pass.

    Logic: "If they're bribing, they must be hiding something!"
    Exploitable with honest bribe trick.
    """

    @staticmethod
    def decide(
        merchant,
        bribe_offered: int,
        declaration: dict,
        actual_goods: list[Good],
        history: list[dict],
    ) -> tuple[bool, bool]:
        if bribe_offered > 0:
            # Suspicious! Inspect them!
            return True, False  # Inspect, reject bribe
        else:
            # No bribe? Must be honest, let them pass
            return False, False  # Don't inspect


class CorruptSheriff(SheriffStrategy):
    """
    Corrupt & Greedy Sheriff: Accepts all bribes.

    Logic: "Everyone pays, or I inspect!"
    Very profitable for smugglers with minimal bribes.
    """

    @staticmethod
    def decide(
        merchant,
        bribe_offered: int,
        declaration: dict,
        actual_goods: list[Good],
        history: list[dict],
    ) -> tuple[bool, bool]:
        if bribe_offered > 0:
            # Take the bribe!
            return False, True  # Don't inspect, accept bribe
        else:
            # No bribe? Threaten them! (but let pass for simulation)
            return False, False


class GreedySheriff(SheriffStrategy):
    """
    Greedy Sheriff: Demands high bribes (50%+ of declared value).

    Logic: "If most merchants are smuggling, I'll squeeze them for maximum bribes.
            Only accept substantial bribes (50%+ of goods value), otherwise inspect."

    This sheriff sits between Smart and Corrupt - selective but predictable.
    """

    @staticmethod
    def decide(
        merchant,
        bribe_offered: int,
        declaration,
        actual_goods: list[Good],
        history: list[dict],
    ) -> tuple[bool, bool]:
        from core.mechanics.goods import GOOD_BY_ID

        # Calculate declared value (declaration can be dict or Declaration object)
        declared_id = (
            declaration["declared_id"]
            if isinstance(declaration, dict)
            else declaration.good_id
        )
        count = (
            declaration["count"] if isinstance(declaration, dict) else declaration.count
        )
        declared_good = GOOD_BY_ID[declared_id]
        declared_value = declared_good.value * count

        if bribe_offered > 0:
            # Calculate bribe ratio
            bribe_ratio = bribe_offered / max(declared_value, 1)

            if bribe_ratio >= 0.5:
                # High bribe (50%+) - accept it!
                return False, True  # Don't inspect, accept bribe
            elif bribe_ratio >= 0.4:
                # Medium-high bribe (40-50%) - 70% chance to accept
                if random.random() < 0.7:
                    return False, True
                else:
                    return True, False  # Inspect
            else:
                # Low bribe (<40%) - too cheap! Inspect them!
                return True, False  # Inspect, reject bribe
        else:
            # No bribe - inspect sometimes (40% chance)
            return random.random() < 0.4, False


class SmartSheriff(SheriffStrategy):
    """
    Smart Adaptive Sheriff: Learns from results and adjusts strategy.

    Logic: Tracks catch rate and adapts inspection rate accordingly.
    Most realistic and challenging opponent.
    """

    @staticmethod
    def decide(
        merchant,
        bribe_offered: int,
        declaration,
        actual_goods: list[Good],
        history: list[dict],
    ) -> tuple[bool, bool]:
        from core.mechanics.goods import GOOD_BY_ID

        # Calculate current catch rate from recent history
        recent = history[-20:] if len(history) >= 20 else history
        if recent:
            inspections = [h for h in recent if h.get("opened", False)]
            if inspections:
                catches = sum(1 for h in inspections if h.get("caught", False))
                catch_rate = catches / len(inspections) if inspections else 0.5
            else:
                catch_rate = 0.5
        else:
            catch_rate = 0.5

        # Calculate smuggling rate (how many caught vs total encounters)
        # High smuggling rate means we should be more vigilant
        smuggling_rate = 0.0
        if recent and len(recent) >= 5:
            total_caught = sum(1 for h in recent if h.get("caught", False))
            smuggling_rate = total_caught / len(recent)

        # Adjust inspection rate based on success
        if catch_rate > 0.6:
            # Catching lots of smugglers - inspect more
            inspection_rate = 0.6
        elif catch_rate < 0.3:
            # Not catching many - inspect less
            inspection_rate = 0.3
        else:
            # Moderate success - maintain current rate
            inspection_rate = 0.45

        # If smuggling rate is high (>30% of encounters are smugglers), be more suspicious
        if smuggling_rate > 0.30:
            inspection_rate += 0.15  # Increase vigilance
        elif smuggling_rate > 0.20:
            inspection_rate += 0.10  # Moderate increase

        # High-value declarations are more suspicious (handle both dict and Declaration object)
        declared_id = (
            declaration["declared_id"]
            if isinstance(declaration, dict)
            else declaration.good_id
        )
        count = (
            declaration["count"] if isinstance(declaration, dict) else declaration.count
        )
        declared_good = GOOD_BY_ID[declared_id]
        declared_value = declared_good.value * count
        if declared_value > 15:
            inspection_rate += 0.15

        # Bribe handling
        if bribe_offered > 0:
            # Calculate if bribe is reasonable
            bribe_ratio = bribe_offered / max(declared_value, 1)

            if bribe_ratio > 0.4:
                # Bribe too high - very suspicious, inspect
                return True, False
            elif bribe_ratio < 0.2:
                # Reasonable bribe - might accept
                if random.random() < 0.6:
                    return False, True  # Accept bribe
                else:
                    return True, False  # Inspect anyway
            else:
                # Medium bribe - 50/50
                if random.random() < 0.5:
                    return False, True
                else:
                    return True, False
        else:
            # No bribe - use inspection rate
            return random.random() < inspection_rate, False


class StrictInspectorSheriff(SheriffStrategy):
    """
    Strict Inspector Sheriff: Inspects EVERYONE, no exceptions.

    Logic: "I trust no one! Everyone gets inspected!"
    This sheriff inspects every single merchant regardless of bribes.
    Exploitable by Silas's Legal Good Trick (honest goods get double value when inspected).
    """

    @staticmethod
    def decide(
        merchant,
        bribe_offered: int,
        declaration: dict,
        actual_goods: list[Good],
        history: list[dict],
    ) -> tuple[bool, bool]:
        # Always inspect, never accept bribes
        return True, False  # Inspect everyone, reject all bribes


# Convenience functions for simulation
def trigger_happy(
    merchant,
    bribe_offered: int,
    declaration: dict,
    actual_goods: list[Good],
    history: list[dict],
) -> tuple[bool, bool]:
    """Trigger Happy sheriff strategy."""
    return TriggerHappySheriff.decide(
        merchant, bribe_offered, declaration, actual_goods, history
    )


def strict_inspector(
    merchant,
    bribe_offered: int,
    declaration: dict,
    actual_goods: list[Good],
    history: list[dict],
) -> tuple[bool, bool]:
    """Strict Inspector sheriff strategy."""
    return StrictInspectorSheriff.decide(
        merchant, bribe_offered, declaration, actual_goods, history
    )


def corrupt_greedy(
    merchant,
    bribe_offered: int,
    declaration: dict,
    actual_goods: list[Good],
    history: list[dict],
) -> tuple[bool, bool]:
    """Corrupt & Greedy sheriff strategy."""
    return CorruptSheriff.decide(
        merchant, bribe_offered, declaration, actual_goods, history
    )


def greedy(
    merchant,
    bribe_offered: int,
    declaration: dict,
    actual_goods: list[Good],
    history: list[dict],
) -> tuple[bool, bool]:
    """Greedy sheriff strategy."""
    return GreedySheriff.decide(
        merchant, bribe_offered, declaration, actual_goods, history
    )


def smart_adaptive(
    merchant,
    bribe_offered: int,
    declaration: dict,
    actual_goods: list[Good],
    history: list[dict],
) -> tuple[bool, bool]:
    """Smart Adaptive sheriff strategy."""
    return SmartSheriff.decide(
        merchant, bribe_offered, declaration, actual_goods, history
    )


class VengefulSheriff(SheriffStrategy):
    """
    Vengeful Sheriff: Remembers merchants who lie and targets them relentlessly.

    Logic: "You lied to me before? I'll NEVER trust you again!"
    Tracks each merchant's lie rate and becomes increasingly suspicious of known liars.
    - Lie rate > 50%: Inspects 80% of the time, rarely accepts bribes
    - Lie rate 30-50%: Inspects 50% of the time, accepts high bribes only
    - Lie rate < 30%: Inspects 20% of the time, accepts reasonable bribes

    Creates long-term consequences for lying and rewards honest merchants.
    """

    @staticmethod
    def decide(
        merchant,
        bribe_offered: int,
        declaration: dict,
        actual_goods: list[Good],
        history: list[dict],
    ) -> tuple[bool, bool]:
        from core.mechanics.goods import GOOD_BY_ID

        # Calculate merchant's historical lie rate
        merchant_history = [
            h for h in history if h.get("merchant_name") == merchant.name
        ]

        if len(merchant_history) < 3:
            # Not enough history - use moderate inspection rate
            inspection_rate = 0.4
            bribe_acceptance_threshold = 0.4  # Accept bribes >40% of value
        else:
            # Calculate lie rate from ALL encounters (not just inspections)
            # This gives a better picture of merchant behavior
            inspected = [h for h in merchant_history if h.get("opened", False)]

            if len(inspected) >= 3:
                # Have enough inspection data - use actual lie rate
                caught_lying = sum(1 for h in inspected if h.get("caught", False))
                lie_rate = caught_lying / len(inspected)
            else:
                # Not enough inspections - use moderate risk
                lie_rate = 0.3

            # Adjust behavior based on lie rate
            if lie_rate > 0.5:
                # Known liar! Very suspicious
                inspection_rate = 0.8
                bribe_acceptance_threshold = 0.8  # Only accept huge bribes
            elif lie_rate > 0.3:
                # Somewhat suspicious
                inspection_rate = 0.5
                bribe_acceptance_threshold = 0.6  # Accept high bribes
            else:
                # Trustworthy merchant
                inspection_rate = 0.2
                bribe_acceptance_threshold = 0.3  # Accept reasonable bribes

        # Get declared value
        declared_id = (
            declaration["declared_id"]
            if isinstance(declaration, dict)
            else declaration.good_id
        )
        count = (
            declaration["count"] if isinstance(declaration, dict) else declaration.count
        )
        declared_good = GOOD_BY_ID[declared_id]
        declared_value = declared_good.value * count

        # Handle bribe
        if bribe_offered > 0:
            bribe_ratio = bribe_offered / max(declared_value, 1)

            if bribe_ratio >= bribe_acceptance_threshold:
                # Bribe is high enough - accept it
                return False, True
            else:
                # Bribe too low - inspect!
                return True, False
        else:
            # No bribe - use inspection rate based on merchant's reputation
            return random.random() < inspection_rate, False


class MonteCarloSheriffStrategy(SheriffStrategy):
    """
    Monte Carlo Sheriff: Uses probabilistic simulation to make optimal decisions.

    Logic: "Let me calculate the probability this is a lie based on deck statistics..."
    This sheriff simulates deck draws to understand what declarations are realistic,
    then uses Bayesian reasoning and expected value calculations to decide.

    Most sophisticated sheriff - makes mathematically optimal decisions.
    """

    # Singleton instance (expensive to initialize, so reuse)
    _instance = None

    @classmethod
    def get_instance(cls):
        """Get or create the Monte Carlo Sheriff instance."""
        if cls._instance is None:
            from core.players.monte_carlo_sheriff import create_monte_carlo_sheriff

            cls._instance = create_monte_carlo_sheriff(
                simulation_count=100, risk_tolerance=0.5, bribe_weight=1.2
            )
        return cls._instance

    @staticmethod
    def decide(
        merchant,
        bribe_offered: int,
        declaration: dict,
        actual_goods: list[Good],
        history: list[dict],
    ) -> tuple[bool, bool]:
        # Get the Monte Carlo Sheriff instance
        mc_sheriff = MonteCarloSheriffStrategy.get_instance()

        # Convert declaration to expected format
        if not isinstance(declaration, dict):
            declaration = {"good_id": declaration.good_id, "count": declaration.count}

        # Get merchant-specific history
        merchant_history = [
            h for h in history if h.get("merchant_name") == merchant.name
        ]

        # Use Monte Carlo Sheriff's decision logic
        should_inspect = mc_sheriff.should_inspect(
            merchant.name, declaration, bribe_offered, merchant_history
        )

        # If inspecting, don't accept bribe
        # If not inspecting and bribe offered, accept it
        accept_bribe = not should_inspect and bribe_offered > 0

        return should_inspect, accept_bribe


def vengeful(
    merchant,
    bribe_offered: int,
    declaration: dict,
    actual_goods: list[Good],
    history: list[dict],
) -> tuple[bool, bool]:
    """Vengeful sheriff strategy (remembers liars)."""
    return VengefulSheriff.decide(
        merchant, bribe_offered, declaration, actual_goods, history
    )


def monte_carlo(
    merchant,
    bribe_offered: int,
    declaration: dict,
    actual_goods: list[Good],
    history: list[dict],
) -> tuple[bool, bool]:
    """Monte Carlo sheriff strategy (probabilistic/optimal)."""
    return MonteCarloSheriffStrategy.decide(
        merchant, bribe_offered, declaration, actual_goods, history
    )


# Sheriff registry for easy access
SHERIFF_STRATEGIES = {
    "trigger_happy": trigger_happy,
    "strict_inspector": strict_inspector,
    "corrupt": corrupt_greedy,
    "greedy": greedy,
    "smart": smart_adaptive,
    "vengeful": vengeful,
    "monte_carlo": monte_carlo,
}


def get_sheriff_strategy(name: str):
    """Get a sheriff strategy by name."""
    return SHERIFF_STRATEGIES.get(name.lower())
