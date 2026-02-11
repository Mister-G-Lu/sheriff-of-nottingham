"""
Unit tests for ui/narration.py
Tests narration helper functions.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Setup headless mode before importing pygame modules
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

from ui.narration import (
    narrate_arrival, show_declaration, show_bribe, show_inspection_result,
    show_threat, show_bribe_offer, show_merchant_refuses, show_merchant_gives_up,
    show_bribe_accepted, show_bribe_rejected, show_proactive_bribe,
    prompt_initial_decision, prompt_negotiation_response
)


class TestNarrateArrival:
    """Tests for narrate_arrival function"""
    
    @patch('builtins.print')
    @patch('ui.pygame_ui.get_ui')
    def test_narrate_arrival_with_portrait_file(self, mock_get_ui, mock_print):
        """Test merchant arrival with portrait file"""
        mock_ui = Mock()
        mock_ui.load_portrait_file.return_value = True
        mock_get_ui.return_value = mock_ui
        
        merchant = Mock()
        merchant.name = "Alice"
        merchant.intro = "A friendly baker"
        merchant.portrait_file = "baker.png"
        
        narrate_arrival(merchant)
        
        mock_ui.load_portrait_file.assert_called_once_with("baker.png")
        assert any("Alice" in str(call) for call in mock_print.call_args_list)
    
    @patch('builtins.print')
    @patch('ui.pygame_ui.get_ui')
    def test_narrate_arrival_without_portrait_file(self, mock_get_ui, mock_print):
        """Test merchant arrival without portrait file"""
        mock_ui = Mock()
        mock_get_ui.return_value = mock_ui
        
        merchant = Mock()
        merchant.name = "Bob"
        merchant.intro = "A mysterious trader"
        merchant.portrait_file = None
        
        narrate_arrival(merchant)
        
        mock_ui.load_portrait.assert_called_once_with("Bob")
        assert any("Bob" in str(call) for call in mock_print.call_args_list)
    
    @patch('builtins.print')
    @patch('ui.pygame_ui.get_ui')
    def test_narrate_arrival_portrait_load_failure(self, mock_get_ui, mock_print):
        """Test merchant arrival when portrait fails to load"""
        mock_ui = Mock()
        mock_ui.load_portrait_file.return_value = False
        mock_get_ui.return_value = mock_ui
        
        merchant = Mock()
        merchant.name = "Charlie"
        merchant.intro = "A shady merchant"
        merchant.portrait_file = "missing.png"
        
        narrate_arrival(merchant)
        
        # Should still print narration
        assert any("Charlie" in str(call) for call in mock_print.call_args_list)


class TestShowDeclaration:
    """Tests for show_declaration function"""
    
    @patch('builtins.print')
    def test_show_declaration(self, mock_print):
        """Test showing merchant declaration"""
        merchant = Mock()
        merchant.name = "Alice"
        
        declaration = Mock()
        declaration.count = 3
        declaration.good_id = "cheese"
        
        show_declaration(merchant, declaration)
        
        printed_text = ' '.join(str(call) for call in mock_print.call_args_list)
        assert "Alice" in printed_text
        assert "3" in printed_text
        assert "cheese" in printed_text


class TestShowBribe:
    """Tests for show_bribe function"""
    
    @patch('builtins.print')
    def test_show_bribe_with_offer(self, mock_print):
        """Test showing bribe offer"""
        merchant = Mock()
        merchant.name = "Alice"
        
        show_bribe(merchant, "50 gold")
        
        printed_text = ' '.join(str(call) for call in mock_print.call_args_list)
        assert "Alice" in printed_text
        assert "50 gold" in printed_text
    
    @patch('builtins.print')
    def test_show_bribe_no_offer(self, mock_print):
        """Test showing no bribe"""
        merchant = Mock()
        merchant.name = "Bob"
        
        show_bribe(merchant, "")
        
        printed_text = ' '.join(str(call) for call in mock_print.call_args_list)
        assert "Bob" in printed_text
        assert "no bribe" in printed_text


class TestShowInspectionResult:
    """Tests for show_inspection_result function"""
    
    @patch('builtins.print')
    def test_inspection_caught_contraband(self, mock_print):
        """Test showing inspection that caught contraband"""
        merchant = Mock()
        merchant.name = "Alice"
        
        show_inspection_result(merchant, sheriff_opens=True, caught=True)
        
        printed_text = ' '.join(str(call) for call in mock_print.call_args_list)
        assert "Alice" in printed_text
        assert "contraband" in printed_text
    
    @patch('builtins.print')
    def test_inspection_found_nothing(self, mock_print):
        """Test showing inspection that found nothing"""
        merchant = Mock()
        merchant.name = "Bob"
        
        show_inspection_result(merchant, sheriff_opens=True, caught=False)
        
        printed_text = ' '.join(str(call) for call in mock_print.call_args_list)
        assert "Bob" in printed_text
        assert "nothing amiss" in printed_text
    
    @patch('builtins.print')
    def test_no_inspection(self, mock_print):
        """Test showing no inspection"""
        merchant = Mock()
        merchant.name = "Charlie"
        
        show_inspection_result(merchant, sheriff_opens=False, caught=False)
        
        printed_text = ' '.join(str(call) for call in mock_print.call_args_list)
        assert "Charlie" in printed_text
        assert "pass without inspection" in printed_text


class TestShowThreat:
    """Tests for show_threat function"""
    
    @patch('builtins.print')
    def test_show_threat(self, mock_print):
        """Test showing threat to inspect"""
        merchant = Mock()
        merchant.name = "Alice"
        
        show_threat(merchant)
        
        printed_text = ' '.join(str(call) for call in mock_print.call_args_list)
        assert "Alice" in printed_text
        assert "suspicious" in printed_text


class TestShowBribeOffer:
    """Tests for show_bribe_offer function"""
    
    @patch('builtins.print')
    def test_show_bribe_offer_first_round(self, mock_print):
        """Test showing first bribe offer"""
        merchant = Mock()
        merchant.name = "Alice"
        
        show_bribe_offer(merchant, amount=50, round_number=1)
        
        printed_text = ' '.join(str(call) for call in mock_print.call_args_list)
        assert "Alice" in printed_text
        assert "50 gold" in printed_text
    
    @patch('builtins.print')
    def test_show_bribe_offer_counter(self, mock_print):
        """Test showing counter bribe offer"""
        merchant = Mock()
        merchant.name = "Bob"
        
        show_bribe_offer(merchant, amount=75, round_number=2)
        
        printed_text = ' '.join(str(call) for call in mock_print.call_args_list)
        assert "Bob" in printed_text
        assert "75 gold" in printed_text
        assert "counters" in printed_text


class TestShowMerchantRefuses:
    """Tests for show_merchant_refuses function"""
    
    @patch('builtins.print')
    def test_show_merchant_refuses(self, mock_print):
        """Test showing merchant refusal"""
        merchant = Mock()
        merchant.name = "Alice"
        
        show_merchant_refuses(merchant)
        
        printed_text = ' '.join(str(call) for call in mock_print.call_args_list)
        assert "Alice" in printed_text
        assert "nothing to hide" in printed_text


class TestShowMerchantGivesUp:
    """Tests for show_merchant_gives_up function"""
    
    @patch('builtins.print')
    def test_show_merchant_gives_up(self, mock_print):
        """Test showing merchant giving up"""
        merchant = Mock()
        merchant.name = "Bob"
        
        show_merchant_gives_up(merchant)
        
        # Verify print was called at least twice (name line + message line)
        assert mock_print.call_count >= 2
        
        # Check that merchant name appears in first call
        first_call = str(mock_print.call_args_list[0])
        assert "Bob" in first_call
        assert "shakes" in first_call
        
        # Check that second call contains a refusal message (one of the variations)
        second_call = str(mock_print.call_args_list[1])
        # Just verify it's a non-empty message (the random choice makes exact matching difficult)
        assert len(second_call) > 10  # Should be a substantial message


class TestShowBribeAccepted:
    """Tests for show_bribe_accepted function"""
    
    @patch('builtins.print')
    def test_show_bribe_accepted(self, mock_print):
        """Test showing bribe acceptance"""
        merchant = Mock()
        merchant.name = "Alice"
        
        show_bribe_accepted(merchant, amount=50)
        
        printed_text = ' '.join(str(call) for call in mock_print.call_args_list)
        assert "Alice" in printed_text
        assert "50 gold" in printed_text


class TestShowBribeRejected:
    """Tests for show_bribe_rejected function"""
    
    @patch('builtins.print')
    def test_show_bribe_rejected(self, mock_print):
        """Test showing bribe rejection"""
        merchant = Mock()
        merchant.name = "Bob"
        
        show_bribe_rejected(merchant)
        
        printed_text = ' '.join(str(call) for call in mock_print.call_args_list)
        assert "Bob" in printed_text
        assert "cannot be bought" in printed_text


class TestShowProactiveBribe:
    """Tests for show_proactive_bribe function"""
    
    @patch('builtins.print')
    def test_show_proactive_bribe_lying(self, mock_print):
        """Test showing proactive bribe when lying"""
        merchant = Mock()
        merchant.name = "Alice"
        
        show_proactive_bribe(merchant, amount=50, is_lying=True)
        
        printed_text = ' '.join(str(call) for call in mock_print.call_args_list)
        assert "Alice" in printed_text
        assert "50 gold" in printed_text
        assert "nervously" in printed_text
    
    @patch('builtins.print')
    def test_show_proactive_bribe_honest(self, mock_print):
        """Test showing proactive bribe when honest"""
        merchant = Mock()
        merchant.name = "Bob"
        
        show_proactive_bribe(merchant, amount=30, is_lying=False)
        
        printed_text = ' '.join(str(call) for call in mock_print.call_args_list)
        assert "Bob" in printed_text
        assert "30 gold" in printed_text
        assert "smiles" in printed_text


class TestPromptInitialDecision:
    """Tests for prompt_initial_decision function"""
    
    @patch('ui.pygame_ui.get_ui')
    def test_prompt_with_proactive_bribe(self, mock_get_ui):
        """Test prompting with proactive bribe"""
        mock_ui = Mock()
        mock_ui.show_choices.return_value = 'accept'
        mock_get_ui.return_value = mock_ui
        
        result = prompt_initial_decision(has_proactive_bribe=True, bribe_amount=50)
        
        assert result == 'accept'
        mock_ui.show_choices.assert_called_once()
        
        # Check that 'accept' option is in choices
        call_args = mock_ui.show_choices.call_args
        choices = call_args[0][1]
        assert any(choice[0] == 'accept' for choice in choices)
    
    @patch('ui.pygame_ui.get_ui')
    def test_prompt_without_proactive_bribe(self, mock_get_ui):
        """Test prompting without proactive bribe"""
        mock_ui = Mock()
        mock_ui.show_choices.return_value = 'inspect'
        mock_get_ui.return_value = mock_ui
        
        result = prompt_initial_decision(has_proactive_bribe=False)
        
        assert result == 'inspect'
        
        # Check that 'accept' option is NOT in choices
        call_args = mock_ui.show_choices.call_args
        choices = call_args[0][1]
        assert not any(choice[0] == 'accept' for choice in choices)


class TestPromptNegotiationResponse:
    """Tests for prompt_negotiation_response function"""
    
    @patch('ui.pygame_ui.get_ui')
    def test_prompt_accept(self, mock_get_ui):
        """Test accepting bribe"""
        mock_ui = Mock()
        mock_ui.show_choices.return_value = 'accept'
        mock_get_ui.return_value = mock_ui
        
        choice, amount = prompt_negotiation_response(current_offer=50)
        
        assert choice == 'accept'
        assert amount == 0
    
    @patch('ui.pygame_ui.get_ui')
    def test_prompt_reject(self, mock_get_ui):
        """Test rejecting bribe"""
        mock_ui = Mock()
        mock_ui.show_choices.return_value = 'reject'
        mock_get_ui.return_value = mock_ui
        
        choice, amount = prompt_negotiation_response(current_offer=50)
        
        assert choice == 'reject'
        assert amount == 0
    
    @patch('ui.pygame_ui.get_ui')
    def test_prompt_counter_valid(self, mock_get_ui):
        """Test counter offer with valid amount"""
        mock_ui = Mock()
        mock_ui.show_choices.return_value = 'counter'
        mock_ui.get_input.return_value = '75'
        mock_get_ui.return_value = mock_ui
        
        choice, amount = prompt_negotiation_response(current_offer=50)
        
        assert choice == 'counter'
        assert amount == 75
    
    @patch('ui.pygame_ui.get_ui')
    def test_prompt_counter_too_low(self, mock_get_ui):
        """Test counter offer with amount too low"""
        mock_ui = Mock()
        mock_ui.show_choices.return_value = 'counter'
        mock_ui.get_input.return_value = '40'
        mock_get_ui.return_value = mock_ui
        
        choice, amount = prompt_negotiation_response(current_offer=50)
        
        assert choice == 'counter'
        assert amount == 55  # Default to current + 5
    
    @patch('ui.pygame_ui.get_ui')
    def test_prompt_counter_invalid(self, mock_get_ui):
        """Test counter offer with invalid input"""
        mock_ui = Mock()
        mock_ui.show_choices.return_value = 'counter'
        mock_ui.get_input.return_value = 'invalid'
        mock_get_ui.return_value = mock_ui
        
        choice, amount = prompt_negotiation_response(current_offer=50)
        
        assert choice == 'counter'
        assert amount == 55  # Default to current + 5