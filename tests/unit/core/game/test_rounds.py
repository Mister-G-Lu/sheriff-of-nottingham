import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from core.game.rounds import resolve_inspection, Declaration
from core.players.sheriff import Sheriff
from core.players.merchants import Merchant
from core.mechanics.goods import APPLE, SILK

# Import test helpers
from tests.test_helpers import create_test_merchant, create_test_sheriff


def test_resolve_inspection_declared_ok():
    s = create_test_sheriff(perception=5)
    m = create_test_merchant()
    decl = Declaration(good_id="apple", count=2)
    actual = [APPLE, APPLE]
    assert resolve_inspection(s, m, decl, actual) == (False, False)


def test_resolve_inspection_opens_and_catches(monkeypatch):
    s = create_test_sheriff(perception=10)
    m = create_test_merchant(bluff_skill=1)
    decl = Declaration(good_id="apple", count=2)
    actual = [SILK]
    monkeypatch.setattr("core.game.rounds.random.randint", lambda a, b: 10)
    monkeypatch.setattr("core.players.merchants.Merchant.roll_bluff", lambda self: 1)
    opens, caught = resolve_inspection(s, m, decl, actual)
    assert opens is True and caught is True


def test_resolve_inspection_records_contraband_when_slips(monkeypatch):
    from core.game.rounds import RoundState

    s = create_test_sheriff(perception=1)
    m = create_test_merchant(bluff_skill=10)
    decl = Declaration(good_id="apple", count=1)
    actual = [SILK]
    # Force sheriff roll low so he doesn't open
    monkeypatch.setattr("core.game.rounds.random.randint", lambda a, b: 1)
    rs = RoundState(merchant=m, bag_actual=actual, declaration=decl)
    opens, caught = resolve_inspection(s, m, decl, actual, round_state=rs)
    assert opens is False and caught is False
    assert rs.contraband_passed_count == 1
    assert rs.contraband_passed_value == SILK.value
