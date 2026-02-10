"""Sheriff: stats (Perception, Authority, Reputation) and experience."""

from dataclasses import dataclass, field


@dataclass
class Sheriff:
    """The Sheriff inspecting merchants. Can level up experience."""
    perception: int = 5   # affects lie detection vs merchant bluff
    authority: int = 5
    reputation: int = 5
    experience: int = 0

    def level_up(self, amount: int = 1) -> None:
        self.experience += amount
        # Optional: raise perception/authority every N experience
        if self.experience % 3 == 0:
            self.perception = min(10, self.perception + 1)
