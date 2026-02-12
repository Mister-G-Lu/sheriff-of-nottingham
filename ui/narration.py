"""Narration helpers: merchant arrival, declaration, bribe display."""

from core.game.rounds import Declaration
from core.players.merchants import Merchant


def narrate_arrival(merchant: Merchant) -> None:
    """Narrate merchant arrival and show portrait."""
    from ui.pygame_ui import get_ui

    ui = get_ui()

    # Load portrait
    if merchant.portrait_file:
        success = ui.load_portrait_file(merchant.portrait_file)
        if not success:
            print(f"[DEBUG] Failed to load portrait: {merchant.portrait_file}")

    print(f"--- {merchant.name} approaches the gate ---")
    print("")
    print(f"{merchant.intro}")
    print("")


def show_declaration(merchant: Merchant, declaration: Declaration) -> None:
    """Display what the merchant declares."""
    print("")
    print(f"{merchant.name} declares: {declaration.count} x {declaration.good_id}")
    print("")


def show_bribe(merchant: Merchant, bribe: str) -> None:
    """Display bribe offer (legacy function for backward compatibility)."""
    if bribe:
        print(f"{merchant.name} offers: {bribe}")
    else:
        print(f"{merchant.name} offers no bribe.")
    print()


def show_inspection_result(
    merchant: Merchant, sheriff_opens: bool, caught: bool
) -> None:
    """Report whether the Sheriff opened the bag and caught a lie."""
    if sheriff_opens:
        if caught:
            print(f"The Sheriff inspects {merchant.name}'s bag and finds contraband!")
        else:
            print(
                f"The Sheriff inspects {merchant.name}'s bag and finds nothing amiss."
            )
    else:
        print(f"The Sheriff lets {merchant.name} pass without inspection.")
    print()


def show_threat(merchant: Merchant) -> None:
    """Display Sheriff's threat to inspect."""
    print(f"\n[You narrow your eyes at {merchant.name}'s bag...]")
    print('You say: "That bag looks suspicious. I think I need to inspect it."')
    print()


def show_bribe_offer(merchant: Merchant, amount: int, round_number: int = 1) -> None:
    """Display merchant's bribe offer."""
    if round_number == 1:
        print(f"{merchant.name} shifts nervously and says:")
        print(
            f'  "Perhaps... {amount} gold would help you see that everything is in order?"'
        )
    else:
        print(f"{merchant.name} counters:")
        print(f'  "How about {amount} gold instead?"')
    print()


def show_merchant_refuses(merchant: Merchant) -> None:
    """Display merchant refusing to bribe."""
    print(f"{merchant.name} stands firm:")
    print('  "I have nothing to hide. Inspect if you must."')
    print()


def show_merchant_gives_up(merchant: Merchant) -> None:
    """Display merchant giving up on negotiation."""
    import random

    # Varied responses to make it clear they won't go higher
    responses = [
        "I won't go any higher. Just inspect the bag if you must.",
        "That's my final offer. I'm not paying more than that.",
        "This is ridiculous. I'm done negotiating - inspect it yourself.",
        "No more. That's all I'm willing to pay. Take it or leave it.",
        "I can't afford that. Just open the bag and be done with it.",
        "You're asking too much. I'd rather take my chances with inspection.",
    ]

    print(f"{merchant.name} shakes their head firmly:")
    print(f'  "{random.choice(responses)}"')
    print()


def show_bribe_accepted(merchant: Merchant, amount: int) -> None:
    """Display bribe acceptance."""
    print(f"\n[You pocket the {amount} gold and wave {merchant.name} through]")
    print('You say: "Everything seems to be in order. Move along."')
    print()


def show_bribe_rejected(merchant: Merchant) -> None:
    """Display bribe rejection."""
    print(f"\n[You push the gold back to {merchant.name}]")
    print('You say: "I cannot be bought. Open the bag."')
    print()


def show_proactive_bribe(merchant, amount: int, is_lying: bool) -> None:
    """Display merchant's proactive bribe offer (before any threat).

    Merchants know you don't know what's in their bag. They might offer bribes:
    - To hide contraband
    - To avoid hassle if lying about legal goods mix
    - For goodwill even when being honest
    """
    if is_lying:
        # Nervous - either has contraband or lying about legal goods mix
        print(f"{merchant.name} glances around nervously and leans in:")
        print(
            f'  "Sheriff, I know you\'re busy... perhaps {amount} gold would help speed things along?"'
        )
    else:
        # Being honest but still offering (goodwill/building relationship)
        print(f"{merchant.name} smiles warmly:")
        print(
            f'  "I appreciate your service, Sheriff. Here\'s {amount} gold for your trouble."'
        )
    print("")


def prompt_initial_decision(
    has_proactive_bribe: bool = False, bribe_amount: int = 0
) -> str:
    """Ask player what to do after seeing merchant and declaration.

    Returns:
        'accept' - accept proactive bribe and let pass
        'threaten' - threaten to inspect (may trigger negotiation)
        'inspect' - inspect immediately
        'pass' - let them pass without inspection
    """
    from ui.pygame_ui import get_ui

    ui = get_ui()

    if has_proactive_bribe:
        choices = [
            ("accept", f"Accept {bribe_amount} gold"),
            ("threaten", "Threaten to inspect"),
            ("inspect", "Inspect immediately"),
            ("pass", "Wave them through"),
        ]
    else:
        choices = [
            ("threaten", "Threaten to inspect"),
            ("inspect", "Inspect immediately"),
            ("pass", "Let them pass"),
        ]

    return ui.show_choices("What do you do?", choices)


def prompt_negotiation_response(current_offer: int) -> tuple[str, int]:
    """Ask player how to respond to bribe offer.

    Returns:
        Tuple of (choice, demand_amount)
        choice: 'accept', 'reject', or 'counter'
        demand_amount: only relevant if choice is 'counter'
    """
    from ui.pygame_ui import get_ui

    ui = get_ui()

    choices = [
        ("accept", "Accept bribe"),
        ("reject", "Reject and inspect"),
        ("counter", "Demand more gold"),
    ]

    choice = ui.show_choices(f"Current offer: {current_offer} gold", choices)

    if choice == "accept":
        return "accept", 0
    elif choice == "reject":
        return "reject", 0
    elif choice == "counter":
        # For counter-offer, ask for amount via text input
        demand_str = ui.get_input(
            f"How much gold do you demand? (more than {current_offer})"
        )
        try:
            demand_amount = int(demand_str)
            if demand_amount > current_offer:
                return "counter", demand_amount
            else:
                ui.display_text(
                    f"You must demand more than {current_offer} gold. Defaulting to {current_offer + 5}.",
                    clear_previous=False,
                )
                return "counter", current_offer + 5
        except ValueError:
            ui.display_text(
                f"Invalid amount. Defaulting to {current_offer + 5}.",
                clear_previous=False,
            )
            return "counter", current_offer + 5
