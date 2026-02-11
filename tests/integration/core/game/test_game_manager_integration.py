"""
Integration tests extracted from test_game_manager_complete.py
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from core.game.game_manager import run_game
from core.game.rounds import Declaration
from core.mechanics.goods import APPLE


class TestRunGameIntegration:
    """Integration tests for run_game"""
    
    @patch('core.game.game_manager.GOOD_BY_ID', {'apple': Mock(id='apple', value=5)})
    @patch('core.game.game_manager.record_encounter')
    @patch('core.game.game_manager.process_pass_without_inspection')
    @patch('core.game.game_manager.prompt_initial_decision')
    @patch('core.game.game_manager.show_declaration')
    @patch('core.game.game_manager.choose_tell')
    @patch('core.game.game_manager.build_bag_and_declaration')
    @patch('core.game.game_manager.narrate_arrival')
    @patch('core.game.game_manager.update_stats_bar')
    @patch('core.game.game_manager.show_end_game_summary')
    @patch('core.game.game_manager.get_game_master_state')
    @patch('core.game.game_manager.reset_game_master_state')
    @patch('core.game.game_manager.load_merchants')
    @patch('core.game.game_manager.print_intro')
    def test_run_game_multiple_merchants(self, mock_intro, mock_load, mock_reset, mock_get_state,
                                        mock_summary, mock_update, mock_narrate, mock_build,
                                        mock_choose_tell, mock_show_decl, mock_prompt,
                                        mock_process_pass, mock_record):
        """Test run_game with multiple merchants"""
        # Setup 3 merchants
        merchants = [Mock(name=f"Merchant{i}", should_offer_proactive_bribe=Mock(return_value=False)) for i in range(3)]
        mock_load.return_value = merchants
        
        mock_game_state = Mock()
        mock_get_state.return_value = mock_game_state
        
        mock_declaration = Mock()
        mock_declaration.good_id = "apple"
        mock_declaration.count = 2
        mock_goods = []
        mock_build.return_value = (mock_declaration, mock_goods, True)
        
        mock_choose_tell.return_value = ""
        mock_prompt.return_value = 'pass'
        mock_process_pass.return_value = (True, False)
        
        # Run game
        with patch('core.game.game_manager.update_sheriff_reputation'):
            run_game()
        
        # Verify all merchants were processed
        assert mock_narrate.call_count == 3
        assert mock_build.call_count == 3
        assert mock_process_pass.call_count == 3
        assert mock_record.call_count == 3
        mock_summary.assert_called_once()
