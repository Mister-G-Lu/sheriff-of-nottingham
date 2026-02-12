"""
Unit tests for core/players/sheriff.py
Tests the Sheriff class
"""

# Must be first import - sets up test environment
import os

import tests.test_setup  # noqa: F401

# Setup headless mode
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"


from core.players.sheriff import Sheriff


class TestSheriffInit:
    """Tests for Sheriff initialization"""

    def test_sheriff_default_init(self):
        """Test Sheriff with default values"""
        sheriff = Sheriff()

        assert sheriff.reputation == 5
        assert sheriff.authority == 1
        assert sheriff.perception == 1  # STARTING_PERCEPTION = 1

    def test_sheriff_custom_reputation(self):
        """Test Sheriff with custom reputation"""
        sheriff = Sheriff(reputation=8)

        assert sheriff.reputation == 8
        assert sheriff.authority == 1

    def test_sheriff_custom_authority(self):
        """Test Sheriff with custom authority"""
        sheriff = Sheriff(authority=3)

        assert sheriff.reputation == 5
        assert sheriff.authority == 3

    def test_sheriff_custom_perception(self):
        """Test Sheriff with custom perception"""
        sheriff = Sheriff(perception=7)

        assert sheriff.perception == 7

    def test_sheriff_all_custom(self):
        """Test Sheriff with all custom values"""
        sheriff = Sheriff(reputation=10, authority=5, perception=8)

        assert sheriff.reputation == 10
        assert sheriff.authority == 5
        assert sheriff.perception == 8


class TestSheriffAttributes:
    """Tests for Sheriff attribute manipulation"""

    def test_reputation_can_change(self):
        """Test that reputation can be modified"""
        sheriff = Sheriff(reputation=5)

        sheriff.reputation = 3
        assert sheriff.reputation == 3

        sheriff.reputation = 10
        assert sheriff.reputation == 10

    def test_authority_can_change(self):
        """Test that authority can be modified"""
        sheriff = Sheriff(authority=1)

        sheriff.authority = 5
        assert sheriff.authority == 5

    def test_perception_can_change(self):
        """Test that perception can be modified"""
        sheriff = Sheriff(perception=5)

        sheriff.perception = 10
        assert sheriff.perception == 10

    def test_reputation_floor(self):
        """Test reputation can go to 0"""
        sheriff = Sheriff(reputation=1)

        sheriff.reputation = 0
        assert sheriff.reputation == 0

    def test_reputation_ceiling(self):
        """Test reputation can reach maximum"""
        sheriff = Sheriff(reputation=9)

        sheriff.reputation = 10
        assert sheriff.reputation == 10


class TestSheriffReputationImpact:
    """Tests for how reputation affects gameplay mechanics"""

    def test_reputation_affects_negotiation_threat_level(self):
        """Test that higher reputation increases threat level in negotiations"""
        from core.mechanics.negotiation import create_negotiation_state
        from core.players.merchants import Merchant

        # Create test merchant
        merchant = Merchant(
            id="test",
            name="Test Merchant",
            intro="Test",
            tells_honest=["calm"],
            tells_lying=["nervous"],
            bluff_skill=5,
            risk_tolerance=5,
            greed=5,
            honesty_bias=5,
        )

        # Low reputation sheriff
        low_rep_sheriff = Sheriff(reputation=2, authority=2)
        low_rep_negotiation = create_negotiation_state(
            low_rep_sheriff, merchant, goods_value=20
        )

        # High reputation sheriff
        high_rep_sheriff = Sheriff(reputation=8, authority=2)
        high_rep_negotiation = create_negotiation_state(
            high_rep_sheriff, merchant, goods_value=20
        )

        # Threat level formula: (authority + reputation) // 2
        # Low: (2 + 2) // 2 = 2
        # High: (2 + 8) // 2 = 5
        assert low_rep_negotiation.threat_level == 2
        assert high_rep_negotiation.threat_level == 5
        assert high_rep_negotiation.threat_level > low_rep_negotiation.threat_level

    def test_reputation_and_authority_combined_threat(self):
        """Test that reputation and authority combine for maximum threat"""
        from core.mechanics.negotiation import create_negotiation_state
        from core.players.merchants import Merchant

        merchant = Merchant(
            id="test",
            name="Test",
            intro="Test",
            tells_honest=["calm"],
            tells_lying=["nervous"],
            bluff_skill=5,
            risk_tolerance=5,
            greed=5,
            honesty_bias=5,
        )

        # Maximum reputation and authority
        max_sheriff = Sheriff(reputation=10, authority=10)
        max_negotiation = create_negotiation_state(max_sheriff, merchant, goods_value=20)

        # Threat level capped at 10: min(10, (10 + 10) // 2) = 10
        assert max_negotiation.threat_level == 10

    def test_zero_reputation_sheriff_has_low_threat(self):
        """Test that sheriff with zero reputation has minimal threat"""
        from core.mechanics.negotiation import create_negotiation_state
        from core.players.merchants import Merchant

        merchant = Merchant(
            id="test",
            name="Test",
            intro="Test",
            tells_honest=["calm"],
            tells_lying=["nervous"],
            bluff_skill=5,
            risk_tolerance=5,
            greed=5,
            honesty_bias=5,
        )

        # Zero reputation, minimal authority
        weak_sheriff = Sheriff(reputation=0, authority=1)
        weak_negotiation = create_negotiation_state(
            weak_sheriff, merchant, goods_value=20
        )

        # Threat level: (1 + 0) // 2 = 0
        assert weak_negotiation.threat_level == 0

    def test_reputation_affects_leveling_up(self):
        """Test that sheriff gains experience and perception through leveling"""
        sheriff = Sheriff(experience=0, perception=1)

        # Level up 3 times (perception increases every 3 levels)
        sheriff.level_up(1)
        assert sheriff.experience == 1
        assert sheriff.perception == 1  # Not yet

        sheriff.level_up(1)
        assert sheriff.experience == 2
        assert sheriff.perception == 1  # Not yet

        sheriff.level_up(1)
        assert sheriff.experience == 3
        assert sheriff.perception == 2  # Increased!

    def test_perception_caps_at_10(self):
        """Test that perception doesn't exceed maximum"""
        sheriff = Sheriff(experience=0, perception=9)

        # Level up 3 times
        sheriff.level_up(3)

        # Perception should cap at 10
        assert sheriff.perception == 10

        # Level up more
        sheriff.level_up(3)

        # Should still be capped
        assert sheriff.perception == 10
