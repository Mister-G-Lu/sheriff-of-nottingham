"""
Pygame Window Management
Handles window initialization, rendering, and portrait display
"""

import pygame
import sys
from pathlib import Path
from typing import Optional

# Color definitions
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 180, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (200, 200, 200)

# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

# UI Layout - Gameplay portraits (centered horizontally)
PORTRAIT_WIDTH = 400
PORTRAIT_HEIGHT = 400
PORTRAIT_Y = 60  # Moved down to make room for stats bar

TEXT_BOX_X = 50
TEXT_BOX_Y = 500
TEXT_BOX_WIDTH = SCREEN_WIDTH - 100
TEXT_BOX_HEIGHT = 250

# Title screen layout
TITLE_PORTRAIT_WIDTH = 500
TITLE_PORTRAIT_HEIGHT = 700
TITLE_PORTRAIT_Y = 50

# Fonts
FONT_SIZE_NORMAL = 20
FONT_SIZE_LARGE = 28
FONT_SIZE_SMALL = 16


class PygameWindow:
    """Handles Pygame window initialization and rendering"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Sheriff of Nottingham")
        
        # Load fonts
        self.font_normal = pygame.font.Font(None, FONT_SIZE_NORMAL)
        self.font_large = pygame.font.Font(None, FONT_SIZE_LARGE)
        self.font_small = pygame.font.Font(None, FONT_SIZE_SMALL)
        
        # Current portrait
        self.current_portrait: Optional[pygame.Surface] = None
        self.portrait_alpha: int = 0  # For fade-in effect (0-255)
        self.portrait_fade_speed: int = 15  # Alpha increase per frame
        
        # Clock for frame rate
        self.clock = pygame.time.Clock()
        
        # Get project root for loading assets
        self.project_root = Path(__file__).parent.parent
        
        # Load marketplace background
        self.marketplace_background: Optional[pygame.Surface] = None
        self._load_marketplace_background()
    
    def load_portrait(self, character_name: str) -> bool:
        """Load a character portrait PNG from the characters/portraits folder"""
        # Map character names to PNG files
        portrait_map = {
            'alice': 'baker.png',
            'baker': 'baker.png',
            'benedict': 'trader.png',
            'trader': 'trader.png',
            'cedric': 'blacksmith.png',
            'blacksmith': 'blacksmith.png',
            'broker': 'broker.png',
            'silas': 'broker.png',
            'sheriff': 'sheriff.png',
        }
        
        # Try to find the portrait file
        char_lower = character_name.lower()
        portrait_file = None
        
        for key, filename in portrait_map.items():
            if key in char_lower:
                portrait_file = filename
                break
        
        if not portrait_file:
            # Default to no portrait
            self.current_portrait = None
            return False
        
        portrait_path = self.project_root / 'characters' / 'portraits' / portrait_file
        
        try:
            # Load and scale the portrait
            portrait = pygame.image.load(str(portrait_path))
            # Scale to fit portrait area while maintaining aspect ratio
            portrait = pygame.transform.scale(portrait, (PORTRAIT_WIDTH, PORTRAIT_HEIGHT))
            # Convert to surface with alpha channel for fade effect
            portrait = portrait.convert_alpha()
            self.current_portrait = portrait
            self.portrait_alpha = 0  # Start fade-in from transparent
            return True
        except (pygame.error, FileNotFoundError) as e:
            print(f"Warning: Could not load portrait {portrait_path}: {e}")
            self.current_portrait = None
            return False
    
    def clear_portrait(self):
        """Clear the current portrait"""
        self.current_portrait = None
        self.portrait_alpha = 0
    
    def _load_marketplace_background(self):
        """Load and prepare the marketplace background image"""
        marketplace_path = self.project_root / 'characters' / 'portraits' / 'marketplace.png'
        try:
            # Load the image
            bg_image = pygame.image.load(str(marketplace_path))
            # Scale to screen size
            bg_image = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            # Create a surface with alpha channel for opacity
            self.marketplace_background = bg_image.copy()
            self.marketplace_background.set_alpha(int(255 * 0.4))  # opacity
        except (pygame.error, FileNotFoundError) as e:
            print(f"Warning: Could not load marketplace background: {e}")
            self.marketplace_background = None
    
    def show_title_screen(self, title_text: str):
        """Display title screen with title on left half and sheriff portrait on right half"""
        # Clear screen
        self.screen.fill(BLACK)
        
        # Calculate half-screen positions
        left_half_center = SCREEN_WIDTH // 4
        right_half_start = SCREEN_WIDTH // 2
        right_half_center = right_half_start + (SCREEN_WIDTH // 4)
        
        # Load and display sheriff portrait on right half
        sheriff_path = self.project_root / 'characters' / 'portraits' / 'sheriff.png'
        try:
            sheriff_portrait = pygame.image.load(str(sheriff_path))
            # Scale to fit right half
            sheriff_portrait = pygame.transform.scale(sheriff_portrait, 
                                                     (TITLE_PORTRAIT_WIDTH, TITLE_PORTRAIT_HEIGHT))
            
            # Position in right half (centered in that half)
            portrait_x = right_half_center - (TITLE_PORTRAIT_WIDTH // 2)
            self.screen.blit(sheriff_portrait, (portrait_x, TITLE_PORTRAIT_Y))
            
            # Draw border around portrait
            pygame.draw.rect(self.screen, GRAY, 
                           (portrait_x - 2, TITLE_PORTRAIT_Y - 2, 
                            TITLE_PORTRAIT_WIDTH + 4, TITLE_PORTRAIT_HEIGHT + 4), 2)
        except (pygame.error, FileNotFoundError):
            pass  # Skip if portrait not found
        
        # Display title text on left half - large and centered vertically
        # Use a larger custom font for the title
        try:
            title_font = pygame.font.Font(None, 56)
        except:
            title_font = self.font_large
        
        # Split title into lines
        lines = title_text.strip().split('\n')
        
        # Calculate vertical center
        y_offset = SCREEN_HEIGHT // 2 - 50
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Render title text
            text_surface = title_font.render(line, True, WHITE)
            
            # Center text in left half
            text_rect = text_surface.get_rect()
            text_rect.centerx = left_half_center
            text_rect.y = y_offset
            
            self.screen.blit(text_surface, text_rect)
            y_offset += text_surface.get_height() + 15
        
        pygame.display.flip()
    
    def render_portrait(self):
        """Render the current portrait with fade-in effect (centered horizontally)"""
        if self.current_portrait:
            portrait_x = (SCREEN_WIDTH - PORTRAIT_WIDTH) // 2
            
            # Gradually increase alpha for fade-in effect
            if self.portrait_alpha < 255:
                self.portrait_alpha = min(255, self.portrait_alpha + self.portrait_fade_speed)
            
            # Create a copy with current alpha level
            portrait_surface = self.current_portrait.copy()
            portrait_surface.set_alpha(self.portrait_alpha)
            
            self.screen.blit(portrait_surface, (portrait_x, PORTRAIT_Y))
            
            # Draw border around portrait (also fade in)
            if self.portrait_alpha > 50:  # Only show border after portrait is somewhat visible
                border_alpha = min(255, self.portrait_alpha)
                border_color = (*GRAY[:3], border_alpha) if len(GRAY) == 4 else GRAY
                pygame.draw.rect(self.screen, GRAY, 
                               (portrait_x - 2, PORTRAIT_Y - 2, 
                                PORTRAIT_WIDTH + 4, PORTRAIT_HEIGHT + 4), 2)
    
    def clear_screen(self):
        """Clear the screen to black and render background if available"""
        self.screen.fill(BLACK)
        # Draw marketplace background if loaded (during gameplay, not title screen)
        if self.marketplace_background:
            self.screen.blit(self.marketplace_background, (0, 0))
    
    def update_display(self):
        """Update the pygame display"""
        pygame.display.flip()
    
    def handle_events(self):
        """Handle basic pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
    
    def close(self):
        """Close the pygame window"""
        pygame.quit()
