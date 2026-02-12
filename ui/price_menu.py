"""
Price Menu - Shows all goods and contraband prices
Accessible via button on right side of screen
"""

import pygame

from core.mechanics.goods import ALL_CONTRABAND, ALL_LEGAL
from ui.ui_constants import (
    DARK_GRAY,
    DARK_GREEN,
    DARK_RED,
    GRAY,
    GREEN,
    LIGHT_GRAY,
    PRICE_BUTTON_HEIGHT,
    PRICE_BUTTON_MARGIN,
    PRICE_BUTTON_WIDTH,
    PRICE_BUTTON_Y_OFFSET,
    PRICE_MENU_HEIGHT,
    PRICE_MENU_WIDTH,
    PRICE_MENU_Y_OFFSET,
    RED,
    WHITE,
)


class PriceMenu:
    """Displays a price reference menu for goods and contraband"""

    def __init__(self, screen, font_normal, font_small):
        self.screen = screen
        self.font_normal = font_normal
        self.font_small = font_small

        # Button position (top right corner, below stats bar)
        self.button_width = PRICE_BUTTON_WIDTH
        self.button_height = PRICE_BUTTON_HEIGHT
        self.button_x = screen.get_width() - self.button_width - PRICE_BUTTON_MARGIN
        self.button_y = PRICE_BUTTON_Y_OFFSET
        self.button_rect = pygame.Rect(
            self.button_x, self.button_y, self.button_width, self.button_height
        )

        # Menu state
        self.is_open = False
        self.visible = True  # Can be hidden during special screens like "How to Play"

        # Menu panel dimensions
        self.menu_width = PRICE_MENU_WIDTH
        self.menu_height = PRICE_MENU_HEIGHT
        self.menu_x = screen.get_width() - self.menu_width - PRICE_BUTTON_MARGIN
        self.menu_y = PRICE_MENU_Y_OFFSET
        self.menu_rect = pygame.Rect(
            self.menu_x, self.menu_y, self.menu_width, self.menu_height
        )

    def handle_click(self, pos):
        """Handle mouse click - toggle menu if button clicked"""
        if self.button_rect.collidepoint(pos):
            self.is_open = not self.is_open
            return True
        return False

    def render_button(self):
        """Render the 'Show Prices' button"""
        # Button background
        color = DARK_GREEN if not self.is_open else DARK_RED
        pygame.draw.rect(self.screen, color, self.button_rect)
        pygame.draw.rect(self.screen, WHITE, self.button_rect, 2)

        # Button text
        text = "Hide Prices" if self.is_open else "Show Prices"
        text_surface = self.font_small.render(text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.button_rect.center)
        self.screen.blit(text_surface, text_rect)

    def render_menu(self):
        """Render the price menu panel"""
        if not self.is_open:
            return

        # Menu background with border
        pygame.draw.rect(self.screen, DARK_GRAY, self.menu_rect)
        pygame.draw.rect(self.screen, WHITE, self.menu_rect, 2)

        # Title
        title_surface = self.font_normal.render("GOODS PRICES", True, WHITE)
        title_rect = title_surface.get_rect(
            centerx=self.menu_rect.centerx, y=self.menu_y + 15
        )
        self.screen.blit(title_surface, title_rect)

        # Starting Y position for items
        y_offset = self.menu_y + 50

        # Legal goods section
        legal_title = self.font_normal.render("Legal Goods:", True, GREEN)
        self.screen.blit(legal_title, (self.menu_x + 20, y_offset))
        y_offset += 30

        # Sort legal goods by value
        sorted_legal = sorted(ALL_LEGAL, key=lambda g: g.value)

        for good in sorted_legal:
            # Good name and value
            name_surface = self.font_small.render(f"  {good.name}", True, WHITE)
            value_surface = self.font_small.render(f"{good.value} gold", True, GREEN)

            self.screen.blit(name_surface, (self.menu_x + 30, y_offset))
            self.screen.blit(value_surface, (self.menu_x + 220, y_offset))
            y_offset += 25

        # Separator
        y_offset += 10
        pygame.draw.line(
            self.screen,
            GRAY,
            (self.menu_x + 20, y_offset),
            (self.menu_x + self.menu_width - 20, y_offset),
            2,
        )
        y_offset += 20

        # Contraband section
        contraband_title = self.font_normal.render("Contraband:", True, RED)
        self.screen.blit(contraband_title, (self.menu_x + 20, y_offset))
        y_offset += 30

        # Sort contraband by value
        sorted_contraband = sorted(ALL_CONTRABAND, key=lambda g: g.value)

        for good in sorted_contraband:
            # Good name and value
            name_surface = self.font_small.render(f"  {good.name}", True, WHITE)
            value_surface = self.font_small.render(f"{good.value} gold", True, RED)

            self.screen.blit(name_surface, (self.menu_x + 30, y_offset))
            self.screen.blit(value_surface, (self.menu_x + 220, y_offset))
            y_offset += 25

        # Footer note
        y_offset += 15
        note_lines = [
            "Tip: Bribes should be based",
            "on the value of contraband",
            "being smuggled.",
        ]

        for line in note_lines:
            note_surface = self.font_small.render(line, True, LIGHT_GRAY)
            note_rect = note_surface.get_rect(
                centerx=self.menu_rect.centerx, y=y_offset
            )
            self.screen.blit(note_surface, note_rect)
            y_offset += 20

    def render(self):
        """Render both button and menu"""
        if not self.visible:
            return
        self.render_button()
        self.render_menu()
