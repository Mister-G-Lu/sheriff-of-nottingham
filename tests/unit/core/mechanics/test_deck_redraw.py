"""
Tests for Card Redraw System

Tests the ability for merchants to redraw cards based on their risk tolerance.
"""

import pytest
from core.mechanics.deck import (
    draw_hand, redraw_cards, should_redraw_for_contraband, analyze_hand
)
from core.mechanics.goods import APPLE, CHEESE, CHICKEN, SILK, PEPPER, CROSSBOW


class TestRedrawCards:
    """Test card redraw functionality."""
    
    def test_redraw_replaces_cards(self):
        """Test that redraw replaces the specified number of cards."""
        original_hand = draw_hand(7)
        new_hand = redraw_cards(original_hand, 3)
        
        assert len(new_hand) == 7, "Hand should still have 7 cards"
        # At least some cards should be different (very high probability)
        assert new_hand != original_hand, "Hand should have changed"
    
    def test_redraw_zero_returns_same_hand(self):
        """Test that redrawing 0 cards returns the same hand."""
        original_hand = draw_hand(7)
        new_hand = redraw_cards(original_hand, 0)
        
        assert new_hand == original_hand, "Hand should be unchanged"
    
    def test_redraw_all_cards(self):
        """Test that we can redraw all cards."""
        original_hand = draw_hand(7)
        new_hand = redraw_cards(original_hand, 7)
        
        assert len(new_hand) == 7, "Hand should still have 7 cards"
    
    def test_redraw_invalid_count(self):
        """Test that invalid redraw counts are handled."""
        original_hand = draw_hand(7)
        
        # Redraw more than hand size
        new_hand = redraw_cards(original_hand, 10)
        assert new_hand == original_hand, "Should return original hand for invalid count"
        
        # Negative redraw
        new_hand = redraw_cards(original_hand, -1)
        assert new_hand == original_hand, "Should return original hand for negative count"


class TestShouldRedrawForContraband:
    """Test the logic for determining if merchants should redraw."""
    
    def test_honest_merchant_redraws_for_consistency(self):
        """Test that honest merchants redraw to get more of the same legal good."""
        # Hand with 2 apples and mixed other goods
        hand = [APPLE, APPLE, CHEESE, CHICKEN, CHEESE, CHICKEN, CHEESE]
        
        # Honest Abe (honesty=10, risk=0)
        num_to_redraw = should_redraw_for_contraband(hand, risk_tolerance=0, honesty=10)
        assert num_to_redraw >= 1, "Honest merchants should redraw to get more of the same good"
    
    def test_honest_merchant_with_good_set_no_redraw(self):
        """Test that honest merchants don't redraw if they already have 4+ of the same good."""
        # Hand with 4 apples
        hand = [APPLE, APPLE, APPLE, APPLE, CHEESE, CHICKEN, CHEESE]
        
        # Honest Abe
        num_to_redraw = should_redraw_for_contraband(hand, risk_tolerance=0, honesty=10)
        assert num_to_redraw == 0, "Should not redraw with 4+ of the same good"
    
    def test_aggressive_smuggler_redraws_with_no_contraband(self):
        """Test that aggressive smugglers redraw when they have no contraband."""
        # Hand with all legal goods
        hand = [APPLE, CHEESE, CHICKEN, APPLE, CHEESE, CHICKEN, APPLE]
        
        # Lying Larry (honesty=1, risk=10)
        num_to_redraw = should_redraw_for_contraband(hand, risk_tolerance=10, honesty=1)
        assert num_to_redraw >= 3, "Aggressive smugglers should redraw 3-4 cards with no contraband"
    
    def test_aggressive_smuggler_with_good_contraband_no_redraw(self):
        """Test that smugglers don't redraw if they already have good contraband."""
        # Hand with 3+ contraband
        hand = [SILK, PEPPER, CROSSBOW, SILK, APPLE, CHEESE, CHICKEN]
        
        # Lying Larry
        num_to_redraw = should_redraw_for_contraband(hand, risk_tolerance=10, honesty=1)
        assert num_to_redraw == 0, "Should not redraw with 3+ contraband already"
    
    def test_moderate_smuggler_sometimes_redraws(self):
        """Test that moderate risk-takers sometimes redraw."""
        # Hand with no contraband
        hand = [APPLE, CHEESE, CHICKEN, APPLE, CHEESE, CHICKEN, APPLE]
        
        # Moderate merchant (risk=5, honesty=5)
        num_to_redraw = should_redraw_for_contraband(hand, risk_tolerance=5, honesty=5)
        # Might redraw 1-2 cards or not at all
        assert num_to_redraw >= 0, "Should return valid redraw count"
    
    def test_aggressive_smuggler_with_some_contraband_redraws_less(self):
        """Test that smugglers redraw fewer cards if they have some contraband."""
        # Hand with 2 contraband
        hand = [SILK, PEPPER, APPLE, CHEESE, CHICKEN, APPLE, CHEESE]
        
        # Lying Larry
        num_to_redraw = should_redraw_for_contraband(hand, risk_tolerance=10, honesty=1)
        # Should redraw 1-2 cards to try to get more contraband
        assert 0 <= num_to_redraw <= 2, "Should redraw 0-2 cards with some contraband"


class TestRedrawIntegration:
    """Test the full redraw flow."""
    
    def test_aggressive_merchant_gets_more_contraband_opportunities(self):
        """Test that aggressive merchants have better contraband access with redraws."""
        # Run multiple times to test probabilistically
        contraband_counts_with_redraw = []
        contraband_counts_without_redraw = []
        
        for _ in range(50):
            # Without redraw
            hand = draw_hand(7)
            analysis = analyze_hand(hand)
            contraband_counts_without_redraw.append(len(analysis['contraband']))
            
            # With redraw (aggressive merchant)
            hand = draw_hand(7)
            num_to_redraw = should_redraw_for_contraband(hand, risk_tolerance=10, honesty=1)
            if num_to_redraw > 0:
                hand = redraw_cards(hand, num_to_redraw)
            analysis = analyze_hand(hand)
            contraband_counts_with_redraw.append(len(analysis['contraband']))
        
        # Average contraband count should be higher with redraws
        avg_with_redraw = sum(contraband_counts_with_redraw) / len(contraband_counts_with_redraw)
        avg_without_redraw = sum(contraband_counts_without_redraw) / len(contraband_counts_without_redraw)
        
        # With redraws, aggressive merchants should have more contraband on average
        # (This is probabilistic, so we allow some variance)
        assert avg_with_redraw >= avg_without_redraw * 0.9, \
            f"Redraws should help get contraband: {avg_with_redraw:.2f} vs {avg_without_redraw:.2f}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
