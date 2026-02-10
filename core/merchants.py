"""Merchants: loaded from characters/ with personality, lore, tells, bluff skill."""

import json
import random
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

from core.goods import Good, ALL_LEGAL, ALL_CONTRABAND, GOOD_BY_ID


@dataclass
class Merchant:
    """A merchant with personality, lore, and bluff/lie cues."""
    id: str
    name: str
    personality: str
    lore: str
    tells_honest: list[str]   # cues when telling truth
    tells_lying: list[str]    # cues when lying
    bluff_skill: int = 5      # used vs Sheriff perception for lie detection
    portrait_file: Optional[str] = None  # e.g. "alice.txt"
    appearance: str = ""      # visual description to help generate images
    # Aggregated history summary for inspector queries (only summaries, no ids)
    past_smuggles_count: int = 0
    past_smuggles_value: int = 0
    past_legal_sold_count: int = 0
    past_legal_sold_value: int = 0

    def roll_bluff(self) -> int:
        """Roll for bluff (e.g. d10 + bluff_skill)."""
        return random.randint(1, 10) + self.bluff_skill
    def choose_declaration(self, history: list[dict] | None = None) -> dict:
        """Choose what to declare and what to actually carry.

        history items are expected to be dicts with keys:
          - 'declaration': {'good_id': str, 'count': int}
          - 'actual_ids': list[str]
          - 'caught_lie': bool
          - 'opened': bool
          - optionally 'profit': int

        Returns a dict: {'declared_id', 'count', 'actual_ids', 'lie'}
        Default merchant behaviour: tell the truth with a small legal stack.
        """
        # Default behaviour: truthful, 1-2 apples
        declared = ALL_LEGAL[0].id
        actual_ids = [declared]
        return {"declared_id": declared, "count": 1, "actual_ids": actual_ids, "lie": False}

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


def characters_dir() -> Path:
    root = Path(__file__).resolve().parent.parent
    return root / "characters"


def load_merchants(limit: Optional[int] = None) -> list[Merchant]:
    """Load merchants from characters/*.json, randomly ordered. Optionally limit count."""
    chars_dir = characters_dir()
    if not chars_dir.exists():
        return []

    jsons = list(chars_dir.glob("*.json"))
    random.shuffle(jsons)
    if limit is not None:
        jsons = jsons[:limit]

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
                personality=data.get("personality", ""),
                lore=data.get("lore", ""),
                tells_honest=data.get("tells_honest", []),
                tells_lying=data.get("tells_lying", []),
                bluff_skill=int(data.get("bluff_skill", 5)),
                portrait_file=data.get("portrait_file"),
                appearance=data.get("appearance", ""),
            )
            merchants.append(m)
        except (json.JSONDecodeError, KeyError) as e:
            continue
    return merchants


class InformationBroker(Merchant):
    """A special merchant that analyzes recent merchant history to decide strategy.

    He inspects previous rounds' declarations and outcomes (see `choose_declaration`'s
    `history` parameter description) and biases his choice. By default he prefers
    a bold lie, but if the recent pattern is overwhelmingly lies he'll tell the
    truth to get a data point, and vice versa.
    """

    def choose_declaration(self, history: list[dict] | None = None) -> dict:
        if not history:
            # No data: default to a bold lie (contraband high value)
            contraband = sorted(ALL_CONTRABAND, key=lambda g: g.value, reverse=True)[0]
            declared = ALL_LEGAL[0].id
            return {"declared_id": declared, "count": 1, "actual_ids": [contraband.id], "lie": True}

        # Analyze history: determine whether previous merchants mostly lied
        lies = 0
        truths = 0
        successful_lies: list[dict] = []
        for item in history:
            decl = item.get("declaration", {})
            actual = item.get("actual_ids", [])
            declared_ok = (
                decl.get("count") == len(actual)
                and all(a == decl.get("good_id") for a in actual)
            )
            if declared_ok:
                truths += 1
            else:
                lies += 1
                if not item.get("caught_lie", False):
                    # compute profit if not provided
                    profit = item.get("profit")
                    if profit is None:
                        profit = sum(GOOD_BY_ID.get(a, ALL_CONTRABAND[0]).value for a in actual)
                    successful_lies.append({"actual": actual, "profit": profit, "decl": decl})

        # If everyone lied before, he will say truth to get a data point there.
        prefer_truth = lies > truths

        if prefer_truth and truths < len(history):
            # Choose truth: copy a common declared legal good or default to apple
            declared = ALL_LEGAL[0].id
            return {"declared_id": declared, "count": 1, "actual_ids": [declared], "lie": False}

        # Otherwise, analyze successful lies and pick the most profitable pattern
        if successful_lies:
            best = max(successful_lies, key=lambda x: x["profit"])
            # Hide that contraband under a common legal declaration
            declared = ALL_LEGAL[0].id
            return {"declared_id": declared, "count": len(best["actual"]), "actual_ids": best["actual"], "lie": True}

        # Fallback: bold lie with top contraband
        contraband = sorted(ALL_CONTRABAND, key=lambda g: g.value, reverse=True)[0]
        declared = ALL_LEGAL[0].id
        return {"declared_id": declared, "count": 1, "actual_ids": [contraband.id], "lie": True}


def load_portrait(merchant: Merchant) -> str:
    """Load ASCII portrait from merchant's .txt file in characters/. Returns '' if missing."""
    chars_dir = characters_dir()
    name = merchant.portrait_file or f"{merchant.id}.txt"
    path = chars_dir / name
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8").strip()
    except OSError:
        return ""
