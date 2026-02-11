"""
Integration tests extracted from test_merchant_loader_comprehensive.py
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from core.players.merchant_loader import load_merchants
from core.players.merchants import Merchant, InformationBroker


class TestLoadMerchantsIntegration:
    """Integration tests for merchant loading"""
    
    @patch('core.players.merchant_loader.log_debug')
    @patch('core.players.merchant_loader.log_info')
    @patch('builtins.open', new_callable=mock_open)
    @patch('core.players.merchant_loader.characters_dir')
    def test_complete_loading_workflow(self, mock_chars_dir, mock_file, mock_log_info, mock_log_debug):
        """Test complete merchant loading workflow"""
        merchants_data = [
            {
                "id": "alice",
                "name": "Alice Baker",
                "intro": "A baker",
                "bluff_skill": 5,
                "role": None
            },
            {
                "id": "silas",
                "name": "Silas Voss",
                "intro": "A broker",
                "bluff_skill": 8,
                "role": "broker"
            }
        ]
        
        mock_files = [Mock(stem="alice", name="alice.json"), Mock(stem="silas", name="silas.json")]
        
        mock_data_dir = Mock()
        mock_data_dir.exists.return_value = True
        mock_data_dir.glob.return_value = mock_files
        
        mock_path = Mock()
        mock_path.__truediv__ = Mock(return_value=mock_data_dir)
        mock_chars_dir.return_value = mock_path
        
        with patch('json.load', side_effect=merchants_data):
            result = load_merchants()
        
        assert len(result) == 2
        assert result[0].name == "Alice Baker"
        assert result[0].__class__.__name__ == "Merchant"
        assert result[1].name == "Silas Voss"
        assert result[1].__class__.__name__ == "InformationBroker"
        
        # Verify logging
        assert mock_log_info.call_count >= 2
        assert mock_log_debug.call_count == 2
