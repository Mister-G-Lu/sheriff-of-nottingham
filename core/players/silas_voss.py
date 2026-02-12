"""
Silas Voss - Information Broker Merchant

An information broker who analyzes sheriff behavior patterns and adapts his strategy:
- Uses "Legal Good Trick" against strict inspectors (honest goods + bribe)
- Detects corrupt/greedy sheriffs and smuggles aggressively
- Learns what bribe sizes sheriffs accept
"""

import random

from core.mechanics.goods import GOOD_BY_ID
from core.players.merchants import Merchant


class SilasVoss(Merchant):
    """Information Broker who analyzes sheriff patterns and adapts strategy accordingly."""

    def choose_declaration(self, history: list = None) -> dict:
        """Choose what to declare based on profit analysis and sheriff patterns."""
        from core.mechanics.deck import redraw_cards, should_redraw_for_silas
        from core.systems.game_master_state import get_game_master_state

        # Get collective merchant history
        game_state = get_game_master_state()
        full_history = game_state.get_history_for_tier(None)

        # Decide strategy: honest or smuggle
        play_honest = self._should_play_honest(full_history)

        # Get goods and make declaration
        hand = self.hand if hasattr(self, "hand") else []
        if not hand:
            # Fallback: declare 4 apples
            return {
                "declared_id": "apple",
                "count": 4,
                "actual_ids": ["apple"] * 4,
                "lie": False,
            }

        # STRATEGIC CARD REDRAWING using Silas's sophisticated analysis
        # Prepare sheriff analysis data
        recent = full_history[-10:] if len(full_history) >= 10 else full_history
        inspections = sum(1 for h in recent if h.get("opened", False))
        inspection_rate = inspections / len(recent) if recent else 0.5

        caught = sum(1 for h in recent if h.get("caught", False))
        catch_rate = caught / len(recent) if recent else 0.5

        sheriff_analysis = {
            "inspection_rate": inspection_rate,
            "catch_rate": catch_rate,
            "history": full_history,
        }

        # Adaptive redraw strategy based on sheriff type
        sheriff_type = self._detect_sheriff_type(full_history)

        if sheriff_type in ["corrupt", "greedy"]:
            # CORRUPT/GREEDY: Maximize contraband aggressively
            # Redraw ALL legal cards to get maximum contraband
            legal_cards = [g for g in hand if g.is_legal()]
            if len(legal_cards) > 0:
                hand = redraw_cards(
                    hand,
                    len(legal_cards),
                    prefer_contraband=True,
                    prefer_high_value=True,
                )
                self.hand = hand
        else:
            # Normal redraw strategy
            num_to_redraw = should_redraw_for_silas(hand, sheriff_analysis)
            if num_to_redraw > 0:
                if play_honest:
                    hand = redraw_cards(
                        hand, num_to_redraw, prefer_legal=True, prefer_high_value=True
                    )
                else:
                    hand = redraw_cards(hand, num_to_redraw, prefer_contraband=True)
                self.hand = hand

        # Use existing declaration builders instead of custom logic
        from collections import Counter

        from ai_strategy.declaration_builder import (
            build_contraband_high_declaration,
            build_honest_declaration,
        )

        if play_honest:
            # Honest play: use honest declaration builder
            return build_honest_declaration(available_goods={"hand": hand})
        else:
            # Smuggling: check if we have contraband
            contraband = [g for g in hand if not g.is_legal()]
            if contraband:
                # Use contraband high declaration builder for optimal selection
                # It already prioritizes high-value contraband and set bonuses
                available_goods = Counter(g.id for g in hand)
                return build_contraband_high_declaration(
                    available_goods=available_goods
                )
            else:
                # No contraband, play honest
                return build_honest_declaration(available_goods={"hand": hand})

    def _detect_sheriff_type(self, history: list) -> str:
        """
        Detect sheriff behavior pattern.
        Returns: 'corrupt', 'greedy', 'strict', or 'unknown'
        """
        if len(history) < 5:
            return "unknown"

        recent = history[-10:] if len(history) >= 10 else history

        # Check overall inspection rate (including all merchants)
        total_rounds = len(recent)
        inspected_rounds = sum(1 for h in recent if h.get("opened", False))
        overall_inspection_rate = (
            inspected_rounds / total_rounds if total_rounds > 0 else 0
        )

        # If sheriff is inspecting frequently overall, treat as STRICT
        # This catches suspicious/paranoid sheriffs who inspect a lot
        if overall_inspection_rate > 0.50:
            return "strict"

        bribed = [h for h in recent if h.get("bribe_offered", 0) > 0]

        if len(bribed) < 3:
            # Not enough bribe data in recent history, look at longer history
            longer_history = history[-20:] if len(history) >= 20 else history
            bribed = [h for h in longer_history if h.get("bribe_offered", 0) > 0]

            # Still not enough bribe data, but check if sheriff is suspicious
            if overall_inspection_rate > 0.40:
                return "strict"
            return "unknown"

        # Calculate acceptance rate
        accepted = sum(1 for h in bribed if h.get("bribe_accepted", False))
        acceptance_rate = accepted / len(bribed)

        # CORRUPT: Accepts most bribes (>80%)
        if acceptance_rate > 0.80:
            return "corrupt"

        # STRICT: High inspection rate among bribes (>40%) OR low acceptance (<30%)
        # Catches sheriffs who inspect bribes frequently or reject most bribes
        # This includes Trigger Happy (inspects ALL bribes) and strict inspectors
        inspected = sum(1 for h in bribed if h.get("opened", False))
        inspection_rate = inspected / len(bribed)

        # If inspection rate is very high (>60%) or acceptance is very low (<20%), definitely strict
        if inspection_rate > 0.60 or acceptance_rate < 0.20:
            return "strict"

        # If inspection rate is high (>40%) or acceptance is low (<30%), likely strict
        if inspection_rate > 0.40 or acceptance_rate < 0.30:
            return "strict"

        # GREEDY: Moderate acceptance (30-80%), prefers high bribes
        if 0.30 <= acceptance_rate <= 0.80:
            greedy_result = self._detect_greedy_pattern(bribed)
            if greedy_result:
                return "greedy"

        return "unknown"

    def _detect_greedy_pattern(self, bribed: list) -> bool:
        """
        Detect if sheriff prefers high bribes over low bribes (greedy pattern).
        Extracted into separate function for testability.

        Args:
            bribed: List of history entries where bribes were offered

        Returns:
            True if greedy pattern detected, False otherwise
        """
        # Check if high bribes get accepted more than low bribes
        high_bribes = [h for h in bribed if self._get_bribe_ratio(h) >= 0.45]
        low_bribes = [h for h in bribed if self._get_bribe_ratio(h) < 0.45]

        if len(high_bribes) >= 2 and len(low_bribes) >= 2:
            high_acceptance = sum(
                1 for h in high_bribes if h.get("bribe_accepted", False)
            ) / len(high_bribes)
            low_acceptance = sum(
                1 for h in low_bribes if h.get("bribe_accepted", False)
            ) / len(low_bribes)

            if high_acceptance > low_acceptance + 0.10:
                return True

        return False

    def _get_bribe_ratio(self, history_entry: dict) -> float:
        """Calculate bribe amount as ratio of declared value."""
        bribe_amt = history_entry.get("bribe_offered", 0)
        if bribe_amt == 0:
            return 0.0

        # Get declared value
        declaration = history_entry.get("declaration", {})
        if isinstance(declaration, dict):
            declared_count = declaration.get("count", 0)
            declared_good_id = declaration.get("good_id", "apple")
        else:
            declared_count = history_entry.get("declared_count", 0)
            declared_good_id = history_entry.get("declared_good", "apple")

        declared_good = GOOD_BY_ID.get(declared_good_id, GOOD_BY_ID["apple"])
        declared_value = declared_good.value * declared_count

        if declared_value == 0:
            return 0.0

        return bribe_amt / declared_value

    def _should_play_honest(self, history: list) -> bool:
        """Decide whether to play honest based on sheriff type."""
        if len(history) < 3:
            return random.random() < 0.50

        sheriff_type = self._detect_sheriff_type(history)

        # CORRUPT: Always smuggle
        if sheriff_type == "corrupt":
            return False

        # GREEDY: Smuggle most of the time
        if sheriff_type == "greedy":
            return random.random() < 0.15

        # STRICT: Use Legal Good Trick (honest goods + bribe)
        if sheriff_type == "strict":
            return True

        # UNKNOWN: Use catch rate analysis
        recent = history[-10:] if len(history) >= 10 else history
        if len(recent) >= 4:
            caught_count = sum(
                1
                for h in recent
                if h.get("caught", False) or h.get("caught_lie", False)
            )
            catch_rate = caught_count / len(recent)

            if catch_rate > 0.40:
                return random.random() < 0.85
            elif catch_rate > 0.30:
                return random.random() < 0.70

        return False

    def should_offer_proactive_bribe(
        self,
        sheriff_authority: int,
        sheriff_reputation: int,
        actual_goods: list,
        declared_goods: list,
    ) -> bool:
        """Decide whether to offer a bribe based on sheriff type and goods."""
        from core.systems.game_master_state import get_game_master_state

        has_contraband = any(not g.is_legal() for g in actual_goods)
        is_lying = len(actual_goods) != len(declared_goods) or any(
            a.id != d.id for a, d in zip(actual_goods, declared_goods)
        )

        game_state = get_game_master_state()
        history = game_state.get_history_for_tier(None)

        # EARLY EXPLORATION: Offer bribes in first 10 rounds to gather data
        if len(history) < 10 and random.random() < 0.40:
            return True

        sheriff_type = self._detect_sheriff_type(history)

        # CORRUPT: Bribe sometimes when smuggling (50%)
        if sheriff_type == "corrupt" and (has_contraband or is_lying):
            return random.random() < 0.50

        # GREEDY: Always bribe when smuggling
        if sheriff_type == "greedy" and (has_contraband or is_lying):
            return True

        # STRICT: Use Legal Good Trick (bribe with honest goods)
        if sheriff_type == "strict" and not has_contraband and not is_lying:
            return True

        # If smuggling, use personality-based logic from parent class
        if has_contraband or is_lying:
            return super().should_offer_proactive_bribe(
                sheriff_authority, sheriff_reputation, actual_goods, declared_goods
            )

        # Otherwise, don't bribe when honest (unless strict sheriff detected)
        return False

    def calculate_proactive_bribe(
        self,
        actual_goods: list,
        is_lying: bool,
        sheriff_authority: int,
        declared_goods: list = None,
    ) -> int:
        """Calculate bribe amount based on sheriff type and detected patterns."""
        from core.systems.game_master_state import get_game_master_state

        has_contraband = any(not g.is_legal() for g in actual_goods)

        # Calculate declared value
        if declared_goods:
            declared_value = sum(g.value for g in declared_goods)
        else:
            declared_value = sum(g.value for g in actual_goods)

        game_state = get_game_master_state()
        history = game_state.get_history_for_tier(None)
        sheriff_type = self._detect_sheriff_type(history)

        if has_contraband or is_lying:
            # CORRUPT: Low bribes (15-25%)
            if sheriff_type == "corrupt":
                return max(1, int(declared_value * random.uniform(0.15, 0.25)))

            # GREEDY: High bribes with learning
            if sheriff_type == "greedy":
                avg_ratio = self._learn_successful_bribe_ratio(history)
                if avg_ratio > 0:
                    target_ratio = avg_ratio * random.uniform(0.97, 1.03)
                    target_ratio = max(target_ratio, 0.50)
                    return max(1, int(declared_value * target_ratio))
                else:
                    return max(1, int(declared_value * random.uniform(0.55, 0.70)))

            # UNKNOWN: Moderate bribes (30-60%)
            return max(1, int(declared_value * random.uniform(0.30, 0.60)))
        else:
            # LEGAL GOOD TRICK: Honest goods + small bribe (20-35%)
            total_value = sum(g.value for g in actual_goods)
            return max(1, int(total_value * random.uniform(0.20, 0.35)))

    def _learn_successful_bribe_ratio(self, history: list) -> float:
        """Analyze history to learn what bribe ratios get accepted."""
        if len(history) < 3:
            return 0.0

        # Look at more history for better learning
        recent = history[-20:] if len(history) >= 20 else history
        successful_ratios = []

        for h in recent:
            if h.get("bribe_accepted", False) and h.get("bribe_offered", 0) > 0:
                ratio = self._get_bribe_ratio(h)
                if ratio > 0:
                    successful_ratios.append(ratio)

        # Return average if we have at least 1 successful bribe
        if len(successful_ratios) >= 1:
            # Weight recent successes more heavily
            if len(successful_ratios) > 5:
                # Use last 5 successful bribes with more weight
                recent_ratios = successful_ratios[-5:]
                return sum(recent_ratios) / len(recent_ratios)
            return sum(successful_ratios) / len(successful_ratios)

        return 0.0
