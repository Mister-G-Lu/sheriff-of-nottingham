from core.mechanics.goods import GOOD_BY_ID, APPLE, SILK, good_by_id


def test_good_properties():
    assert APPLE.is_legal()
    assert not APPLE.is_contraband()
    assert SILK.is_contraband()


def test_good_by_id_lookup():
    g = good_by_id("bread")
    assert g is not None
    assert g.name == "Bread"
