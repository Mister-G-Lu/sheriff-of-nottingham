"""
Comprehensive unit tests for core/game/game_manager.py
Target: 80%+ coverage
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call

# Path setup and headless mode handled by tests/conftest.py
from core.game.game_manager import (
    process_proactive_bribe,
    process_pass_without_inspection,
    display_inspection_results,
    process_inspection,
    record_encounter,
    run_game
)

class TestProcessProactiveBribe:
    """Tests for process_proactive_bribe function"""
    
    @patch('core.game.game_manager.show_bribe_accepted_status')
    @patch('core.game.game_manager.update_stats_bar')
    @patch('builtins.print')
    def test_process_proactive_bribe_updates_state(self, mock_print, mock_update_stats, mock_show_status):
        """Test that proactive bribe updates sheriff and stats"""
        merchant = Mock()
        sheriff = Mock()
        sheriff.reputation = 5
        stats = Mock()
        
        process_proactive_bribe(merchant, 50, sheriff, stats, 1, 10)
        
        stats.record_bribe.assert_called_once_with(50)
        assert sheriff.reputation == 4  # Decreased by 1
        mock_show_status.assert_called_once_with(50, 4)
        mock_update_stats.assert_called_once_with(sheriff, stats, 1, 10)
    
    @patch('core.game.game_manager.show_bribe_accepted_status')
    @patch('core.game.game_manager.update_stats_bar')
    def test_process_proactive_bribe_reputation_floor(self, mock_update_stats, mock_show_status):
        """Test that reputation doesn't go below 0"""
        merchant = Mock()
        sheriff = Mock()
        sheriff.reputation = 0
        stats = Mock()
        
        process_proactive_bribe(merchant, 30, sheriff, stats, 1, 10)
        
        assert sheriff.reputation == 0  # Stays at 0

class TestProcessPassWithoutInspection:
    """Tests for process_pass_without_inspection function"""
    
    @patch('core.game.game_manager.show_merchant_sold_goods')
    @patch('core.game.game_manager.show_inspection_result')
    @patch('core.game.game_manager.handle_pass_without_inspection')
    def test_pass_honest_merchant(self, mock_handle_pass, mock_show_result, mock_show_sold):
        """Test passing honest merchant without inspection"""
        merchant = Mock()
        merchant.name = "Alice"
        merchant.gold = 100
        
        mock_good = Mock()
        mock_good.value = 10
        actual_goods = [mock_good, mock_good]
        
        declaration = Mock()
        declaration.good_id = "apple"
        declaration.count = 2
        
        stats = Mock()
        
        mock_handle_pass.return_value = {
            'was_honest': True,
            'caught_lie': False,
            'goods_passed': actual_goods,
            'goods_confiscated': [],
            'penalty_paid': 0,
            'sheriff_gold_gained': 0
        }
        
        was_honest, caught_lie = process_pass_without_inspection(merchant, actual_goods, declaration, stats)
        
        assert was_honest is True
        assert caught_lie is False
        assert merchant.gold == 120  # 100 + (2 * 10)
        stats.record_pass.assert_called_once_with(True)
        mock_show_result.assert_called_once_with(merchant, False, False)
        mock_show_sold.assert_called_once_with("Alice", 20, 120)
    
    @patch('core.game.game_manager.show_merchant_sold_goods')
    @patch('core.game.game_manager.show_inspection_result')
    @patch('core.game.game_manager.handle_pass_without_inspection')
    def test_pass_lying_merchant(self, mock_handle_pass, mock_show_result, mock_show_sold):
        """Test passing lying merchant without inspection"""
        merchant = Mock()
        merchant.name = "Bob"
        merchant.gold = 50
        
        mock_good = Mock()
        mock_good.value = 15
        actual_goods = [mock_good]
        
        declaration = Mock()
        stats = Mock()
        
        mock_handle_pass.return_value = {
            'was_honest': False,
            'caught_lie': False,
            'goods_passed': actual_goods,
            'goods_confiscated': [],
            'penalty_paid': 0,
            'sheriff_gold_gained': 0
        }
        
        was_honest, caught_lie = process_pass_without_inspection(merchant, actual_goods, declaration, stats)
        
        assert was_honest is False
        assert caught_lie is False
        assert merchant.gold == 65  # 50 + 15
        stats.record_pass.assert_called_once_with(False)

class TestDisplayInspectionResults:
    """Tests for display_inspection_results function"""
    
    @patch('core.game.game_manager.show_inspection_footer')
    @patch('core.game.game_manager.show_bluff_succeeded')
    @patch('core.game.game_manager.show_bag_contents')
    @patch('core.game.game_manager.show_inspection_header')
    def test_display_bluff_succeeded(self, mock_header, mock_contents, mock_bluff, mock_footer):
        """Test displaying results when bluff succeeded"""
        merchant = Mock()
        merchant.name = "Charlie"
        merchant.gold = 100
        
        declaration = Mock()
        declaration.count = 3
        declaration.good_id = "cheese"
        
        mock_good = Mock()
        mock_good.value = 8
        actual_goods = [mock_good, mock_good, mock_good]
        
        result = {
            'was_honest': False,
            'caught_lie': False,
            'goods_passed': actual_goods,
            'goods_confiscated': [],
            'penalty_paid': 0,
            'sheriff_gold_gained': 0
        }
        
        display_inspection_results(merchant, declaration, actual_goods, result)
        
        mock_header.assert_called_once_with("Charlie", 3, "cheese")
        mock_contents.assert_called_once_with(actual_goods)
        mock_bluff.assert_called_once_with("Charlie", 24, 124)
        mock_footer.assert_called_once()
        assert merchant.gold == 124
    
    @patch('core.game.game_manager.show_inspection_footer')
    @patch('core.game.game_manager.show_honest_verdict')
    @patch('core.game.game_manager.show_bag_contents')
    @patch('core.game.game_manager.show_inspection_header')
    def test_display_honest_verdict(self, mock_header, mock_contents, mock_honest, mock_footer):
        """Test displaying results for honest merchant"""
        merchant = Mock()
        merchant.name = "Diana"
        merchant.gold = 80
        
        declaration = Mock()
        declaration.count = 2
        declaration.good_id = "bread"
        
        mock_good = Mock()
        mock_good.value = 5
        actual_goods = [mock_good, mock_good]
        
        result = {
            'was_honest': True,
            'caught_lie': False,
            'goods_passed': actual_goods,
            'goods_confiscated': [],
            'penalty_paid': 0,
            'sheriff_gold_gained': 0
        }
        
        display_inspection_results(merchant, declaration, actual_goods, result)
        
        mock_header.assert_called_once()
        mock_contents.assert_called_once()
        mock_honest.assert_called_once_with(2, 10, "Diana", 90)
        mock_footer.assert_called_once()
        assert merchant.gold == 90
    
    @patch('core.game.game_manager.show_inspection_footer')
    @patch('core.game.game_manager.show_lying_verdict')
    @patch('core.game.game_manager.show_bag_contents')
    @patch('core.game.game_manager.show_inspection_header')
    def test_display_lying_verdict(self, mock_header, mock_contents, mock_lying, mock_footer):
        """Test displaying results for lying merchant caught"""
        merchant = Mock()
        merchant.name = "Eve"
        merchant.gold = 60
        
        declaration = Mock()
        actual_goods = []
        
        mock_passed = Mock()
        mock_passed.value = 5
        mock_confiscated = Mock()
        mock_confiscated.value = 10
        
        result = {
            'was_honest': False,
            'caught_lie': True,
            'goods_passed': [mock_passed],
            'goods_confiscated': [mock_confiscated],
            'penalty_paid': 5,
            'sheriff_gold_gained': 5
        }
        
        display_inspection_results(merchant, declaration, actual_goods, result)
        
        mock_lying.assert_called_once()
        assert merchant.gold == 65  # 60 + 5 from passed goods

class TestProcessInspection:
    """Tests for process_inspection function"""
    
    @patch('core.game.game_manager.update_sheriff_reputation')
    @patch('core.game.game_manager.display_inspection_results')
    @patch('core.game.game_manager.show_inspection_result')
    @patch('core.game.game_manager.handle_inspection')
    def test_process_inspection_honest(self, mock_handle, mock_show_result, mock_display, mock_update_rep):
        """Test inspecting honest merchant"""
        merchant = Mock()
        actual_goods = []
        declaration = Mock()
        sheriff = Mock()
        stats = Mock()
        
        mock_handle.return_value = {
            'was_honest': True,
            'caught_lie': False,
            'goods_passed': actual_goods,
            'goods_confiscated': [],
            'penalty_paid': 0,
            'sheriff_gold_gained': 0
        }
        
        was_honest, caught_lie = process_inspection(merchant, actual_goods, declaration, sheriff, stats)
        
        assert was_honest is True
        assert caught_lie is False
        stats.record_inspection.assert_called_once_with(True, False)
        mock_show_result.assert_called_once_with(merchant, True, False)
        mock_display.assert_called_once()
        mock_update_rep.assert_called_once()
    
    @patch('core.game.game_manager.update_sheriff_reputation')
    @patch('core.game.game_manager.display_inspection_results')
    @patch('core.game.game_manager.show_inspection_result')
    @patch('core.game.game_manager.handle_inspection')
    def test_process_inspection_caught_lying(self, mock_handle, mock_show_result, mock_display, mock_update_rep):
        """Test inspecting and catching lying merchant"""
        merchant = Mock()
        actual_goods = []
        declaration = Mock()
        sheriff = Mock()
        stats = Mock()
        
        mock_handle.return_value = {
            'was_honest': False,
            'caught_lie': True,
            'goods_passed': [],
            'goods_confiscated': actual_goods,
            'penalty_paid': 10,
            'sheriff_gold_gained': 10
        }
        
        was_honest, caught_lie = process_inspection(merchant, actual_goods, declaration, sheriff, stats)
        
        assert was_honest is False
        assert caught_lie is True
        stats.record_inspection.assert_called_once_with(False, True)

class TestRecordEncounter:
    """Tests for record_encounter function"""
    
    def test_record_encounter_basic(self):
        """Test recording encounter in game state"""
        game_state = Mock()
        merchant = Mock()
        merchant.name = "Frank"
        
        declaration = Mock()
        declaration.good_id = "apple"
        declaration.count = 3
        
        mock_good = Mock()
        mock_good.id = "apple"
        actual_goods = [mock_good, mock_good, mock_good]
        
        bribe_info = {'amount': 0, 'accepted': False, 'proactive': False}
        
        record_encounter(game_state, merchant, declaration, actual_goods, True, False, bribe_info)
        
        game_state.record_event.assert_called_once()
        call_args = game_state.record_event.call_args[1]
        assert call_args['merchant_name'] == "Frank"
        assert call_args['declared_good'] == "apple"
        assert call_args['declared_count'] == 3
        assert call_args['was_opened'] is True
        assert call_args['caught_lie'] is False
    
    def test_record_encounter_with_bribe(self):
        """Test recording encounter with bribe"""
        game_state = Mock()
        merchant = Mock()
        merchant.name = "Grace"
        
        declaration = Mock()
        declaration.good_id = "cheese"
        declaration.count = 2
        
        actual_goods = []
        bribe_info = {'amount': 50, 'accepted': True, 'proactive': True}
        
        record_encounter(game_state, merchant, declaration, actual_goods, False, False, bribe_info)
        
        call_args = game_state.record_event.call_args[1]
        assert call_args['bribe_offered'] == 50
        assert call_args['bribe_accepted'] is True
        assert call_args['proactive_bribe'] is True

class TestRunGame:
    """Tests for run_game main loop"""
    
    @patch('core.game.game_manager.show_end_game_summary')
    @patch('core.game.game_manager.update_stats_bar')
    @patch('core.game.game_manager.load_merchants')
    @patch('core.game.game_manager.print_intro')
    @patch('core.game.game_manager.reset_game_master_state')
    def test_run_game_no_merchants(self, mock_reset, mock_intro, mock_load, mock_update, mock_summary):
        """Test run_game when no merchants are found"""
        mock_load.return_value = []
        
        with patch('builtins.print') as mock_print:
            run_game()
        
        mock_intro.assert_called_once()
        mock_load.assert_called_once_with(limit=8)
        # Should print error message
        assert any("No merchants found" in str(call) for call in mock_print.call_args_list)
        # Should not call end game summary
        mock_summary.assert_not_called()
    
    @patch('core.game.game_manager.record_encounter')
    @patch('core.game.game_manager.process_pass_without_inspection')
    @patch('core.game.game_manager.prompt_initial_decision')
    @patch('core.game.game_manager.show_proactive_bribe')
    @patch('core.game.game_manager.show_declaration')
    @patch('core.game.game_manager.show_tell')
    @patch('core.game.game_manager.choose_tell')
    @patch('core.game.game_manager.build_bag_and_declaration')
    @patch('core.game.game_manager.narrate_arrival')
    @patch('core.game.game_manager.update_stats_bar')
    @patch('core.game.game_manager.show_end_game_summary')
    @patch('core.game.game_manager.get_game_master_state')
    @patch('core.game.game_manager.reset_game_master_state')
    @patch('core.game.game_manager.load_merchants')
    @patch('core.game.game_manager.print_intro')
    def test_run_game_pass_decision(self, mock_intro, mock_load, mock_reset, mock_get_state,
                                    mock_summary, mock_update, mock_narrate, mock_build,
                                    mock_choose_tell, mock_show_tell, mock_show_decl,
                                    mock_show_bribe, mock_prompt, mock_process_pass, mock_record):
        """Test run_game with pass decision"""
        # Setup mocks
        mock_merchant = Mock()
        mock_merchant.name = "Test Merchant"
        mock_merchant.should_offer_proactive_bribe.return_value = False
        mock_load.return_value = [mock_merchant]
        
        mock_game_state = Mock()
        mock_get_state.return_value = mock_game_state
        
        mock_declaration = Mock()
        mock_declaration.good_id = "apple"
        mock_declaration.count = 2
        mock_goods = []
        mock_build.return_value = (mock_declaration, mock_goods, True)
        
        mock_choose_tell.return_value = "calm demeanor"
        mock_prompt.return_value = 'pass'
        mock_process_pass.return_value = (True, False)
        
        # Run game
        with patch('core.game.game_manager.update_sheriff_reputation'):
            run_game()
        
        # Verify flow
        mock_intro.assert_called_once()
        mock_load.assert_called_once_with(limit=8)
        mock_narrate.assert_called_once_with(mock_merchant)
        mock_build.assert_called_once()
        mock_prompt.assert_called_once()
        mock_process_pass.assert_called_once()
        mock_summary.assert_called_once()
    
    @patch('core.game.game_manager.record_encounter')
    @patch('core.game.game_manager.process_inspection')
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
    def test_run_game_inspect_decision(self, mock_intro, mock_load, mock_reset, mock_get_state,
                                       mock_summary, mock_update, mock_narrate, mock_build,
                                       mock_choose_tell, mock_show_decl, mock_prompt,
                                       mock_process_inspect, mock_record):
        """Test run_game with inspect decision"""
        # Setup mocks
        mock_merchant = Mock()
        mock_merchant.name = "Test Merchant"
        mock_merchant.should_offer_proactive_bribe.return_value = False
        mock_load.return_value = [mock_merchant]
        
        mock_game_state = Mock()
        mock_get_state.return_value = mock_game_state
        
        mock_declaration = Mock()
        mock_declaration.good_id = "bread"
        mock_declaration.count = 3
        mock_goods = []
        mock_build.return_value = (mock_declaration, mock_goods, False)
        
        mock_choose_tell.return_value = ""
        mock_prompt.return_value = 'inspect'
        mock_process_inspect.return_value = (False, True)
        
        # Run game
        run_game()
        
        # Verify inspection was called
        mock_process_inspect.assert_called_once()
        mock_record.assert_called_once()
        mock_summary.assert_called_once()
    
    @patch('core.game.game_manager.record_encounter')
    @patch('core.game.game_manager.run_negotiation')
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
    def test_run_game_threaten_bribe_accepted(self, mock_intro, mock_load, mock_reset, mock_get_state,
                                              mock_summary, mock_update, mock_narrate, mock_build,
                                              mock_choose_tell, mock_show_decl, mock_prompt,
                                              mock_process_pass, mock_negotiation, mock_record):
        """Test run_game with threaten decision and bribe accepted"""
        # Setup mocks
        mock_merchant = Mock()
        mock_merchant.name = "Test Merchant"
        mock_merchant.should_offer_proactive_bribe.return_value = False
        mock_load.return_value = [mock_merchant]
        
        mock_game_state = Mock()
        mock_get_state.return_value = mock_game_state
        
        mock_declaration = Mock()
        mock_declaration.good_id = "cheese"
        mock_declaration.count = 1
        mock_goods = []
        mock_build.return_value = (mock_declaration, mock_goods, False)
        
        mock_choose_tell.return_value = ""
        mock_prompt.return_value = 'threaten'
        mock_negotiation.return_value = False  # Bribe accepted
        mock_process_pass.return_value = (False, False)
        
        # Run game
        run_game()
        
        # Verify negotiation was called and bribe accepted
        mock_negotiation.assert_called_once()
        mock_process_pass.assert_called_once()
        mock_summary.assert_called_once()

class TestRunGameProactiveBribe:
    """Tests for run_game with proactive bribe scenarios"""
    
    @patch('core.game.game_manager.record_encounter')
    @patch('core.game.game_manager.process_pass_without_inspection')
    @patch('core.game.game_manager.process_proactive_bribe')
    @patch('core.game.game_manager.prompt_initial_decision')
    @patch('core.game.game_manager.show_proactive_bribe')
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
    def test_run_game_accept_proactive_bribe(self, mock_intro, mock_load, mock_reset, mock_get_state,
                                             mock_summary, mock_update, mock_narrate, mock_build,
                                             mock_choose_tell, mock_show_decl, mock_show_bribe,
                                             mock_prompt, mock_process_bribe, mock_process_pass, mock_record):
        """Test run_game with accepting proactive bribe"""
        # Setup mocks
        mock_merchant = Mock()
        mock_merchant.name = "Test Merchant"
        mock_merchant.should_offer_proactive_bribe.return_value = True
        mock_merchant.calculate_proactive_bribe.return_value = 40
        mock_load.return_value = [mock_merchant]
        
        mock_game_state = Mock()
        mock_get_state.return_value = mock_game_state
        
        mock_declaration = Mock()
        mock_declaration.good_id = "silk"
        mock_declaration.count = 2
        mock_goods = []
        mock_build.return_value = (mock_declaration, mock_goods, False)
        
        mock_choose_tell.return_value = ""
        mock_prompt.return_value = 'accept'
        mock_process_pass.return_value = (False, False)
        
        # Run game
        run_game()
        
        # Verify proactive bribe was shown and accepted
        mock_show_bribe.assert_called_once()
        mock_process_bribe.assert_called_once()
        mock_process_pass.assert_called_once()
        mock_summary.assert_called_once()

