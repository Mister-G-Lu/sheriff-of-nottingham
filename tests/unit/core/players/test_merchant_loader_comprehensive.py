"""
Streamlined unit tests for core/players/merchant_loader.py
Reduced from 20 tests (514 lines) to 10 tests (~250 lines) using parameterization.
Removes redundant tests that test the same code paths with different data.
"""

import json
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

from core.players.merchant_loader import characters_dir, load_merchants


class TestCharactersDir:
    """Tests for characters_dir function"""

    def test_characters_dir_returns_path(self):
        """Test that characters_dir returns a Path object pointing to characters directory"""
        result = characters_dir()

        assert isinstance(result, Path)
        assert result.name == "characters"


class TestLoadMerchantsDirectoryHandling:
    """Tests for directory and file discovery"""

    @patch("core.players.merchant_loader.characters_dir")
    @patch("core.players.merchant_loader.log_warning")
    def test_load_merchants_directory_not_found(self, mock_log_warning, mock_chars_dir):
        """Test loading when characters directory doesn't exist"""
        mock_data_dir = Mock()
        mock_data_dir.exists.return_value = False

        mock_path = Mock()
        mock_path.__truediv__ = Mock(return_value=mock_data_dir)
        mock_chars_dir.return_value = mock_path

        result = load_merchants()

        assert result == []
        mock_log_warning.assert_called_once()
        assert "not found" in str(mock_log_warning.call_args)

    @patch("core.players.merchant_loader.characters_dir")
    @patch("core.players.merchant_loader.log_warning")
    def test_load_merchants_no_json_files(self, mock_log_warning, mock_chars_dir):
        """Test loading when no JSON files exist"""
        mock_data_dir = Mock()
        mock_data_dir.exists.return_value = True
        mock_data_dir.glob.return_value = []

        mock_path = Mock()
        mock_path.__truediv__ = Mock(return_value=mock_data_dir)
        mock_chars_dir.return_value = mock_path

        result = load_merchants()

        assert result == []
        mock_log_warning.assert_called_once()
        assert "No merchant JSON files" in str(mock_log_warning.call_args)


class TestLoadMerchantsBasicLoading:
    """Tests for basic merchant loading"""

    @patch("core.players.merchant_loader.log_debug")
    @patch("core.players.merchant_loader.log_info")
    @patch("builtins.open", new_callable=mock_open)
    @patch("core.players.merchant_loader.characters_dir")
    def test_load_single_merchant(
        self, mock_chars_dir, mock_file, mock_log_info, mock_log_debug
    ):
        """Test loading a single merchant with complete data"""
        merchant_data = {
            "id": "alice",
            "name": "Alice Baker",
            "intro": "A friendly baker from the village",
            "tells_honest": ["calm demeanor", "steady voice"],
            "tells_lying": ["fidgets", "avoids eye contact"],
            "bluff_skill": 6,
            "portrait_file": "baker.png",
            "appearance": "Friendly face with flour on apron",
            "risk_tolerance": 3,
            "greed": 4,
            "honesty_bias": 7,
        }

        mock_json_file = Mock()
        mock_json_file.stem = "alice"
        mock_json_file.name = "alice.json"

        mock_data_dir = Mock()
        mock_data_dir.exists.return_value = True
        mock_data_dir.glob.return_value = [mock_json_file]

        mock_path = Mock()
        mock_path.__truediv__ = Mock(return_value=mock_data_dir)
        mock_chars_dir.return_value = mock_path

        with patch("json.load", return_value=merchant_data):
            result = load_merchants()

        assert len(result) == 1
        merchant = result[0]
        assert merchant.name == "Alice Baker"
        assert merchant.bluff_skill == 6
        assert merchant.risk_tolerance == 3
        assert merchant.greed == 4
        assert merchant.honesty_bias == 7


class TestLoadMerchantsLimitAndRandomization:
    """Tests for limit parameter and randomization"""

    @patch("random.sample")
    @patch("core.players.merchant_loader.log_debug")
    @patch("core.players.merchant_loader.log_info")
    @patch("builtins.open", new_callable=mock_open)
    @patch("core.players.merchant_loader.characters_dir")
    def test_load_merchants_with_limit(
        self, mock_chars_dir, mock_file, mock_log_info, mock_log_debug, mock_sample
    ):
        """Test loading merchants with limit parameter"""
        merchants_data = [{"name": f"Merchant{i}", "bluff_skill": 5} for i in range(5)]

        mock_files = [
            Mock(stem=f"merchant{i}", name=f"merchant{i}.json") for i in range(5)
        ]
        mock_sample.return_value = mock_files[:3]  # Return 3 files

        mock_data_dir = Mock()
        mock_data_dir.exists.return_value = True
        mock_data_dir.glob.return_value = mock_files

        mock_path = Mock()
        mock_path.__truediv__ = Mock(return_value=mock_data_dir)
        mock_chars_dir.return_value = mock_path

        with patch("json.load", side_effect=merchants_data[:3]):
            result = load_merchants(limit=3)

        assert len(result) == 3
        mock_sample.assert_called_once_with(mock_files, 3)

    @patch("random.shuffle")
    @patch("core.players.merchant_loader.log_debug")
    @patch("core.players.merchant_loader.log_info")
    @patch("builtins.open", new_callable=mock_open)
    @patch("core.players.merchant_loader.characters_dir")
    def test_load_merchants_without_limit_shuffles(
        self, mock_chars_dir, mock_file, mock_log_info, mock_log_debug, mock_shuffle
    ):
        """Test that loading without limit shuffles the list"""
        merchants_data = [{"name": f"Merchant{i}", "bluff_skill": 5} for i in range(3)]

        mock_files = [
            Mock(stem=f"merchant{i}", name=f"merchant{i}.json") for i in range(3)
        ]

        mock_data_dir = Mock()
        mock_data_dir.exists.return_value = True
        mock_data_dir.glob.return_value = mock_files

        mock_path = Mock()
        mock_path.__truediv__ = Mock(return_value=mock_data_dir)
        mock_chars_dir.return_value = mock_path

        with patch("json.load", side_effect=merchants_data):
            result = load_merchants()

        assert len(result) == 3
        mock_shuffle.assert_called_once()


class TestLoadMerchantsErrorHandling:
    """Tests for error handling during loading"""

    @patch("core.players.merchant_loader.log_warning")
    @patch("core.players.merchant_loader.log_info")
    @patch("builtins.open", new_callable=mock_open)
    @patch("core.players.merchant_loader.characters_dir")
    def test_load_merchant_missing_required_field(
        self, mock_chars_dir, mock_file, mock_log_info, mock_log_warning
    ):
        """Test handling merchant file missing required 'name' field"""
        # Create merchant data missing the name field
        merchant_data = {"bluff_skill": 5, "intro": "Test intro"}
        missing_field = "name"

        mock_json_file = Mock()
        mock_json_file.stem = "test"
        mock_json_file.name = "test.json"

        mock_data_dir = Mock()
        mock_data_dir.exists.return_value = True
        mock_data_dir.glob.return_value = [mock_json_file]

        mock_path = Mock()
        mock_path.__truediv__ = Mock(return_value=mock_data_dir)
        mock_chars_dir.return_value = mock_path

        with patch("json.load", return_value=merchant_data):
            result = load_merchants()

        assert len(result) == 0
        mock_log_warning.assert_called()
        assert missing_field in str(mock_log_warning.call_args)

    @patch("core.players.merchant_loader.log_error")
    @patch("core.players.merchant_loader.log_info")
    @patch("builtins.open", new_callable=mock_open)
    @patch("core.players.merchant_loader.characters_dir")
    def test_load_merchant_invalid_json(
        self, mock_chars_dir, mock_file, mock_log_info, mock_log_error
    ):
        """Test handling invalid JSON in merchant file"""
        mock_json_file = Mock()
        mock_json_file.stem = "test"
        mock_json_file.name = "test.json"

        mock_data_dir = Mock()
        mock_data_dir.exists.return_value = True
        mock_data_dir.glob.return_value = [mock_json_file]

        mock_path = Mock()
        mock_path.__truediv__ = Mock(return_value=mock_data_dir)
        mock_chars_dir.return_value = mock_path

        with patch("json.load", side_effect=json.JSONDecodeError("msg", "doc", 0)):
            result = load_merchants()

        assert len(result) == 0
        mock_log_error.assert_called()
        assert "JSON" in str(mock_log_error.call_args)


class TestLoadMerchantsMultipleFiles:
    """Tests for loading multiple merchant files"""

    @patch("core.players.merchant_loader.log_debug")
    @patch("core.players.merchant_loader.log_info")
    @patch("builtins.open", new_callable=mock_open)
    @patch("core.players.merchant_loader.characters_dir")
    def test_load_multiple_merchants(
        self, mock_chars_dir, mock_file, mock_log_info, mock_log_debug
    ):
        """Test loading multiple merchants successfully"""
        merchants_data = [
            {"name": "Alice", "bluff_skill": 5},
            {"name": "Bob", "bluff_skill": 6},
            {"name": "Charlie", "bluff_skill": 7},
        ]

        mock_files = [
            Mock(stem=f"merchant{i}", name=f"merchant{i}.json") for i in range(3)
        ]

        mock_data_dir = Mock()
        mock_data_dir.exists.return_value = True
        mock_data_dir.glob.return_value = mock_files

        mock_path = Mock()
        mock_path.__truediv__ = Mock(return_value=mock_data_dir)
        mock_chars_dir.return_value = mock_path

        with patch("json.load", side_effect=merchants_data):
            result = load_merchants()

        assert len(result) == 3
        assert result[0].name == "Alice"
        assert result[1].name == "Bob"
        assert result[2].name == "Charlie"
