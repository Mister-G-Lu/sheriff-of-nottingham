"""
Simple tests for reputation system.
"""

import pytest

from core.mechanics.goods import SILK
from core.players.sheriff import Sheriff
from core.systems.reputation import update_sheriff_reputation


class TestReputationUpdates:
    """Test reputation update logic."""

    def test_reputation_increases_on_catching_liar(self):
        """Test reputation increases when catching a liar."""
        sheriff = Sheriff(perception=5, reputation=5)
        initial_rep = sheriff.reputation

        # Catch a liar
        update_sheriff_reputation(sheriff, inspected=True, is_honest=False)

        assert sheriff.reputation > initial_rep

    def test_reputation_decreases_on_false_accusation(self):
        """Test reputation decreases on false accusation."""
        sheriff = Sheriff(perception=5, reputation=5)
        initial_rep = sheriff.reputation

        # Wrongly accuse honest merchant
        update_sheriff_reputation(sheriff, inspected=True, is_honest=True)

        assert sheriff.reputation < initial_rep

    def test_reputation_increases_on_trusting_honest(self):
        """Test reputation increases when trusting honest merchant."""
        sheriff = Sheriff(perception=5, reputation=5)
        initial_rep = sheriff.reputation

        # Trust honest merchant
        update_sheriff_reputation(sheriff, inspected=False, is_honest=True)

        assert sheriff.reputation >= initial_rep

    def test_reputation_decreases_on_missing_contraband(self):
        """Test reputation decreases when contraband slips through."""
        sheriff = Sheriff(perception=5, reputation=5)
        initial_rep = sheriff.reputation

        # Miss contraband
        actual_goods = [SILK, SILK]  # Contraband
        update_sheriff_reputation(
            sheriff, inspected=False, is_honest=False, actual_goods=actual_goods
        )

        assert sheriff.reputation < initial_rep

    def test_reputation_bounded_at_10(self):
        """Test reputation doesn't exceed 10."""
        sheriff = Sheriff(perception=5, reputation=10)

        # Try to increase beyond 10
        update_sheriff_reputation(sheriff, inspected=True, is_honest=False)

        assert sheriff.reputation <= 10

    def test_reputation_bounded_at_0(self):
        """Test reputation doesn't go below 0."""
        sheriff = Sheriff(perception=5, reputation=0)

        # Try to decrease below 0
        actual_goods = [SILK, SILK]
        update_sheriff_reputation(
            sheriff, inspected=False, is_honest=False, actual_goods=actual_goods
        )

        assert sheriff.reputation >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
