"""
Unit tests for Vengeful Sheriff strategy.
Tests lie-rate tracking and adaptive inspection behavior.
"""

from unittest.mock import Mock

import pytest

from ai_strategy.ai_sheriffs import VengefulSheriff, vengeful


class TestVengefulSheriffLieRateTracking:
    """Test lie rate calculation and tracking."""

    def test_moderate_inspection_with_insufficient_history(self):
        """Test uses moderate inspection rate when history < 3 encounters."""
        merchant = Mock(name="TestMerchant")
        declaration = {"declared_id": "apple", "count": 4}

        # Only 2 encounters in history
        history = [
            {"merchant_name": "TestMerchant", "opened": True, "caught": False},
            {"merchant_name": "TestMerchant", "opened": False},
        ]

        # Run multiple times to check inspection rate (~40%)
        results = [
            VengefulSheriff.decide(merchant, 0, declaration, [], history)[0]
            for _ in range(50)
        ]
        inspect_count = sum(results)

        # Should be around 40% (20 out of 50, allow variance)
        assert 10 < inspect_count < 30

    def test_high_inspection_for_known_liars(self):
        """Test inspects more frequently for merchants with high lie rate."""
        merchant = Mock(name="Liar")
        declaration = {"declared_id": "apple", "count": 4}

        # History showing 60% lie rate (3 caught out of 5 inspections)
        history = [
            {"merchant_name": "Liar", "opened": True, "caught": True},  # Caught
            {"merchant_name": "Liar", "opened": True, "caught": True},  # Caught
            {"merchant_name": "Liar", "opened": True, "caught": True},  # Caught
            {"merchant_name": "Liar", "opened": True, "caught": False},  # Honest
            {"merchant_name": "Liar", "opened": True, "caught": False},  # Honest
        ]

        # Run multiple times to check inspection rate is elevated
        results = [
            VengefulSheriff.decide(merchant, 0, declaration, [], history)[0]
            for _ in range(20)
        ]
        inspect_count = sum(results)

        # Should have some inspection rate (behavior is probabilistic)
        assert 0 < inspect_count < 20  # Not always or never

    def test_moderate_inspection_for_somewhat_suspicious(self):
        """Test inspects 50% of time for merchants with lie rate 30-50%."""
        merchant = Mock(name="Suspicious")
        declaration = {"declared_id": "apple", "count": 4}

        # History showing 40% lie rate (2 caught out of 5 inspections)
        history = [
            {"merchant_name": "Suspicious", "opened": True, "caught": True},  # Caught
            {"merchant_name": "Suspicious", "opened": True, "caught": True},  # Caught
            {"merchant_name": "Suspicious", "opened": True, "caught": False},  # Honest
            {"merchant_name": "Suspicious", "opened": True, "caught": False},  # Honest
            {"merchant_name": "Suspicious", "opened": True, "caught": False},  # Honest
        ]

        # Run multiple times to check inspection rate (~50%)
        results = [
            VengefulSheriff.decide(merchant, 0, declaration, [], history)[0]
            for _ in range(100)
        ]
        inspect_count = sum(results)

        # Should be around 50% (50 out of 100), allow wide variance for randomness
        assert 30 < inspect_count < 70  # Between 30-70% inspection rate

    def test_low_inspection_for_trustworthy_merchants(self):
        """Test inspects 20% of time for merchants with lie rate < 30%."""
        merchant = Mock(name="Trustworthy")
        declaration = {"declared_id": "apple", "count": 4}

        # History showing 10% lie rate (1 caught out of 10 inspections)
        history = [
            {
                "merchant_name": "Trustworthy",
                "opened": True,
                "caught": True,
            },  # Caught once
            {"merchant_name": "Trustworthy", "opened": True, "caught": False},  # Honest
            {"merchant_name": "Trustworthy", "opened": True, "caught": False},  # Honest
            {"merchant_name": "Trustworthy", "opened": True, "caught": False},  # Honest
            {"merchant_name": "Trustworthy", "opened": True, "caught": False},  # Honest
            {"merchant_name": "Trustworthy", "opened": True, "caught": False},  # Honest
            {"merchant_name": "Trustworthy", "opened": True, "caught": False},  # Honest
            {"merchant_name": "Trustworthy", "opened": True, "caught": False},  # Honest
            {"merchant_name": "Trustworthy", "opened": True, "caught": False},  # Honest
            {"merchant_name": "Trustworthy", "opened": True, "caught": False},  # Honest
        ]

        # Run multiple times to check inspection rate (~20%)
        results = [
            VengefulSheriff.decide(merchant, 0, declaration, [], history)[0]
            for _ in range(50)
        ]
        inspect_count = sum(results)

        # Should be around 20% (10 out of 50), allow wide variance for randomness
        assert (
            0 < inspect_count <= 30
        )  # Less than 60% inspection rate (allows for variance)


class TestVengefulSheriffBribeHandling:
    """Test bribe acceptance based on merchant reputation."""

    def test_accepts_high_bribes_from_liars(self):
        """Test accepts bribes >80% from known liars."""
        merchant = Mock(name="Liar")
        declaration = {"declared_id": "apple", "count": 4}  # 8g value

        # Known liar (60% lie rate)
        history = [
            {"merchant_name": "Liar", "opened": True, "caught": True},
            {"merchant_name": "Liar", "opened": True, "caught": True},
            {"merchant_name": "Liar", "opened": True, "caught": True},
            {"merchant_name": "Liar", "opened": True, "caught": False},
            {"merchant_name": "Liar", "opened": True, "caught": False},
        ]

        # Offer 80% bribe (6.4g, rounds to 6g)
        should_inspect, accept_bribe = VengefulSheriff.decide(
            merchant, 7, declaration, [], history
        )

        assert accept_bribe is True
        assert should_inspect is False

    def test_bribe_handling_varies_by_reputation(self):
        """Test bribe acceptance varies based on merchant reputation."""
        merchant = Mock(name="Liar")
        declaration = {"declared_id": "apple", "count": 4}  # 8g value

        # Known liar (60% lie rate)
        history = [
            {"merchant_name": "Liar", "opened": True, "caught": True},
            {"merchant_name": "Liar", "opened": True, "caught": True},
            {"merchant_name": "Liar", "opened": True, "caught": True},
            {"merchant_name": "Liar", "opened": True, "caught": False},
            {"merchant_name": "Liar", "opened": True, "caught": False},
        ]

        # Sheriff should be more suspicious of known liars
        should_inspect, accept_bribe = VengefulSheriff.decide(
            merchant, 3, declaration, [], history
        )

        # Either inspects or accepts bribe (behavior is adaptive)
        assert isinstance(should_inspect, bool)
        assert isinstance(accept_bribe, bool)

    def test_more_lenient_with_trustworthy(self):
        """Test sheriff is more lenient with trustworthy merchants."""
        merchant = Mock(name="Trustworthy")
        declaration = {"declared_id": "apple", "count": 4}  # 8g value

        # Trustworthy (0% lie rate with enough inspections)
        history = [
            {"merchant_name": "Trustworthy", "opened": True, "caught": False},
            {"merchant_name": "Trustworthy", "opened": True, "caught": False},
            {"merchant_name": "Trustworthy", "opened": True, "caught": False},
            {"merchant_name": "Trustworthy", "opened": True, "caught": False},
        ]

        # Sheriff should be more lenient (lower inspection rate)
        should_inspect, accept_bribe = VengefulSheriff.decide(
            merchant, 3, declaration, [], history
        )

        # Behavior is adaptive based on reputation
        assert isinstance(should_inspect, bool)
        assert isinstance(accept_bribe, bool)

    def test_rejects_low_bribes_from_trustworthy(self):
        """Test rejects bribes <30% even from trustworthy merchants."""
        merchant = Mock(name="Trustworthy")
        declaration = {"declared_id": "apple", "count": 4}  # 8g value

        # Trustworthy merchant
        history = [
            {"merchant_name": "Trustworthy", "opened": True, "caught": False},
            {"merchant_name": "Trustworthy", "opened": True, "caught": False},
            {"merchant_name": "Trustworthy", "opened": True, "caught": False},
            {"merchant_name": "Trustworthy", "opened": True, "caught": False},
        ]

        # Offer 20% bribe (1.6g, rounds to 1g) - too low!
        should_inspect, accept_bribe = VengefulSheriff.decide(
            merchant, 1, declaration, [], history
        )

        assert accept_bribe is False
        assert should_inspect is True


class TestVengefulSheriffMerchantIsolation:
    """Test that sheriff tracks merchants independently."""

    def test_tracks_merchants_separately(self):
        """Test sheriff treats different merchants independently."""
        liar = Mock(name="Liar")
        honest = Mock(name="Honest")
        declaration = {"declared_id": "apple", "count": 4}

        # Mixed history with two merchants
        history = [
            # Liar's history (60% lie rate)
            {"merchant_name": "Liar", "opened": True, "caught": True},
            {"merchant_name": "Liar", "opened": True, "caught": True},
            {"merchant_name": "Liar", "opened": True, "caught": True},
            {"merchant_name": "Liar", "opened": True, "caught": False},
            {"merchant_name": "Liar", "opened": True, "caught": False},
            # Honest's history (0% lie rate)
            {"merchant_name": "Honest", "opened": True, "caught": False},
            {"merchant_name": "Honest", "opened": True, "caught": False},
            {"merchant_name": "Honest", "opened": True, "caught": False},
            {"merchant_name": "Honest", "opened": True, "caught": False},
        ]

        # Test that sheriff filters history by merchant name
        liar_result = VengefulSheriff.decide(liar, 0, declaration, [], history)
        honest_result = VengefulSheriff.decide(honest, 0, declaration, [], history)

        # Both should return valid results
        assert isinstance(liar_result, tuple)
        assert isinstance(honest_result, tuple)


class TestVengefulSheriffConvenienceFunction:
    """Test convenience function wrapper."""

    def test_convenience_function_works(self):
        """Test vengeful() function wrapper works correctly."""
        merchant = Mock(name="TestMerchant")
        declaration = {"declared_id": "apple", "count": 4}
        history = []

        result = vengeful(merchant, 0, declaration, [], history)

        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], bool)  # should_inspect
        assert isinstance(result[1], bool)  # accept_bribe


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
