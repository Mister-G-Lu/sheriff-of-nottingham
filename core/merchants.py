"""Merchants: loaded from characters/ with personality, lore, tells, bluff skill."""

import json
import random
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

from core.goods import Good


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

    def roll_bluff(self) -> int:
        """Roll for bluff (e.g. d10 + bluff_skill)."""
        return random.randint(1, 10) + self.bluff_skill


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
            m = Merchant(
                id=data.get("id", path.stem),
                name=data.get("name", path.stem),
                personality=data.get("personality", ""),
                lore=data.get("lore", ""),
                tells_honest=data.get("tells_honest", []),
                tells_lying=data.get("tells_lying", []),
                bluff_skill=int(data.get("bluff_skill", 5)),
                portrait_file=data.get("portrait_file"),
            )
            merchants.append(m)
        except (json.JSONDecodeError, KeyError) as e:
            continue
    return merchants


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
