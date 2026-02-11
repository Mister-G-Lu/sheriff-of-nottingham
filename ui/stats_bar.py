"""
Stats Bar - Persistent display of sheriff and game stats at top of screen
"""

import pygame
from typing import Optional

from core.constants import (
    # Colors
    WHITE, BLACK, GOLD, GREEN, RED, GRAY, DARK_GRAY,
    # Layout
    STATS_BAR_HEIGHT, STATS_BAR_PADDING, STATS_BAR_MARGIN,
    SCREEN_WIDTH
)


class StatsBar:
    """Displays sheriff stats at the top of the screen"""
    
    def __init__(self, screen: pygame.Surface, font: pygame.font.Font):
        self.screen = screen
        self.font = font
        self.screen_width = screen.get_width()
        
        # Current stats to display
        self.sheriff = None
        self.stats = None
        self.merchant_count = 0
        self.total_merchants = 0
    
    def update(self, sheriff=None, stats=None, merchant_count: int = 0, total_merchants: int = 0):
        """
        Update the stats to display.
        
        Args:
            sheriff: Sheriff object with reputation, perception, experience
            stats: GameStats object with bribes, smugglers caught, etc.
            merchant_count: Current merchant number
            total_merchants: Total merchants in game
        """
        self.sheriff = sheriff
        self.stats = stats
        self.merchant_count = merchant_count
        self.total_merchants = total_merchants
    
    def render(self):
        """Render the stats bar at the top of the screen"""
        if not self.sheriff:
            return  # Don't render if no sheriff data
        
        # Draw background bar
        bar_rect = pygame.Rect(0, 0, self.screen_width, STATS_BAR_HEIGHT)
        pygame.draw.rect(self.screen, DARK_GRAY, bar_rect)
        pygame.draw.line(self.screen, GRAY, (0, STATS_BAR_HEIGHT), 
                        (self.screen_width, STATS_BAR_HEIGHT), 2)
        
        # Calculate positions for stats
        x_pos = STATS_BAR_PADDING
        y_pos = STATS_BAR_PADDING
        
        # Merchant progress (left side)
        if self.total_merchants > 0:
            progress_text = f"Merchant: {self.merchant_count}/{self.total_merchants}"
            self._render_stat(progress_text, x_pos, y_pos, WHITE)
            x_pos += 180
        
        # Reputation (with color coding)
        rep = self.sheriff.reputation
        rep_color = GREEN if rep >= 7 else (GOLD if rep >= 4 else RED)
        rep_text = f"⭐ Reputation: {rep}/10"
        self._render_stat(rep_text, x_pos, y_pos, rep_color)
        x_pos += 180
        
        # Perception
        perception_text = f"👁 Perception: {self.sheriff.perception}/10"
        self._render_stat(perception_text, x_pos, y_pos, WHITE)
        x_pos += 180
        
        # Experience
        exp_text = f"✨ XP: {self.sheriff.experience}"
        self._render_stat(exp_text, x_pos, y_pos, WHITE)
        x_pos += 140
        
        # Game stats (if available)
        if self.stats:
            # Smugglers caught
            caught_text = f"🎯 Caught: {self.stats.smugglers_caught}"
            self._render_stat(caught_text, x_pos, y_pos, GREEN)
            x_pos += 140
            
            # Bribes taken
            if self.stats.bribes_accepted > 0:
                bribe_text = f"💰 Bribes: {self.stats.bribes_accepted} ({self.stats.gold_earned}g)"
                self._render_stat(bribe_text, x_pos, y_pos, GOLD)
    
    def _render_stat(self, text: str, x: int, y: int, color: tuple):
        """Helper to render a single stat"""
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))
