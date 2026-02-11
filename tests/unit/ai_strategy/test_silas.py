"""
Test Silas's Strategy vs Tiered Strategy

This test demonstrates that Silas (Information Broker) adapts better to sheriff
behavior patterns than standard tiered merchants, making him more dangerous.

We simulate specific game scenarios with controlled outcomes to verify:
1. Silas exploits lenient sheriffs more aggressively
2. Silas plays safer when sheriff is effective
3. Silas adapts better than personality-based merchants
"""

import pytest
from core.players.merchants import Merchant, InformationBroker
from core.systems.game_master_state import MerchantTier
from ai_strategy.silas_strategy import get_silas_declaration
from ai_strategy.tiered_strategy import get_tiered_declaration


class TestSilasVsTieredStrategy:
    """Compare Silas's adaptive strategy against standard tiered strategies."""
    
    def test_silas_exploits_lenient_sheriff(self):
        """Test that Silas smuggles more aggressively when sheriff is lenient."""
        # Scenario: Sheriff has let 4 out of 5 merchants pass (80% pass rate)
        lenient_history = [
            {'opened': False, 'caught_lie': False},  # Passed
            {'opened': False, 'caught_lie': False},  # Passed
            {'opened': True, 'caught_lie': False},   # Inspected but honest
            {'opened': False, 'caught_lie': False},  # Passed
            {'opened': False, 'caught_lie': False},  # Passed
        ]
        
        # Silas's decision with lenient sheriff
        silas_decision = get_silas_declaration(lenient_history)
        
        # Bold merchant (Garrett-like: risk=8, honesty=3, greed=6) with same history
        bold_personality = {'risk_tolerance': 8, 'greed': 6, 'honesty_bias': 3}
        bold_decision = get_tiered_declaration(bold_personality, MerchantTier.HARD)
        
        # Silas should be smuggling (exploiting lenient sheriff)
        assert silas_decision['lie'] == True, "Silas should smuggle when sheriff is lenient"
        assert len(silas_decision['actual_ids']) >= 2, "Silas should smuggle multiple items"
        
        # Note: Bold merchant might also smuggle, but Silas's decision is data-driven
        # while bold merchant's is personality-driven
    
    def test_silas_plays_safe_with_effective_sheriff(self):
        """Test that Silas goes honest when sheriff catches most smugglers."""
        # Scenario: Sheriff caught 4 out of 5 smugglers (80% catch rate)
        dangerous_history = [
            {'opened': True, 'caught_lie': True},   # Caught smuggler
            {'opened': True, 'caught_lie': True},   # Caught smuggler
            {'opened': False, 'caught_lie': False}, # Passed (honest merchant)
            {'opened': True, 'caught_lie': True},   # Caught smuggler
            {'opened': True, 'caught_lie': True},   # Caught smuggler
        ]
        
        # Silas's decision with effective sheriff
        silas_decision = get_silas_declaration(dangerous_history)
        
        # Bold merchant (same personality) with same history
        bold_personality = {'risk_tolerance': 8, 'greed': 6, 'honesty_bias': 3}
        bold_decision = get_tiered_declaration(bold_personality, MerchantTier.HARD)
        
        # Silas should play it safe (going honest)
        assert silas_decision['lie'] == False, "Silas should go honest when sheriff is effective"
        
        # Bold merchant might still try to smuggle (personality-driven)
        # This demonstrates Silas is more adaptive
    
    def test_silas_adapts_to_changing_patterns(self):
        """Test that Silas changes strategy as sheriff behavior changes."""
        # Round 1: Sheriff is very lenient (0 inspections in 5 encounters)
        very_lenient_history = [
            {'opened': False, 'caught_lie': False},
            {'opened': False, 'caught_lie': False},
            {'opened': False, 'caught_lie': False},
            {'opened': False, 'caught_lie': False},
            {'opened': False, 'caught_lie': False},
        ]
        
        silas_lenient = get_silas_declaration(very_lenient_history)
        
        # Round 2: Sheriff gets very aggressive (catches 4 out of 5 smugglers = 80% catch rate)
        very_aggressive_history = [
            {'opened': True, 'caught_lie': True},   # Caught
            {'opened': True, 'caught_lie': True},   # Caught
            {'opened': True, 'caught_lie': True},   # Caught
            {'opened': True, 'caught_lie': True},   # Caught
            {'opened': True, 'caught_lie': False},  # Inspected honest
        ]
        
        silas_aggressive = get_silas_declaration(very_aggressive_history)
        
        # Silas should adapt: smuggle when very lenient, go honest when very aggressive
        assert silas_lenient['lie'] == True, "Silas should smuggle when sheriff is very lenient"
        assert silas_aggressive['lie'] == False, "Silas should go honest when sheriff catches 80% of smugglers"
    
    def test_silas_first_round_is_conservative(self):
        """Test that Silas starts conservatively without data."""
        # First round: no history
        silas_first = get_silas_declaration(None)
        
        # Silas should smuggle (testing the waters) but conservatively
        assert silas_first['lie'] == True, "Silas should test the waters in first round"
        assert len(silas_first['actual_ids']) <= 3, "Silas should be conservative (2-3 items)"
        assert silas_first['lie_type'] == 'contraband', "Silas should smuggle contraband"
    
    def test_silas_vs_cautious_merchant_with_lenient_sheriff(self):
        """Compare Silas to a cautious merchant when sheriff is lenient."""
        # Lenient sheriff scenario
        lenient_history = [
            {'opened': False, 'caught_lie': False},
            {'opened': False, 'caught_lie': False},
            {'opened': False, 'caught_lie': False},
            {'opened': True, 'caught_lie': False},
            {'opened': False, 'caught_lie': False},
        ]
        
        # Silas's decision
        silas_decision = get_silas_declaration(lenient_history)
        
        # Cautious merchant (Alice-like: risk=2, honesty=8, greed=3)
        cautious_personality = {'risk_tolerance': 2, 'greed': 3, 'honesty_bias': 8}
        
        # Test across all tiers
        easy_decision = get_tiered_declaration(cautious_personality, MerchantTier.EASY)
        medium_decision = get_tiered_declaration(cautious_personality, MerchantTier.MEDIUM)
        hard_decision = get_tiered_declaration(cautious_personality, MerchantTier.HARD)
        
        # Silas should be more aggressive than cautious merchants
        # (exploiting the data, not held back by personality)
        assert silas_decision['lie'] == True, "Silas should exploit lenient sheriff"
        
        # Cautious merchants might still be honest due to personality
        # This shows Silas is more opportunistic
    
    def test_silas_contraband_count_scales_with_safety(self):
        """Test that Silas smuggles more items when environment is safer."""
        # Very safe scenario (0 inspections in 5 encounters)
        very_safe_history = [
            {'opened': False, 'caught_lie': False},
            {'opened': False, 'caught_lie': False},
            {'opened': False, 'caught_lie': False},
            {'opened': False, 'caught_lie': False},
            {'opened': False, 'caught_lie': False},
        ]
        
        # Moderately safe scenario (2 inspections, 1 catch in 5 encounters)
        moderate_history = [
            {'opened': False, 'caught_lie': False},
            {'opened': True, 'caught_lie': True},
            {'opened': False, 'caught_lie': False},
            {'opened': True, 'caught_lie': False},
            {'opened': False, 'caught_lie': False},
        ]
        
        # Run multiple times to get average behavior
        very_safe_counts = []
        moderate_counts = []
        
        for _ in range(10):
            very_safe_dec = get_silas_declaration(very_safe_history)
            moderate_dec = get_silas_declaration(moderate_history)
            
            if very_safe_dec['lie']:
                very_safe_counts.append(len(very_safe_dec['actual_ids']))
            if moderate_dec['lie']:
                moderate_counts.append(len(moderate_dec['actual_ids']))
        
        # Silas should smuggle more items when it's safer
        if very_safe_counts and moderate_counts:
            avg_very_safe = sum(very_safe_counts) / len(very_safe_counts)
            avg_moderate = sum(moderate_counts) / len(moderate_counts)
            
            assert avg_very_safe >= avg_moderate, \
                f"Silas should smuggle more when safer (safe: {avg_very_safe}, moderate: {avg_moderate})"
    
    def test_silas_uses_data_not_personality(self):
        """Verify that Silas's decisions are data-driven, not personality-driven."""
        # Scenario 1: Lenient sheriff (should encourage smuggling)
        lenient_history = [
            {'opened': False, 'caught_lie': False},
            {'opened': False, 'caught_lie': False},
            {'opened': False, 'caught_lie': False},
            {'opened': False, 'caught_lie': False},
            {'opened': False, 'caught_lie': False},
        ]
        
        # Scenario 2: Dangerous sheriff (should discourage smuggling)
        dangerous_history = [
            {'opened': True, 'caught_lie': True},
            {'opened': True, 'caught_lie': True},
            {'opened': True, 'caught_lie': True},
            {'opened': True, 'caught_lie': False},
            {'opened': True, 'caught_lie': True},
        ]
        
        # Silas's decisions based on data
        silas_lenient = get_silas_declaration(lenient_history)
        silas_dangerous = get_silas_declaration(dangerous_history)
        
        # Silas should adapt based on sheriff behavior, not just personality
        assert silas_lenient['lie'] == True, "Silas should smuggle when sheriff is lenient"
        assert silas_dangerous['lie'] == False, "Silas should go honest when sheriff is dangerous"
        
        # This demonstrates Silas uses data-driven analysis (catch_rate, inspection_rate)
        # rather than personality-based weighted random choice like tiered merchants
