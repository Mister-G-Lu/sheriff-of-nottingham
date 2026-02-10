import json
from core.merchants import Merchant, load_portrait, load_merchants


def test_roll_bluff_monkeypatched(monkeypatch):
    m = Merchant(id="x", name="X", personality="", lore="", tells_honest=[], tells_lying=[], bluff_skill=5)
    monkeypatch.setattr("core.merchants.random.randint", lambda a, b: 3)
    assert m.roll_bluff() == 8


def test_load_portrait_missing(tmp_path, monkeypatch):
    monkeypatch.setattr("core.merchants.characters_dir", lambda: tmp_path)
    m = Merchant(id="x", name="X", personality="", lore="", tells_honest=[], tells_lying=[])
    assert load_portrait(m) == ""


def test_load_merchants_limit(tmp_path, monkeypatch):
    a = tmp_path / "a.json"
    b = tmp_path / "b.json"
    a.write_text(json.dumps({"id": "a", "name": "A"}), encoding="utf-8")
    b.write_text(json.dumps({"id": "b", "name": "B"}), encoding="utf-8")
    monkeypatch.setattr("core.merchants.characters_dir", lambda: tmp_path)
    merchants = load_merchants(limit=1)
    assert len(merchants) <= 1


def test_merchant_records_smuggle_and_legal_delivery():
    from core.rounds import RoundState, Declaration
    from core.goods import SILK, APPLE

    m = Merchant(id="m", name="M", personality="", lore="", tells_honest=[], tells_lying=[])
    # Simulate a round where contraband slipped by (sheriff didn't open)
    rs = RoundState(merchant=m, bag_actual=[SILK, APPLE])
    rs.sheriff_opens = False
    # Simulate that contraband passed (summary fields set by resolve_inspection normally)
    rs.contraband_passed_count = 1
    rs.contraband_passed_value = SILK.value
    m.record_round_result(rs)

    summary = m.smuggle_summary()
    assert summary["contraband_passed_count"] == 1
    assert summary["contraband_passed_value"] == SILK.value
    # Legal delivery should include the apple since the bag wasn't opened
    assert summary["legal_sold_count"] == 1
    assert summary["legal_sold_value"] == APPLE.value
