"""
Monte Carlo Sheriff: A probabilistic sheriff that uses simulation to make optimal decisions.

This sheriff simulates deck draws to calculate the probability that a declaration is honest,
then uses expected value calculations to decide whether to inspect or accept bribes.
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Optional

from core.mechanics.deck import draw_hand, redraw_cards
from core.mechanics.goods import GOOD_BY_ID, Good
from core.players.sheriff import Sheriff


@dataclass
class MonteCarloSheriff(Sheriff):
    """
    A sheriff that uses Monte Carlo simulation and Bayesian reasoning to make decisions.

    On initialization, simulates many deck draws to build probability distributions for:
    - What honest merchants (redrawing for legal goods) typically declare
    - What smugglers (redrawing for contraband) typically declare

    Uses these distributions to calculate P(honest | declaration) and make optimal
    inspection decisions based on expected value.
    """

    # Simulation parameters
    simulation_count: int = 100

    # Probability distributions (built on initialization)
    honest_distribution: dict[tuple[str, int], float] = None
    smuggler_distribution: dict[tuple[str, int], float] = None

    # Decision parameters
    risk_tolerance: float = (
        0.5  # How much evidence needed to inspect (0=aggressive, 1=cautious)
    )
    bribe_weight: float = (
        1.2  # Multiplier for bribe value (1.2 = bribes worth 20% more)
    )

    def __post_init__(self):
        """Initialize probability distributions after dataclass initialization."""
        if self.honest_distribution is None:
            self.honest_distribution = {}
        if self.smuggler_distribution is None:
            self.smuggler_distribution = {}

        # Build probability distributions
        self._initialize_distributions()

    def _initialize_distributions(self):
        """
        Run Monte Carlo simulations to build probability distributions.
        This is the core of the sheriff's intelligence.
        """
        print(
            f"[Monte Carlo Sheriff] Running {self.simulation_count} simulations to learn deck probabilities..."
        )

        # Simulate honest merchant draws
        honest_declarations = self._simulate_draws(
            strategy="honest", n=self.simulation_count
        )
        self.honest_distribution = self._build_probability_table(honest_declarations)

        # Simulate smuggler draws
        smuggler_declarations = self._simulate_draws(
            strategy="smuggle", n=self.simulation_count
        )
        self.smuggler_distribution = self._build_probability_table(
            smuggler_declarations
        )

        print(
            f"[Monte Carlo Sheriff] Learned probabilities for {len(self.honest_distribution)} declaration types"
        )

    def _simulate_draws(self, strategy: str, n: int) -> list[tuple[str, int]]:
        """
        Simulate n deck draws using the specified strategy.

        Args:
            strategy: 'honest' (redraw for legal) or 'smuggle' (redraw for contraband)
            n: Number of simulations to run

        Returns:
            List of (good_id, count) tuples representing likely declarations
        """
        declarations = []

        for _ in range(n):
            # Draw initial hand (6 cards)
            hand = draw_hand(hand_size=6)

            # Apply redraw strategy
            if strategy == "honest":
                # Redraw contraband for legal goods
                contraband_count = sum(1 for g in hand if g.is_contraband)
                if contraband_count > 0 and contraband_count <= 4:
                    # Redraw contraband cards for legal goods
                    hand = redraw_cards(hand, contraband_count, prefer_legal=True)

            elif strategy == "smuggle":
                # Redraw legal goods for contraband
                legal_count = sum(1 for g in hand if not g.is_contraband)
                if legal_count > 0 and legal_count <= 4:
                    # Redraw legal cards for contraband
                    hand = redraw_cards(hand, legal_count, prefer_contraband=True)

            # Determine most likely declaration from this hand
            declaration = self._extract_likely_declaration(hand)
            if declaration:
                declarations.append(declaration)

        return declarations

    def _extract_likely_declaration(
        self, hand: list[Good]
    ) -> Optional[tuple[str, int]]:
        """
        Extract the most likely declaration from a hand.
        Merchants typically declare the most common good type.
        """
        if not hand:
            return None

        # Count each good type
        good_counts = defaultdict(int)
        for good in hand:
            good_counts[good.id] += 1

        # Find most common good
        if not good_counts:
            return None

        most_common_good = max(good_counts.items(), key=lambda x: x[1])
        return most_common_good

    def _build_probability_table(
        self, declarations: list[tuple[str, int]]
    ) -> dict[tuple[str, int], float]:
        """
        Build probability table from simulation results.

        Returns:
            Dict mapping (good_id, count) -> probability
        """
        if not declarations:
            return {}

        # Count occurrences
        counts = defaultdict(int)
        for decl in declarations:
            counts[decl] += 1

        # Convert to probabilities
        total = len(declarations)
        probabilities = {decl: count / total for decl, count in counts.items()}

        return probabilities

    def should_inspect(
        self,
        merchant_name: str,
        declaration: dict,
        bribe_offered: int,
        merchant_history: list[dict] = None,
    ) -> bool:
        """
        Decide whether to inspect based on expected value calculation.

        Args:
            merchant_name: Name of the merchant
            declaration: Declaration dict with 'good_id' and 'count'
            bribe_offered: Bribe amount (0 if no bribe)
            merchant_history: List of past interactions with this merchant

        Returns:
            True if should inspect, False if should let pass (or accept bribe)
        """
        # Extract declaration info
        declared_good = declaration.get("good_id", "apple")
        declared_count = declaration.get("count", 4)

        # Calculate probability that declaration is honest
        p_honest = self._calculate_honesty_probability(
            declared_good, declared_count, merchant_history
        )

        # Calculate expected values
        ev_inspect = self._calculate_inspection_ev(
            declared_good, declared_count, p_honest
        )

        ev_accept = bribe_offered * self.bribe_weight

        # Decision logic with risk tolerance
        # If very confident it's a lie (p_honest < risk_tolerance), inspect
        # Otherwise, compare expected values
        if p_honest < self.risk_tolerance:
            return ev_inspect > ev_accept
        else:
            # When uncertain, weight bribes more heavily
            return ev_inspect > ev_accept * 1.5

    def _calculate_honesty_probability(
        self,
        declared_good: str,
        declared_count: int,
        merchant_history: list[dict] = None,
    ) -> float:
        """
        Calculate P(honest | declaration, history) using Bayes' theorem.

        P(honest | declaration) = P(declaration | honest) * P(honest) / P(declaration)
        """
        decl_key = (declared_good, declared_count)

        # Get probabilities from simulation
        p_decl_given_honest = self.honest_distribution.get(decl_key, 0.01)
        p_decl_given_smuggle = self.smuggler_distribution.get(decl_key, 0.01)

        # Calculate prior P(honest) from merchant history
        p_honest_prior = self._get_merchant_honesty_rate(merchant_history)

        # Bayes' theorem
        numerator = p_decl_given_honest * p_honest_prior
        denominator = p_decl_given_honest * p_honest_prior + p_decl_given_smuggle * (
            1 - p_honest_prior
        )

        if denominator == 0:
            return 0.5  # No information, assume 50/50

        return numerator / denominator

    def _get_merchant_honesty_rate(self, history: list[dict] = None) -> float:
        """
        Calculate merchant's historical honesty rate.

        Returns:
            Float between 0 and 1 (default 0.5 if no history)
        """
        if not history:
            return 0.5  # Default prior

        # Count honest vs dishonest encounters
        honest_count = 0
        total_count = 0

        for entry in history:
            if entry.get("opened"):
                total_count += 1
                # If opened and not caught, was honest
                if not entry.get("caught", False):
                    honest_count += 1
            else:
                # If not opened, assume was honest (conservative estimate)
                total_count += 1
                honest_count += 1

        if total_count == 0:
            return 0.5

        return honest_count / total_count

    def _calculate_inspection_ev(
        self, declared_good: str, declared_count: int, p_honest: float
    ) -> float:
        """
        Calculate expected value of inspecting.

        EV(inspect) = P(lie) * value_if_caught - P(honest) * penalty_if_wrong
        """
        # Get declared value
        good = GOOD_BY_ID.get(declared_good, GOOD_BY_ID["apple"])
        declared_value = good.value * declared_count

        # If they're lying, estimate contraband value
        # Assume smugglers carry high-value contraband
        avg_contraband_value = declared_value * 1.8  # Contraband typically worth more

        # Penalty for inspecting honest merchant
        penalty = declared_value

        # Expected value calculation
        p_lie = 1 - p_honest
        ev = p_lie * avg_contraband_value - p_honest * penalty

        return ev

    def should_accept_bribe(
        self,
        merchant_name: str,
        declaration: dict,
        bribe_offered: int,
        merchant_history: list[dict] = None,
    ) -> bool:
        """
        Decide whether to accept a bribe.
        This is the inverse of should_inspect with bribe consideration.
        """
        # If no bribe offered, this doesn't apply
        if bribe_offered <= 0:
            return False

        # Use the same logic as should_inspect
        should_inspect_result = self.should_inspect(
            merchant_name, declaration, bribe_offered, merchant_history
        )

        # Accept bribe if we wouldn't inspect
        return not should_inspect_result

    def get_inspection_reasoning(
        self,
        merchant_name: str,
        declaration: dict,
        bribe_offered: int,
        merchant_history: list[dict] = None,
    ) -> str:
        """
        Get human-readable explanation of inspection decision.
        Useful for debugging and player feedback.
        """
        declared_good = declaration.get("good_id", "apple")
        declared_count = declaration.get("count", 4)

        p_honest = self._calculate_honesty_probability(
            declared_good, declared_count, merchant_history
        )

        ev_inspect = self._calculate_inspection_ev(
            declared_good, declared_count, p_honest
        )

        ev_accept = bribe_offered * self.bribe_weight

        decision = (
            "INSPECT"
            if self.should_inspect(
                merchant_name, declaration, bribe_offered, merchant_history
            )
            else "LET PASS"
        )

        reasoning = (
            f"[Monte Carlo Sheriff Analysis]\n"
            f"Declaration: {declared_count} {declared_good}\n"
            f"Bribe: {bribe_offered}g\n"
            f"P(Honest): {p_honest:.1%}\n"
            f"EV(Inspect): {ev_inspect:.1f}g\n"
            f"EV(Accept): {ev_accept:.1f}g\n"
            f"Decision: {decision}"
        )

        return reasoning


def create_monte_carlo_sheriff(
    simulation_count: int = 100, risk_tolerance: float = 0.5, bribe_weight: float = 1.2
) -> MonteCarloSheriff:
    """
    Factory function to create a Monte Carlo Sheriff with custom parameters.

    Args:
        simulation_count: Number of simulations to run (default 100)
        risk_tolerance: How cautious the sheriff is (0=aggressive, 1=cautious)
        bribe_weight: How much to value bribes (1.0=face value, 1.2=20% bonus)

    Returns:
        Configured MonteCarloSheriff instance
    """
    return MonteCarloSheriff(
        simulation_count=simulation_count,
        risk_tolerance=risk_tolerance,
        bribe_weight=bribe_weight,
    )
