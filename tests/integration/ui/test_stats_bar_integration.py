"""
Integration tests extracted from test_stats_bar.py
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pygame
from ui.stats_bar import StatsBar


class TestStatsBarIntegration:
    """Integration tests for StatsBar"""
    
    def test_full_update_and_render_cycle(self):
        """Test complete update and render cycle"""
        pygame.init()
        screen = pygame.display.set_mode((1200, 800))
        font = pygame.font.Font(None, 20)
        
        stats_bar = StatsBar(screen, font)
        
        # Create mock data
        mock_sheriff = Mock()
        mock_sheriff.reputation = 8
        mock_sheriff.perception = 9
        mock_sheriff.experience = 300
        
        mock_stats = Mock()
        mock_stats.smugglers_caught = 10
        mock_stats.bribes_accepted = 5
        mock_stats.gold_earned = 500
        
        # Update and render
        stats_bar.update(
            sheriff=mock_sheriff,
            stats=mock_stats,
            merchant_count=7,
            total_merchants=15
        )
        stats_bar.render()
        
        # Verify state
        assert stats_bar.sheriff == mock_sheriff
        assert stats_bar.stats == mock_stats
        assert stats_bar.merchant_count == 7
        assert stats_bar.total_merchants == 15
        
        pygame.quit()
    
    def test_multiple_updates(self):
        """Test multiple updates to stats bar"""
        pygame.init()
        screen = pygame.display.set_mode((1200, 800))
        font = pygame.font.Font(None, 20)
        
        stats_bar = StatsBar(screen, font)
        
        mock_sheriff = Mock()
        mock_sheriff.reputation = 5
        mock_sheriff.perception = 6
        mock_sheriff.experience = 100
        
        # First update
        stats_bar.update(sheriff=mock_sheriff, merchant_count=1, total_merchants=10)
        stats_bar.render()
        
        # Update sheriff stats
        mock_sheriff.reputation = 7
        mock_sheriff.experience = 150
        
        # Second update
        stats_bar.update(sheriff=mock_sheriff, merchant_count=2, total_merchants=10)
        stats_bar.render()
        
        # Verify updated values
        assert stats_bar.sheriff.reputation == 7
        assert stats_bar.sheriff.experience == 150
        assert stats_bar.merchant_count == 2
        
        pygame.quit()
    
    def test_render_without_stats_object(self):
        """Test rendering when stats object is None"""
        pygame.init()
        screen = pygame.display.set_mode((1200, 800))
        font = pygame.font.Font(None, 20)
        
        stats_bar = StatsBar(screen, font)
        
        mock_sheriff = Mock()
        mock_sheriff.reputation = 7
        mock_sheriff.perception = 8
        mock_sheriff.experience = 100
        
        # Update with sheriff but no stats
        stats_bar.update(sheriff=mock_sheriff, stats=None)
        
        # Should render without errors (stats section won't display)
        stats_bar.render()
        
        pygame.quit()
