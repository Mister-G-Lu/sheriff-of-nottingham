from core.merchants import Merchant
from core.rounds import RoundState
from core.goods import SILK, APPLE
from ui.narration import show_merchant_smuggle_summary, show_endgame_summary


def test_smuggle_summary_and_endgame_prints(capsys):
    m = Merchant(id="m", name="M", personality="", lore="", tells_honest=[], tells_lying=[])
    # Simulate stored aggregates
    m.past_smuggles_count = 2
    m.past_smuggles_value = SILK.value * 2
    m.past_legal_sold_count = 3
    m.past_legal_sold_value = APPLE.value * 3

    # A round where an inspection saw 1 contraband and 1 legal
    r = RoundState(merchant=m, bag_actual=[SILK, APPLE])
    r.sheriff_opens = True

    show_merchant_smuggle_summary(m)
    show_endgame_summary([r], [m])

    captured = capsys.readouterr().out
    assert "Contraband slipped past" in captured
    assert "End of Game Summary" in captured