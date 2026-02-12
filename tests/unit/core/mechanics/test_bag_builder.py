"""
Unit tests for core/mechanics/bag_builder.py
Tests bag and declaration creation logic
"""

# Must be first import - sets up test environment
import os
from unittest.mock import Mock, patch

import tests.test_setup  # noqa: F401

# Setup headless mode
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"


from core.mechanics.bag_builder import build_bag_and_declaration, choose_tell


class TestBuildBagAndDeclaration:
    """Tests for build_bag_and_declaration function"""

    @patch("core.mechanics.bag_builder.GOOD_BY_ID")
    def test_build_bag_honest_merchant(self, mock_goods):
        """Test building bag for honest merchant"""
        mock_merchant = Mock()
        mock_merchant.choose_declaration.return_value = {
            "declared_id": "apple",
            "count": 3,
            "actual_ids": ["apple", "apple", "apple"],
            "lie": False,
        }

        mock_good = Mock()
        mock_good.id = "apple"
        mock_goods.__getitem__.return_value = mock_good

        declaration, actual_goods, is_honest = build_bag_and_declaration(mock_merchant)

        assert declaration.good_id == "apple"
        assert declaration.count == 3
        assert len(actual_goods) == 3
        assert is_honest is True
        mock_merchant.choose_declaration.assert_called_once_with(None)

    @patch("core.mechanics.bag_builder.GOOD_BY_ID")
    def test_build_bag_lying_merchant(self, mock_goods):
        """Test building bag for lying merchant"""
        mock_merchant = Mock()
        mock_merchant.choose_declaration.return_value = {
            "declared_id": "cheese",
            "count": 2,
            "actual_ids": ["cheese", "silk"],  # Silk is contraband
            "lie": True,
        }

        mock_cheese = Mock()
        mock_cheese.id = "cheese"
        mock_silk = Mock()
        mock_silk.id = "silk"

        def get_good(good_id):
            return mock_cheese if good_id == "cheese" else mock_silk

        mock_goods.__getitem__.side_effect = get_good

        declaration, actual_goods, is_honest = build_bag_and_declaration(mock_merchant)

        assert declaration.good_id == "cheese"
        assert declaration.count == 2
        assert len(actual_goods) == 2
        assert is_honest is False

    @patch("core.mechanics.bag_builder.GOOD_BY_ID")
    def test_build_bag_with_history(self, mock_goods):
        """Test building bag with encounter history"""
        mock_merchant = Mock()
        mock_merchant.choose_declaration.return_value = {
            "declared_id": "bread",
            "count": 1,
            "actual_ids": ["bread"],
            "lie": False,
        }

        mock_good = Mock()
        mock_goods.__getitem__.return_value = mock_good

        history = [
            {
                "declaration": {"good_id": "apple", "count": 2},
                "opened": True,
                "caught_lie": False,
            }
        ]

        declaration, actual_goods, is_honest = build_bag_and_declaration(
            mock_merchant, history
        )

        mock_merchant.choose_declaration.assert_called_once_with(history)
        assert is_honest is True

    @patch("core.mechanics.bag_builder.GOOD_BY_ID")
    def test_build_bag_different_counts(self, mock_goods):
        """Test building bags with different item counts"""
        mock_merchant = Mock()

        mock_good = Mock()
        mock_goods.__getitem__.return_value = mock_good

        # Test with 1 item
        mock_merchant.choose_declaration.return_value = {
            "declared_id": "apple",
            "count": 1,
            "actual_ids": ["apple"],
            "lie": False,
        }

        declaration, actual_goods, is_honest = build_bag_and_declaration(mock_merchant)
        assert len(actual_goods) == 1

        # Test with 5 items
        mock_merchant.choose_declaration.return_value = {
            "declared_id": "cheese",
            "count": 5,
            "actual_ids": ["cheese"] * 5,
            "lie": False,
        }

        declaration, actual_goods, is_honest = build_bag_and_declaration(mock_merchant)
        assert len(actual_goods) == 5


class TestChooseTell:
    """Tests for choose_tell function"""

    def test_choose_tell_honest(self):
        """Test choosing tell for honest merchant"""
        mock_merchant = Mock()
        mock_merchant.tells_honest = ["calm demeanor", "steady voice"]
        mock_merchant.tells_lying = ["fidgets", "avoids eye contact"]

        tell = choose_tell(mock_merchant, is_honest=True)

        assert tell in mock_merchant.tells_honest

    def test_choose_tell_lying(self):
        """Test choosing tell for lying merchant"""
        mock_merchant = Mock()
        mock_merchant.tells_honest = ["calm demeanor"]
        mock_merchant.tells_lying = ["nervous", "sweating"]

        tell = choose_tell(mock_merchant, is_honest=False)

        assert tell in mock_merchant.tells_lying

    def test_choose_tell_empty_honest_list(self):
        """Test choosing tell when honest list is empty"""
        mock_merchant = Mock()
        mock_merchant.tells_honest = []
        mock_merchant.tells_lying = ["nervous"]

        tell = choose_tell(mock_merchant, is_honest=True)

        assert tell == ""

    def test_choose_tell_empty_lying_list(self):
        """Test choosing tell when lying list is empty"""
        mock_merchant = Mock()
        mock_merchant.tells_honest = ["calm"]
        mock_merchant.tells_lying = []

        tell = choose_tell(mock_merchant, is_honest=False)

        assert tell == ""

    def test_choose_tell_single_item(self):
        """Test choosing tell with single item in list"""
        mock_merchant = Mock()
        mock_merchant.tells_honest = ["only one tell"]
        mock_merchant.tells_lying = ["only lying tell"]

        tell_honest = choose_tell(mock_merchant, is_honest=True)
        tell_lying = choose_tell(mock_merchant, is_honest=False)

        assert tell_honest == "only one tell"
        assert tell_lying == "only lying tell"

    def test_choose_tell_randomness(self):
        """Test that choose_tell can return different values"""
        mock_merchant = Mock()
        mock_merchant.tells_honest = ["tell1", "tell2", "tell3"]
        mock_merchant.tells_lying = ["lie1", "lie2"]

        # Get multiple tells
        tells = [choose_tell(mock_merchant, is_honest=True) for _ in range(10)]

        # All should be from honest list
        assert all(tell in mock_merchant.tells_honest for tell in tells)
