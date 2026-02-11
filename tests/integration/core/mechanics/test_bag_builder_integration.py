"""
Integration tests extracted from test_bag_builder.py
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from core.mechanics.bag_builder import build_bag_and_declaration, choose_tell


class TestBagBuilderIntegration:
    """Integration tests for bag_builder module"""
    
    @patch('core.mechanics.bag_builder.GOOD_BY_ID')
    def test_full_merchant_encounter_flow(self, mock_goods):
        """Test complete flow of building bag and choosing tell"""
        mock_merchant = Mock()
        mock_merchant.choose_declaration.return_value = {
            'declared_id': 'apple',
            'count': 2,
            'actual_ids': ['apple', 'silk'],
            'lie': True
        }
        mock_merchant.tells_honest = ["calm"]
        mock_merchant.tells_lying = ["nervous", "fidgets"]
        
        mock_apple = Mock()
        mock_silk = Mock()
        mock_goods.__getitem__.side_effect = lambda x: mock_apple if x == 'apple' else mock_silk
        
        # Build bag
        declaration, actual_goods, is_honest = build_bag_and_declaration(mock_merchant)
        
        # Choose tell
        tell = choose_tell(mock_merchant, is_honest)
        
        assert declaration.good_id == 'apple'
        assert len(actual_goods) == 2
        assert is_honest is False
        assert tell in mock_merchant.tells_lying
