from core.rounds import resolve_inspection, Declaration
from core.sheriff import Sheriff
from core.merchants import Merchant
from core.goods import APPLE, SILK


def test_resolve_inspection_declared_ok():
    s = Sheriff(perception=5)
    m = Merchant(id="m", name="M", personality="", lore="", tells_honest=[], tells_lying=[])
    decl = Declaration(good_id="apple", count=2)
    actual = [APPLE, APPLE]
    assert resolve_inspection(s, m, decl, actual) == (False, False)


def test_resolve_inspection_opens_and_catches(monkeypatch):
    s = Sheriff(perception=10)
    m = Merchant(id="m", name="M", personality="", lore="", tells_honest=[], tells_lying=[], bluff_skill=1)
    decl = Declaration(good_id="apple", count=2)
    actual = [SILK]
    monkeypatch.setattr("core.rounds.random.randint", lambda a, b: 10)
    monkeypatch.setattr("core.merchants.Merchant.roll_bluff", lambda self: 1)
    opens, caught = resolve_inspection(s, m, decl, actual)
    assert opens is True and caught is True


def test_resolve_inspection_records_contraband_when_slips(monkeypatch):
    from core.rounds import RoundState

    s = Sheriff(perception=1)
    m = Merchant(id="m", name="M", personality="", lore="", tells_honest=[], tells_lying=[], bluff_skill=10)
    decl = Declaration(good_id="apple", count=1)
    actual = [SILK]
    # Force sheriff roll low so he doesn't open
    monkeypatch.setattr("core.rounds.random.randint", lambda a, b: 1)
    rs = RoundState(merchant=m, bag_actual=actual, declaration=decl)
    opens, caught = resolve_inspection(s, m, decl, actual, round_state=rs)
    assert opens is False and caught is False
    assert rs.contraband_passed_count == 1
    assert rs.contraband_passed_value == SILK.value
