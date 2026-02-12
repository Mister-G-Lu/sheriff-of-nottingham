"""
Centralized Game Master State - Thread-Safe History Tracking

This module provides a centralized system for tracking all game events:
- Inspection outcomes
- Bribe offers and results
- Merchant declarations vs actual contents
- Sheriff behavior patterns

All merchants query this single source of truth, with tier-based access:
- Easy merchants: Last 1-2 relevant events
- Medium merchants: Last 3-4 relevant events
- Hard merchants: Full history access

Uses context variables for thread-safe, test-isolated state management.
"""

from contextvars import ContextVar
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class MerchantTier(Enum):
    """Difficulty tier for merchant AI sophistication."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass
class InspectionEvent:
    """Record of a single merchant encounter."""

    merchant_name: str
    declared_good: str
    declared_count: int
    actual_goods: list[str]  # List of good IDs
    was_opened: bool  # Did sheriff inspect?
    caught_lie: bool  # Was merchant lying and caught?
    bribe_offered: int  # Gold offered (0 if none)
    bribe_accepted: bool  # Did sheriff accept bribe?
    proactive_bribe: bool  # Was bribe offered before threat?
    round_number: int  # Which round of the game


@dataclass
class GameMasterState:
    """
    Centralized game state tracking all events.

    This is the single source of truth for all game history.
    Merchants query subsets based on their tier.
    """

    events: list[InspectionEvent] = field(default_factory=list)
    current_round: int = 0

    def record_event(
        self,
        merchant_name: str,
        declared_good: str,
        declared_count: int,
        actual_goods: list[str],
        was_opened: bool,
        caught_lie: bool,
        bribe_offered: int = 0,
        bribe_accepted: bool = False,
        proactive_bribe: bool = False,
    ) -> None:
        """Record a new inspection event."""
        event = InspectionEvent(
            merchant_name=merchant_name,
            declared_good=declared_good,
            declared_count=declared_count,
            actual_goods=actual_goods,
            was_opened=was_opened,
            caught_lie=caught_lie,
            bribe_offered=bribe_offered,
            bribe_accepted=bribe_accepted,
            proactive_bribe=proactive_bribe,
            round_number=self.current_round,
        )
        self.events.append(event)
        self.current_round += 1

    def get_history_for_tier(self, tier: MerchantTier) -> list[dict]:
        """
        Get history slice appropriate for merchant tier.

        Args:
            tier: Merchant difficulty tier

        Returns:
            List of event dictionaries (most recent first)
        """
        if tier == MerchantTier.EASY:
            # Last 1-2 events
            slice_size = min(2, len(self.events))
        elif tier == MerchantTier.MEDIUM:
            # Last 3-4 events
            slice_size = min(4, len(self.events))
        else:  # HARD
            # Full history
            slice_size = len(self.events)

        # Get most recent events
        recent_events = self.events[-slice_size:] if slice_size > 0 else []

        # Convert to dict format for compatibility with existing code
        return [self._event_to_dict(event) for event in recent_events]

    def _event_to_dict(self, event: InspectionEvent) -> dict:
        """Convert InspectionEvent to dictionary format."""
        return {
            "merchant_name": event.merchant_name,
            "declaration": {
                "good_id": event.declared_good,
                "count": event.declared_count,
            },
            "actual_ids": event.actual_goods,
            "opened": event.was_opened,
            "caught_lie": event.caught_lie,
            "bribe_offered": event.bribe_offered,
            "bribe_accepted": event.bribe_accepted,
            "proactive_bribe": event.proactive_bribe,
            "round_number": event.round_number,
        }

    def get_sheriff_stats(self) -> dict:
        """
        Calculate sheriff behavior statistics.

        Returns:
            Dict with inspection_rate, catch_rate, bribe_acceptance_rate, etc.
        """
        if not self.events:
            return {
                "inspection_rate": 0.5,
                "catch_rate": 0.5,
                "bribe_acceptance_rate": 0.3,
                "total_encounters": 0,
            }

        total = len(self.events)
        inspections = sum(1 for e in self.events if e.was_opened)
        catches = sum(1 for e in self.events if e.caught_lie)
        bribes_offered = sum(1 for e in self.events if e.bribe_offered > 0)
        bribes_accepted = sum(1 for e in self.events if e.bribe_accepted)

        # Calculate rates
        inspection_rate = inspections / total if total > 0 else 0.5
        catch_rate = catches / inspections if inspections > 0 else 0.5
        bribe_acceptance_rate = (
            bribes_accepted / bribes_offered if bribes_offered > 0 else 0.3
        )

        return {
            "inspection_rate": inspection_rate,
            "catch_rate": catch_rate,
            "bribe_acceptance_rate": bribe_acceptance_rate,
            "total_encounters": total,
            "total_inspections": inspections,
            "total_catches": catches,
            "bribes_offered": bribes_offered,
            "bribes_accepted": bribes_accepted,
        }

    def get_recent_inspection_pattern(self, last_n: int = 5) -> str:
        """
        Analyze recent inspection pattern.

        Returns:
            String describing pattern: 'aggressive', 'moderate', 'lenient'
        """
        if not self.events:
            return "moderate"

        recent = self.events[-last_n:]
        inspection_rate = sum(1 for e in recent if e.was_opened) / len(recent)

        if inspection_rate > 0.7:
            return "aggressive"
        elif inspection_rate < 0.3:
            return "lenient"
        else:
            return "moderate"


# Context variable for thread-safe, test-isolated state management
_game_state_ctx: ContextVar[Optional[GameMasterState]] = ContextVar(
    "game_state", default=None
)


class GameStateManager:
    """Manager for game state using context variables.

    This provides thread-safe state management with automatic test isolation.
    Each context (test, thread, etc.) gets its own independent state.
    """

    @staticmethod
    def get() -> GameMasterState:
        """Get current game state, creating if needed.

        Returns:
            GameMasterState: Current game state for this context
        """
        state = _game_state_ctx.get()
        if state is None:
            state = GameMasterState()
            _game_state_ctx.set(state)
        return state

    @staticmethod
    def set(state: GameMasterState) -> None:
        """Set the current game state.

        Args:
            state: GameMasterState to set as current
        """
        _game_state_ctx.set(state)

    @staticmethod
    def reset() -> None:
        """Reset to a new game state."""
        _game_state_ctx.set(GameMasterState())


# Backward compatibility functions - existing code continues to work!
def get_game_master_state() -> GameMasterState:
    """Get or create the game master state.

    Uses context variables for thread-safe, test-isolated state management.
    Each test automatically gets its own isolated state.

    Returns:
        GameMasterState: Current game state for this context
    """
    return GameStateManager.get()


def reset_game_master_state() -> None:
    """Reset the game master state (for new games).

    Creates a fresh GameMasterState in the current context.
    """
    GameStateManager.reset()
