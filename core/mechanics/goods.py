"""Good types: legal goods and contraband."""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class GoodKind(str, Enum):
    LEGAL = "legal"
    CONTRABAND = "contraband"


@dataclass
class Good:
    """A single good type (e.g. apple, silk)."""
    id: str
    name: str
    kind: GoodKind
    value: int  # base value when delivered

    def is_legal(self) -> bool:
        return self.kind == GoodKind.LEGAL

    def is_contraband(self) -> bool:
        return self.kind == GoodKind.CONTRABAND


# Legal goods (green)
APPLE = Good("apple", "Apple", GoodKind.LEGAL, 2)
CHEESE = Good("cheese", "Cheese", GoodKind.LEGAL, 3)
BREAD = Good("bread", "Bread", GoodKind.LEGAL, 3)
CHICKEN = Good("chicken", "Chicken", GoodKind.LEGAL, 4)

# Contraband (red)
SILK = Good("silk", "Silk", GoodKind.CONTRABAND, 6)
PEPPER = Good("pepper", "Pepper", GoodKind.CONTRABAND, 8)
MEAD = Good("mead", "Mead", GoodKind.CONTRABAND, 10)
CROSSBOW = Good("crossbow", "Crossbow", GoodKind.CONTRABAND, 15)

ALL_LEGAL: tuple[Good, ...] = (APPLE, CHEESE, BREAD, CHICKEN)
ALL_CONTRABAND: tuple[Good, ...] = (SILK, PEPPER, MEAD, CROSSBOW)
ALL_GOODS: tuple[Good, ...] = ALL_LEGAL + ALL_CONTRABAND

GOOD_BY_ID: dict[str, Good] = {g.id: g for g in ALL_GOODS}


def good_by_id(id: str) -> Optional[Good]:
    return GOOD_BY_ID.get(id)
