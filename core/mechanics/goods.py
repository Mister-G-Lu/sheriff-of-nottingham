"""Good types: legal goods and contraband."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from core.constants import (
    APPLE_VALUE,
    BREAD_VALUE,
    CHEESE_VALUE,
    CHICKEN_VALUE,
    CROSSBOW_VALUE,
    MEAD_VALUE,
    PEPPER_VALUE,
    SILK_VALUE,
)


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
APPLE = Good("apple", "Apple", GoodKind.LEGAL, APPLE_VALUE)
CHEESE = Good("cheese", "Cheese", GoodKind.LEGAL, CHEESE_VALUE)
BREAD = Good("bread", "Bread", GoodKind.LEGAL, BREAD_VALUE)
CHICKEN = Good("chicken", "Chicken", GoodKind.LEGAL, CHICKEN_VALUE)

# Contraband (red)
SILK = Good("silk", "Silk", GoodKind.CONTRABAND, SILK_VALUE)
PEPPER = Good("pepper", "Pepper", GoodKind.CONTRABAND, PEPPER_VALUE)
MEAD = Good("mead", "Mead", GoodKind.CONTRABAND, MEAD_VALUE)
CROSSBOW = Good("crossbow", "Crossbow", GoodKind.CONTRABAND, CROSSBOW_VALUE)

ALL_LEGAL: tuple[Good, ...] = (APPLE, CHEESE, BREAD, CHICKEN)
ALL_CONTRABAND: tuple[Good, ...] = (SILK, PEPPER, MEAD, CROSSBOW)
ALL_GOODS: tuple[Good, ...] = ALL_LEGAL + ALL_CONTRABAND

GOOD_BY_ID: dict[str, Good] = {g.id: g for g in ALL_GOODS}


def good_by_id(id: str) -> Optional[Good]:
    return GOOD_BY_ID.get(id)
