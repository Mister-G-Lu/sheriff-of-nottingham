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
