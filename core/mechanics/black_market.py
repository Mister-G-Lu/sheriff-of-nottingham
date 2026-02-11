"""Black market contact system for reputation restoration."""

from dataclasses import dataclass


@dataclass
class BlackMarketContact:
    """Represents a shadowy figure who can 'fix' reputation problems."""
    name: str = "The Broker"
    contraband_threshold: int = 30  # Total contraband value needed
    reputation_restore: int = 5     # How much reputation restored
    has_appeared: bool = False
    deal_accepted: bool = False


def check_black_market_offer(stats, sheriff) -> tuple[bool, int]:
    """Check if black market contact should appear.
    
    Appears when:
    - Sheriff has low reputation (1-3)
    - Significant contraband has passed through (30+ gold value)
    
    Args:
        stats: GameStats object
        sheriff: Sheriff object
    
    Returns:
        Tuple of (should_appear, contraband_value_passed)
    """
    # Calculate total contraband value that passed through
    # This is tracked when merchants pass without inspection
    contraband_passed = stats.missed_smugglers  # Number of smugglers missed
    
    # Estimate contraband value (rough calculation)
    # Average contraband value is ~6-10 gold per smuggler
    estimated_contraband_value = contraband_passed * 8
    
    # Offer appears if:
    # 1. Reputation is critically low (1-3)
    # 2. Enough contraband has passed through
    should_appear = (
        1 <= sheriff.reputation <= 3 and
        estimated_contraband_value >= 30
    )
    
    return should_appear, estimated_contraband_value


def show_black_market_offer(contact: BlackMarketContact, contraband_value: int, sheriff) -> None:
    """Display the black market contact's offer."""
    print("\n" + "="*70)
    print("🕵️  A SHADOWY FIGURE APPROACHES".center(70))
    print("="*70)
    print()
    print("As the last merchant departs, a cloaked figure emerges from the shadows.")
    print(f"You recognize them - {contact.name}, a notorious black market dealer.")
    print()
    print(f'"{contact.name}" speaks in a low voice:')
    print()
    print(f'  "Sheriff... I\'ve been watching. You\'ve let quite a bit of my... merchandise"')
    print(f'   pass through your gate. {contraband_value} gold worth of contraband, by my count."')
    print()
    print(f'  "Your reputation is hanging by a thread - only {sheriff.reputation} out of 10."')
    print(f'   One more mistake and the Prince will have your head."')
    print()
    print(f'  "But I can help you. I have... connections. For the right price, I can make"')
    print(f'   certain... favorable reports reach the Prince\'s ears. Your reputation could"')
    print(f'   be restored to {sheriff.reputation + contact.reputation_restore}. Clean slate."')
    print()
    print(f'  "All I ask is that you continue to be... understanding... with my associates."')
    print(f'   Let my goods flow freely, and I\'ll keep you in your position."')
    print()
    print("="*70)
    print(f"OFFER: Restore reputation to {sheriff.reputation + contact.reputation_restore} (currently {sheriff.reputation})")
    print(f"COST: You've already paid by letting contraband through")
    print(f"CONSEQUENCE: You're now in debt to the black market")
    print("="*70)
    print()


def prompt_black_market_decision() -> bool:
    """Ask player if they accept the black market deal.
    
    Returns:
        True if accepted, False if rejected
    """
    # Check if we're using Pygame UI
    try:
        from ui.pygame_ui import get_ui
        USING_PYGAME = True
    except ImportError:
        USING_PYGAME = False
    
    if USING_PYGAME:
        # Use Pygame choice buttons
        ui = get_ui()
        choices = [
            ('accept', 'Accept - Restore reputation'),
            ('refuse', 'Refuse - Stay independent')
        ]
        choice = ui.show_choices("Do you accept the Broker's offer?", choices)
        return choice == 'accept'
    else:
        # Terminal mode
        print("Do you accept the Broker's offer?")
        print("  [y] Accept - Restore reputation, but owe the black market")
        print("  [n] Refuse - Maintain your independence, stay at low reputation")
        print()
        
        while True:
            choice = input("Your choice: ").strip().lower()
            if choice in {'y', 'yes'}:
                return True
            elif choice in {'n', 'no'}:
                return False
            else:
                print("Please choose 'y' or 'n'.")


def accept_black_market_deal(contact: BlackMarketContact, sheriff) -> None:
    """Process accepting the black market deal."""
    contact.deal_accepted = True
    old_rep = sheriff.reputation
    sheriff.reputation = min(10, sheriff.reputation + contact.reputation_restore)
    
    print()
    print("="*70)
    print()
    print(f'The Broker nods slowly. "Wise choice, Sheriff."')
    print()
    print(f'Within days, favorable reports mysteriously reach the Prince.')
    print(f'Your reputation improves from {old_rep} to {sheriff.reputation}.')
    print()
    print(f'But you know the truth - you\'re now in the Broker\'s pocket.')
    print(f'The black market owns you.')
    print()
    print("="*70)
    print()


def reject_black_market_deal(contact: BlackMarketContact) -> None:
    """Process rejecting the black market deal."""
    print()
    print("="*70)
    print()
    print(f'The Broker\'s eyes narrow. "Foolish. But I respect your... principles."')
    print()
    print(f'"When you\'re begging in the streets after the Prince fires you,"')
    print(f' remember that I offered you a way out."')
    print()
    print(f'The figure melts back into the shadows.')
    print()
    print("Your reputation remains low, but your soul remains your own.")
    print()
    print("="*70)
    print()


def add_black_market_ending_note(stats, contact: BlackMarketContact) -> str:
    """Add a note to the ending if player accepted black market deal.
    
    Returns:
        String to append to ending text, or empty string
    """
    if not contact.deal_accepted:
        return ""
    
    return """
    
⚠️  BLACK MARKET DEBT ⚠️

However, your success comes with a dark secret...
You owe your position to the Broker and the black market.
They own you now. Your reputation may be restored, but at what cost?

The contraband flows freely through Nottingham's gates.
You are complicit. You are corrupt.
And there's no going back.
"""
