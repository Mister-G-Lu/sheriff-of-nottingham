"""
Unit tests for ui/stats_bar.py
Tests the StatsBar class for displaying sheriff and game statistics.
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Setup headless mode before importing pygame modules
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame
from ui.stats_bar import StatsBar

class TestStatsBarInit:
    """Tests for StatsBar initialization"""
    
    def test_init_stores_screen_and_font(self):
        """Test that initialization stores screen and font"""
        pygame.init()
        screen = pygame.display.set_mode((1200, 800))
        font = pygame.font.Font(None, 20)
        
        stats_bar = StatsBar(screen, font)
        
        assert stats_bar.screen == screen
        assert stats_bar.font == font
        assert stats_bar.screen_width == 1200
        
        pygame.quit()
    
    def test_init_default_values(self):
        """Test that initialization sets default values"""
        pygame.init()
        screen = pygame.display.set_mode((1200, 800))
        font = pygame.font.Font(None, 20)
        
        stats_bar = StatsBar(screen, font)
        
        assert stats_bar.sheriff is None
        assert stats_bar.stats is None
        assert stats_bar.merchant_count == 0
        assert stats_bar.total_merchants == 0
        
        pygame.quit()

class TestStatsBarUpdate:
    """Tests for StatsBar.update method"""
    
    def test_update_with_sheriff(self):
        """Test updating with sheriff data"""
        pygame.init()
        screen = pygame.display.set_mode((1200, 800))
        font = pygame.font.Font(None, 20)
        
        stats_bar = StatsBar(screen, font)
        
        mock_sheriff = Mock()
        mock_sheriff.reputation = 7
        mock_sheriff.perception = 8
        mock_sheriff.experience = 100
        
        stats_bar.update(sheriff=mock_sheriff)
        
        assert stats_bar.sheriff == mock_sheriff
        
        pygame.quit()
    
    def test_update_with_stats(self):
        """Test updating with game stats"""
        pygame.init()
        screen = pygame.display.set_mode((1200, 800))
        font = pygame.font.Font(None, 20)
        
        stats_bar = StatsBar(screen, font)
        
        mock_stats = Mock()
        mock_stats.smugglers_caught = 5
        mock_stats.bribes_accepted = 3
        mock_stats.gold_earned = 150
        
        stats_bar.update(stats=mock_stats)
        
        assert stats_bar.stats == mock_stats
        
        pygame.quit()
    
    def test_update_with_merchant_count(self):
        """Test updating with merchant count"""
        pygame.init()
        screen = pygame.display.set_mode((1200, 800))
        font = pygame.font.Font(None, 20)
        
        stats_bar = StatsBar(screen, font)
        
        stats_bar.update(merchant_count=3, total_merchants=10)
        
        assert stats_bar.merchant_count == 3
        assert stats_bar.total_merchants == 10
        
        pygame.quit()
    
    def test_update_with_all_parameters(self):
        """Test updating with all parameters"""
        pygame.init()
        screen = pygame.display.set_mode((1200, 800))
        font = pygame.font.Font(None, 20)
        
        stats_bar = StatsBar(screen, font)
        
        mock_sheriff = Mock()
        mock_sheriff.reputation = 9
        mock_sheriff.perception = 7
        mock_sheriff.experience = 250
        
        mock_stats = Mock()
        mock_stats.smugglers_caught = 8
        mock_stats.bribes_accepted = 2
        mock_stats.gold_earned = 200
        
        stats_bar.update(
            sheriff=mock_sheriff,
            stats=mock_stats,
            merchant_count=5,
            total_merchants=12
        )
        
        assert stats_bar.sheriff == mock_sheriff
        assert stats_bar.stats == mock_stats
        assert stats_bar.merchant_count == 5
        assert stats_bar.total_merchants == 12
        
        pygame.quit()

class TestStatsBarRender:
    """Tests for StatsBar.render method"""
    
    def test_render_without_sheriff_returns_early(self):
        """Test that render returns early if no sheriff data"""
        pygame.init()
        screen = pygame.display.set_mode((1200, 800))
        font = pygame.font.Font(None, 20)
        
        stats_bar = StatsBar(screen, font)
        
        # Should not raise any errors
        stats_bar.render()
        
        pygame.quit()
    
    def test_render_with_sheriff_only(self):
        """Test rendering with only sheriff data"""
        pygame.init()
        screen = pygame.display.set_mode((1200, 800))
        font = pygame.font.Font(None, 20)
        
        stats_bar = StatsBar(screen, font)
        
        mock_sheriff = Mock()
        mock_sheriff.reputation = 7
        mock_sheriff.perception = 8
        mock_sheriff.experience = 100
        
        stats_bar.update(sheriff=mock_sheriff)
        
        # Should not raise any errors
        stats_bar.render()
        
        pygame.quit()
    
    def test_render_with_sheriff_and_stats(self):
        """Test rendering with sheriff and game stats"""
        pygame.init()
        screen = pygame.display.set_mode((1200, 800))
        font = pygame.font.Font(None, 20)
        
        stats_bar = StatsBar(screen, font)
        
        mock_sheriff = Mock()
        mock_sheriff.reputation = 7
        mock_sheriff.perception = 8
        mock_sheriff.experience = 100
        
        mock_stats = Mock()
        mock_stats.smugglers_caught = 5
        mock_stats.bribes_accepted = 3
        mock_stats.gold_earned = 150
        
        stats_bar.update(sheriff=mock_sheriff, stats=mock_stats)
        
        # Should not raise any errors
        stats_bar.render()
        
        pygame.quit()
    
    def test_render_with_merchant_progress(self):
        """Test rendering with merchant progress"""
        pygame.init()
        screen = pygame.display.set_mode((1200, 800))
        font = pygame.font.Font(None, 20)
        
        stats_bar = StatsBar(screen, font)
        
        mock_sheriff = Mock()
        mock_sheriff.reputation = 7
        mock_sheriff.perception = 8
        mock_sheriff.experience = 100
        
        stats_bar.update(
            sheriff=mock_sheriff,
            merchant_count=3,
            total_merchants=10
        )
        
        # Should not raise any errors
        stats_bar.render()
        
        pygame.quit()
    
    def test_render_with_all_data(self):
        """Test rendering with all data"""
        pygame.init()
        screen = pygame.display.set_mode((1200, 800))
        font = pygame.font.Font(None, 20)
        
        stats_bar = StatsBar(screen, font)
        
        mock_sheriff = Mock()
        mock_sheriff.reputation = 9
        mock_sheriff.perception = 7
        mock_sheriff.experience = 250
        
        mock_stats = Mock()
        mock_stats.smugglers_caught = 8
        mock_stats.bribes_accepted = 2
        mock_stats.gold_earned = 200
        
        stats_bar.update(
            sheriff=mock_sheriff,
            stats=mock_stats,
            merchant_count=5,
            total_merchants=12
        )
        
        # Should not raise any errors
        stats_bar.render()
        
        pygame.quit()
    
    def test_render_with_high_reputation(self):
        """Test rendering with high reputation (green color)"""
        pygame.init()
        screen = pygame.display.set_mode((1200, 800))
        font = pygame.font.Font(None, 20)
        
        stats_bar = StatsBar(screen, font)
        
        mock_sheriff = Mock()
        mock_sheriff.reputation = 9  # >= 7, should be green
        mock_sheriff.perception = 8
        mock_sheriff.experience = 100
        
        stats_bar.update(sheriff=mock_sheriff)
        stats_bar.render()
        
        pygame.quit()
    
    def test_render_with_medium_reputation(self):
        """Test rendering with medium reputation (gold color)"""
        pygame.init()
        screen = pygame.display.set_mode((1200, 800))
        font = pygame.font.Font(None, 20)
        
        stats_bar = StatsBar(screen, font)
        
        mock_sheriff = Mock()
        mock_sheriff.reputation = 5  # >= 4 and < 7, should be gold
        mock_sheriff.perception = 8
        mock_sheriff.experience = 100
        
        stats_bar.update(sheriff=mock_sheriff)
        stats_bar.render()
        
        pygame.quit()
    
    def test_render_with_low_reputation(self):
        """Test rendering with low reputation (red color)"""
        pygame.init()
        screen = pygame.display.set_mode((1200, 800))
        font = pygame.font.Font(None, 20)
        
        stats_bar = StatsBar(screen, font)
        
        mock_sheriff = Mock()
        mock_sheriff.reputation = 2  # < 4, should be red
        mock_sheriff.perception = 8
        mock_sheriff.experience = 100
        
        stats_bar.update(sheriff=mock_sheriff)
        stats_bar.render()
        
        pygame.quit()

class TestStatsBarRenderStat:
    """Tests for StatsBar._render_stat helper method"""
    
    def test_render_stat(self):
        """Test rendering a single stat"""
        pygame.init()
        screen = pygame.display.set_mode((1200, 800))
        font = pygame.font.Font(None, 20)
        
        stats_bar = StatsBar(screen, font)
        
        # Should not raise any errors
        stats_bar._render_stat("Test: 100", 10, 10, (255, 255, 255))
        
        pygame.quit()
    
    def test_render_stat_different_colors(self):
        """Test rendering stats with different colors"""
        pygame.init()
        screen = pygame.display.set_mode((1200, 800))
        font = pygame.font.Font(None, 20)
        
        stats_bar = StatsBar(screen, font)
        
        # Test different colors
        stats_bar._render_stat("White", 10, 10, (255, 255, 255))
        stats_bar._render_stat("Green", 100, 10, (0, 255, 0))
        stats_bar._render_stat("Red", 200, 10, (255, 0, 0))
        stats_bar._render_stat("Gold", 300, 10, (255, 215, 0))
        
        pygame.quit()

