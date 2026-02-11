import unittest
import json
from core.players.merchants import Merchant, load_merchants


def test_roll_bluff_monkeypatched():
    m = Merchant(id="x", name="X", intro="Test merchant", tells_honest=[], tells_lying=[], bluff_skill=5)
    # Test that roll_bluff returns an integer
    result = m.roll_bluff()
    assert isinstance(result, int)
    # roll_bluff returns random.randint(1, 10) + bluff_skill
    # With bluff_skill=5, range is 6-15
    assert 6 <= result <= 15


def test_merchant_portrait_file():
    """Test that merchant portrait_file attribute works."""
    m = Merchant(id="x", name="X", intro="Test merchant", tells_honest=[], tells_lying=[], portrait_file="test.png")
    assert m.portrait_file == "test.png"
    assert isinstance(m.portrait_file, str)


def test_load_merchants_limit(tmp_path, monkeypatch):
    a = tmp_path / "a.json"
    b = tmp_path / "b.json"
    a.write_text(json.dumps({"id": "a", "name": "A"}), encoding="utf-8")
    b.write_text(json.dumps({"id": "b", "name": "B"}), encoding="utf-8")
    monkeypatch.setattr("core.players.merchant_loader.characters_dir", lambda: tmp_path)
    merchants = load_merchants(limit=1)
    assert len(merchants) <= 1


def test_merchant_records_smuggle_and_legal_delivery():
    from core.game.rounds import RoundState, Declaration
    from core.mechanics.goods import SILK, APPLE

    m = Merchant(id="m", name="M", intro="Test merchant", tells_honest=[], tells_lying=[])
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
