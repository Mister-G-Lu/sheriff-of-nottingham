"""
Test Legal Lie Penalty

Verify that merchants pay the correct penalty when caught lying about legal goods.
Example: Declaring "3 Cheese" but carrying "3 Chicken"
"""

import pytest
from core.mechanics.goods import APPLE, CHEESE, BREAD, CHICKEN
from core.mechanics.inspection import handle_inspection
from core.players.merchants import Merchant
from core.players.sheriff import Sheriff
from core.systems.game_master_state import MerchantTier


def create_test_merchant():
    """Create a test merchant with known stats."""
    return Merchant(
        id='test_merchant',
        name='Test Merchant',
        intro='A test merchant',
        gold=100,
        bluff_skill=5,
        tells_honest=['honest tell'],
        tells_lying=['lying tell'],
        difficulty_tier=MerchantTier.MEDIUM
    )


def create_test_sheriff():
    """Create a test sheriff with known stats."""
    return Sheriff(perception=5)


class TestLegalLiePenalty:
    """Test that legal lies incur proper penalties."""
    
    def test_legal_lie_caught_pays_penalty(self):
        """Test that merchant pays penalty when caught in a legal lie."""
        merchant = create_test_merchant()
        sheriff = create_test_sheriff()
        
        # Merchant declares 3 cheese but carries 3 chicken (all legal, but wrong type)
        declaration = {'good_id': 'cheese', 'count': 3}
        actual_goods = [CHICKEN, CHICKEN, CHICKEN]
        
        # Force sheriff to catch the lie by setting high perception
        sheriff.perception = 10
        
        # Run inspection multiple times to ensure we catch at least once
        caught_at_least_once = False
        for _ in range(10):
            merchant.gold = 100  # Reset gold
            result = handle_inspection(merchant, actual_goods, declaration, sheriff)
            
            if result['caught_lie']:
                caught_at_least_once = True
                
                # Verify penalty calculation
                # 3 chickens @ 4g each = 12g total value
                # Penalty = 50% of 12g = 6g
                expected_penalty = 6
                
                assert result['was_honest'] == False, "Should not be honest"
                assert result['caught_lie'] == True, "Should catch the lie"
                assert len(result['goods_confiscated']) == 3, "Should confiscate all 3 chickens"
                assert len(result['goods_passed']) == 0, "Should pass 0 goods (no cheese found)"
                assert result['penalty_paid'] == expected_penalty, \
                    f"Should pay {expected_penalty}g penalty, got {result['penalty_paid']}g"
                assert merchant.gold == 100 - expected_penalty, \
                    f"Merchant should have {100 - expected_penalty}g left"
                break
        
        assert caught_at_least_once, "Sheriff should catch the lie at least once in 10 attempts"
    
    def test_legal_lie_not_caught_no_penalty(self):
        """Test that merchant pays no penalty when legal lie is not caught."""
        merchant = create_test_merchant()
        sheriff = create_test_sheriff()
        
        # Merchant declares 3 cheese but carries 3 chicken
        declaration = {'good_id': 'cheese', 'count': 3}
        actual_goods = [CHICKEN, CHICKEN, CHICKEN]
        
        # Force sheriff to miss the lie by setting low perception
        sheriff.perception = 0
        merchant.bluff_skill = 10
        
        # Run inspection multiple times to ensure we miss at least once
        missed_at_least_once = False
        for _ in range(10):
            merchant.gold = 100  # Reset gold
            result = handle_inspection(merchant, actual_goods, declaration, sheriff)
            
            if not result['caught_lie']:
                missed_at_least_once = True
                
                assert result['was_honest'] == False, "Should not be honest"
                assert result['caught_lie'] == False, "Should not catch the lie"
                assert len(result['goods_passed']) == 3, "All goods should pass"
                assert len(result['goods_confiscated']) == 0, "No goods confiscated"
                assert result['penalty_paid'] == 0, "No penalty when not caught"
                assert merchant.gold == 100, "Merchant keeps all gold"
                break
        
        assert missed_at_least_once, "Sheriff should miss the lie at least once in 10 attempts"
    
    def test_partial_legal_lie_penalty(self):
        """Test penalty when merchant partially lies with legal goods."""
        merchant = create_test_merchant()
        sheriff = create_test_sheriff()
        sheriff.perception = 10  # Force catch
        
        # Merchant declares 3 cheese but carries 1 cheese + 2 chicken
        declaration = {'good_id': 'cheese', 'count': 3}
        actual_goods = [CHEESE, CHICKEN, CHICKEN]
        
        # Run inspection
        for _ in range(10):
            merchant.gold = 100
            result = handle_inspection(merchant, actual_goods, declaration, sheriff)
            
            if result['caught_lie']:
                # Expected: 1 cheese passes (truthfully declared), 2 chickens confiscated
                # Penalty = 50% of (2 * 4g) = 4g
                expected_penalty = 4
                
                assert len(result['goods_passed']) == 1, "1 cheese should pass"
                assert len(result['goods_confiscated']) == 2, "2 chickens should be confiscated"
                assert result['penalty_paid'] == expected_penalty, \
                    f"Should pay {expected_penalty}g penalty"
                break
    
    def test_mixed_legal_goods_different_values(self):
        """Test penalty with legal goods of different values."""
        merchant = create_test_merchant()
        sheriff = create_test_sheriff()
        sheriff.perception = 10
        
        # Declare 4 apples (2g each) but carry 2 bread (3g) + 2 chicken (4g)
        declaration = {'good_id': 'apple', 'count': 4}
        actual_goods = [BREAD, BREAD, CHICKEN, CHICKEN]
        
        for _ in range(10):
            merchant.gold = 100
            result = handle_inspection(merchant, actual_goods, declaration, sheriff)
            
            if result['caught_lie']:
                # All 4 goods confiscated (no apples found)
                # Total value: 2*3g + 2*4g = 14g
                # Penalty: 50% of 14g = 7g
                expected_penalty = 7
                
                assert len(result['goods_confiscated']) == 4, "All goods should be confiscated"
                assert result['penalty_paid'] == expected_penalty, \
                    f"Should pay {expected_penalty}g penalty"
                break


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
