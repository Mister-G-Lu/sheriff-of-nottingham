"""ASCII and narration helpers: merchant arrival, declaration, bribe display."""

from core.merchants import Merchant, load_portrait
from core.rounds import Declaration


def show_portrait(merchant: Merchant) -> None:
    """Print merchant's ASCII portrait from their .txt file if present (empty .txt = no output)."""
    art = load_portrait(merchant)
    if art:
        print(art)


def narrate_arrival(merchant: Merchant) -> None:
    """Narrate merchant arrival and show portrait."""
    print(f"\n--- {merchant.name} approaches the gate ---")
    print(f"  {merchant.personality}")
    if merchant.lore:
        print(f"  {merchant.lore}")
    show_portrait(merchant)
    print()


def show_declaration(merchant: Merchant, declaration: Declaration) -> None:
    """Display what the merchant declares."""
    print(f"{merchant.name} declares: {declaration.count} x {declaration.good_id}")
    print()


def show_bribe(merchant: Merchant, bribe: str) -> None:
    """Display bribe offer."""
    if bribe:
        print(f"{merchant.name} offers: {bribe}")
    else:
        print(f"{merchant.name} offers no bribe.")
    print()


def show_inspection_result(merchant: Merchant, sheriff_opens: bool, caught: bool) -> None:
    """Report whether the Sheriff opened the bag and caught a lie."""
    if sheriff_opens:
        if caught:
            print(f"The Sheriff inspects {merchant.name}'s bag and finds contraband!")
        else:
            print(f"The Sheriff inspects {merchant.name}'s bag and finds nothing amiss.")
    else:
        print(f"The Sheriff lets {merchant.name} pass without inspection.")
    print()
