"""
The Gambler - A merchant who plays by his cards, not by the sheriff.

Strategy:
- Honest by default (builds trust and reputation)
- When dealt 2+ of same contraband → Goes all-in!
- Hard mulligan to maximize contraband set
- Smuggles with NO bribe, relying on honest reputation
- "I was always honest before, why would I lie now?"
"""

from collections import Counter

from core.players.merchants import Merchant


class Gambler(Merchant):
    """The Gambler - plays by his cards, not by the sheriff."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rounds_played = 0
        self.times_honest = 0

    def choose_declaration(self, history: list = None) -> dict:
        """Choose declaration based on cards dealt, not sheriff behavior."""
        from ai_strategy.declaration_builder import build_honest_declaration
        from core.mechanics.deck import redraw_cards

        hand = self.hand if hasattr(self, "hand") else []
        if not hand:
            # Fallback
            return {
                "declared_id": "apple",
                "count": 4,
                "actual_ids": ["apple"] * 4,
                "lie": False,
            }

        self.rounds_played += 1

        # Check for contraband opportunity
        contraband = [g for g in hand if not g.is_legal()]
        contraband_counts = Counter(g.id for g in contraband)

        # Find if we have 2+ of same contraband (SET BONUS opportunity!)
        max_contraband_count = (
            max(contraband_counts.values()) if contraband_counts else 0
        )

        # THE BIG PLAY: If we have 2+ of same contraband, GO ALL-IN!
        if max_contraband_count >= 2:
            # HARD MULLIGAN: Redraw ALL non-matching cards to maximize this contraband set
            best_contraband_id = max(contraband_counts, key=contraband_counts.get)

            # Keep only the best contraband, redraw everything else
            cards_to_keep = [g for g in hand if g.id == best_contraband_id]
            num_to_redraw = len(hand) - len(cards_to_keep)

            if num_to_redraw > 0:
                # Redraw aggressively for more of the same contraband
                hand = redraw_cards(
                    hand, num_to_redraw, prefer_contraband=True, prefer_high_value=True
                )
                self.hand = hand

            # Build the big contraband play
            contraband = [g for g in hand if not g.is_legal()]
            if contraband:
                # Sort by value and try to get sets
                contraband_sorted = sorted(
                    contraband, key=lambda g: g.value, reverse=True
                )
                contraband_counts = Counter(g.id for g in contraband_sorted)

                # Build optimal contraband bag (prioritize sets)
                actual_goods = []
                for good_id, _count in contraband_counts.most_common():
                    goods_of_type = [g for g in contraband_sorted if g.id == good_id]
                    # Take up to 5 total, prioritize sets of 3 for max bonus
                    to_take = min(len(goods_of_type), 5 - len(actual_goods))
                    actual_goods.extend(goods_of_type[:to_take])
                    if len(actual_goods) >= 5:
                        break

                # Declare legal goods (the lie!)
                legal_goods = [g for g in hand if g.is_legal()]
                declared_good = legal_goods[0].id if legal_goods else "apple"
                actual_ids = [g.id for g in actual_goods]

                return {
                    "declared_id": declared_good,
                    "count": len(actual_ids),
                    "actual_ids": actual_ids,
                    "lie": True,
                }

        # Default: Play honest (builds reputation for the big play)
        self.times_honest += 1
        return build_honest_declaration(available_goods={"hand": hand})

    def should_offer_proactive_bribe(
        self,
        sheriff_authority: int,
        sheriff_reputation: int,
        actual_goods: list,
        declared_goods: list,
    ) -> bool:
        """The Gambler NEVER bribes - he relies on his honest reputation."""
        # Check if we're lying (the big play)
        has_contraband = any(not g.is_legal() for g in actual_goods)
        is_lying = len(actual_goods) != len(declared_goods) or any(
            a.id != d.id for a, d in zip(actual_goods, declared_goods)
        )

        if has_contraband or is_lying:
            return False

        return False

    def calculate_proactive_bribe(
        self,
        actual_goods: list,
        is_lying: bool,
        sheriff_authority: int,
        declared_goods: list = None,
    ) -> int:
        return 0
