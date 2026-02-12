"""
Unit tests for merchant bribe calculation logic
Tests that bribes are reasonable relative to goods values
"""

# Must be first import - sets up test environment
import tests.test_setup  # noqa: F401
from core.mechanics.goods import APPLE, BREAD, CROSSBOW, SILK
from core.players.merchants import Merchant


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
            honesty_bias=5,
        )

        # Scenario: 3x Bread + 1x Crossbow
        actual_goods = [BREAD, BREAD, BREAD, CROSSBOW]
        contraband_value = sum(g.value for g in actual_goods if not g.is_legal())

        # Run multiple times to check range
        bribes = []
        for _ in range(20):
            bribe = merchant.calculate_proactive_bribe(
                actual_goods=actual_goods, is_lying=True, sheriff_authority=1
            )
            bribes.append(bribe)

        avg_bribe = sum(bribes) / len(bribes)
        max(bribes)
        min_bribe = min(bribes)

        # Moderate risk tolerance should offer reasonable bribes
        assert min_bribe >= 1, f"Minimum bribe {min_bribe} should be at least 1 gold"
        # Bribes should be reasonable relative to contraband value
        assert avg_bribe < contraband_value * 0.8, (
            f"Average bribe {avg_bribe} should be less than 80% of contraband value ({contraband_value}g)"
        )

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
            honesty_bias=5,
        )

        # Scenario: 3x Crossbow
        actual_goods = [CROSSBOW, CROSSBOW, CROSSBOW]
        contraband_value = sum(g.value for g in actual_goods if not g.is_legal())

        bribes = []
        for _ in range(20):
            bribe = merchant.calculate_proactive_bribe(
                actual_goods=actual_goods, is_lying=True, sheriff_authority=1
            )
            bribes.append(bribe)

        avg_bribe = sum(bribes) / len(bribes)
        max(bribes)

        # For high-value contraband with moderate risk tolerance, bribes should be reasonable
        assert avg_bribe >= 2, f"Average bribe {avg_bribe} should be at least 2 gold"
        # Bribes should be a reasonable fraction of contraband value
        assert avg_bribe < contraband_value * 0.8, (
            f"Average bribe {avg_bribe} should be less than 80% of contraband value ({contraband_value}g)"
        )

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
            honesty_bias=5,
        )

        # Scenario: 3x Bread (9g) but lying about what's declared
        actual_goods = [BREAD, BREAD, BREAD]

        bribes = []
        for _ in range(20):
            bribe = merchant.calculate_proactive_bribe(
                actual_goods=actual_goods,
                is_lying=True,  # Lying about legal goods
                sheriff_authority=1,
            )
            bribes.append(bribe)

        avg_bribe = sum(bribes) / len(bribes)
        max_bribe = max(bribes)

        # Should be small amount (2-5g range)
        assert max_bribe <= 6, (
            f"Maximum bribe {max_bribe} should be small for legal goods lie"
        )
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
            honesty_bias=5,
        )

        # Scenario: 3x Apple (6g) and being honest
        actual_goods = [APPLE, APPLE, APPLE]

        bribes = []
        for _ in range(20):
            bribe = merchant.calculate_proactive_bribe(
                actual_goods=actual_goods,
                is_lying=False,  # Honest
                sheriff_authority=1,
            )
            bribes.append(bribe)

        avg_bribe = sum(bribes) / len(bribes)
        max_bribe = max(bribes)

        # Should be very small goodwill amount (1-3g)
        assert max_bribe <= 4, (
            f"Maximum bribe {max_bribe} should be very small for honest merchant"
        )
        assert avg_bribe >= 1, f"Average bribe {avg_bribe} should be at least 1 gold"
        assert avg_bribe <= 3, (
            f"Average bribe {avg_bribe} should be small goodwill gesture (1-3g)"
        )

    def test_bribe_is_reasonable_for_cautious_merchant(self):
        """Test that even very cautious merchants offer reasonable bribes"""
        merchant = Merchant(
            id="test",
            name="Test Merchant",
            intro="Test",
            tells_honest=["honest"],
            tells_lying=["lying"],
            risk_tolerance=0,  # Very cautious (would offer a lot)
            greed=0,
            honesty_bias=0,
        )

        # Scenario: High value contraband
        actual_goods = [CROSSBOW, CROSSBOW]
        contraband_value = sum(g.value for g in actual_goods if not g.is_legal())

        bribes = []
        for _ in range(20):
            bribe = merchant.calculate_proactive_bribe(
                actual_goods=actual_goods,
                is_lying=True,
                sheriff_authority=5,  # High authority (increases bribe)
            )
            bribes.append(bribe)

        max(bribes)
        avg_bribe = sum(bribes) / len(bribes)

        # Even very cautious merchants should offer reasonable bribes
        # (Game allows bribes to exceed contraband value as a strategic choice)
        assert avg_bribe >= contraband_value * 0.3, (
            f"Average bribe {avg_bribe} should be at least 30% of contraband value ({contraband_value}g) for cautious merchant"
        )
        assert avg_bribe <= contraband_value * 1.5, (
            f"Average bribe {avg_bribe} should not be excessive (max 150% of contraband value {contraband_value}g)"
        )

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
            honesty_bias=5,
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
            honesty_bias=5,
        )

        actual_goods = [SILK, SILK]  # 12g contraband

        # Get average bribes for each
        cautious_bribes = [
            cautious.calculate_proactive_bribe(actual_goods, True, 1) for _ in range(20)
        ]
        bold_bribes = [
            bold.calculate_proactive_bribe(actual_goods, True, 1) for _ in range(20)
        ]

        avg_cautious = sum(cautious_bribes) / len(cautious_bribes)
        avg_bold = sum(bold_bribes) / len(bold_bribes)

        # Cautious merchant should offer significantly more than bold merchant
        assert avg_cautious > avg_bold * 1.5, (
            f"Cautious merchant (avg {avg_cautious}g) should offer significantly more than bold merchant (avg {avg_bold}g)"
        )

        # Bold merchant might offer 0 sometimes
        assert min(bold_bribes) == 0 or min(bold_bribes) < 3, (
            f"Bold merchant should sometimes offer very little or nothing (min: {min(bold_bribes)}g)"
        )

        # Cautious merchant should offer substantial bribes
        assert avg_cautious > 5, (
            f"Cautious merchant should offer substantial bribes (avg: {avg_cautious}g)"
        )

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
            honesty_bias=5,
        )

        # Test various contraband scenarios with moderate risk tolerance
        # Moderate risk (5) should offer reasonable bribes relative to contraband value
        test_cases = [
            [SILK],  # 1x Silk
            [CROSSBOW],  # 1x Crossbow
            [SILK, SILK],  # 2x Silk
            [CROSSBOW, CROSSBOW],  # 2x Crossbow
        ]

        for goods in test_cases:
            contraband_value = sum(g.value for g in goods if not g.is_legal())
            bribes = [
                merchant.calculate_proactive_bribe(goods, True, 1) for _ in range(10)
            ]
            avg_bribe = sum(bribes) / len(bribes)
            max(bribes)

            # Bribes should be reasonable relative to contraband value
            assert avg_bribe >= 1, (
                f"For {contraband_value}g contraband, avg bribe {avg_bribe} should be at least 1g"
            )
            assert avg_bribe <= contraband_value * 0.8, (
                f"For {contraband_value}g contraband, avg bribe {avg_bribe} should not exceed 80% of contraband value"
            )
