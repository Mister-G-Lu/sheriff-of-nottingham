"""
Pygame Text Display
Handles text rendering, typewriter effect, and scrolling
"""

import pygame
import sys
import time
from typing import List

# Import constants from window module
from ui.pygame_window import (
    BLACK, WHITE, GREEN, GRAY, DARK_GRAY,
    TEXT_BOX_X, TEXT_BOX_Y, TEXT_BOX_WIDTH, TEXT_BOX_HEIGHT,
    FONT_SIZE_NORMAL, FONT_SIZE_SMALL
)


class PygameText:
    """Handles text display with typewriter effect and scrolling"""
    
    def __init__(self, window):
        self.window = window
        
        # Text state
        self.text_lines: List[str] = []
        self.text_scroll_offset: int = 0
        
        # Text display speed settings
        self.text_speed_wpm: int = 500  # Words per minute (increased for smoother feel)
        self.text_display_complete: bool = True
    
    def wrap_text(self, text: str, max_width: int, font: pygame.font.Font) -> List[str]:
        """Wrap text to fit within a given width"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            # Test if adding this word exceeds max width
            test_line = ' '.join(current_line + [word])
            test_surface = font.render(test_line, True, WHITE)
            
            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                # Start a new line
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        # Add the last line
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def display_text(self, text: str, clear_previous: bool = True, animate: bool = True):
        """Display text in the text box area with optional typewriter effect"""
        if clear_previous:
            self.text_lines = []
            self.text_scroll_offset = 0
        
        # Skip empty text
        if not text or not text.strip():
            self.render()
            return
        
        # Split by newlines first to preserve intentional line breaks
        lines = text.split('\n')
        
        # Collect all wrapped lines
        new_lines = []
        for line in lines:
            if line.strip():  # Non-empty line
                # Wrap text to fit in text box
                wrapped = self.wrap_text(line, TEXT_BOX_WIDTH - 40, self.window.font_normal)
                new_lines.extend(wrapped)
            else:  # Empty line - preserve as spacing
                new_lines.append('')
        
        if animate and self.text_speed_wpm > 0:
            # Display text with typewriter effect
            self._display_text_animated(new_lines)
        else:
            # Display text immediately
            self.text_lines.extend(new_lines)
            
            # Auto-scroll to bottom when new text is added
            max_lines = (TEXT_BOX_HEIGHT - 40) // (FONT_SIZE_NORMAL + 5)
            if len(self.text_lines) > max_lines:
                self.text_scroll_offset = len(self.text_lines) - max_lines
            
            self.render()
    
    def _display_text_animated(self, new_lines: List[str]):
        """Display text with typewriter effect based on WPM setting"""
        # Calculate delay between words based on WPM (in seconds)
        # WPM = words per minute, so delay = 60 seconds / WPM
        word_delay = 60.0 / self.text_speed_wpm if self.text_speed_wpm > 0 else 0
        
        # Add a brief pause before starting typewriter effect (300ms)
        # This gives the portrait time to start fading in
        initial_pause = 0.3
        pause_start = time.time()
        
        # Wait for initial pause
        while time.time() - pause_start < initial_pause:
            self.window.clock.tick(60)
            self.render()
            # Check for skip during pause
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                    # Skip the pause
                    break
        
        self.text_display_complete = False
        skipped = False
        line_index = 0
        last_word_time = time.time()
        
        while line_index < len(new_lines):
            line = new_lines[line_index]
            
            # Check for skip input (click or key press)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                    skipped = True
                    break
                # Handle scrolling during animation
                if event.type == pygame.MOUSEWHEEL:
                    self._handle_scroll(event.y)
            
            if skipped:
                # Complete current line if it's being typed
                if len(self.text_lines) > 0 and line.strip():
                    self.text_lines[-1] = line
                # Display all remaining lines immediately
                for remaining_line in new_lines[line_index + 1:]:
                    self.text_lines.append(remaining_line)
                break
            
            if not line.strip():
                # Empty line - add immediately
                self.text_lines.append('')
                line_index += 1
                continue
            
            # Split line into words
            words = line.split()
            current_line_words = []
            
            # Add a new line for this sentence
            self.text_lines.append('')
            current_line_index = len(self.text_lines) - 1
            
            for word in words:
                # Check for skip during word display
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                        skipped = True
                        break
                    if event.type == pygame.MOUSEWHEEL:
                        self._handle_scroll(event.y)
                
                if skipped:
                    # Complete the current line with all remaining words
                    self.text_lines[current_line_index] = line
                    # Display all remaining lines
                    for remaining_line in new_lines[line_index + 1:]:
                        self.text_lines.append(remaining_line)
                    break
                
                current_line_words.append(word)
                
                # Update the current line being displayed
                self.text_lines[current_line_index] = ' '.join(current_line_words)
                
                # Auto-scroll to bottom
                max_lines = (TEXT_BOX_HEIGHT - 40) // (FONT_SIZE_NORMAL + 5)
                if len(self.text_lines) > max_lines:
                    self.text_scroll_offset = len(self.text_lines) - max_lines
                
                # Calculate how long to wait for accurate WPM timing
                current_time = time.time()
                elapsed = current_time - last_word_time
                remaining_delay = word_delay - elapsed
                
                if remaining_delay > 0:
                    # Wait the remaining time to achieve target WPM
                    # Use small sleep intervals to keep UI responsive
                    end_time = time.time() + remaining_delay
                    while time.time() < end_time:
                        # Process events during wait to keep UI responsive
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                                skipped = True
                                break
                        if skipped:
                            break
                        time.sleep(0.001)  # 1ms sleep to avoid busy waiting
                
                # Render after delay
                self.render()
                last_word_time = time.time()
            
            if skipped:
                break
            
            line_index += 1
        
        # Auto-scroll to bottom after animation
        max_lines = (TEXT_BOX_HEIGHT - 40) // (FONT_SIZE_NORMAL + 5)
        if len(self.text_lines) > max_lines:
            self.text_scroll_offset = len(self.text_lines) - max_lines
        
        self.text_display_complete = True
        self.render()
    
    def _handle_scroll(self, scroll_amount: int):
        """Handle mouse wheel scrolling"""
        max_lines = (TEXT_BOX_HEIGHT - 40) // (FONT_SIZE_NORMAL + 5)
        max_scroll = max(0, len(self.text_lines) - max_lines)
        self.text_scroll_offset -= scroll_amount * 3
        self.text_scroll_offset = max(0, min(self.text_scroll_offset, max_scroll))
        self.render()
    
    def render(self):
        """Render text in the text box"""
        # Clear screen and render portrait
        self.window.clear_screen()
        self.window.render_portrait()
        
        # Render stats bar and price menu at top (before text box so they're always visible)
        try:
            from ui.pygame_ui import get_ui
            ui = get_ui()
            ui.stats_bar.render()
            ui.price_menu.render()  # Render price menu button
        except:
            pass  # Stats bar/price menu not available
        
        # Draw text box background
        pygame.draw.rect(self.window.screen, DARK_GRAY, 
                        (TEXT_BOX_X, TEXT_BOX_Y, TEXT_BOX_WIDTH, TEXT_BOX_HEIGHT))
        pygame.draw.rect(self.window.screen, GRAY, 
                        (TEXT_BOX_X, TEXT_BOX_Y, TEXT_BOX_WIDTH, TEXT_BOX_HEIGHT), 2)
        
        # Render text lines with scrolling
        y_offset = TEXT_BOX_Y + 20
        max_lines = (TEXT_BOX_HEIGHT - 40) // (FONT_SIZE_NORMAL + 5)
        
        # Calculate which lines to display based on scroll offset
        start_line = self.text_scroll_offset
        end_line = min(start_line + max_lines, len(self.text_lines))
        visible_lines = self.text_lines[start_line:end_line]
        
        for line in visible_lines:
            text_surface = self.window.font_normal.render(line, True, WHITE)
            self.window.screen.blit(text_surface, (TEXT_BOX_X + 20, y_offset))
            y_offset += FONT_SIZE_NORMAL + 5
        
        # Draw scroll indicator if there's more content
        if len(self.text_lines) > max_lines:
            scroll_text = f"[Scroll: {start_line + 1}-{end_line} of {len(self.text_lines)} lines]"
            scroll_surface = self.window.font_small.render(scroll_text, True, GRAY)
            self.window.screen.blit(scroll_surface, (TEXT_BOX_X + TEXT_BOX_WIDTH - 250, TEXT_BOX_Y + 5))
        
        # Draw text display indicator if text is still being animated
        if not self.text_display_complete:
            indicator_text = "[Click or press any key to skip...]"
            indicator_surface = self.window.font_small.render(indicator_text, True, GREEN)
            self.window.screen.blit(indicator_surface, (TEXT_BOX_X + 20, TEXT_BOX_Y + 5))
        
        self.window.update_display()
    
    def clear_text(self):
        """Clear all text from the text box"""
        self.text_lines = []
        self.text_scroll_offset = 0
        self.render()
