"""Sheriff: stats (Perception, Authority, Reputation) and experience."""

from dataclasses import dataclass

from core.constants import (
    STARTING_AUTHORITY,
    STARTING_EXPERIENCE,
    STARTING_PERCEPTION,
    STARTING_REPUTATION,
)


@dataclass
class Sheriff:
    """The Sheriff inspecting merchants. Can level up experience."""

    perception: int = STARTING_PERCEPTION  # affects lie detection vs merchant bluff
    authority: int = STARTING_AUTHORITY
    reputation: int = STARTING_REPUTATION
    experience: int = STARTING_EXPERIENCE

    def level_up(self, amount: int = 1) -> None:
        self.experience += amount
        # Optional: raise perception/authority every N experience
        if self.experience % 3 == 0:
            self.perception = min(10, self.perception + 1)
