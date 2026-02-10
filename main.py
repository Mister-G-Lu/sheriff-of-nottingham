"""
Sheriff of Nottingham — interactive inspector game.

Run from project root:

    python main.py
"""

import random

from core.merchants import load_merchants, Merchant
from core.sheriff import Sheriff
from core.rounds import Declaration
from core.goods import GOOD_BY_ID, ALL_LEGAL, ALL_CONTRABAND, Good
from ui.narration import narrate_arrival, show_declaration, show_bribe, show_inspection_result


def print_intro() -> None:
    """Short lore intro about who you are."""
    print("=== Sheriff of Nottingham ===\n")
    print(
        "You are the newly appointed inspector at Nottingham's eastern gate.\n"
        "Each dawn, carts and merchants crowd before your post, swearing their bags\n"
        "hold nothing but honest bread, cheese, and chickens.\n"
    )
    print(
        "But the Prince demands higher taxes, smugglers grow bolder, and the people\n"
        "whisper that Sheriffs grow fat while they go hungry. Your reputation will\n"
        "rise or fall with every bag you open—or every lie you let walk past you.\n"
    )


def build_bag_and_declaration() -> tuple[Declaration, list[Good], bool]:
    """Create a bag (true contents) and what the merchant declares. Returns (declaration, goods, is_honest)."""
    legal_ids = [g.id for g in ALL_LEGAL]
    contraband_ids = [g.id for g in ALL_CONTRABAND]

    # Flip a coin: honest or smuggler this round
    is_honest = random.random() > 0.5

    declared_id = random.choice(legal_ids)
    declared_count = random.randint(1, 5)

    if is_honest:
        good = GOOD_BY_ID[declared_id]
        actual_goods = [good] * declared_count
    else:
        # Bag is mostly / entirely contraband
        actual_goods = [GOOD_BY_ID[random.choice(contraband_ids)]] * random.randint(1, 3)

    declaration = Declaration(good_id=declared_id, count=declared_count)
    return declaration, actual_goods, is_honest


def choose_tell(merchant: Merchant, is_honest: bool) -> str:
    """Pick a random tell line depending on whether the merchant is honest this round."""
    pool = merchant.tells_honest if is_honest else merchant.tells_lying
    return random.choice(pool) if pool else ""


def prompt_inspection(decision_prompt: str = "Inspect the bag or let them pass? [i/p]: ") -> bool:
    """Ask the player whether to inspect (True) or pass (False)."""
    while True:
        choice = input(decision_prompt).strip().lower()
        if choice in {"i", "inspect"}:
            return True
        if choice in {"p", "pass"}:
            return False
        print("Please answer with 'i' to inspect or 'p' to pass.")


def update_sheriff_reputation(sheriff: Sheriff, inspected: bool, is_honest: bool) -> None:
    """
    Simple reputation / experience model:
    - Inspect + lying: big win (rep +1, XP +1)
    - Inspect + honest: overreach (rep -1)
    - Pass + honest: fair (rep +1)
    - Pass + lying: failure (rep -2)
    """
    if inspected and not is_honest:
        sheriff.reputation = min(10, sheriff.reputation + 1)
        sheriff.level_up(1)
        print("Your keen eye exposes a lie. The townsfolk speak well of you tonight.")
    elif inspected and is_honest:
        sheriff.reputation = max(0, sheriff.reputation - 1)
        print("You find nothing amiss. Word spreads that you harass honest folk.")
    elif not inspected and is_honest:
        sheriff.reputation = min(10, sheriff.reputation + 1)
        print("You spare an honest soul more delays. Trust in you grows a little.")
    else:  # not inspected and not honest
        sheriff.reputation = max(0, sheriff.reputation - 2)
        print("Contraband slips through the gate. Whispers of incompetence—or corruption—follow you.")

    print(
        f"[Sheriff] Perception: {sheriff.perception}  "
        f"Authority: {sheriff.authority}  "
        f"Reputation: {sheriff.reputation}  "
        f"Experience: {sheriff.experience}"
    )
    print()


def main() -> None:
    print_intro()

    sheriff = Sheriff(perception=5, authority=5, reputation=5, experience=0)
    merchants = load_merchants(limit=3)
    if not merchants:
        print("No merchants found in characters/. Add .json (and optional .txt portraits).")
        return

    for merchant in merchants:
        narrate_arrival(merchant)

        declaration, actual_goods, is_honest = build_bag_and_declaration()
        tell = choose_tell(merchant, is_honest)
        if tell:
            print(f"You notice: {tell}.")
        print()

        show_declaration(merchant, declaration)

        bribe = "2 gold" if random.random() > 0.5 else ""
        show_bribe(merchant, bribe)

        inspected = prompt_inspection()
        sheriff_opens = inspected
        declared_ok = (
            len(actual_goods) == declaration.count
            and all(g.id == declaration.good_id for g in actual_goods)
        )
        caught = inspected and not declared_ok

        show_inspection_result(merchant, sheriff_opens, caught)
        update_sheriff_reputation(sheriff, inspected, declared_ok)

    print("--- Your shift at the eastern gate ends. ---")


if __name__ == "__main__":
    main()

