"""
Unit tests for merchant bribe calculation logic
Tests that bribes are reasonable relative to goods values
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from core.players.merchants import Merchant
from core.mechanics.goods import BREAD, CROSSBOW, SILK, APPLE


class TestProactiveBribeCalculation:
    """Tests for proactive bribe calculation"""
    
    def test_bribe_for_contraband_is_fraction_of_value(self):
        """Test that bribes for contraband scale with risk tolerance (inverted)"""
        # Moderate risk tolerance merchant
        merchant = Merchant(
            id="test",
            name="Test Merchant",
            intro="Test",
            tells_honest=["honest"],
            tells_lying=["lying"],
            risk_tolerance=5,  # Moderate risk = moderate bribes
            greed=5,
            honesty_bias=5
        )
        
        # Scenario: 3x Bread (9g total) + 1x Crossbow (8g contraband)
        actual_goods = [BREAD, BREAD, BREAD, CROSSBOW]
        contraband_value = 8
        
        # Run multiple times to check range
        bribes = []
        for _ in range(20):
            bribe = merchant.calculate_proactive_bribe(
                actual_goods=actual_goods,
                is_lying=True,
                sheriff_authority=1
            )
            bribes.append(bribe)
        
        avg_bribe = sum(bribes) / len(bribes)
        max_bribe = max(bribes)
        min_bribe = min(bribes)
        
        # Moderate risk tolerance should offer moderate bribes (20-60% of contraband)
        assert min_bribe >= 1, f"Minimum bribe {min_bribe} should be at least 1 gold"
        assert max_bribe < contraband_value, f"Maximum bribe {max_bribe} should be less than contraband value ({contraband_value}g)"
        assert avg_bribe < contraband_value * 0.7, f"Average bribe {avg_bribe} should be less than 70% of contraband value"
    
    def test_bribe_for_high_value_contraband(self):
        """Test bribes for expensive contraband like crossbows"""
        merchant = Merchant(
            id="test",
            name="Test Merchant",
            intro="Test",
            tells_honest=["honest"],
            tells_lying=["lying"],
            risk_tolerance=5,  # Moderate risk tolerance
            greed=5,
            honesty_bias=5
        )
        
        # Scenario: 3x Crossbow (24g total contraband)
        actual_goods = [CROSSBOW, CROSSBOW, CROSSBOW]
        contraband_value = 24
        
        bribes = []
        for _ in range(20):
            bribe = merchant.calculate_proactive_bribe(
                actual_goods=actual_goods,
                is_lying=True,
                sheriff_authority=1
            )
            bribes.append(bribe)
        
        avg_bribe = sum(bribes) / len(bribes)
        max_bribe = max(bribes)
        
        # For 24g contraband with moderate risk tolerance, bribes should be reasonable
        # Capped at contraband_value - 1 = 23g max
        assert max_bribe < contraband_value, f"Maximum bribe {max_bribe} should not exceed contraband value ({contraband_value}g)"
        assert avg_bribe >= 2, f"Average bribe {avg_bribe} should be at least 2 gold"
        assert avg_bribe <= 18, f"Average bribe {avg_bribe} should be reasonable for moderate risk tolerance"
    
    def test_bribe_for_lying_about_legal_goods(self):
        """Test bribes when lying about legal goods mix (no contraband)"""
        merchant = Merchant(
            id="test",
            name="Test Merchant",
            intro="Test",
            tells_honest=["honest"],
            tells_lying=["lying"],
            risk_tolerance=5,
            greed=5,
            honesty_bias=5
        )
        
        # Scenario: 3x Bread (9g) but lying about what's declared
        actual_goods = [BREAD, BREAD, BREAD]
        
        bribes = []
        for _ in range(20):
            bribe = merchant.calculate_proactive_bribe(
                actual_goods=actual_goods,
                is_lying=True,  # Lying about legal goods
                sheriff_authority=1
            )
            bribes.append(bribe)
        
        avg_bribe = sum(bribes) / len(bribes)
        max_bribe = max(bribes)
        
        # Should be small amount (2-5g range)
        assert max_bribe <= 6, f"Maximum bribe {max_bribe} should be small for legal goods lie"
        assert avg_bribe >= 1, f"Average bribe {avg_bribe} should be at least 1 gold"
        assert avg_bribe <= 5, f"Average bribe {avg_bribe} should be small (2-5g range)"
    
    def test_bribe_for_honest_merchant(self):
        """Test bribes for honest merchants (goodwill gesture)"""
        merchant = Merchant(
            id="test",
            name="Test Merchant",
            intro="Test",
            tells_honest=["honest"],
            tells_lying=["lying"],
            risk_tolerance=5,
            greed=5,
            honesty_bias=5
        )
        
        # Scenario: 3x Apple (6g) and being honest
        actual_goods = [APPLE, APPLE, APPLE]
        
        bribes = []
        for _ in range(20):
            bribe = merchant.calculate_proactive_bribe(
                actual_goods=actual_goods,
                is_lying=False,  # Honest
                sheriff_authority=1
            )
            bribes.append(bribe)
        
        avg_bribe = sum(bribes) / len(bribes)
        max_bribe = max(bribes)
        
        # Should be very small goodwill amount (1-3g)
        assert max_bribe <= 4, f"Maximum bribe {max_bribe} should be very small for honest merchant"
        assert avg_bribe >= 1, f"Average bribe {avg_bribe} should be at least 1 gold"
        assert avg_bribe <= 3, f"Average bribe {avg_bribe} should be small goodwill gesture (1-3g)"
    
    def test_bribe_never_exceeds_contraband_value(self):
        """Test that bribes never exceed contraband value - 1"""
        merchant = Merchant(
            id="test",
            name="Test Merchant",
            intro="Test",
            tells_honest=["honest"],
            tells_lying=["lying"],
            risk_tolerance=0,  # Very cautious (would offer a lot)
            greed=0,
            honesty_bias=0
        )
        
        # Scenario: High value contraband
        actual_goods = [CROSSBOW, CROSSBOW]  # 16g contraband
        contraband_value = 16
        
        bribes = []
        for _ in range(20):
            bribe = merchant.calculate_proactive_bribe(
                actual_goods=actual_goods,
                is_lying=True,
                sheriff_authority=5  # High authority (increases bribe)
            )
            bribes.append(bribe)
        
        max_bribe = max(bribes)
        
        # Even very cautious merchants should not offer more than contraband is worth
        assert max_bribe < contraband_value, \
            f"Maximum bribe {max_bribe} should not exceed contraband value ({contraband_value}g)"
    
    def test_risk_tolerance_affects_bribe_amount(self):
        """Test that low risk tolerance = high bribes, high risk tolerance = low/no bribes"""
        # Cautious merchant (low risk tolerance)
        cautious = Merchant(
            id="cautious",
            name="Cautious",
            intro="Test",
            tells_honest=["honest"],
            tells_lying=["lying"],
            risk_tolerance=1,  # Very cautious
            greed=5,
            honesty_bias=5
        )
        
        # Bold merchant (high risk tolerance)
        bold = Merchant(
            id="bold",
            name="Bold",
            intro="Test",
            tells_honest=["honest"],
            tells_lying=["lying"],
            risk_tolerance=9,  # Very bold
            greed=5,
            honesty_bias=5
        )
        
        actual_goods = [SILK, SILK]  # 12g contraband
        
        # Get average bribes for each
        cautious_bribes = [cautious.calculate_proactive_bribe(actual_goods, True, 1) for _ in range(20)]
        bold_bribes = [bold.calculate_proactive_bribe(actual_goods, True, 1) for _ in range(20)]
        
        avg_cautious = sum(cautious_bribes) / len(cautious_bribes)
        avg_bold = sum(bold_bribes) / len(bold_bribes)
        
        # Cautious merchant should offer significantly more than bold merchant
        assert avg_cautious > avg_bold * 1.5, \
            f"Cautious merchant (avg {avg_cautious}g) should offer significantly more than bold merchant (avg {avg_bold}g)"
        
        # Bold merchant might offer 0 sometimes
        assert min(bold_bribes) == 0 or min(bold_bribes) < 3, \
            f"Bold merchant should sometimes offer very little or nothing (min: {min(bold_bribes)}g)"
        
        # Cautious merchant should offer substantial bribes
        assert avg_cautious > 5, \
            f"Cautious merchant should offer substantial bribes (avg: {avg_cautious}g)"
    
    def test_bribe_amounts_are_reasonable(self):
        """Test that bribe amounts are generally reasonable across different scenarios"""
        merchant = Merchant(
            id="test",
            name="Test Merchant",
            intro="Test",
            tells_honest=["honest"],
            tells_lying=["lying"],
            risk_tolerance=5,
            greed=5,
            honesty_bias=5
        )
        
        # Test various contraband scenarios with moderate risk tolerance
        # Moderate risk (5) should offer 20-60% of contraband value
        test_cases = [
            ([SILK], 6, 1, 6),  # 1x Silk (6g) -> expect 1-6g bribe
            ([CROSSBOW], 8, 1, 7),  # 1x Crossbow (8g) -> expect 1-7g bribe
            ([SILK, SILK], 12, 2, 11),  # 2x Silk (12g) -> expect 2-11g bribe
            ([CROSSBOW, CROSSBOW], 16, 2, 15),  # 2x Crossbow (16g) -> expect 2-15g bribe
        ]
        
        for goods, contraband_value, min_expected, max_expected in test_cases:
            bribes = [merchant.calculate_proactive_bribe(goods, True, 1) for _ in range(10)]
            avg_bribe = sum(bribes) / len(bribes)
            max_bribe = max(bribes)
            
            assert max_bribe <= max_expected, \
                f"For {contraband_value}g contraband, max bribe {max_bribe} should not exceed {max_expected}g"
            assert avg_bribe >= min_expected * 0.5, \
                f"For {contraband_value}g contraband, avg bribe {avg_bribe} should be at least {min_expected * 0.5}g"
