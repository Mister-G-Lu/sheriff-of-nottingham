"""
Pygame Window Management
Handles window initialization, rendering, and portrait display
"""

import pygame
import sys
from pathlib import Path
from typing import Optional

from core.constants import (
    # Colors
    BLACK, WHITE, GREEN, DARK_GREEN, GRAY, DARK_GRAY, LIGHT_GRAY,
    # Screen dimensions
    SCREEN_WIDTH, SCREEN_HEIGHT,
    # Portrait layout
    PORTRAIT_WIDTH, PORTRAIT_HEIGHT, PORTRAIT_Y,
    TITLE_PORTRAIT_WIDTH, TITLE_PORTRAIT_HEIGHT, TITLE_PORTRAIT_Y,
    # Text box layout
    TEXT_BOX_X, TEXT_BOX_Y, TEXT_BOX_WIDTH, TEXT_BOX_HEIGHT,
    # Fonts
    FONT_SIZE_SMALL, FONT_SIZE_NORMAL, FONT_SIZE_LARGE, FONT_SIZE_TITLE,
    # Animation
    PORTRAIT_SLIDE_SPEED, PORTRAIT_INITIAL_OFFSET
)


class PygameWindow:
    """Handles Pygame window initialization and rendering"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Sheriff of Nottingham")
        
        # Get project root for loading assets (must be set before loading fonts)
        self.project_root = Path(__file__).parent.parent
        
        # Load fonts
        self.font_normal = pygame.font.Font(None, FONT_SIZE_NORMAL)
        self.font_large = pygame.font.Font(None, FONT_SIZE_LARGE)
        self.font_small = pygame.font.Font(None, FONT_SIZE_SMALL)
        
        # Load title font - try Cinzel first, then fall back to system fonts
        self.font_title = None
        cinzel_path = self.project_root / 'assets' / 'fonts' / 'Cinzel-Regular.ttf'
        
        # Try to load Cinzel font
        if cinzel_path.exists():
            try:
                loaded_font = pygame.font.Font(str(cinzel_path), FONT_SIZE_TITLE)
                # Validate the font works by rendering a test
                test_surface = loaded_font.render("TEST", True, WHITE)
                if test_surface is not None:
                    self.font_title = loaded_font
            except Exception as e:
                pass  # Silently fall back to system font
        
        # Use system font if Cinzel didn't load (more reliable)
        if self.font_title is None:
            # Try multiple font options in order of preference
            for font_name in ['Georgia', 'Times New Roman', 'Palatino', 'serif', 'arial']:
                try:
                    self.font_title = pygame.font.SysFont(font_name, FONT_SIZE_TITLE, bold=True)
                    # Test that it works
                    test = self.font_title.render("TEST", True, WHITE)
                    if test is not None:
                        break
                except:
                    continue
            
            # Last resort: use the large font we already loaded
            if self.font_title is None:
                self.font_title = self.font_large
        
        # Current portrait
        self.current_portrait: Optional[pygame.Surface] = None
        self.portrait_slide_offset: int = PORTRAIT_INITIAL_OFFSET  # For slide-in effect (starts off-screen left)
        self.portrait_slide_speed: int = PORTRAIT_SLIDE_SPEED  # Pixels per frame
        
        # Clock for frame rate
        self.clock = pygame.time.Clock()
        
        # Load marketplace background
        self.marketplace_background: Optional[pygame.Surface] = None
        self._load_marketplace_background()
    
    def load_portrait_file(self, portrait_filename: str) -> bool:
        """Load a portrait PNG directly by filename from characters/portraits folder"""
        portrait_path = self.project_root / 'characters' / 'portraits' / portrait_filename
        
        try:
            # Load and scale the portrait
            portrait = pygame.image.load(str(portrait_path))
            # Scale to fit portrait area while maintaining aspect ratio
            portrait = pygame.transform.scale(portrait, (PORTRAIT_WIDTH, PORTRAIT_HEIGHT))
            # Convert to surface with alpha channel
            portrait = portrait.convert_alpha()
            self.current_portrait = portrait
            self.portrait_slide_offset = -PORTRAIT_WIDTH  # Start off-screen left
            return True
        except (pygame.error, FileNotFoundError) as e:
            print(f"Warning: Could not load portrait {portrait_path}: {e}")
            self.current_portrait = None
            return False
    
    def load_portrait(self, character_name: str) -> bool:
        """Load a character portrait PNG from the characters/portraits folder (legacy method)"""
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
        
        # Use the new load_portrait_file method
        return self.load_portrait_file(portrait_file)
    
    def clear_portrait(self):
        """Clear the current portrait"""
        self.current_portrait = None
        self.portrait_slide_offset = -PORTRAIT_WIDTH
    
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
        """Display title screen with title centered at top, directly above sheriff portrait"""
        # Clear screen
        self.screen.fill(BLACK)
        
        # Use Cinzel font for the title (with validation)
        title_font = self.font_title
        if title_font is None or not hasattr(title_font, 'render'):
            title_font = self.font_large
        
        # Split title into lines
        lines = title_text.strip().split('\n')
        
        # Calculate title position - centered at top with some padding
        title_top_padding = 80
        y_offset = title_top_padding
        
        # Render title text centered at top
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            try:
                # Render title text
                text_surface = title_font.render(line, True, WHITE)
                
                # Center text horizontally
                text_rect = text_surface.get_rect()
                text_rect.centerx = SCREEN_WIDTH // 2
                text_rect.y = y_offset
                
                self.screen.blit(text_surface, text_rect)
                y_offset += text_surface.get_height() + 15
            except pygame.error as e:
                # In headless mode, font rendering may fail
                # Check if we're in headless mode before skipping
                import os
                if os.environ.get('SDL_VIDEODRIVER') == 'dummy':
                    y_offset += 50  # Add approximate spacing in headless mode
                else:
                    # In normal mode, print error and try with fallback font
                    print(f"Warning: Title rendering failed: {e}")
                    try:
                        fallback_surface = self.font_large.render(line, True, WHITE)
                        text_rect = fallback_surface.get_rect()
                        text_rect.centerx = SCREEN_WIDTH // 2
                        text_rect.y = y_offset
                        self.screen.blit(fallback_surface, text_rect)
                        y_offset += fallback_surface.get_height() + 15
                    except:
                        y_offset += 50
        
        # Load and display sheriff portrait centered below title
        sheriff_path = self.project_root / 'characters' / 'portraits' / 'sheriff.png'
        try:
            sheriff_portrait = pygame.image.load(str(sheriff_path))
            # Scale portrait
            sheriff_portrait = pygame.transform.scale(sheriff_portrait, 
                                                     (TITLE_PORTRAIT_WIDTH, TITLE_PORTRAIT_HEIGHT))
            
            # Position portrait centered horizontally, below the title
            portrait_x = (SCREEN_WIDTH - TITLE_PORTRAIT_WIDTH) // 2
            portrait_y = y_offset + 40  # Add some spacing below title
            
            self.screen.blit(sheriff_portrait, (portrait_x, portrait_y))
            
            # Draw border around portrait
            pygame.draw.rect(self.screen, GRAY, 
                           (portrait_x - 2, portrait_y - 2, 
                            TITLE_PORTRAIT_WIDTH + 4, TITLE_PORTRAIT_HEIGHT + 4), 2)
        except (pygame.error, FileNotFoundError):
            pass  # Skip if portrait not found
        
        pygame.display.flip()
    
    def render_portrait(self):
        """Render the current portrait with slide-in effect from left"""
        if self.current_portrait:
            # Calculate target position (centered horizontally)
            target_x = (SCREEN_WIDTH - PORTRAIT_WIDTH) // 2
            
            # Gradually slide in from left
            if self.portrait_slide_offset < 0:
                self.portrait_slide_offset = min(0, self.portrait_slide_offset + self.portrait_slide_speed)
            
            # Current X position (target + offset)
            current_x = target_x + self.portrait_slide_offset
            
            # Draw portrait at current position
            self.screen.blit(self.current_portrait, (current_x, PORTRAIT_Y))
            
            # Draw border around portrait
            pygame.draw.rect(self.screen, GRAY, 
                           (current_x - 2, PORTRAIT_Y - 2, 
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
        """Close the pygame window."""
        import os
        pygame.quit()
        # Clean up SDL environment variable if it was set
        if hasattr(self, 'headless') and self.headless:
            os.environ.pop('SDL_VIDEODRIVER', None)
