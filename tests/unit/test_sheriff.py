from core.players.sheriff import Sheriff


def test_level_up_increments_experience_and_perception():
    s = Sheriff(perception=5, experience=2)
    s.level_up(1)
    assert s.experience == 3
    assert s.perception == 6


def test_level_up_caps_perception():
    s = Sheriff(perception=10, experience=2)
    s.level_up(1)
    assert s.experience == 3
    assert s.perception == 10
