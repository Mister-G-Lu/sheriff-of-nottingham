"""Game statistics tracking for end-game summary."""

from dataclasses import dataclass


@dataclass
class GameStats:
    """Track statistics throughout a game session."""
    merchants_processed: int = 0
    smugglers_caught: int = 0      # Caught lying merchants
    honest_inspected: int = 0       # Inspected honest merchants (false accusations)
    bribes_accepted: int = 0        # Number of bribes taken
    gold_earned: int = 0            # Total gold from bribes
    
    # Inspection accuracy
    total_inspections: int = 0
    correct_inspections: int = 0    # Caught smuggler OR trusted honest merchant
    
    # Missed opportunities
    missed_smugglers: int = 0       # Let smuggler pass without inspection
    
    def record_inspection(self, was_honest: bool, caught_lie: bool) -> None:
        """Record an inspection result.
        
        Args:
            was_honest: Whether the merchant was actually honest
            caught_lie: Whether we caught them lying (only relevant if not honest)
        """
        self.total_inspections += 1
        
        if not was_honest:
            # Merchant was lying
            if caught_lie:
                self.smugglers_caught += 1
                self.correct_inspections += 1
        else:
            # Merchant was honest
            self.honest_inspected += 1
            # Not a correct decision (false accusation)
    
    def record_pass(self, was_honest: bool) -> None:
        """Record letting a merchant pass without inspection.
        
        Args:
            was_honest: Whether the merchant was actually honest
        """
        if was_honest:
            self.correct_inspections += 1  # Correctly trusted them
        else:
            self.missed_smugglers += 1  # Missed a smuggler
    
    def record_bribe(self, amount: int) -> None:
        """Record accepting a bribe.
        
        Args:
            amount: Gold amount received
        """
        self.bribes_accepted += 1
        self.gold_earned += amount
    
    def accuracy_percentage(self) -> float:
        """Calculate inspection accuracy percentage."""
        total_decisions = self.total_inspections + self.missed_smugglers
        if total_decisions == 0:
            return 0.0
        return (self.correct_inspections / total_decisions) * 100


# NOTE: End game summary and rating logic has been moved to core/end_game.py
# This keeps game_stats.py focused on statistics tracking only.
