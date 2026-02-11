"""
Sheriff Reputation Management
Handles reputation and experience updates based on decisions
"""

from core.players.sheriff import Sheriff
from core.systems.game_stats import GameStats
from core.mechanics.goods import Good


def update_sheriff_reputation(sheriff: Sheriff, inspected: bool, is_honest: bool, 
                             stats: GameStats = None, actual_goods: list[Good] = None) -> None:
    """
    Update sheriff's reputation based on decision outcome.
    
    Reputation changes:
    - Inspect + lying: big win (rep +1, XP +1)
    - Inspect + honest: overreach (rep -1)
    - Pass + honest: fair (rep +1)
    - Pass + lying (contraband): failure (rep -2)
    - Pass + lying (all legal): honest mistake (rep +0, XP +1)
    
    Args:
        sheriff: Sheriff object to update
        inspected: Whether the bag was inspected
        is_honest: Whether the merchant was telling the truth
        stats: Optional GameStats for tracking
        actual_goods: Optional list of goods for contraband checking
    """
    if inspected and not is_honest:
        sheriff.reputation = min(10, sheriff.reputation + 1)
        sheriff.level_up(1)
        print("Your keen eye exposes a lie. The townsfolk speak well of you tonight.")
    elif inspected and is_honest:
        sheriff.reputation = max(0, sheriff.reputation - 1)
        print("You wrongly accused an honest merchant. Your reputation suffers.")
    elif not inspected and is_honest:
        sheriff.reputation = min(10, sheriff.reputation + 1)
        print("You trusted an honest merchant. The Prince approves.")
    elif not inspected and not is_honest:
        # Merchant lied and got away with it
        # Check if they smuggled contraband or just lied about legal goods
        if actual_goods:
            has_contraband = any(g.is_contraband() for g in actual_goods)
            if has_contraband:
                # Serious failure - let contraband through
                sheriff.reputation = max(0, sheriff.reputation - 2)
                print("Contraband slipped past your watch. The Prince is displeased.")
            else:
                # They lied about legal goods (e.g., 3 apples declared as 2 cheese)
                # This is an honest mistake - no reputation loss, but gain experience
                sheriff.level_up(1)
                print("A clever merchant tricked you, but no contraband passed. You learn from this.")
        else:
            # Fallback if no goods info provided
            sheriff.reputation = max(0, sheriff.reputation - 2)
            print("A lie slipped past you. Your reputation takes a hit.")
    
    print(f"[Sheriff] Reputation: {sheriff.reputation}/10  |  Experience: {sheriff.experience}")
