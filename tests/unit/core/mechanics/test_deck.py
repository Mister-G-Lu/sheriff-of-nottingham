"""
Tests for Deck System

Tests the weighted probability deck system for drawing merchant hands.
"""

import pytest
from core.mechanics.deck import (
    draw_hand, get_card_probability, get_expected_count_in_hand,
    analyze_hand, select_from_hand, get_best_available_substitute,
    CARD_WEIGHTS, TOTAL_CARDS
)
from core.mechanics.goods import GOOD_BY_ID


class TestDeckProbabilities:
    """Test card probability calculations."""
    
    def test_total_cards_sum(self):
        """Test that total cards equals sum of all weights."""
        assert TOTAL_CARDS == 205, "Total cards should be 205"
    
    def test_apple_probability(self):
        """Test that apples have highest probability."""
        apple_prob = get_card_probability('apple')
        assert apple_prob == 48 / 205, "Apple probability should be 48/205"
        
        # Apples should be most common
        for good_id in CARD_WEIGHTS:
            if good_id != 'apple':
                assert apple_prob > get_card_probability(good_id)
    
    def test_crossbow_probability(self):
        """Test that crossbows have lowest probability."""
        crossbow_prob = get_card_probability('crossbow')
        assert crossbow_prob == 5 / 205, "Crossbow probability should be 5/205"
        
        # Crossbows should be rarest
        for good_id in CARD_WEIGHTS:
            if good_id != 'crossbow':
                assert crossbow_prob < get_card_probability(good_id)
    
    def test_expected_count_in_hand(self):
        """Test expected count calculation."""
        # With 6 cards, expect ~1.4 apples on average
        apple_expected = get_expected_count_in_hand('apple', 6)
        assert 1.3 < apple_expected < 1.5, "Should expect ~1.4 apples in 6-card hand"
        
        # With 6 cards, expect ~0.15 crossbows on average
        crossbow_expected = get_expected_count_in_hand('crossbow', 6)
        assert 0.1 < crossbow_expected < 0.2, "Should expect ~0.15 crossbows in 6-card hand"


class TestDrawHand:
    """Test hand drawing functionality."""
    
    def test_draw_hand_size(self):
        """Test that draw_hand returns correct number of cards."""
        hand = draw_hand(6)
        assert len(hand) == 6, "Should draw 6 cards"
        
        hand = draw_hand(10)
        assert len(hand) == 10, "Should draw 10 cards"
    
    def test_draw_hand_returns_goods(self):
        """Test that draw_hand returns Good objects."""
        hand = draw_hand(6)
        for card in hand:
            assert hasattr(card, 'id'), "Card should be a Good object"
            assert hasattr(card, 'value'), "Card should have value"
            assert hasattr(card, 'is_legal'), "Card should have is_legal method"
    
    def test_draw_hand_distribution(self):
        """Test that hand distribution roughly matches probabilities over many draws."""
        # Draw 1000 hands and count card types
        counts = {good_id: 0 for good_id in CARD_WEIGHTS}
        
        for _ in range(1000):
            hand = draw_hand(6)
            for card in hand:
                counts[card.id] += 1
        
        total_drawn = sum(counts.values())
        
        # Check that apples are most common
        assert counts['apple'] > counts['crossbow'] * 5, "Apples should be much more common than crossbows"
        
        # Check that distribution is roughly correct (within 20% tolerance)
        for good_id, weight in CARD_WEIGHTS.items():
            expected_proportion = weight / TOTAL_CARDS
            actual_proportion = counts[good_id] / total_drawn
            
            # Allow 20% tolerance due to randomness
            assert abs(actual_proportion - expected_proportion) < expected_proportion * 0.2, \
                f"{good_id} distribution should be close to expected"


class TestAnalyzeHand:
    """Test hand analysis functionality."""
    
    def test_analyze_all_legal_hand(self):
        """Test analyzing a hand with only legal goods."""
        hand = [
            GOOD_BY_ID['apple'],
            GOOD_BY_ID['apple'],
            GOOD_BY_ID['cheese'],
            GOOD_BY_ID['bread'],
            GOOD_BY_ID['chicken'],
            GOOD_BY_ID['chicken']
        ]
        
        analysis = analyze_hand(hand)
        
        assert len(analysis['legal']) == 6, "Should have 6 legal goods"
        assert len(analysis['contraband']) == 0, "Should have 0 contraband"
        assert analysis['counts']['apple'] == 2, "Should have 2 apples"
        assert analysis['counts']['chicken'] == 2, "Should have 2 chickens"
    
    def test_analyze_mixed_hand(self):
        """Test analyzing a hand with legal and contraband."""
        hand = [
            GOOD_BY_ID['apple'],
            GOOD_BY_ID['cheese'],
            GOOD_BY_ID['pepper'],
            GOOD_BY_ID['silk'],
            GOOD_BY_ID['crossbow'],
            GOOD_BY_ID['mead']
        ]
        
        analysis = analyze_hand(hand)
        
        assert len(analysis['legal']) == 2, "Should have 2 legal goods"
        assert len(analysis['contraband']) == 4, "Should have 4 contraband"
        assert analysis['contraband_value'] > analysis['legal_value'], \
            "Contraband should be worth more than legal goods"


class TestSelectFromHand:
    """Test selecting goods from hand."""
    
    def test_select_available_goods(self):
        """Test selecting goods that are available in hand."""
        hand = [
            GOOD_BY_ID['apple'],
            GOOD_BY_ID['apple'],
            GOOD_BY_ID['cheese'],
            GOOD_BY_ID['bread']
        ]
        
        selected = select_from_hand(hand, ['apple', 'apple', 'cheese'], max_count=3)
        
        assert len(selected) == 3, "Should select 3 goods"
        assert sum(1 for g in selected if g.id == 'apple') == 2, "Should have 2 apples"
        assert sum(1 for g in selected if g.id == 'cheese') == 1, "Should have 1 cheese"
    
    def test_select_unavailable_goods(self):
        """Test selecting goods that aren't in hand."""
        hand = [
            GOOD_BY_ID['apple'],
            GOOD_BY_ID['cheese']
        ]
        
        # Try to select crossbows that aren't in hand
        selected = select_from_hand(hand, ['crossbow', 'crossbow', 'crossbow'], max_count=3)
        
        assert len(selected) == 0, "Should select 0 goods if none are available"
    
    def test_select_respects_max_count(self):
        """Test that selection respects bag size limit."""
        hand = [GOOD_BY_ID['apple']] * 10
        
        selected = select_from_hand(hand, ['apple'] * 10, max_count=6)
        
        assert len(selected) == 6, "Should respect max_count of 6"


class TestBestSubstitute:
    """Test finding substitute goods."""
    
    def test_substitute_for_legal_good(self):
        """Test finding substitute for unavailable legal good."""
        hand = [
            GOOD_BY_ID['cheese'],  # 3g
            GOOD_BY_ID['bread'],   # 3g
            GOOD_BY_ID['chicken']  # 4g
        ]
        
        # Want apple (2g), should get cheese or bread (closest value)
        substitute = get_best_available_substitute(hand, 'apple', is_legal=True)
        
        assert substitute is not None, "Should find a substitute"
        assert substitute.is_legal(), "Substitute should be legal"
        assert substitute.id in ['cheese', 'bread'], "Should pick closest value legal good"
    
    def test_substitute_for_contraband(self):
        """Test finding substitute for unavailable contraband."""
        hand = [
            GOOD_BY_ID['silk'],    # 6g
            GOOD_BY_ID['pepper'],  # 7g
            GOOD_BY_ID['mead']     # 8g
        ]
        
        # Want crossbow (9g), should get mead (8g, closest value)
        substitute = get_best_available_substitute(hand, 'crossbow', is_legal=False)
        
        assert substitute is not None, "Should find a substitute"
        assert not substitute.is_legal(), "Substitute should be contraband"
        assert substitute.id == 'mead', "Should pick mead (8g is closest to crossbow 9g)"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
