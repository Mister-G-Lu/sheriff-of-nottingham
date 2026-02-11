"""
Quick demo runner for a full \"AI vs AI\" inspection day.

Run from project root:

    python tests/demo_round.py
"""

import random

from core.players.merchants import load_merchants
from core.players.sheriff import Sheriff
from core.game.rounds import Declaration, resolve_inspection
from core.mechanics.goods import GOOD_BY_ID, ALL_LEGAL, ALL_CONTRABAND
from ui.narration import narrate_arrival, show_declaration, show_bribe, show_inspection_result


def run_demo_day() -> None:
    print("=== Sheriff of Nottingham (demo day) ===\n")

    sheriff = Sheriff(perception=5, authority=5, reputation=5, experience=0)
    merchants = load_merchants(limit=3)
    if not merchants:
        print("No merchants found in characters/. Add .json (and optional .txt portraits).")
        return

    for merchant in merchants:
        narrate_arrival(merchant)

        # Demo: pick a random declaration (one good type + count)
        legal_ids = [g.id for g in ALL_LEGAL]
        contraband_ids = [g.id for g in ALL_CONTRABAND]
        declared_id = random.choice(legal_ids)
        declared_count = random.randint(1, 5)
        declaration = Declaration(good_id=declared_id, count=declared_count)
        show_declaration(merchant, declaration)

        # Demo bribe (simple text for now)
        bribe = "2 gold" if random.random() > 0.5 else ""
        show_bribe(merchant, bribe)

        # Simulate bag: sometimes honest, sometimes contraband
        if random.random() > 0.5:
            good = GOOD_BY_ID[declared_id]
            actual_goods = [good] * declared_count
        else:
            actual_goods = [GOOD_BY_ID[random.choice(contraband_ids)]] * random.randint(1, 3)

        sheriff_opens, caught = resolve_inspection(sheriff, merchant, declaration, actual_goods)
        show_inspection_result(merchant, sheriff_opens, caught)

        if caught:
            sheriff.level_up(1)

    print("--- Demo day ends ---")


if __name__ == "__main__":
    run_demo_day()

