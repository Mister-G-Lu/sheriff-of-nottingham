"""
Test Helper Utilities

Provides reusable fixtures and helper functions to reduce code duplication
across test files.
"""

import pygame
from unittest.mock import Mock
from contextlib import contextmanager


# ============================================================================
# Pygame Test Helpers
# ============================================================================

@contextmanager
def pygame_context():
    """
    Context manager for pygame initialization and cleanup.
    
    Usage:
        with pygame_context():
            # Your pygame test code here
            window = PygameWindow()
            # ...
    """
    pygame.init()
    try:
        yield
    finally:
        pygame.quit()


def create_mock_pygame_window(with_fonts=True, with_screen=True, with_portrait=False):
    """
    Create a mock pygame window with common attributes.
    
    Args:
        with_fonts: Include font mocks (default True)
        with_screen: Include screen mock (default True)
        with_portrait: Include portrait rendering mocks (default False)
    
    Returns:
        Mock window object with configured attributes
    
    Usage:
        mock_window = create_mock_pygame_window()
        text_display = PygameText(mock_window)
    """
    mock_window = Mock()
    
    if with_fonts:
        mock_window.font_normal = pygame.font.Font(None, 24)
        mock_window.font_large = pygame.font.Font(None, 36)
        mock_window.font_small = pygame.font.Font(None, 18)
    
    if with_screen:
        mock_window.screen = pygame.display.set_mode((1200, 800))
    
    if with_portrait:
        mock_window.clear_screen = Mock()
        mock_window.render_portrait = Mock()
        mock_window.update_display = Mock()
    
    return mock_window


def create_pygame_font(size=24):
    """
    Create a pygame font for testing.
    
    Args:
        size: Font size (default 24)
    
    Returns:
        pygame.font.Font instance
    """
    return pygame.font.Font(None, size)


# ============================================================================
# Game Object Test Helpers
# ============================================================================

def create_test_merchant(
    merchant_id="test",
    name="Test Merchant",
    intro="A test merchant",
    tells_honest=None,
    tells_lying=None,
    bluff_skill=5,
    gold=50,
    risk_tolerance=5,
    greed=5,
    honesty_bias=5,
    portrait_file=None
):
    """
    Create a test Merchant with default values.
    
    Args:
        merchant_id: Merchant ID (default "test")
        name: Merchant name (default "Test Merchant")
        intro: Introduction text (default "A test merchant")
        tells_honest: List of honest tells (default [])
        tells_lying: List of lying tells (default [])
        bluff_skill: Bluff skill level (default 5)
        gold: Starting gold (default 50)
        risk_tolerance: Risk tolerance level (default 5)
        greed: Greed level (default 5)
        honesty_bias: Honesty bias level (default 5)
        portrait_file: Portrait filename (default None)
    
    Returns:
        Merchant instance
    
    Usage:
        merchant = create_test_merchant(bluff_skill=8, gold=100)
    """
    from core.players.merchants import Merchant
    
    return Merchant(
        id=merchant_id,
        name=name,
        intro=intro,
        tells_honest=tells_honest or [],
        tells_lying=tells_lying or [],
        bluff_skill=bluff_skill,
        gold=gold,
        risk_tolerance=risk_tolerance,
        greed=greed,
        honesty_bias=honesty_bias,
        portrait_file=portrait_file
    )


def create_test_sheriff(perception=5, reputation=10):
    """
    Create a test Sheriff with default values.
    
    Args:
        perception: Perception level (default 5)
        reputation: Reputation level (default 10)
    
    Returns:
        Sheriff instance
    
    Usage:
        sheriff = create_test_sheriff(perception=8)
    """
    from core.players.sheriff import Sheriff
    
    return Sheriff(perception=perception, reputation=reputation)


def create_test_goods(good_type="legal", count=3):
    """
    Create a list of test goods.
    
    Args:
        good_type: Type of goods - "legal", "contraband", or "mixed" (default "legal")
        count: Number of goods (default 3)
    
    Returns:
        List of Good instances
    
    Usage:
        goods = create_test_goods("contraband", 2)
    """
    from core.mechanics.goods import APPLE, CHEESE, SILK, PEPPER
    
    if good_type == "legal":
        return [APPLE] * count
    elif good_type == "contraband":
        return [SILK] * count
    elif good_type == "mixed":
        # Alternate between legal and contraband
        result = []
        for i in range(count):
            result.append(APPLE if i % 2 == 0 else SILK)
        return result
    else:
        raise ValueError(f"Unknown good_type: {good_type}")


def create_test_declaration(good_id="apple", count=3):
    """
    Create a test Declaration.
    
    Args:
        good_id: ID of the good being declared (default "apple")
        count: Number of goods declared (default 3)
    
    Returns:
        Declaration instance
    
    Usage:
        declaration = create_test_declaration("silk", 5)
    """
    from core.game.rounds import Declaration
    
    return Declaration(good_id=good_id, count=count)


def create_test_round_state(merchant=None, bag_actual=None):
    """
    Create a test RoundState.
    
    Args:
        merchant: Merchant instance (creates default if None)
        bag_actual: List of goods in bag (creates default if None)
    
    Returns:
        RoundState instance
    
    Usage:
        rs = create_test_round_state()
    """
    from core.game.rounds import RoundState
    
    if merchant is None:
        merchant = create_test_merchant()
    
    if bag_actual is None:
        bag_actual = create_test_goods("legal", 3)
    
    return RoundState(merchant=merchant, bag_actual=bag_actual)


# ============================================================================
# Mock Data Helpers
# ============================================================================

def create_mock_merchant_json(
    merchant_id="test",
    name="Test Merchant",
    bluff_skill=5,
    role=None
):
    """
    Create mock merchant JSON data for testing merchant loading.
    
    Args:
        merchant_id: Merchant ID
        name: Merchant name
        bluff_skill: Bluff skill level
        role: Special role (e.g., "broker") or None
    
    Returns:
        Dictionary representing merchant JSON data
    
    Usage:
        data = create_mock_merchant_json("alice", "Alice Baker", bluff_skill=6)
    """
    return {
        "id": merchant_id,
        "name": name,
        "intro": f"Introduction for {name}",
        "tells_honest": ["calm", "steady"],
        "tells_lying": ["nervous", "fidgety"],
        "bluff_skill": bluff_skill,
        "role": role
    }


# ============================================================================
# Assertion Helpers
# ============================================================================

def assert_merchant_properties(merchant, expected_name=None, expected_bluff=None, expected_gold=None):
    """
    Assert common merchant properties.
    
    Args:
        merchant: Merchant instance to check
        expected_name: Expected name (optional)
        expected_bluff: Expected bluff skill (optional)
        expected_gold: Expected gold amount (optional)
    
    Usage:
        assert_merchant_properties(merchant, expected_name="Alice", expected_bluff=6)
    """
    if expected_name is not None:
        assert merchant.name == expected_name, f"Expected name {expected_name}, got {merchant.name}"
    
    if expected_bluff is not None:
        assert merchant.bluff_skill == expected_bluff, f"Expected bluff {expected_bluff}, got {merchant.bluff_skill}"
    
    if expected_gold is not None:
        assert merchant.gold == expected_gold, f"Expected gold {expected_gold}, got {merchant.gold}"


def assert_inspection_result(result, expected_honest=None, expected_caught=None):
    """
    Assert inspection result properties.
    
    Args:
        result: Inspection result dictionary
        expected_honest: Expected was_honest value (optional)
        expected_caught: Expected caught_lie value (optional)
    
    Usage:
        assert_inspection_result(result, expected_honest=True, expected_caught=False)
    """
    assert result is not None, "Inspection result should not be None"
    
    if expected_honest is not None:
        assert result['was_honest'] == expected_honest, \
            f"Expected was_honest={expected_honest}, got {result['was_honest']}"
    
    if expected_caught is not None:
        assert result['caught_lie'] == expected_caught, \
            f"Expected caught_lie={expected_caught}, got {result['caught_lie']}"
    
    # Verify required keys exist
    assert 'goods_passed' in result
    assert 'goods_confiscated' in result


# ============================================================================
# Fixture Helpers
# ============================================================================

def setup_pygame_test():
    """
    Setup function for pygame tests.
    Call at the beginning of test functions that use pygame.
    
    Returns:
        Tuple of (pygame initialized, mock_window)
    
    Usage:
        def test_something():
            pygame_init, mock_window = setup_pygame_test()
            # ... test code ...
            teardown_pygame_test()
    """
    pygame.init()
    mock_window = create_mock_pygame_window()
    return True, mock_window


def teardown_pygame_test():
    """
    Teardown function for pygame tests.
    Call at the end of test functions that use pygame.
    
    Usage:
        def test_something():
            setup_pygame_test()
            # ... test code ...
            teardown_pygame_test()
    """
    pygame.quit()
